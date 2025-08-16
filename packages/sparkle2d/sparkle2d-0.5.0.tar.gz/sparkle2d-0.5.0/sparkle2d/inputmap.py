"""
Input sistemi - Action-based input mapping
"""

from typing import Dict, List, Set, Optional, Callable
from enum import Enum
import pyglet


class InputState(Enum):
    """Input durumları"""
    RELEASED = 0
    PRESSED = 1
    DOWN = 2


class InputMap:
    """Action-based input sistemi"""
    
    def __init__(self):
        self._actions: Dict[str, List[str]] = {}
        self._key_states: Dict[int, InputState] = {}
        self._prev_key_states: Dict[int, InputState] = {}
        self._action_states: Dict[str, InputState] = {}
        self._prev_action_states: Dict[str, InputState] = {}
        
        # Tuş kodları
        self._key_map = {
            'A': pyglet.window.key.A,
            'B': pyglet.window.key.B,
            'C': pyglet.window.key.C,
            'D': pyglet.window.key.D,
            'E': pyglet.window.key.E,
            'F': pyglet.window.key.F,
            'G': pyglet.window.key.G,
            'H': pyglet.window.key.H,
            'I': pyglet.window.key.I,
            'J': pyglet.window.key.J,
            'K': pyglet.window.key.K,
            'L': pyglet.window.key.L,
            'M': pyglet.window.key.M,
            'N': pyglet.window.key.N,
            'O': pyglet.window.key.O,
            'P': pyglet.window.key.P,
            'Q': pyglet.window.key.Q,
            'R': pyglet.window.key.R,
            'S': pyglet.window.key.S,
            'T': pyglet.window.key.T,
            'U': pyglet.window.key.U,
            'V': pyglet.window.key.V,
            'W': pyglet.window.key.W,
            'X': pyglet.window.key.X,
            'Y': pyglet.window.key.Y,
            'Z': pyglet.window.key.Z,
            'SPACE': pyglet.window.key.SPACE,
            'ENTER': pyglet.window.key.ENTER,
            'ESCAPE': pyglet.window.key.ESCAPE,
            'LEFT': pyglet.window.key.LEFT,
            'RIGHT': pyglet.window.key.RIGHT,
            'UP': pyglet.window.key.UP,
            'DOWN': pyglet.window.key.DOWN,
            'SHIFT': pyglet.window.key.LSHIFT,
            'CTRL': pyglet.window.key.LCTRL,
            'ALT': pyglet.window.key.LALT,
            'TAB': pyglet.window.key.TAB,
            'BACKSPACE': pyglet.window.key.BACKSPACE,
            'DELETE': pyglet.window.key.DELETE,
            'HOME': pyglet.window.key.HOME,
            'END': pyglet.window.key.END,
            'PAGEUP': pyglet.window.key.PAGEUP,
            'PAGEDOWN': pyglet.window.key.PAGEDOWN,
            'F1': pyglet.window.key.F1,
            'F2': pyglet.window.key.F2,
            'F3': pyglet.window.key.F3,
            'F4': pyglet.window.key.F4,
            'F5': pyglet.window.key.F5,
            'F6': pyglet.window.key.F6,
            'F7': pyglet.window.key.F7,
            'F8': pyglet.window.key.F8,
            'F9': pyglet.window.key.F9,
            'F10': pyglet.window.key.F10,
            'F11': pyglet.window.key.F11,
            'F12': pyglet.window.key.F12,
        }
    
    def bind(self, action: str, keys: str) -> None:
        """Action'a tuş bağla"""
        key_list = [k.strip() for k in keys.split(',')]
        self._actions[action] = key_list
    
    def unbind(self, action: str) -> None:
        """Action'ın tuş bağlantısını kaldır"""
        if action in self._actions:
            del self._actions[action]
    
    def _get_key_code(self, key_name: str) -> int:
        """Tuş adından kod döndür"""
        key_name = key_name.upper()
        if key_name in self._key_map:
            return self._key_map[key_name]
        raise ValueError(f"Bilinmeyen tuş: {key_name}")
    
    def _is_action_triggered(self, action: str) -> bool:
        """Action'ın tetiklendiğini kontrol et"""
        if action not in self._actions:
            return False
        
        for key_name in self._actions[action]:
            try:
                key_code = self._get_key_code(key_name)
                if key_code in self._key_states:
                    return self._key_states[key_code] == InputState.PRESSED
            except ValueError:
                continue
        return False
    
    def _is_action_down(self, action: str) -> bool:
        """Action'ın basılı olduğunu kontrol et"""
        if action not in self._actions:
            return False
        
        for key_name in self._actions[action]:
            try:
                key_code = self._get_key_code(key_name)
                if key_code in self._key_states:
                    state = self._key_states[key_code]
                    return state == InputState.DOWN or state == InputState.PRESSED
            except ValueError:
                continue
        return False
    
    def _is_action_released(self, action: str) -> bool:
        """Action'ın bırakıldığını kontrol et"""
        if action not in self._actions:
            return False
        
        for key_name in self._actions[action]:
            try:
                key_code = self._get_key_code(key_name)
                if key_code in self._key_states:
                    return self._key_states[key_code] == InputState.RELEASED
            except ValueError:
                continue
        return False
    
    def action_pressed(self, action: str) -> bool:
        """Action'ın bu frame'de basıldığını kontrol et"""
        return self._action_states.get(action, InputState.RELEASED) == InputState.PRESSED
    
    def action_down(self, action: str) -> bool:
        """Action'ın basılı olduğunu kontrol et"""
        return self._action_states.get(action, InputState.RELEASED) in [InputState.DOWN, InputState.PRESSED]
    
    def action_released(self, action: str) -> bool:
        """Action'ın bu frame'de bırakıldığını kontrol et"""
        return self._action_states.get(action, InputState.RELEASED) == InputState.RELEASED
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Tuş basma eventi"""
        if symbol not in self._key_states:
            self._key_states[symbol] = InputState.PRESSED
        else:
            self._key_states[symbol] = InputState.DOWN
    
    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Tuş bırakma eventi"""
        self._key_states[symbol] = InputState.RELEASED
    
    def update(self) -> None:
        """Input durumlarını güncelle"""
        # Önceki durumları kaydet
        self._prev_key_states = self._key_states.copy()
        self._prev_action_states = self._action_states.copy()
        
        # Action durumlarını güncelle
        for action in self._actions:
            if self._is_action_triggered(action):
                self._action_states[action] = InputState.PRESSED
            elif self._is_action_down(action):
                self._action_states[action] = InputState.DOWN
            elif self._is_action_released(action):
                self._action_states[action] = InputState.RELEASED
        
        # Basılı tuşları DOWN durumuna geçir
        for symbol, state in self._key_states.items():
            if state == InputState.PRESSED:
                self._key_states[symbol] = InputState.DOWN
        
        # Bırakılan tuşları temizle
        keys_to_remove = []
        for symbol, state in self._key_states.items():
            if state == InputState.RELEASED:
                keys_to_remove.append(symbol)
        
        for symbol in keys_to_remove:
            del self._key_states[symbol]
    
    def get_bindings(self) -> Dict[str, List[str]]:
        """Tüm bağlantıları döndür"""
        return self._actions.copy()
    
    def clear(self) -> None:
        """Tüm input durumlarını temizle"""
        self._key_states.clear()
        self._prev_key_states.clear()
        self._action_states.clear()
        self._prev_action_states.clear()
