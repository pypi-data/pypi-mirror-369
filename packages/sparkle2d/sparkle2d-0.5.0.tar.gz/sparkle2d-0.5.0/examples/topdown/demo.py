"""
Top-down demo oyunu
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from sparkle2d.app import App
from sparkle2d.scene import Scene
from sparkle2d.ecs import Entity, Transform, Sprite, Tag
from sparkle2d.systems.render import RenderSystem
from sparkle2d.particles import ParticleEmitter


class TopDownScene(Scene):
    """Top-down demo sahnesi"""
    
    def __init__(self):
        super().__init__()
        self.player = None
        self.particle_emitter = None
        self.render_system = None
    
    def on_enter(self):
        """Scene'e girildiğinde"""
        super().on_enter()
        
        # Render sistemi ekle
        self.render_system = RenderSystem(self.app.camera)
        self.app.entity_manager.add_system(self.render_system)
        
        # Input bağlantıları
        self.app.input_map.bind("move_left", "A,LEFT")
        self.app.input_map.bind("move_right", "D,RIGHT")
        self.app.input_map.bind("move_up", "W,UP")
        self.app.input_map.bind("move_down", "S,DOWN")
        self.app.input_map.bind("action", "SPACE")
        
        # Player oluştur
        self.player = self.app.entity_manager.create_entity()
        self.player.add_component(Transform(x=400, y=300))
        self.player.add_component(Sprite(width=32, height=32))
        self.player.add_component(Tag(name="player"))
        
        # Particle emitter oluştur
        self.particle_emitter = ParticleEmitter({
            'rate': 20,
            'life': 2.0,
            'speed': 30,
            'angle': 0,
            'angle_variance': 360,
            'gravity': (0, -50),
            'color': (255, 255, 255, 255),
            'end_color': (255, 255, 255, 0),
            'size': 3,
            'end_size': 1
        })
        
        # Kamera player'ı takip etsin
        self.app.camera.follow(self.player, 0.05)
    
    def update(self, dt):
        """Scene güncelleme"""
        super().update(dt)
        
        # Player hareketi
        if self.player:
            transform = self.player.get_component(Transform)
            
            # Input kontrolü
            if self.app.input_map.action_down("move_left"):
                transform.x -= 150 * dt
            if self.app.input_map.action_down("move_right"):
                transform.x += 150 * dt
            if self.app.input_map.action_down("move_up"):
                transform.y += 150 * dt
            if self.app.input_map.action_down("move_down"):
                transform.y -= 150 * dt
            
            # Particle emitter pozisyonunu güncelle
            if self.particle_emitter:
                self.particle_emitter.set_position(transform.x, transform.y)
                self.particle_emitter.update(dt)
            
            # Action tuşu ile particle burst
            if self.app.input_map.action_pressed("action"):
                if self.particle_emitter:
                    self.particle_emitter.burst(10)
    
    def draw(self):
        """Scene çizim"""
        # Arka plan
        import pyglet.gl as gl
        gl.glClearColor(0.1, 0.1, 0.2, 1.0)
        
        # Scene çizimini çağır
        super().draw()
        
        # Particle'ları çiz
        if self.particle_emitter:
            self.particle_emitter.draw()


def main():
    """Ana fonksiyon"""
    # Uygulama oluştur
    app = App(title="Sparkle2D Top-Down Demo", width=800, height=600)
    
    # Scene ekle
    scene = TopDownScene()
    app.push_scene(scene)
    
    # Uygulamayı çalıştır
    app.run()


if __name__ == "__main__":
    main()
