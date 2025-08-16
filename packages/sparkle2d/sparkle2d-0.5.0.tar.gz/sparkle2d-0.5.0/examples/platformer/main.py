"""
Platformer örnek oyunu
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sparkle2d.app import App
from sparkle2d.scene import Scene
from sparkle2d.ecs import Entity, Transform, Sprite, Tag
from sparkle2d.systems.render import RenderSystem
from sparkle2d.systems.input import InputSystem


class PlatformerScene(Scene):
    """Platformer oyun sahnesi"""
    
    def __init__(self):
        super().__init__()
        self.player = None
        self.render_system = None
        self.input_system = None
    
    def on_enter(self):
        """Scene'e girildiğinde"""
        super().on_enter()
        
        # Sistemleri ekle
        self.render_system = RenderSystem(self.app.camera)
        self.input_system = InputSystem(self.app.input_map)
        
        self.app.entity_manager.add_system(self.render_system)
        self.app.entity_manager.add_system(self.input_system)
        
        # Input bağlantıları
        self.app.input_map.bind("move_left", "A,LEFT")
        self.app.input_map.bind("move_right", "D,RIGHT")
        self.app.input_map.bind("jump", "SPACE")
        
        # Player oluştur
        self.player = self.app.entity_manager.create_entity()
        self.player.add_component(Transform(x=100, y=100))
        self.player.add_component(Sprite(width=32, height=32))
        self.player.add_component(Tag(name="player"))
        
        # Lua script yükle
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "player.lua")
        if os.path.exists(script_path):
            self.script = self.app.scripting.load_script(script_path)
            self.script.start()
        
        # Hot reload etkinleştir
        self.app.scripting.enable_watchdog(os.path.join(os.path.dirname(__file__), "scripts"))
    
    def update(self, dt):
        """Scene güncelleme"""
        super().update(dt)
        
        # Player hareketi
        if self.player:
            transform = self.player.get_component(Transform)
            
            # Input kontrolü
            if self.app.input_map.action_down("move_left"):
                transform.x -= 100 * dt
            if self.app.input_map.action_down("move_right"):
                transform.x += 100 * dt
            if self.app.input_map.action_pressed("jump"):
                # Basit zıplama
                transform.y += 50
        
        # Kamera player'ı takip etsin
        if self.player:
            transform = self.player.get_component(Transform)
            self.app.camera.follow(self.player, 0.1)
    
    def draw(self):
        """Scene çizim"""
        # Arka plan
        import pyglet.gl as gl
        gl.glClearColor(0.2, 0.3, 0.5, 1.0)
        
        # Scene çizimini çağır
        super().draw()


def main():
    """Ana fonksiyon"""
    # Uygulama oluştur
    app = App(title="Sparkle2D Platformer", width=800, height=600)
    
    # Scene ekle
    scene = PlatformerScene()
    app.push_scene(scene)
    
    # Uygulamayı çalıştır
    app.run()


if __name__ == "__main__":
    main()
