"""
Hafif Entity Component System
"""

from typing import Dict, List, Any, Optional, Type, Set
from dataclasses import dataclass
import uuid


class Component:
    """Base component sınıfı"""
    pass


@dataclass
class Transform(Component):
    """Transform component"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0


@dataclass
class Sprite(Component):
    """Sprite component"""
    image_path: str = ""
    image: Any = None
    width: float = 0.0
    height: float = 0.0
    alpha: float = 1.0
    visible: bool = True


@dataclass
class Tag(Component):
    """Tag component"""
    name: str = ""


@dataclass
class Physics(Component):
    """Physics component"""
    body_id: Optional[int] = None
    body_type: str = "dynamic"  # dynamic, static, kinematic
    gravity_scale: float = 1.0
    fixed_rotation: bool = False


class Entity:
    """Entity sınıfı"""
    
    def __init__(self, entity_id: Optional[str] = None):
        self.id = entity_id or str(uuid.uuid4())
        self.components: Dict[Type[Component], Component] = {}
        self.tags: Set[str] = set()
        self.active = True
    
    def add_component(self, component: Component) -> None:
        """Component ekle"""
        self.components[type(component)] = component
        
        # Tag component ise tags set'ine ekle
        if isinstance(component, Tag):
            self.tags.add(component.name)
    
    def remove_component(self, component_type: Type[Component]) -> None:
        """Component kaldır"""
        if component_type in self.components:
            component = self.components[component_type]
            
            # Tag component ise tags set'inden kaldır
            if isinstance(component, Tag):
                self.tags.discard(component.name)
            
            del self.components[component_type]
    
    def get_component(self, component_type: Type[Component]) -> Optional[Component]:
        """Component al"""
        return self.components.get(component_type)
    
    def has_component(self, component_type: Type[Component]) -> bool:
        """Component var mı kontrol et"""
        return component_type in self.components
    
    def has_tag(self, tag: str) -> bool:
        """Tag var mı kontrol et"""
        return tag in self.tags
    
    def destroy(self) -> None:
        """Entity'yi yok et"""
        self.active = False
        self.components.clear()
        self.tags.clear()


class System:
    """Base system sınıfı"""
    
    def __init__(self):
        self.entities: List[Entity] = []
        self.required_components: Set[Type[Component]] = set()
    
    def add_entity(self, entity: Entity) -> None:
        """Entity ekle"""
        if self._check_requirements(entity):
            self.entities.append(entity)
    
    def remove_entity(self, entity: Entity) -> None:
        """Entity kaldır"""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def _check_requirements(self, entity: Entity) -> bool:
        """Entity gerekli component'lere sahip mi kontrol et"""
        for component_type in self.required_components:
            if not entity.has_component(component_type):
                return False
        return True
    
    def update(self, dt: float) -> None:
        """System'i güncelle (override edilmeli)"""
        pass


class RenderSystem(System):
    """Render sistemi"""
    
    def __init__(self, camera):
        super().__init__()
        self.camera = camera
        self.required_components = {Transform, Sprite}
    
    def update(self, dt: float) -> None:
        """Render güncelleme"""
        # Aktif entity'leri filtrele
        active_entities = [e for e in self.entities if e.active]
        
        # Z sırasına göre sırala
        active_entities.sort(key=lambda e: e.get_component(Transform).z)
        
        # Render
        for entity in active_entities:
            self._render_entity(entity)
    
    def _render_entity(self, entity: Entity) -> None:
        """Entity'yi render et"""
        transform = entity.get_component(Transform)
        sprite = entity.get_component(Sprite)
        
        if not sprite.visible or not sprite.image:
            return
        
        # Kamera görüş alanında mı kontrol et
        if not self.camera.is_in_view(transform.x, transform.y, 
                                     max(sprite.width, sprite.height)):
            return
        
        # Render
        import pyglet.gl as gl
        gl.glPushMatrix()
        gl.glTranslatef(transform.x, transform.y, transform.z)
        gl.glRotatef(transform.rotation, 0, 0, 1)
        gl.glScalef(transform.scale_x, transform.scale_y, 1.0)
        
        # Alpha ayarla
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(1.0, 1.0, 1.0, sprite.alpha)
        
        # Sprite çiz
        sprite.image.blit(-sprite.width/2, -sprite.height/2)
        
        gl.glPopMatrix()
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)


class InputSystem(System):
    """Input sistemi"""
    
    def __init__(self, input_map):
        super().__init__()
        self.input_map = input_map
        self.required_components = {Transform}
    
    def update(self, dt: float) -> None:
        """Input güncelleme"""
        # Input map'i güncelle
        self.input_map.update()
        
        # Entity'lerde input işle
        for entity in self.entities:
            if entity.active:
                self._process_entity_input(entity, dt)
    
    def _process_entity_input(self, entity: Entity, dt: float) -> None:
        """Entity input'unu işle"""
        # Bu method override edilebilir
        pass


class EntityManager:
    """Entity yöneticisi"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.systems: List[System] = []
        self.next_entity_id = 1
    
    def create_entity(self) -> Entity:
        """Yeni entity oluştur"""
        entity = Entity(str(self.next_entity_id))
        self.next_entity_id += 1
        self.entities[entity.id] = entity
        
        # Sistemlere ekle
        for system in self.systems:
            system.add_entity(entity)
        
        return entity
    
    def destroy_entity(self, entity_id: str) -> None:
        """Entity'yi yok et"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.destroy()
            
            # Sistemlerden kaldır
            for system in self.systems:
                system.remove_entity(entity)
            
            del self.entities[entity_id]
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Entity al"""
        return self.entities.get(entity_id)
    
    def get_entities_with_tag(self, tag: str) -> List[Entity]:
        """Tag'e sahip entity'leri döndür"""
        return [e for e in self.entities.values() if e.has_tag(tag)]
    
    def get_entities_with_component(self, component_type: Type[Component]) -> List[Entity]:
        """Component'e sahip entity'leri döndür"""
        return [e for e in self.entities.values() if e.has_component(component_type)]
    
    def add_system(self, system: System) -> None:
        """Sistem ekle"""
        self.systems.append(system)
        
        # Mevcut entity'leri sisteme ekle
        for entity in self.entities.values():
            system.add_entity(entity)
    
    def remove_system(self, system: System) -> None:
        """Sistem kaldır"""
        if system in self.systems:
            self.systems.remove(system)
    
    def update(self, dt: float) -> None:
        """Tüm sistemleri güncelle"""
        # Ölü entity'leri temizle
        dead_entities = [eid for eid, entity in self.entities.items() if not entity.active]
        for eid in dead_entities:
            self.destroy_entity(eid)
        
        # Sistemleri güncelle
        for system in self.systems:
            system.update(dt)
    
    def clear(self) -> None:
        """Tüm entity'leri temizle"""
        self.entities.clear()
        for system in self.systems:
            system.entities.clear()
