"""
InputMap testleri
"""

import pytest
from sparkle2d.inputmap import InputMap, InputState


class TestInputMap:
    """InputMap test sınıfı"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.input_map = InputMap()
    
    def test_bind_action(self):
        """Action bağlama testi"""
        self.input_map.bind("move_left", "A,LEFT")
        self.input_map.bind("move_right", "D,RIGHT")
        
        bindings = self.input_map.get_bindings()
        assert "move_left" in bindings
        assert "move_right" in bindings
        assert bindings["move_left"] == ["A", "LEFT"]
        assert bindings["move_right"] == ["D", "RIGHT"]
    
    def test_unbind_action(self):
        """Action bağlantısını kaldırma testi"""
        self.input_map.bind("move_left", "A,LEFT")
        self.input_map.unbind("move_left")
        
        bindings = self.input_map.get_bindings()
        assert "move_left" not in bindings
    
    def test_action_transitions(self):
        """Action durum geçişleri testi"""
        self.input_map.bind("move_left", "A")
        
        # Başlangıçta hiçbir action aktif değil
        assert not self.input_map.action_down("move_left")
        assert not self.input_map.action_pressed("move_left")
        assert not self.input_map.action_released("move_left")
        
        # Tuş basma simülasyonu
        self.input_map.on_key_press(65, 0)  # A tuşu
        self.input_map.update()
        
        # İlk frame'de pressed olmalı
        assert self.input_map.action_pressed("move_left")
        assert self.input_map.action_down("move_left")
        assert not self.input_map.action_released("move_left")
        
        # İkinci frame
        self.input_map.update()
        
        # Artık pressed değil, sadece down olmalı
        assert not self.input_map.action_pressed("move_left")
        assert self.input_map.action_down("move_left")
        assert not self.input_map.action_released("move_left")
        
        # Tuş bırakma simülasyonu
        self.input_map.on_key_release(65, 0)  # A tuşu
        self.input_map.update()
        
        # Released olmalı
        assert not self.input_map.action_pressed("move_left")
        assert not self.input_map.action_down("move_left")
        assert self.input_map.action_released("move_left")
        
        # Sonraki frame'de hiçbiri aktif olmamalı
        self.input_map.update()
        assert not self.input_map.action_pressed("move_left")
        assert not self.input_map.action_down("move_left")
        assert not self.input_map.action_released("move_left")
    
    def test_multiple_keys_same_action(self):
        """Aynı action için birden fazla tuş testi"""
        self.input_map.bind("move_left", "A,LEFT")
        
        # A tuşu ile test
        self.input_map.on_key_press(65, 0)  # A tuşu
        self.input_map.update()
        assert self.input_map.action_pressed("move_left")
        
        # Tuşları temizle
        self.input_map.clear()
        
        # LEFT tuşu ile test
        self.input_map.on_key_press(65361, 0)  # LEFT tuşu
        self.input_map.update()
        assert self.input_map.action_pressed("move_left")
    
    def test_unknown_key(self):
        """Bilinmeyen tuş testi"""
        with pytest.raises(ValueError):
            self.input_map._get_key_code("UNKNOWN_KEY")
    
    def test_clear_input(self):
        """Input temizleme testi"""
        self.input_map.bind("move_left", "A")
        self.input_map.on_key_press(65, 0)
        self.input_map.update()
        
        assert self.input_map.action_down("move_left")
        
        self.input_map.clear()
        
        assert not self.input_map.action_down("move_left")
        assert not self.input_map.action_pressed("move_left")
        assert not self.input_map.action_released("move_left")
    
    def test_action_not_bound(self):
        """Bağlanmamış action testi"""
        # Bağlanmamış action'lar için False döndürmeli
        assert not self.input_map.action_down("nonexistent_action")
        assert not self.input_map.action_pressed("nonexistent_action")
        assert not self.input_map.action_released("nonexistent_action")
