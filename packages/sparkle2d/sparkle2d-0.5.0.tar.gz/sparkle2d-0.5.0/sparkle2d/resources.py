"""
Resource yönetimi - cache, refcount, preload
"""

import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import pyglet
from PIL import Image
import json


class ResourceManager:
    """Resource yönetimi - cache, refcount, preload"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._refcounts: Dict[str, int] = {}
        self._base_path = Path("assets")
    
    def set_base_path(self, path: str) -> None:
        """Asset base path'ini ayarla"""
        self._base_path = Path(path)
    
    def get_path(self, resource_path: str) -> Path:
        """Resource'ın tam yolunu döndür"""
        return self._base_path / resource_path
    
    def load_image(self, path: str) -> pyglet.image.ImageData:
        """Resim yükle (cache'li)"""
        full_path = self.get_path(path)
        
        if str(full_path) in self._cache:
            self._refcounts[str(full_path)] += 1
            return self._cache[str(full_path)]
        
        if not full_path.exists():
            raise FileNotFoundError(f"Resim bulunamadı: {full_path}")
        
        # PIL ile yükle ve pyglet'e dönüştür
        pil_image = Image.open(full_path)
        image_data = pil_image.convert("RGBA")
        
        # pyglet ImageData oluştur
        width, height = image_data.size
        raw_data = image_data.tobytes()
        
        pyglet_image = pyglet.image.ImageData(
            width, height, "RGBA", raw_data, pitch=width * 4
        )
        
        self._cache[str(full_path)] = pyglet_image
        self._refcounts[str(full_path)] = 1
        
        return pyglet_image
    
    def load_sound(self, path: str) -> pyglet.media.Source:
        """Ses dosyası yükle (cache'li)"""
        full_path = self.get_path(path)
        
        if str(full_path) in self._cache:
            self._refcounts[str(full_path)] += 1
            return self._cache[str(full_path)]
        
        if not full_path.exists():
            raise FileNotFoundError(f"Ses dosyası bulunamadı: {full_path}")
        
        sound = pyglet.media.load(str(full_path))
        self._cache[str(full_path)] = sound
        self._refcounts[str(full_path)] = 1
        
        return sound
    
    def load_json(self, path: str) -> dict:
        """JSON dosyası yükle (cache'li)"""
        full_path = self.get_path(path)
        
        if str(full_path) in self._cache:
            self._refcounts[str(full_path)] += 1
            return self._cache[str(full_path)]
        
        if not full_path.exists():
            raise FileNotFoundError(f"JSON dosyası bulunamadı: {full_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self._cache[str(full_path)] = data
        self._refcounts[str(full_path)] = 1
        
        return data
    
    def unload(self, path: str) -> None:
        """Resource'ı unload et (refcount azalt)"""
        full_path = str(self.get_path(path))
        
        if full_path in self._refcounts:
            self._refcounts[full_path] -= 1
            
            if self._refcounts[full_path] <= 0:
                # Refcount 0 ise cache'den kaldır
                del self._cache[full_path]
                del self._refcounts[full_path]
    
    def preload(self, paths: list[str]) -> None:
        """Birden fazla resource'ı önceden yükle"""
        for path in paths:
            try:
                if path.endswith(('.png', '.jpg', '.jpeg')):
                    self.load_image(path)
                elif path.endswith(('.wav', '.ogg', '.mp3')):
                    self.load_sound(path)
                elif path.endswith('.json'):
                    self.load_json(path)
            except Exception as e:
                print(f"Preload hatası {path}: {e}")
    
    def clear_cache(self) -> None:
        """Tüm cache'i temizle"""
        self._cache.clear()
        self._refcounts.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """Cache bilgilerini döndür"""
        return {
            path: count for path, count in self._refcounts.items()
        }
