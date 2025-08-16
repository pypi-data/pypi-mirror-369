"""
Event sistemi - EventBus sınıfı
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EventPriority(Enum):
    """Event öncelik seviyeleri"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class EventHandler:
    """Event handler bilgileri"""
    callback: Callable
    priority: EventPriority
    once: bool = False


class EventBus:
    """Event sistemi - on/once/off/emit metodları"""
    
    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._to_remove: List[tuple] = []
    
    def on(self, event: str, callback: Callable, priority: EventPriority = EventPriority.NORMAL) -> None:
        """Event dinleyicisi ekle"""
        if event not in self._handlers:
            self._handlers[event] = []
        
        handler = EventHandler(callback, priority, once=False)
        self._handlers[event].append(handler)
        # Önceliğe göre sırala
        self._handlers[event].sort(key=lambda h: h.priority.value, reverse=True)
    
    def once(self, event: str, callback: Callable, priority: EventPriority = EventPriority.NORMAL) -> None:
        """Tek seferlik event dinleyicisi ekle"""
        if event not in self._handlers:
            self._handlers[event] = []
        
        handler = EventHandler(callback, priority, once=True)
        self._handlers[event].append(handler)
        self._handlers[event].sort(key=lambda h: h.priority.value, reverse=True)
    
    def off(self, event: str, callback: Callable) -> None:
        """Event dinleyicisini kaldır"""
        if event in self._handlers:
            self._handlers[event] = [
                h for h in self._handlers[event] 
                if h.callback != callback
            ]
    
    def emit(self, event: str, data: Any = None) -> None:
        """Event gönder"""
        if event not in self._handlers:
            return
        
        # Silinecek handler'ları topla
        self._to_remove.clear()
        
        for handler in self._handlers[event]:
            try:
                handler.callback(data)
                if handler.once:
                    self._to_remove.append((event, handler.callback))
            except Exception as e:
                print(f"Event handler hatası: {e}")
        
        # Tek seferlik handler'ları kaldır
        for event_name, callback in self._to_remove:
            self.off(event_name, callback)
    
    def clear(self, event: Optional[str] = None) -> None:
        """Event handler'larını temizle"""
        if event:
            if event in self._handlers:
                del self._handlers[event]
        else:
            self._handlers.clear()
