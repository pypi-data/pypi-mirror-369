"""
Ana uygulama sınıfı - lifecycle + main loop
"""

import pyglet
import pyglet.gl as gl
from typing import Optional
import time


class App:
    """Ana uygulama sınıfı"""
    
    def __init__(self, title: str = "Sparkle2D", width: int = 800, height: int = 600, 
                 vsync: bool = True, resizable: bool = True):
        # Pencere oluştur
        self.window = pyglet.window.Window(
            width=width, 
            height=height, 
            caption=title,
            vsync=vsync,
            resizable=resizable
        )
        
        # Temel özellikler
        self.width = width
        self.height = height
        self.running = False
        self.fps = 60
        self.max_dt = 1.0 / 30.0  # Max 30 FPS minimum
        
        # Zaman
        self.last_time = time.time()
        self.accumulator = 0.0
        
        # Sistemler
        from .events import EventBus
        from .resources import ResourceManager
        from .inputmap import InputMap
        from .camera import Camera2D
        from .tween import TweenManager
        from .scripting import ScriptingEngine
        from .ecs import EntityManager
        
        self.events = EventBus()
        self.resources = ResourceManager()
        self.input_map = InputMap()
        self.camera = Camera2D(width, height)
        self.tween_manager = TweenManager()
        self.scripting = ScriptingEngine(self)
        self.entity_manager = EntityManager()
        
        # Scene yöneticisi
        from .scene import SceneManager
        self.scene_manager = SceneManager(self)
        
        # Event bağlantıları
        self._setup_events()
        
        # OpenGL ayarları
        self._setup_gl()
    
    def _setup_events(self) -> None:
        """Event bağlantılarını ayarla"""
        self.window.push_handlers(
            on_key_press=self.input_map.on_key_press,
            on_key_release=self.input_map.on_key_release
        )
        
        # Scene event'lerini de bağla
        self.window.push_handlers(
            on_key_press=self.scene_manager.on_key_press,
            on_key_release=self.scene_manager.on_key_release,
            on_mouse_press=self.scene_manager.on_mouse_press,
            on_mouse_release=self.scene_manager.on_mouse_release,
            on_mouse_motion=self.scene_manager.on_mouse_motion
        )
    
    def _setup_gl(self) -> None:
        """OpenGL ayarları"""
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
    
    def push_scene(self, scene) -> None:
        """Scene ekle"""
        self.scene_manager.push_scene(scene)
    
    def pop_scene(self):
        """Scene kaldır"""
        return self.scene_manager.pop_scene()
    
    def replace_scene(self, scene):
        """Scene değiştir"""
        return self.scene_manager.replace_scene(scene)
    
    def update(self, dt: float) -> None:
        """Ana güncelleme döngüsü"""
        # DT clamp
        dt = min(dt, self.max_dt)
        
        # Input güncelle
        self.input_map.update()
        
        # Kamera güncelle
        self.camera.update(dt)
        
        # Tween güncelle
        self.tween_manager.update(dt)
        
        # Script güncelle
        self.scripting.update(dt)
        
        # Entity manager güncelle
        self.entity_manager.update(dt)
        
        # Scene güncelle
        self.scene_manager.update(dt)
    
    def draw(self) -> None:
        """Ana çizim döngüsü"""
        # Ekranı temizle
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        
        # Kamera transformasyonunu başlat
        self.camera.begin()
        
        # Scene çiz
        self.scene_manager.draw()
        
        # Kamera transformasyonunu bitir
        self.camera.end()
    
    def run(self) -> None:
        """Uygulamayı çalıştır"""
        self.running = True
        self.last_time = time.time()
        
        def on_draw():
            self.draw()
        
        def on_update(dt):
            self.update(dt)
        
        # Event handler'ları ayarla
        self.window.on_draw = on_draw
        
        # Pyglet event loop'u başlat
        pyglet.clock.schedule(on_update)
        pyglet.app.run()
    
    def quit(self) -> None:
        """Uygulamayı kapat"""
        self.running = False
        self.window.close()
    
    def set_fps(self, fps: int) -> None:
        """FPS ayarla"""
        self.fps = fps
        pyglet.clock.set_fps_limit(fps)
    
    def get_fps(self) -> float:
        """Mevcut FPS'i döndür"""
        return pyglet.clock.get_fps()
    
    def resize(self, width: int, height: int) -> None:
        """Pencere boyutunu değiştir"""
        self.width = width
        self.height = height
        self.camera.width = width
        self.camera.height = height
        gl.glViewport(0, 0, width, height)
    
    def set_title(self, title: str) -> None:
        """Pencere başlığını ayarla"""
        self.window.set_caption(title)
    
    def set_vsync(self, enabled: bool) -> None:
        """VSync ayarla"""
        self.window.set_vsync(enabled)
    
    def is_fullscreen(self) -> bool:
        """Tam ekran mı kontrol et"""
        return self.window.fullscreen
    
    def set_fullscreen(self, enabled: bool) -> None:
        """Tam ekran ayarla"""
        self.window.set_fullscreen(enabled)
    
    def get_mouse_position(self) -> tuple:
        """Fare pozisyonunu döndür"""
        return self.window.get_mouse_position()
    
    def set_mouse_visible(self, visible: bool) -> None:
        """Fare görünürlüğünü ayarla"""
        self.window.set_mouse_visible(visible)
    
    def set_mouse_position(self, x: int, y: int) -> None:
        """Fare pozisyonunu ayarla"""
        self.window.set_mouse_position(x, y)
