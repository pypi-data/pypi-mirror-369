"""
2D Kamera sistemi - zoom, follow, bounds, world<->screen dönüşümleri
"""

from typing import Optional, Tuple, List
import pyglet
import pyglet.gl as gl
import math


class Camera2D:
    """2D Kamera sistemi"""
    
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        
        # Pozisyon ve zoom
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0
        
        # Sınırlar
        self.bounds = None  # (min_x, min_y, max_x, max_y)
        
        # Takip edilen entity
        self.follow_target = None
        self.follow_lerp = 0.1
        
        # Shake efekti
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0
    
    def set_position(self, x: float, y: float) -> None:
        """Kamera pozisyonunu ayarla"""
        self.x = x
        self.y = y
        self._apply_bounds()
    
    def set_zoom(self, zoom: float) -> None:
        """Zoom seviyesini ayarla"""
        self.zoom = max(0.1, min(10.0, zoom))
    
    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        """Kamera sınırlarını ayarla"""
        self.bounds = (min_x, min_y, max_x, max_y)
        self._apply_bounds()
    
    def clear_bounds(self) -> None:
        """Kamera sınırlarını kaldır"""
        self.bounds = None
    
    def follow(self, target, lerp: float = 0.1) -> None:
        """Entity'yi takip et"""
        self.follow_target = target
        self.follow_lerp = lerp
    
    def unfollow(self) -> None:
        """Takibi durdur"""
        self.follow_target = None
    
    def shake(self, intensity: float, duration: float) -> None:
        """Kamera sarsıntısı"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_timer = duration
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Dünya koordinatlarını ekran koordinatlarına dönüştür"""
        # Kamera pozisyonunu çıkar
        screen_x = (world_x - self.x) * self.zoom
        screen_y = (world_y - self.y) * self.zoom
        
        # Ekran merkezine kaydır
        screen_x += self.width / 2
        screen_y += self.height / 2
        
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Ekran koordinatlarını dünya koordinatlarına dönüştür"""
        # Ekran merkezini çıkar
        world_x = screen_x - self.width / 2
        world_y = screen_y - self.height / 2
        
        # Zoom'u geri al ve kamera pozisyonunu ekle
        world_x = world_x / self.zoom + self.x
        world_y = world_y / self.zoom + self.y
        
        return world_x, world_y
    
    def get_viewport(self) -> Tuple[float, float, float, float]:
        """Görüş alanını döndür (left, bottom, right, top)"""
        half_width = (self.width / 2) / self.zoom
        half_height = (self.height / 2) / self.zoom
        
        left = self.x - half_width
        bottom = self.y - half_height
        right = self.x + half_width
        top = self.y + half_height
        
        return left, bottom, right, top
    
    def is_in_view(self, x: float, y: float, margin: float = 0.0) -> bool:
        """Nokta görüş alanında mı kontrol et"""
        left, bottom, right, top = self.get_viewport()
        
        return (x >= left - margin and x <= right + margin and 
                y >= bottom - margin and y <= top + margin)
    
    def update(self, dt: float) -> None:
        """Kamerayı güncelle"""
        # Takip hedefini güncelle
        if self.follow_target and hasattr(self.follow_target, 'x') and hasattr(self.follow_target, 'y'):
            target_x = self.follow_target.x
            target_y = self.follow_target.y
            
            # Lerp ile yumuşak takip
            self.x += (target_x - self.x) * self.follow_lerp
            self.y += (target_y - self.y) * self.follow_lerp
        
        # Sınırları uygula
        self._apply_bounds()
        
        # Shake efektini güncelle
        if self.shake_timer > 0:
            self.shake_timer -= dt
            
            if self.shake_timer <= 0:
                self.shake_intensity = 0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            else:
                # Rastgele shake offset'i
                import random
                self.shake_offset_x = (random.random() - 0.5) * self.shake_intensity
                self.shake_offset_y = (random.random() - 0.5) * self.shake_intensity
    
    def begin(self) -> None:
        """Kamera transformasyonunu başlat"""
        gl.glPushMatrix()
        
        # Ekran merkezine kaydır
        gl.glTranslatef(self.width / 2, self.height / 2, 0)
        
        # Zoom uygula
        gl.glScalef(self.zoom, self.zoom, 1.0)
        
        # Kamera pozisyonunu çıkar
        gl.glTranslatef(-self.x, -self.y, 0)
        
        # Shake offset'i uygula
        if self.shake_intensity > 0:
            gl.glTranslatef(self.shake_offset_x, self.shake_offset_y, 0)
    
    def end(self) -> None:
        """Kamera transformasyonunu bitir"""
        gl.glPopMatrix()
    
    def _apply_bounds(self) -> None:
        """Kamera sınırlarını uygula"""
        if not self.bounds:
            return
        
        min_x, min_y, max_x, max_y = self.bounds
        
        # Zoom'a göre görüş alanı hesapla
        half_width = (self.width / 2) / self.zoom
        half_height = (self.height / 2) / self.zoom
        
        # X sınırları
        if self.x - half_width < min_x:
            self.x = min_x + half_width
        elif self.x + half_width > max_x:
            self.x = max_x - half_width
        
        # Y sınırları
        if self.y - half_height < min_y:
            self.y = min_y + half_height
        elif self.y + half_height > max_y:
            self.y = max_y - half_height
