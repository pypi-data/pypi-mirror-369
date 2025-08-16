"""
Render sistemi
"""

import pyglet.gl as gl
from ..ecs import System, Transform, Sprite


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
    
    def _render_entity(self, entity) -> None:
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
