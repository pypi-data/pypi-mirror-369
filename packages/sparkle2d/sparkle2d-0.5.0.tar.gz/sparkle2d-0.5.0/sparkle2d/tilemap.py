"""
Tilemap sistemi - TMX loader, collision -> physics
"""

from typing import Dict, List, Optional, Tuple, Any
import pytmx
import pyglet
import pyglet.gl as gl


class Tilemap:
    """TMX tabanlı tilemap"""
    
    def __init__(self, tmx_path: str):
        self.tmx_path = tmx_path
        self.tmx_data = None
        self.tilesets = {}
        self.layers = {}
        self.collision_objects = []
        
        # Kamera sınırları
        self.bounds = (0, 0, 0, 0)  # min_x, min_y, max_x, max_y
        
        # Fizik dünyası referansı
        self.physics_world = None
        
        self._load_tmx()
    
    def _load_tmx(self) -> None:
        """TMX dosyasını yükle"""
        try:
            self.tmx_data = pytmx.load_pyglet(self.tmx_path)
            
            # Tileset'leri yükle
            for tileset in self.tmx_data.tilesets:
                self.tilesets[tileset.name] = tileset
            
            # Layer'ları yükle
            for layer in self.tmx_data.layers:
                self.layers[layer.name] = layer
            
            # Çarpışma objelerini yükle
            self._load_collision_objects()
            
            # Sınırları hesapla
            self._calculate_bounds()
            
        except Exception as e:
            print(f"TMX yükleme hatası {self.tmx_path}: {e}")
    
    def _load_collision_objects(self) -> None:
        """Çarpışma objelerini yükle"""
        self.collision_objects = []
        
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'objects'):
                for obj in layer.objects:
                    collision_obj = {
                        'name': obj.name,
                        'type': obj.type,
                        'x': obj.x,
                        'y': obj.y,
                        'width': obj.width,
                        'height': obj.height,
                        'properties': obj.properties,
                        'layer': layer.name
                    }
                    
                    # Polygon objeleri
                    if hasattr(obj, 'points'):
                        collision_obj['points'] = obj.points
                    
                    self.collision_objects.append(collision_obj)
    
    def _calculate_bounds(self) -> None:
        """Harita sınırlarını hesapla"""
        if not self.tmx_data:
            return
        
        map_width = self.tmx_data.width * self.tmx_data.tilewidth
        map_height = self.tmx_data.height * self.tmx_data.tileheight
        
        self.bounds = (0, 0, map_width, map_height)
    
    def set_physics_world(self, physics_world) -> None:
        """Fizik dünyasını ayarla"""
        self.physics_world = physics_world
        self._create_physics_objects()
    
    def _create_physics_objects(self) -> None:
        """Fizik objelerini oluştur"""
        if not self.physics_world:
            return
        
        for obj in self.collision_objects:
            obj_type = obj.get('type', 'collision')
            
            if obj_type == 'collision':
                # Statik collision body oluştur
                body_id = self.physics_world.create_body(
                    body_type="static",
                    position=(obj['x'], obj['y'])
                )
                
                # Shape oluştur
                if 'points' in obj:
                    # Polygon shape
                    vertices = [(p[0], p[1]) for p in obj['points']]
                    self.physics_world.create_polygon_shape(
                        body_id, vertices, collision_type="wall"
                    )
                else:
                    # Box shape
                    self.physics_world.create_box_shape(
                        body_id, (obj['width'], obj['height']), 
                        collision_type="wall"
                    )
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Harita sınırlarını döndür"""
        return self.bounds
    
    def get_tile_at(self, x: float, y: float, layer_name: str = "main") -> Optional[int]:
        """Belirli pozisyondaki tile'ı döndür"""
        if not self.tmx_data or layer_name not in self.layers:
            return None
        
        layer = self.layers[layer_name]
        
        # Tile koordinatlarına dönüştür
        tile_x = int(x // self.tmx_data.tilewidth)
        tile_y = int(y // self.tmx_data.tileheight)
        
        # Sınır kontrolü
        if (0 <= tile_x < self.tmx_data.width and 
            0 <= tile_y < self.tmx_data.height):
            return layer.data[tile_y][tile_x]
        
        return None
    
    def is_solid_at(self, x: float, y: float) -> bool:
        """Pozisyon katı mı kontrol et"""
        tile_id = self.get_tile_at(x, y, "collision")
        return tile_id is not None and tile_id != 0
    
    def get_collision_objects_in_area(self, x: float, y: float, width: float, height: float) -> List[Dict]:
        """Alan içindeki çarpışma objelerini döndür"""
        objects = []
        
        for obj in self.collision_objects:
            # AABB çarpışma kontrolü
            if (obj['x'] < x + width and obj['x'] + obj['width'] > x and
                obj['y'] < y + height and obj['y'] + obj['height'] > y):
                objects.append(obj)
        
        return objects
    
    def draw(self, camera) -> None:
        """Tilemap'i çiz"""
        if not self.tmx_data:
            return
        
        # Kamera görüş alanını al
        viewport = camera.get_viewport()
        left, bottom, right, top = viewport
        
        # Tile boyutları
        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight
        
        # Görüş alanındaki tile'ları hesapla
        start_x = max(0, int(left // tile_width))
        end_x = min(self.tmx_data.width, int(right // tile_width) + 1)
        start_y = max(0, int(bottom // tile_height))
        end_y = min(self.tmx_data.height, int(top // tile_height) + 1)
        
        # Layer'ları çiz
        for layer_name, layer in self.layers.items():
            if layer_name == "collision":  # Collision layer'ını çizme
                continue
            
            self._draw_layer(layer, start_x, end_x, start_y, end_y, tile_width, tile_height)
    
    def _draw_layer(self, layer, start_x: int, end_x: int, start_y: int, end_y: int, 
                   tile_width: int, tile_height: int) -> None:
        """Layer'ı çiz"""
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = layer.data[y][x]
                
                if tile_id != 0:  # Boş tile değilse
                    self._draw_tile(tile_id, x * tile_width, y * tile_height, tile_width, tile_height)
        
        gl.glDisable(gl.GL_BLEND)
    
    def _draw_tile(self, tile_id: int, x: float, y: float, width: int, height: int) -> None:
        """Tekil tile'ı çiz"""
        # Tileset bul
        tileset = self._get_tileset_for_tile(tile_id)
        if not tileset:
            return
        
        # Tile koordinatları
        local_tile_id = tile_id - tileset.firstgid
        tileset_width = tileset.width // tileset.tilewidth
        tileset_height = tileset.height // tileset.tileheight
        
        tile_x = (local_tile_id % tileset_width) * tileset.tilewidth
        tile_y = (local_tile_id // tileset_width) * tileset.tileheight
        
        # Texture koordinatları
        tex_width = tileset.width
        tex_height = tileset.height
        
        u1 = tile_x / tex_width
        v1 = 1.0 - (tile_y / tex_height)
        u2 = (tile_x + tileset.tilewidth) / tex_width
        v2 = 1.0 - ((tile_y + tileset.tileheight) / tex_height)
        
        # Tile çiz
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tileset.texture.id)
        
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(u1, v1); gl.glVertex2f(x, y)
        gl.glTexCoord2f(u2, v1); gl.glVertex2f(x + width, y)
        gl.glTexCoord2f(u2, v2); gl.glVertex2f(x + width, y + height)
        gl.glTexCoord2f(u1, v2); gl.glVertex2f(x, y + height)
        gl.glEnd()
        
        gl.glDisable(gl.GL_TEXTURE_2D)
    
    def _get_tileset_for_tile(self, tile_id: int):
        """Tile için tileset bul"""
        for tileset in self.tilesets.values():
            if tileset.firstgid <= tile_id < tileset.firstgid + tileset.tilecount:
                return tileset
        return None
    
    def get_property(self, name: str, default=None):
        """Harita özelliğini al"""
        if self.tmx_data and hasattr(self.tmx_data, 'properties'):
            return self.tmx_data.properties.get(name, default)
        return default
    
    def get_layer_property(self, layer_name: str, property_name: str, default=None):
        """Layer özelliğini al"""
        if layer_name in self.layers:
            layer = self.layers[layer_name]
            if hasattr(layer, 'properties'):
                return layer.properties.get(property_name, default)
        return default
    
    def get_object_property(self, object_name: str, property_name: str, default=None):
        """Obje özelliğini al"""
        for obj in self.collision_objects:
            if obj['name'] == object_name:
                return obj['properties'].get(property_name, default)
        return default
