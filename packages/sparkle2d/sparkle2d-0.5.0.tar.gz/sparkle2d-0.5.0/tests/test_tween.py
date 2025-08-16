"""
Tween testleri
"""

import pytest
import math
from sparkle2d.tween import Tween, TweenManager, Easing


class MockTarget:
    """Test için mock hedef"""
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.alpha = 1.0


class TestEasing:
    """Easing fonksiyonları testi"""
    
    def test_linear(self):
        """Linear easing testi"""
        assert Easing.linear(0.0) == 0.0
        assert Easing.linear(0.5) == 0.5
        assert Easing.linear(1.0) == 1.0
    
    def test_quad_in(self):
        """Quadratic in testi"""
        assert abs(Easing.quad_in(0.0) - 0.0) < 0.001
        assert abs(Easing.quad_in(0.5) - 0.25) < 0.001
        assert abs(Easing.quad_in(1.0) - 1.0) < 0.001
    
    def test_quad_out(self):
        """Quadratic out testi"""
        assert abs(Easing.quad_out(0.0) - 0.0) < 0.001
        assert abs(Easing.quad_out(0.5) - 0.75) < 0.001
        assert abs(Easing.quad_out(1.0) - 1.0) < 0.001
    
    def test_cubic_in(self):
        """Cubic in testi"""
        assert abs(Easing.cubic_in(0.0) - 0.0) < 0.001
        assert abs(Easing.cubic_in(0.5) - 0.125) < 0.001
        assert abs(Easing.cubic_in(1.0) - 1.0) < 0.001
    
    def test_cubic_out(self):
        """Cubic out testi"""
        assert abs(Easing.cubic_out(0.0) - 0.0) < 0.001
        assert abs(Easing.cubic_out(0.5) - 0.875) < 0.001
        assert abs(Easing.cubic_out(1.0) - 1.0) < 0.001
    
    def test_elastic_out(self):
        """Elastic out testi"""
        assert abs(Easing.elastic_out(0.0) - 0.0) < 0.001
        assert abs(Easing.elastic_out(1.0) - 1.0) < 0.001
        
        # Orta değer kontrolü (toleranslı)
        mid_value = Easing.elastic_out(0.5)
        assert 0.0 <= mid_value <= 1.0


class TestTween:
    """Tween testi"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.target = MockTarget()
    
    def test_tween_creation(self):
        """Tween oluşturma testi"""
        tween = Tween(self.target, {"x": 100, "y": 200}, 2.0, "linear")
        
        assert tween.target == self.target
        assert tween.duration == 2.0
        assert tween.easing_name == "linear"
        assert not tween.is_completed
    
    def test_tween_update_linear(self):
        """Linear tween güncelleme testi"""
        tween = Tween(self.target, {"x": 100}, 1.0, "linear")
        
        # Başlangıç değeri
        assert self.target.x == 0.0
        
        # Yarı yolda
        tween.update(0.5)
        assert abs(self.target.x - 50.0) < 0.1
        
        # Tamamlandı
        tween.update(0.5)
        assert abs(self.target.x - 100.0) < 0.1
        assert tween.is_completed
    
    def test_tween_update_quad_out(self):
        """Quadratic out tween testi"""
        tween = Tween(self.target, {"x": 100}, 1.0, "quadOut")
        
        # Yarı yolda (quadOut daha hızlı başlar)
        tween.update(0.5)
        assert self.target.x > 50.0  # QuadOut daha hızlı
        
        # Tamamlandı
        tween.update(0.5)
        assert abs(self.target.x - 100.0) < 0.1
        assert tween.is_completed
    
    def test_tween_multiple_properties(self):
        """Çoklu özellik tween testi"""
        tween = Tween(self.target, {"x": 100, "y": 200, "alpha": 0.5}, 1.0, "linear")
        
        tween.update(1.0)
        
        assert abs(self.target.x - 100.0) < 0.1
        assert abs(self.target.y - 200.0) < 0.1
        assert abs(self.target.alpha - 0.5) < 0.1
        assert tween.is_completed
    
    def test_tween_delay(self):
        """Tween delay testi"""
        tween = Tween(self.target, {"x": 100}, 1.0, "linear", delay=0.5)
        
        # Delay sırasında değer değişmemeli
        tween.update(0.3)
        assert self.target.x == 0.0
        assert not tween.is_completed
        
        # Delay sonrası çalışmalı
        tween.update(0.3)  # 0.6 total
        assert self.target.x > 0.0
        assert not tween.is_completed
        
        # Tamamlanmalı
        tween.update(0.4)
        assert abs(self.target.x - 100.0) < 0.1
        assert tween.is_completed
    
    def test_tween_on_complete_callback(self):
        """Tween tamamlanma callback testi"""
        callback_called = False
        
        def on_complete():
            nonlocal callback_called
            callback_called = True
        
        tween = Tween(self.target, {"x": 100}, 1.0, "linear", on_complete=on_complete)
        
        tween.update(1.0)
        
        assert callback_called
        assert tween.is_completed


class TestTweenManager:
    """TweenManager testi"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.manager = TweenManager()
        self.target = MockTarget()
    
    def test_tween_creation(self):
        """Tween oluşturma testi"""
        tween = self.manager.tween(self.target, {"x": 100}, 1.0, "linear")
        
        assert len(self.manager.tweens) == 1
        assert tween in self.manager.tweens
    
    def test_tween_completion_removal(self):
        """Tween tamamlanma ve kaldırma testi"""
        tween = self.manager.tween(self.target, {"x": 100}, 1.0, "linear")
        
        assert len(self.manager.tweens) == 1
        
        # Tween'i tamamla
        self.manager.update(1.0)
        
        # Tamamlanan tween kaldırılmalı
        assert len(self.manager.tweens) == 0
    
    def test_kill_tweens_of(self):
        """Belirli hedefin tween'lerini durdurma testi"""
        target1 = MockTarget()
        target2 = MockTarget()
        
        tween1 = self.manager.tween(target1, {"x": 100}, 1.0, "linear")
        tween2 = self.manager.tween(target2, {"x": 100}, 1.0, "linear")
        
        assert len(self.manager.tweens) == 2
        
        # target1'in tween'lerini durdur
        self.manager.kill_tweens_of(target1)
        
        assert len(self.manager.tweens) == 1
        assert tween2 in self.manager.tweens
        assert tween1 not in self.manager.tweens
    
    def test_clear_tweens(self):
        """Tüm tween'leri temizleme testi"""
        self.manager.tween(self.target, {"x": 100}, 1.0, "linear")
        self.manager.tween(self.target, {"y": 100}, 1.0, "linear")
        
        assert len(self.manager.tweens) == 2
        
        self.manager.clear()
        
        assert len(self.manager.tweens) == 0
        assert len(self.manager.sequences) == 0
