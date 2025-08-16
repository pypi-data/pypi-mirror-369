"""
Scene yönetimi - push/pop/replace
"""

from typing import Optional, List
from abc import ABC, abstractmethod


class Scene(ABC):
    """Base scene sınıfı"""
    
    def __init__(self):
        self.app = None
        self.is_active = False
        self.is_paused = False
    
    def set_app(self, app) -> None:
        """App referansını ayarla"""
        self.app = app
    
    def on_enter(self) -> None:
        """Scene'e girildiğinde çağrılır"""
        self.is_active = True
        self.is_paused = False
    
    def on_exit(self) -> None:
        """Scene'den çıkıldığında çağrılır"""
        self.is_active = False
    
    def on_pause(self) -> None:
        """Scene duraklatıldığında çağrılır"""
        self.is_paused = True
    
    def on_resume(self) -> None:
        """Scene devam ettirildiğinde çağrılır"""
        self.is_paused = False
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Scene güncelleme"""
        pass
    
    @abstractmethod
    def draw(self) -> None:
        """Scene çizim"""
        pass
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Tuş basma eventi"""
        pass
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Tuş bırakma eventi"""
        pass
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Fare basma eventi"""
        pass
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Fare bırakma eventi"""
        pass
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """Fare hareket eventi"""
        pass


class SceneManager:
    """Scene yöneticisi"""
    
    def __init__(self, app):
        self.app = app
        self.scenes: List[Scene] = []
        self.current_scene: Optional[Scene] = None
    
    def push_scene(self, scene: Scene) -> None:
        """Scene'i stack'e ekle"""
        # Mevcut scene'i duraklat
        if self.current_scene:
            self.current_scene.on_pause()
        
        # Yeni scene'i ayarla
        scene.set_app(self.app)
        scene.on_enter()
        
        self.scenes.append(scene)
        self.current_scene = scene
    
    def pop_scene(self) -> Optional[Scene]:
        """En üstteki scene'i kaldır"""
        if not self.scenes:
            return None
        
        # Mevcut scene'i çıkar
        old_scene = self.scenes.pop()
        old_scene.on_exit()
        
        # Önceki scene'i devam ettir
        if self.scenes:
            self.current_scene = self.scenes[-1]
            self.current_scene.on_resume()
        else:
            self.current_scene = None
        
        return old_scene
    
    def replace_scene(self, scene: Scene) -> Optional[Scene]:
        """Mevcut scene'i yeni scene ile değiştir"""
        old_scene = None
        
        if self.scenes:
            old_scene = self.scenes.pop()
            old_scene.on_exit()
        
        # Yeni scene'i ekle
        scene.set_app(self.app)
        scene.on_enter()
        
        self.scenes.append(scene)
        self.current_scene = scene
        
        return old_scene
    
    def clear_scenes(self) -> None:
        """Tüm scene'leri temizle"""
        for scene in self.scenes:
            scene.on_exit()
        
        self.scenes.clear()
        self.current_scene = None
    
    def update(self, dt: float) -> None:
        """Aktif scene'i güncelle"""
        if self.current_scene and self.current_scene.is_active and not self.current_scene.is_paused:
            self.current_scene.update(dt)
    
    def draw(self) -> None:
        """Aktif scene'i çiz"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.draw()
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Tuş basma eventi"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.on_key_press(symbol, modifiers)
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Tuş bırakma eventi"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.on_key_release(symbol, modifiers)
    
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Fare basma eventi"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.on_mouse_press(x, y, button, modifiers)
    
    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Fare bırakma eventi"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.on_mouse_release(x, y, button, modifiers)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """Fare hareket eventi"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.on_mouse_motion(x, y, dx, dy)
    
    def get_current_scene(self) -> Optional[Scene]:
        """Aktif scene'i döndür"""
        return self.current_scene
    
    def get_scene_count(self) -> int:
        """Scene sayısını döndür"""
        return len(self.scenes)
