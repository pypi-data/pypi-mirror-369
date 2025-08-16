"""
Particle sistemi - rate, life, speed, gravity, color/alpha over time
"""

from typing import List, Dict, Tuple, Optional, Callable
import random
import math
import time


class Particle:
    """Tekil parçacık"""
    
    def __init__(self, x: float, y: float, config: Dict):
        # Pozisyon
        self.x = x
        self.y = y
        
        # Hız
        speed = config.get('speed', 50.0)
        angle = config.get('angle', 0.0)
        angle_variance = config.get('angle_variance', 360.0)
        
        final_angle = angle + random.uniform(-angle_variance/2, angle_variance/2)
        final_angle_rad = math.radians(final_angle)
        
        self.vx = math.cos(final_angle_rad) * speed
        self.vy = math.sin(final_angle_rad) * speed
        
        # Yaşam
        self.life = config.get('life', 1.0)
        self.max_life = self.life
        
        # Renk
        self.color = config.get('color', (255, 255, 255, 255))
        self.start_color = self.color
        self.end_color = config.get('end_color', self.color)
        
        # Boyut
        self.size = config.get('size', 4.0)
        self.start_size = self.size
        self.end_size = config.get('end_size', self.size)
        
        # Yerçekimi
        self.gravity = config.get('gravity', (0, -100))
        
        # Sürtünme
        self.friction = config.get('friction', 0.98)
        
        # Durum
        self.active = True
    
    def update(self, dt: float) -> None:
        """Parçacığı güncelle"""
        if not self.active:
            return
        
        # Yaşam azalt
        self.life -= dt
        if self.life <= 0:
            self.active = False
            return
        
        # Pozisyon güncelle
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Yerçekimi uygula
        self.vx += self.gravity[0] * dt
        self.vy += self.gravity[1] * dt
        
        # Sürtünme uygula
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Renk ve boyut interpolasyonu
        progress = 1.0 - (self.life / self.max_life)
        
        # Renk interpolasyonu
        r = int(self.start_color[0] + (self.end_color[0] - self.start_color[0]) * progress)
        g = int(self.start_color[1] + (self.end_color[1] - self.start_color[1]) * progress)
        b = int(self.start_color[2] + (self.end_color[2] - self.start_color[2]) * progress)
        a = int(self.start_color[3] + (self.end_color[3] - self.start_color[3]) * progress)
        
        self.color = (r, g, b, a)
        
        # Boyut interpolasyonu
        self.size = self.start_size + (self.end_size - self.start_size) * progress
    
    def get_alpha(self) -> float:
        """Alpha değerini döndür"""
        return self.color[3] / 255.0
    
    def is_dead(self) -> bool:
        """Parçacık öldü mü kontrol et"""
        return not self.active


