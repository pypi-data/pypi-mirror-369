"""
Tween engine - easing fonksiyonları ve animasyon sistemi
"""

from typing import Dict, List, Callable, Any, Optional
import math
import time


class Easing:
    """Easing fonksiyonları"""
    
    @staticmethod
    def linear(t: float) -> float:
        """Linear easing"""
        return t
    
    @staticmethod
    def quad_in(t: float) -> float:
        """Quadratic in"""
        return t * t
    
    @staticmethod
    def quad_out(t: float) -> float:
        """Quadratic out"""
        return t * (2 - t)
    
    @staticmethod
    def quad_in_out(t: float) -> float:
        """Quadratic in-out"""
        if t < 0.5:
            return 2 * t * t
        else:
            return -1 + (4 - 2 * t) * t
    
    @staticmethod
    def cubic_in(t: float) -> float:
        """Cubic in"""
        return t * t * t
    
    @staticmethod
    def cubic_out(t: float) -> float:
        """Cubic out"""
        return 1 - (1 - t) ** 3
    
    @staticmethod
    def cubic_in_out(t: float) -> float:
        """Cubic in-out"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - (-2 * t + 2) ** 3 / 2
    
    @staticmethod
    def elastic_out(t: float) -> float:
        """Elastic out"""
        if t == 0:
            return 0
        if t == 1:
            return 1
        return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1
    
    @staticmethod
    def bounce_out(t: float) -> float:
        """Bounce out"""
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t = t - 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t = t - 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t = t - 2.625 / 2.75
            return 7.5625 * t * t + 0.984375


class Tween:
    """Tekil tween animasyonu"""
    
    def __init__(self, target: Any, properties: Dict[str, float], duration: float, 
                 easing: str = "linear", delay: float = 0.0, on_complete: Optional[Callable] = None):
        self.target = target
        self.properties = properties
        self.duration = duration
        self.easing_name = easing
        self.delay = delay
        self.on_complete = on_complete
        
        # Easing fonksiyonu
        self.easing_func = getattr(Easing, easing, Easing.linear)
        
        # Başlangıç değerleri
        self.start_values = {}
        self.end_values = properties.copy()
        
        # Zaman
        self.elapsed = 0.0
        self.is_completed = False
        self.is_started = False
    
    def start(self) -> None:
        """Tween'i başlat"""
        # Başlangıç değerlerini kaydet
        for prop in self.properties:
            if hasattr(self.target, prop):
                self.start_values[prop] = getattr(self.target, prop)
        
        self.is_started = True
    
    def update(self, dt: float) -> bool:
        """Tween'i güncelle, tamamlandıysa True döndür"""
        if not self.is_started:
            self.start()
        
        if self.is_completed:
            return True
        
        # Delay kontrolü
        if self.delay > 0:
            self.delay -= dt
            return False
        
        self.elapsed += dt
        
        # Progress hesapla
        progress = min(1.0, self.elapsed / self.duration)
        eased_progress = self.easing_func(progress)
        
        # Değerleri güncelle
        for prop in self.properties:
            if hasattr(self.target, prop) and prop in self.start_values:
                start_val = self.start_values[prop]
                end_val = self.end_values[prop]
                current_val = start_val + (end_val - start_val) * eased_progress
                setattr(self.target, prop, current_val)
        
        # Tamamlandı mı kontrol et
        if progress >= 1.0:
            self.is_completed = True
            if self.on_complete:
                self.on_complete()
            return True
        
        return False
    
    def reset(self) -> None:
        """Tween'i sıfırla"""
        self.elapsed = 0.0
        self.is_completed = False
        self.is_started = False


class TweenManager:
    """Tween yöneticisi"""
    
    def __init__(self):
        self.tweens: List[Tween] = []
        self.sequences: List['TweenSequence'] = []
    
    def tween(self, target: Any, properties: Dict[str, float], duration: float, 
              easing: str = "linear", delay: float = 0.0, on_complete: Optional[Callable] = None) -> Tween:
        """Yeni tween oluştur ve başlat"""
        tween = Tween(target, properties, duration, easing, delay, on_complete)
        self.tweens.append(tween)
        return tween
    
    def sequence(self, *tweens: Tween) -> 'TweenSequence':
        """Tween sequence oluştur"""
        sequence = TweenSequence(tweens)
        self.sequences.append(sequence)
        return sequence
    
    def parallel(self, *tweens: Tween) -> 'TweenParallel':
        """Paralel tween grubu oluştur"""
        parallel = TweenParallel(tweens)
        self.sequences.append(parallel)
        return parallel
    
    def update(self, dt: float) -> None:
        """Tüm tween'leri güncelle"""
        # Tekil tween'leri güncelle
        completed_tweens = []
        for tween in self.tweens:
            if tween.update(dt):
                completed_tweens.append(tween)
        
        # Tamamlanan tween'leri kaldır
        for tween in completed_tweens:
            if tween in self.tweens:
                self.tweens.remove(tween)
        
        # Sequence'leri güncelle
        completed_sequences = []
        for sequence in self.sequences:
            if sequence.update(dt):
                completed_sequences.append(sequence)
        
        # Tamamlanan sequence'leri kaldır
        for sequence in completed_sequences:
            if sequence in self.sequences:
                self.sequences.remove(sequence)
    
    def clear(self) -> None:
        """Tüm tween'leri temizle"""
        self.tweens.clear()
        self.sequences.clear()
    
    def kill_tweens_of(self, target: Any) -> None:
        """Hedefin tüm tween'lerini durdur"""
        self.tweens = [t for t in self.tweens if t.target != target]
        for sequence in self.sequences:
            sequence.kill_tweens_of(target)


class TweenSequence:
    """Sıralı tween grubu"""
    
    def __init__(self, tweens: List[Tween]):
        self.tweens = list(tweens)
        self.current_index = 0
        self.is_completed = False
    
    def update(self, dt: float) -> bool:
        """Sequence'i güncelle"""
        if self.is_completed:
            return True
        
        if self.current_index >= len(self.tweens):
            self.is_completed = True
            return True
        
        current_tween = self.tweens[self.current_index]
        if current_tween.update(dt):
            self.current_index += 1
        
        return self.is_completed
    
    def kill_tweens_of(self, target: Any) -> None:
        """Hedefin tween'lerini durdur"""
        self.tweens = [t for t in self.tweens if t.target != target]


class TweenParallel:
    """Paralel tween grubu"""
    
    def __init__(self, tweens: List[Tween]):
        self.tweens = list(tweens)
        self.is_completed = False
    
    def update(self, dt: float) -> bool:
        """Parallel grubu güncelle"""
        if self.is_completed:
            return True
        
        # Tüm tween'leri güncelle
        completed_tweens = []
        for tween in self.tweens:
            if tween.update(dt):
                completed_tweens.append(tween)
        
        # Tamamlanan tween'leri kaldır
        for tween in completed_tweens:
            if tween in self.tweens:
                self.tweens.remove(tween)
        
        # Tüm tween'ler tamamlandıysa
        if len(self.tweens) == 0:
            self.is_completed = True
        
        return self.is_completed
    
    def kill_tweens_of(self, target: Any) -> None:
        """Hedefin tween'lerini durdur"""
        self.tweens = [t for t in self.tweens if t.target != target]
