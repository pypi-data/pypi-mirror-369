"""
UI sistemi - Label, Button, Panel, anchoring, focus, 9-slice
"""

from typing import Dict, List, Optional, Callable, Tuple
import pyglet
import pyglet.gl as gl


class UIElement:
    """Base UI element"""
    
    def __init__(self, x: float = 0, y: float = 0, width: float = 100, height: float = 100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Anchor (0-1 arası, sol-alt köşe)
        self.anchor_x = 0.0
        self.anchor_y = 0.0
        
        # Görünürlük
        self.visible = True
        self.enabled = True
        
        # Focus
        self.focused = False
        self.focusable = False
        
        # Event callback'leri
        self.on_click = None
        self.on_hover = None
        self.on_focus = None
        self.on_blur = None
    
    def set_anchor(self, anchor_x: float, anchor_y: float) -> None:
        """Anchor ayarla"""
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
    
    def get_absolute_position(self, parent_width: float, parent_height: float) -> Tuple[float, float]:
        """Mutlak pozisyonu hesapla"""
        abs_x = self.x + (parent_width * self.anchor_x)
        abs_y = self.y + (parent_height * self.anchor_y)
        return abs_x, abs_y
    
    def contains_point(self, px: float, py: float, parent_width: float, parent_height: float) -> bool:
        """Nokta element içinde mi kontrol et"""
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        return (abs_x <= px <= abs_x + self.width and 
                abs_y <= py <= abs_y + self.height)
    
    def handle_mouse_press(self, x: float, y: float, button: int, parent_width: float, parent_height: float) -> bool:
        """Fare basma eventi"""
        if not self.enabled or not self.visible:
            return False
        
        if self.contains_point(x, y, parent_width, parent_height):
            if self.on_click:
                self.on_click(self, x, y, button)
            return True
        return False
    
    def handle_mouse_motion(self, x: float, y: float, parent_width: float, parent_height: float) -> bool:
        """Fare hareket eventi"""
        if not self.enabled or not self.visible:
            return False
        
        if self.contains_point(x, y, parent_width, parent_height):
            if self.on_hover:
                self.on_hover(self, x, y)
            return True
        return False
    
    def set_focus(self, focused: bool) -> None:
        """Focus ayarla"""
        if self.focusable:
            old_focus = self.focused
            self.focused = focused
            
            if focused and not old_focus and self.on_focus:
                self.on_focus(self)
            elif not focused and old_focus and self.on_blur:
                self.on_blur(self)
    
    def draw(self, parent_width: float, parent_height: float) -> None:
        """Element'i çiz (override edilmeli)"""
        pass


class Label(UIElement):
    """Metin etiketi"""
    
    def __init__(self, text: str = "", x: float = 0, y: float = 0, 
                 font_name: str = "Arial", font_size: int = 12, 
                 color: Tuple[int, int, int, int] = (255, 255, 255, 255)):
        super().__init__(x, y, 0, 0)
        
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.color = color
        
        # Pyglet label
        self._create_label()
    
    def _create_label(self) -> None:
        """Pyglet label oluştur"""
        self.label = pyglet.text.Label(
            self.text,
            font_name=self.font_name,
            font_size=self.font_size,
            color=self.color,
            anchor_x='left',
            anchor_y='bottom'
        )
        
        # Boyutları güncelle
        self.width = self.label.content_width
        self.height = self.label.content_height
    
    def set_text(self, text: str) -> None:
        """Metni ayarla"""
        self.text = text
        self.label.text = text
        self.width = self.label.content_width
        self.height = self.label.content_height
    
    def set_color(self, color: Tuple[int, int, int, int]) -> None:
        """Rengi ayarla"""
        self.color = color
        self.label.color = color
    
    def draw(self, parent_width: float, parent_height: float) -> None:
        """Label'ı çiz"""
        if not self.visible:
            return
        
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        
        gl.glPushMatrix()
        gl.glTranslatef(abs_x, abs_y, 0)
        
        self.label.draw()
        
        gl.glPopMatrix()


class Button(UIElement):
    """Buton"""
    
    def __init__(self, text: str = "", x: float = 0, y: float = 0, 
                 width: float = 100, height: float = 30, on_click: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        
        self.text = text
        self.on_click = on_click
        self.focusable = True
        
        # Durum
        self.pressed = False
        self.hovered = False
        
        # Renkler
        self.normal_color = (100, 100, 100, 255)
        self.hover_color = (120, 120, 120, 255)
        self.pressed_color = (80, 80, 80, 255)
        self.disabled_color = (60, 60, 60, 128)
        
        # Label
        self.label = pyglet.text.Label(
            text,
            font_name="Arial",
            font_size=12,
            color=(255, 255, 255, 255),
            anchor_x='center',
            anchor_y='center'
        )
    
    def set_text(self, text: str) -> None:
        """Metni ayarla"""
        self.text = text
        self.label.text = text
    
    def handle_mouse_press(self, x: float, y: float, button: int, parent_width: float, parent_height: float) -> bool:
        """Fare basma eventi"""
        if super().handle_mouse_press(x, y, button, parent_width, parent_height):
            self.pressed = True
            return True
        return False
    
    def handle_mouse_release(self, x: float, y: float, button: int, parent_width: float, parent_height: float) -> bool:
        """Fare bırakma eventi"""
        if self.pressed:
            self.pressed = False
            if self.contains_point(x, y, parent_width, parent_height):
                if self.on_click:
                    self.on_click(self, x, y, button)
                return True
        return False
    
    def handle_mouse_motion(self, x: float, y: float, parent_width: float, parent_height: float) -> bool:
        """Fare hareket eventi"""
        old_hovered = self.hovered
        self.hovered = self.contains_point(x, y, parent_width, parent_height)
        
        if self.hovered != old_hovered and self.on_hover:
            self.on_hover(self, x, y)
        
        return self.hovered
    
    def get_current_color(self) -> Tuple[int, int, int, int]:
        """Mevcut rengi döndür"""
        if not self.enabled:
            return self.disabled_color
        elif self.pressed:
            return self.pressed_color
        elif self.hovered:
            return self.hover_color
        else:
            return self.normal_color
    
    def draw(self, parent_width: float, parent_height: float) -> None:
        """Buton'u çiz"""
        if not self.visible:
            return
        
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        color = self.get_current_color()
        
        # Arka plan
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        gl.glColor4f(color[0]/255.0, color[1]/255.0, color[2]/255.0, color[3]/255.0)
        
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(abs_x, abs_y)
        gl.glVertex2f(abs_x + self.width, abs_y)
        gl.glVertex2f(abs_x + self.width, abs_y + self.height)
        gl.glVertex2f(abs_x, abs_y + self.height)
        gl.glEnd()
        
        # Kenarlık
        gl.glColor4f(0.8, 0.8, 0.8, 1.0)
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f(abs_x, abs_y)
        gl.glVertex2f(abs_x + self.width, abs_y)
        gl.glVertex2f(abs_x + self.width, abs_y + self.height)
        gl.glVertex2f(abs_x, abs_y + self.height)
        gl.glEnd()
        
        # Metin
        gl.glColor4f(1.0, 1.0, 1.0, 1.0)
        gl.glPushMatrix()
        gl.glTranslatef(abs_x + self.width/2, abs_y + self.height/2, 0)
        self.label.draw()
        gl.glPopMatrix()
        
        gl.glDisable(gl.GL_BLEND)


class Panel(UIElement):
    """Panel container"""
    
    def __init__(self, x: float = 0, y: float = 0, width: float = 200, height: float = 200):
        super().__init__(x, y, width, height)
        
        self.children: List[UIElement] = []
        
        # Panel özellikleri
        self.background_color = (50, 50, 50, 200)
        self.border_color = (100, 100, 100, 255)
        self.show_border = True
    
    def add_child(self, child: UIElement) -> None:
        """Alt element ekle"""
        self.children.append(child)
    
    def remove_child(self, child: UIElement) -> None:
        """Alt element kaldır"""
        if child in self.children:
            self.children.remove(child)
    
    def clear_children(self) -> None:
        """Tüm alt elementleri temizle"""
        self.children.clear()
    
    def handle_mouse_press(self, x: float, y: float, button: int, parent_width: float, parent_height: float) -> bool:
        """Fare basma eventi"""
        if not self.enabled or not self.visible:
            return False
        
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        
        # Panel içindeki koordinatları hesapla
        local_x = x - abs_x
        local_y = y - abs_y
        
        # Alt elementlerde kontrol et (ters sırada - üstteki önce)
        for child in reversed(self.children):
            if child.handle_mouse_press(local_x, local_y, button, self.width, self.height):
                return True
        
        # Panel kendisi
        if self.contains_point(x, y, parent_width, parent_height):
            if self.on_click:
                self.on_click(self, x, y, button)
            return True
        
        return False
    
    def handle_mouse_release(self, x: float, y: float, button: int, parent_width: float, parent_height: float) -> bool:
        """Fare bırakma eventi"""
        if not self.enabled or not self.visible:
            return False
        
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        local_x = x - abs_x
        local_y = y - abs_y
        
        for child in reversed(self.children):
            if hasattr(child, 'handle_mouse_release'):
                if child.handle_mouse_release(local_x, local_y, button, self.width, self.height):
                    return True
        
        return False
    
    def handle_mouse_motion(self, x: float, y: float, parent_width: float, parent_height: float) -> bool:
        """Fare hareket eventi"""
        if not self.enabled or not self.visible:
            return False
        
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        local_x = x - abs_x
        local_y = y - abs_y
        
        for child in reversed(self.children):
            if child.handle_mouse_motion(local_x, local_y, self.width, self.height):
                return True
        
        return self.contains_point(x, y, parent_width, parent_height)
    
    def draw(self, parent_width: float, parent_height: float) -> None:
        """Panel'i çiz"""
        if not self.visible:
            return
        
        abs_x, abs_y = self.get_absolute_position(parent_width, parent_height)
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Arka plan
        gl.glColor4f(self.background_color[0]/255.0, self.background_color[1]/255.0, 
                     self.background_color[2]/255.0, self.background_color[3]/255.0)
        
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(abs_x, abs_y)
        gl.glVertex2f(abs_x + self.width, abs_y)
        gl.glVertex2f(abs_x + self.width, abs_y + self.height)
        gl.glVertex2f(abs_x, abs_y + self.height)
        gl.glEnd()
        
        # Kenarlık
        if self.show_border:
            gl.glColor4f(self.border_color[0]/255.0, self.border_color[1]/255.0, 
                         self.border_color[2]/255.0, self.border_color[3]/255.0)
            
            gl.glBegin(gl.GL_LINE_LOOP)
            gl.glVertex2f(abs_x, abs_y)
            gl.glVertex2f(abs_x + self.width, abs_y)
            gl.glVertex2f(abs_x + self.width, abs_y + self.height)
            gl.glVertex2f(abs_x, abs_y + self.height)
            gl.glEnd()
        
        # Alt elementleri çiz
        gl.glPushMatrix()
        gl.glTranslatef(abs_x, abs_y, 0)
        
        for child in self.children:
            child.draw(self.width, self.height)
        
        gl.glPopMatrix()
        
        gl.glDisable(gl.GL_BLEND)


class UIManager:
    """UI yöneticisi"""
    
    def __init__(self, app):
        self.app = app
        self.elements: List[UIElement] = []
        self.focused_element: Optional[UIElement] = None
        self.root_panel = Panel(0, 0, app.width, app.height)
    
    def add_element(self, element: UIElement) -> None:
        """UI element ekle"""
        self.elements.append(element)
        self.root_panel.add_child(element)
    
    def remove_element(self, element: UIElement) -> None:
        """UI element kaldır"""
        if element in self.elements:
            self.elements.remove(element)
            self.root_panel.remove_child(element)
            
            if self.focused_element == element:
                self.focused_element = None
    
    def clear(self) -> None:
        """Tüm UI elementleri temizle"""
        self.elements.clear()
        self.root_panel.clear_children()
        self.focused_element = None
    
    def set_focus(self, element: Optional[UIElement]) -> None:
        """Focus ayarla"""
        if self.focused_element:
            self.focused_element.set_focus(False)
        
        self.focused_element = element
        
        if element:
            element.set_focus(True)
    
    def handle_mouse_press(self, x: float, y: float, button: int) -> bool:
        """Fare basma eventi"""
        return self.root_panel.handle_mouse_press(x, y, button, self.app.width, self.app.height)
    
    def handle_mouse_release(self, x: float, y: float, button: int) -> bool:
        """Fare bırakma eventi"""
        return self.root_panel.handle_mouse_release(x, y, button, self.app.width, self.app.height)
    
    def handle_mouse_motion(self, x: float, y: float) -> bool:
        """Fare hareket eventi"""
        return self.root_panel.handle_mouse_motion(x, y, self.app.width, self.app.height)
    
    def draw(self) -> None:
        """UI'yi çiz"""
        self.root_panel.draw(self.app.width, self.app.height)