class ParticleEmitter:
    """Parçacık yayıcı"""
    
    def __init__(self, config: Dict):
        # Temel ayarlar
        self.rate = config.get('rate', 10.0)  # Parçacık/saniye
        self.burst_count = config.get('burst_count', 1)  # Patlama sayısı
        self.max_particles = config.get('max_particles', 100)
        
        # Pozisyon
        self.x = config.get('x', 0.0)
        self.y = config.get('y', 0.0)
        
        # Yayılma alanı
        self.area_width = config.get('area_width', 0.0)
        self.area_height = config.get('area_height', 0.0)
        
        # Parçacık konfigürasyonu
        self.particle_config = {
            'speed': config.get('speed', 50.0),
            'angle': config.get('angle', 0.0),
            'angle_variance': config.get('angle_variance', 360.0),
            'life': config.get('life', 1.0),
            'color': config.get('color', (255, 255, 255, 255)),
            'end_color': config.get('end_color', (255, 255, 255, 0)),
            'size': config.get('size', 4.0),
            'end_size': config.get('end_size', 1.0),
            'gravity': config.get('gravity', (0, -100)),
            'friction': config.get('friction', 0.98)
        }
        
        # Durum
        self.active = True
        self.particles: List[Particle] = []
        self.emission_timer = 0.0
        self.emission_interval = 1.0 / self.rate if self.rate > 0 else 0.0
        
        # Özel ayarlar
        self.one_shot = config.get('one_shot', False)
        self.duration = config.get('duration', -1.0)  # -1 = sonsuz
        self.elapsed = 0.0
    
    def set_position(self, x: float, y: float) -> None:
        """Pozisyon ayarla"""
        self.x = x
        self.y = y
    
    def emit_particle(self) -> None:
        """Parçacık yay"""
        if len(self.particles) >= self.max_particles:
            return
        
        # Yayılma alanından rastgele pozisyon
        px = self.x + random.uniform(-self.area_width/2, self.area_width/2)
        py = self.y + random.uniform(-self.area_height/2, self.area_height/2)
        
        particle = Particle(px, py, self.particle_config)
        self.particles.append(particle)
    
    def burst(self, count: Optional[int] = None) -> None:
        """Patlama efekti"""
        burst_count = count or self.burst_count
        for _ in range(burst_count):
            self.emit_particle()
    
    def update(self, dt: float) -> None:
        """Emitter'ı güncelle"""
        if not self.active:
            return
        
        self.elapsed += dt
        
        # Süre kontrolü
        if self.duration > 0 and self.elapsed >= self.duration:
            self.active = False
            return
        
        # Sürekli yayma
        if not self.one_shot and self.rate > 0:
            self.emission_timer += dt
            while self.emission_timer >= self.emission_interval:
                self.emit_particle()
                self.emission_timer -= self.emission_interval
        
        # Parçacıkları güncelle
        dead_particles = []
        for particle in self.particles:
            particle.update(dt)
            if particle.is_dead():
                dead_particles.append(particle)
        
        # Ölü parçacıkları kaldır
        for particle in dead_particles:
            self.particles.remove(particle)
    
    def draw(self) -> None:
        """Parçacıkları çiz"""
        import pyglet.gl as gl
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        for particle in self.particles:
            if particle.active:
                # Renk ayarla
                r, g, b, a = particle.color
                gl.glColor4f(r/255.0, g/255.0, b/255.0, a/255.0)
                
                # Parçacık çiz (basit kare)
                size = particle.size
                gl.glBegin(gl.GL_QUADS)
                gl.glVertex2f(particle.x - size, particle.y - size)
                gl.glVertex2f(particle.x + size, particle.y - size)
                gl.glVertex2f(particle.x + size, particle.y + size)
                gl.glVertex2f(particle.x - size, particle.y + size)
                gl.glEnd()
        
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
    
    def stop(self) -> None:
        """Emitter'ı durdur"""
        self.active = False
    
    def reset(self) -> None:
        """Emitter'ı sıfırla"""
        self.active = True
        self.particles.clear()
        self.emission_timer = 0.0
        self.elapsed = 0.0
    
    def get_particle_count(self) -> int:
        """Aktif parçacık sayısını döndür"""
        return len(self.particles)
    
    def is_finished(self) -> bool:
        """Emitter bitti mi kontrol et"""
        return not self.active and len(self.particles) == 0


class ParticleManager:
    """Parçacık yöneticisi"""
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
    
    def create_emitter(self, config: Dict) -> ParticleEmitter:
        """Emitter oluştur"""
        emitter = ParticleEmitter(config)
        self.emitters.append(emitter)
        return emitter
    
    def remove_emitter(self, emitter: ParticleEmitter) -> None:
        """Emitter kaldır"""
        if emitter in self.emitters:
            self.emitters.remove(emitter)
    
    def update(self, dt: float) -> None:
        """Tüm emitter'ları güncelle"""
        finished_emitters = []
        
        for emitter in self.emitters:
            emitter.update(dt)
            if emitter.is_finished():
                finished_emitters.append(emitter)
        
        # Biten emitter'ları kaldır
        for emitter in finished_emitters:
            self.emitters.remove(emitter)
    
    def draw(self) -> None:
        """Tüm emitter'ları çiz"""
        for emitter in self.emitters:
            emitter.draw()
    
    def clear(self) -> None:
        """Tüm emitter'ları temizle"""
        self.emitters.clear()
    
    def get_total_particles(self) -> int:
        """Toplam parçacık sayısını döndür"""
        return sum(emitter.get_particle_count() for emitter in self.emitters)
