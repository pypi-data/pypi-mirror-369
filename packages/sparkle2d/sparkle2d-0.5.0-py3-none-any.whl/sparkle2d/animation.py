"""
Animasyon sistemi - JSON atlas, frame durations
"""

from typing import Dict, List, Optional, Any
import json
import time


class Animation:
    """Tekil animasyon"""
    
    def __init__(self, name: str, frames: List[Dict], fps: float = 12.0, loop: bool = True):
        self.name = name
        self.frames = frames
        self.fps = fps
        self.loop = loop
        
        # Frame süreleri
        self.frame_duration = 1.0 / fps
        self.total_duration = len(frames) * self.frame_duration
        
        # Durum
        self.current_frame = 0
        self.elapsed = 0.0
        self.is_playing = False
        self.is_finished = False
    
    def play(self) -> None:
        """Animasyonu başlat"""
        self.is_playing = True
        self.is_finished = False
        self.current_frame = 0
        self.elapsed = 0.0
    
    def pause(self) -> None:
        """Animasyonu duraklat"""
        self.is_playing = False
    
    def stop(self) -> None:
        """Animasyonu durdur"""
        self.is_playing = False
        self.is_finished = False
        self.current_frame = 0
        self.elapsed = 0.0
    
    def update(self, dt: float) -> None:
        """Animasyonu güncelle"""
        if not self.is_playing or self.is_finished:
            return
        
        self.elapsed += dt
        
        # Frame değişimi kontrolü
        while self.elapsed >= self.frame_duration:
            self.elapsed -= self.frame_duration
            self.current_frame += 1
            
            # Son frame kontrolü
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_finished = True
                    self.is_playing = False
    
    def get_current_frame(self) -> Optional[Dict]:
        """Mevcut frame'i döndür"""
        if 0 <= self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None
    
    def set_frame(self, frame_index: int) -> None:
        """Belirli frame'e geç"""
        if 0 <= frame_index < len(self.frames):
            self.current_frame = frame_index
            self.elapsed = 0.0
    
    def get_progress(self) -> float:
        """Animasyon ilerlemesini döndür (0.0 - 1.0)"""
        if len(self.frames) <= 1:
            return 1.0
        return self.current_frame / (len(self.frames) - 1)


class Animator:
    """Animasyon yöneticisi"""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
        self.sprite = None  # Sprite referansı
    
    def add_animation(self, animation: Animation) -> None:
        """Animasyon ekle"""
        self.animations[animation.name] = animation
    
    def remove_animation(self, name: str) -> None:
        """Animasyon kaldır"""
        if name in self.animations:
            del self.animations[name]
            if self.current_animation == name:
                self.current_animation = None
    
    def play(self, name: str) -> bool:
        """Animasyon oynat"""
        if name in self.animations:
            self.current_animation = name
            self.animations[name].play()
            return True
        return False
    
    def pause(self) -> None:
        """Mevcut animasyonu duraklat"""
        if self.current_animation:
            self.animations[self.current_animation].pause()
    
    def stop(self) -> None:
        """Mevcut animasyonu durdur"""
        if self.current_animation:
            self.animations[self.current_animation].stop()
    
    def update(self, dt: float) -> None:
        """Animasyonu güncelle"""
        if self.current_animation:
            self.animations[self.current_animation].update(dt)
    
    def get_current_frame(self) -> Optional[Dict]:
        """Mevcut frame'i döndür"""
        if self.current_animation:
            return self.animations[self.current_animation].get_current_frame()
        return None
    
    def is_playing(self, name: Optional[str] = None) -> bool:
        """Animasyon oynatılıyor mu kontrol et"""
        if name:
            return name in self.animations and self.animations[name].is_playing
        return (self.current_animation and 
                self.animations[self.current_animation].is_playing)
    
    def is_finished(self) -> bool:
        """Animasyon bitti mi kontrol et"""
        if self.current_animation:
            return self.animations[self.current_animation].is_finished
        return True
    
    def get_current_animation_name(self) -> Optional[str]:
        """Mevcut animasyon adını döndür"""
        return self.current_animation


class AnimationLoader:
    """JSON atlas animasyon yükleyici"""
    
    @staticmethod
    def load_from_json(json_path: str) -> Dict[str, Animation]:
        """JSON dosyasından animasyon yükle"""
        animations = {}
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Atlas bilgileri
            atlas_width = data.get('atlas_width', 1)
            atlas_height = data.get('atlas_height', 1)
            
            # Animasyonlar
            for anim_data in data.get('animations', []):
                name = anim_data.get('name', '')
                fps = anim_data.get('fps', 12.0)
                loop = anim_data.get('loop', True)
                
                frames = []
                for frame_data in anim_data.get('frames', []):
                    frame = {
                        'x': frame_data.get('x', 0),
                        'y': frame_data.get('y', 0),
                        'width': frame_data.get('width', 32),
                        'height': frame_data.get('height', 32),
                        'duration': frame_data.get('duration', 1.0 / fps)
                    }
                    frames.append(frame)
                
                if frames:
                    animation = Animation(name, frames, fps, loop)
                    animations[name] = animation
            
        except Exception as e:
            print(f"Animasyon yükleme hatası {json_path}: {e}")
        
        return animations
    
    @staticmethod
    def create_simple_animation(name: str, frame_count: int, fps: float = 12.0, 
                               frame_width: int = 32, frame_height: int = 32) -> Animation:
        """Basit animasyon oluştur"""
        frames = []
        for i in range(frame_count):
            frame = {
                'x': i * frame_width,
                'y': 0,
                'width': frame_width,
                'height': frame_height,
                'duration': 1.0 / fps
            }
            frames.append(frame)
        
        return Animation(name, frames, fps)
