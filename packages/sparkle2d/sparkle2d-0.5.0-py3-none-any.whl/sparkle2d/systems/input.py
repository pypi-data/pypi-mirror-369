"""
Input sistemi
"""

from ..ecs import System, Transform


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
    
    def _process_entity_input(self, entity, dt: float) -> None:
        """Entity input'unu işle"""
        # Bu method override edilebilir
        pass
