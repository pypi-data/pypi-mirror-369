"""
Fizik sistemi - pymunk wrapper
"""

from typing import Dict, List, Callable, Optional, Tuple, Any
import pymunk
import pymunk.pygame_util


class PhysicsWorld:
    """Pymunk tabanlı fizik dünyası"""
    
    def __init__(self, gravity: Tuple[float, float] = (0, -981)):
        self.space = pymunk.Space()
        self.space.gravity = gravity
        
        # Body ve shape yönetimi
        self.bodies: Dict[int, pymunk.Body] = {}
        self.shapes: Dict[int, pymunk.Shape] = {}
        self.body_to_entity: Dict[int, str] = {}
        self.entity_to_body: Dict[str, int] = {}
        
        # Çarpışma callback'leri
        self.collision_handlers: Dict[Tuple[str, str], Callable] = {}
        self.collision_begin_handlers: Dict[Tuple[str, str], Callable] = {}
        self.collision_end_handlers: Dict[Tuple[str, str], Callable] = {}
        
        # Çarpışma filtreleri
        self.collision_filters: Dict[str, int] = {}
        self.next_filter_id = 1
        
        # Debug çizim
        self.debug_draw = False
    
    def create_body(self, body_type: str = "dynamic", position: Tuple[float, float] = (0, 0), 
                   angle: float = 0.0, mass: float = 1.0, moment: Optional[float] = None) -> int:
        """Fizik body oluştur"""
        # Body tipi
        if body_type == "static":
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        elif body_type == "kinematic":
            body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        else:  # dynamic
            body = pymunk.Body(mass=mass, moment=moment or pymunk.moment_for_circle(mass, 0, 14))
        
        # Pozisyon ve açı
        body.position = position
        body.angle = angle
        
        # Space'e ekle
        self.space.add(body)
        
        # Yönetim
        body_id = id(body)
        self.bodies[body_id] = body
        
        return body_id
    
    def create_circle_shape(self, body_id: int, radius: float, offset: Tuple[float, float] = (0, 0),
                           density: float = 1.0, friction: float = 0.7, 
                           elasticity: float = 0.5, collision_type: str = "default") -> int:
        """Daire şekli oluştur"""
        if body_id not in self.bodies:
            raise ValueError(f"Body bulunamadı: {body_id}")
        
        body = self.bodies[body_id]
        shape = pymunk.Circle(body, radius, offset)
        
        # Özellikler
        shape.density = density
        shape.friction = friction
        shape.elasticity = elasticity
        
        # Çarpışma tipi
        if collision_type not in self.collision_filters:
            self.collision_filters[collision_type] = self.next_filter_id
            self.next_filter_id += 1
        
        shape.collision_type = self.collision_filters[collision_type]
        
        # Space'e ekle
        self.space.add(shape)
        
        # Yönetim
        shape_id = id(shape)
        self.shapes[shape_id] = shape
        
        return shape_id
    
    def create_box_shape(self, body_id: int, size: Tuple[float, float], 
                        offset: Tuple[float, float] = (0, 0), density: float = 1.0,
                        friction: float = 0.7, elasticity: float = 0.5, 
                        collision_type: str = "default") -> int:
        """Kutu şekli oluştur"""
        if body_id not in self.bodies:
            raise ValueError(f"Body bulunamadı: {body_id}")
        
        body = self.bodies[body_id]
        shape = pymunk.Poly.create_box(body, size, offset)
        
        # Özellikler
        shape.density = density
        shape.friction = friction
        shape.elasticity = elasticity
        
        # Çarpışma tipi
        if collision_type not in self.collision_filters:
            self.collision_filters[collision_type] = self.next_filter_id
            self.next_filter_id += 1
        
        shape.collision_type = self.collision_filters[collision_type]
        
        # Space'e ekle
        self.space.add(shape)
        
        # Yönetim
        shape_id = id(shape)
        self.shapes[shape_id] = shape
        
        return shape_id
    
    def create_polygon_shape(self, body_id: int, vertices: List[Tuple[float, float]],
                           offset: Tuple[float, float] = (0, 0), density: float = 1.0,
                           friction: float = 0.7, elasticity: float = 0.5,
                           collision_type: str = "default") -> int:
        """Çokgen şekli oluştur"""
        if body_id not in self.bodies:
            raise ValueError(f"Body bulunamadı: {body_id}")
        
        body = self.bodies[body_id]
        shape = pymunk.Poly(body, vertices, offset)
        
        # Özellikler
        shape.density = density
        shape.friction = friction
        shape.elasticity = elasticity
        
        # Çarpışma tipi
        if collision_type not in self.collision_filters:
            self.collision_filters[collision_type] = self.next_filter_id
            self.next_filter_id += 1
        
        shape.collision_type = self.collision_filters[collision_type]
        
        # Space'e ekle
        self.space.add(shape)
        
        # Yönetim
        shape_id = id(shape)
        self.shapes[shape_id] = shape
        
        return shape_id
    
    def link_entity_to_body(self, entity_id: str, body_id: int) -> None:
        """Entity'yi body ile bağla"""
        self.body_to_entity[body_id] = entity_id
        self.entity_to_body[entity_id] = body_id
    
    def unlink_entity(self, entity_id: str) -> None:
        """Entity bağlantısını kaldır"""
        if entity_id in self.entity_to_body:
            body_id = self.entity_to_body[entity_id]
            del self.entity_to_body[entity_id]
            if body_id in self.body_to_entity:
                del self.body_to_entity[body_id]
    
    def get_body_position(self, body_id: int) -> Tuple[float, float]:
        """Body pozisyonunu döndür"""
        if body_id in self.bodies:
            pos = self.bodies[body_id].position
            return (pos.x, pos.y)
        return (0, 0)
    
    def get_body_angle(self, body_id: int) -> float:
        """Body açısını döndür"""
        if body_id in self.bodies:
            return self.bodies[body_id].angle
        return 0.0
    
    def set_body_position(self, body_id: int, position: Tuple[float, float]) -> None:
        """Body pozisyonunu ayarla"""
        if body_id in self.bodies:
            self.bodies[body_id].position = position
    
    def set_body_angle(self, body_id: int, angle: float) -> None:
        """Body açısını ayarla"""
        if body_id in self.bodies:
            self.bodies[body_id].angle = angle
    
    def set_body_velocity(self, body_id: int, velocity: Tuple[float, float]) -> None:
        """Body hızını ayarla"""
        if body_id in self.bodies:
            self.bodies[body_id].velocity = velocity
    
    def get_body_velocity(self, body_id: int) -> Tuple[float, float]:
        """Body hızını döndür"""
        if body_id in self.bodies:
            vel = self.bodies[body_id].velocity
            return (vel.x, vel.y)
        return (0, 0)
    
    def apply_force(self, body_id: int, force: Tuple[float, float], point: Optional[Tuple[float, float]] = None) -> None:
        """Body'ye kuvvet uygula"""
        if body_id in self.bodies:
            if point:
                self.bodies[body_id].apply_force_at_local_point(force, point)
            else:
                self.bodies[body_id].apply_force_at_local_point(force, (0, 0))
    
    def apply_impulse(self, body_id: int, impulse: Tuple[float, float], point: Optional[Tuple[float, float]] = None) -> None:
        """Body'ye impuls uygula"""
        if body_id in self.bodies:
            if point:
                self.bodies[body_id].apply_impulse_at_local_point(impulse, point)
            else:
                self.bodies[body_id].apply_impulse_at_local_point(impulse, (0, 0))
    
    def on_begin_contact(self, collision_type_a: str, collision_type_b: str, callback: Callable) -> None:
        """Çarpışma başlangıç callback'i"""
        key = (collision_type_a, collision_type_b)
        self.collision_begin_handlers[key] = callback
    
    def on_end_contact(self, collision_type_a: str, collision_type_b: str, callback: Callable) -> None:
        """Çarpışma bitiş callback'i"""
        key = (collision_type_a, collision_type_b)
        self.collision_end_handlers[key] = callback
    
    def _setup_collision_handlers(self) -> None:
        """Çarpışma handler'larını ayarla"""
        # Mevcut handler'ları temizle
        for handler in self.space.collision_handlers.values():
            self.space.remove_collision_handler(handler)
        
        # Yeni handler'ları ekle
        for (type_a, type_b), callback in self.collision_begin_handlers.items():
            if type_a in self.collision_filters and type_b in self.collision_filters:
                handler = self.space.add_collision_handler(
                    self.collision_filters[type_a],
                    self.collision_filters[type_b]
                )
                handler.begin = callback
        
        for (type_a, type_b), callback in self.collision_end_handlers.items():
            if type_a in self.collision_filters and type_b in self.collision_filters:
                handler = self.space.add_collision_handler(
                    self.collision_filters[type_a],
                    self.collision_filters[type_b]
                )
                handler.separate = callback
    
    def update(self, dt: float) -> None:
        """Fizik dünyasını güncelle"""
        # Çarpışma handler'larını güncelle
        self._setup_collision_handlers()
        
        # Fizik simülasyonu
        self.space.step(dt)
    
    def remove_body(self, body_id: int) -> None:
        """Body'yi kaldır"""
        if body_id in self.bodies:
            body = self.bodies[body_id]
            
            # Shape'leri kaldır
            shapes_to_remove = []
            for shape_id, shape in self.shapes.items():
                if shape.body == body:
                    shapes_to_remove.append(shape_id)
            
            for shape_id in shapes_to_remove:
                self.space.remove(self.shapes[shape_id])
                del self.shapes[shape_id]
            
            # Body'yi kaldır
            self.space.remove(body)
            del self.bodies[body_id]
    
    def remove_shape(self, shape_id: int) -> None:
        """Shape'i kaldır"""
        if shape_id in self.shapes:
            self.space.remove(self.shapes[shape_id])
            del self.shapes[shape_id]
    
    def set_gravity(self, gravity: Tuple[float, float]) -> None:
        """Yerçekimini ayarla"""
        self.space.gravity = gravity
    
    def get_gravity(self) -> Tuple[float, float]:
        """Yerçekimini döndür"""
        return self.space.gravity
    
    def enable_debug_draw(self, enabled: bool = True) -> None:
        """Debug çizimi etkinleştir"""
        self.debug_draw = enabled
    
    def draw_debug(self, surface) -> None:
        """Debug çizimi"""
        if self.debug_draw:
            # Pygame surface için debug çizimi
            draw_options = pymunk.pygame_util.DrawOptions(surface)
            self.space.debug_draw(draw_options)
    
    def clear(self) -> None:
        """Tüm fizik nesnelerini temizle"""
        # Shape'leri temizle
        for shape in self.shapes.values():
            self.space.remove(shape)
        self.shapes.clear()
        
        # Body'leri temizle
        for body in self.bodies.values():
            self.space.remove(body)
        self.bodies.clear()
        
        # Bağlantıları temizle
        self.body_to_entity.clear()
        self.entity_to_body.clear()
        
        # Çarpışma handler'larını temizle
        self.collision_begin_handlers.clear()
        self.collision_end_handlers.clear()
