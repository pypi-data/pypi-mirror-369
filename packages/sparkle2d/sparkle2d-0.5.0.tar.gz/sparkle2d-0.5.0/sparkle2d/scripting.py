"""
Lua scripting engine - lupa ile Python-Lua köprüsü
"""

import os
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import lupa


class LuaScript:
    """Lua script wrapper"""
    
    def __init__(self, lua_state, script_path: str):
        self.lua_state = lua_state
        self.script_path = script_path
        self.last_modified = 0
        self.functions = {}
        self._load_script()
    
    def _load_script(self) -> None:
        """Script'i yükle"""
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # Lua'da çalıştır
            self.lua_state.execute(script_content)
            
            # Fonksiyonları kaydet
            self.functions = {
                'start': self.lua_state.globals().get('start'),
                'update': self.lua_state.globals().get('update'),
                'on_key_press': self.lua_state.globals().get('on_key_press'),
                'on_key_release': self.lua_state.globals().get('on_key_release'),
            }
            
            self.last_modified = os.path.getmtime(self.script_path)
            
        except Exception as e:
            print(f"Lua script yükleme hatası {self.script_path}: {e}")
    
    def reload(self) -> bool:
        """Script'i yeniden yükle"""
        try:
            current_mtime = os.path.getmtime(self.script_path)
            if current_mtime > self.last_modified:
                self._load_script()
                return True
        except Exception as e:
            print(f"Script yenileme hatası {self.script_path}: {e}")
        return False
    
    def call_function(self, func_name: str, *args) -> Any:
        """Lua fonksiyonu çağır"""
        func = self.functions.get(func_name)
        if func:
            try:
                return func(*args)
            except Exception as e:
                print(f"Lua fonksiyon hatası {func_name}: {e}")
        return None
    
    def start(self) -> None:
        """start() fonksiyonunu çağır"""
        self.call_function('start')
    
    def update(self, dt: float) -> None:
        """update(dt) fonksiyonunu çağır"""
        self.call_function('update', dt)
    
    def on_key_press(self, key: str) -> None:
        """on_key_press(key) fonksiyonunu çağır"""
        self.call_function('on_key_press', key)
    
    def on_key_release(self, key: str) -> None:
        """on_key_release(key) fonksiyonunu çağır"""
        self.call_function('on_key_release', key)


class ScriptFileHandler(FileSystemEventHandler):
    """Script dosya değişiklik izleyicisi"""
    
    def __init__(self, scripting_engine):
        self.scripting_engine = scripting_engine
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.lua'):
            self.scripting_engine.on_script_modified(event.src_path)


class ScriptingEngine:
    """Lua scripting engine"""
    
    def __init__(self, app):
        self.app = app
        self.lua_state = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.scripts: Dict[str, LuaScript] = {}
        self.watchdog_enabled = False
        self.observer = None
        
        # Lua API fonksiyonlarını kaydet
        self._setup_lua_api()
    
    def _setup_lua_api(self) -> None:
        """Lua API fonksiyonlarını ayarla"""
        lua_globals = self.lua_state.globals()
        
        # Entity yönetimi
        lua_globals['spawn_sprite'] = self._lua_spawn_sprite
        lua_globals['destroy'] = self._lua_destroy
        lua_globals['set_anim'] = self._lua_set_anim
        lua_globals['set_z'] = self._lua_set_z
        lua_globals['tag'] = self._lua_tag
        
        # Kamera kontrolü
        lua_globals['camera_follow'] = self._lua_camera_follow
        lua_globals['camera_set_zoom'] = self._lua_camera_set_zoom
        lua_globals['world_to_screen'] = self._lua_world_to_screen
        lua_globals['screen_to_world'] = self._lua_screen_to_world
        
        # Input sistemi
        lua_globals['bind'] = self._lua_bind
        lua_globals['action_down'] = self._lua_action_down
        lua_globals['action_pressed'] = self._lua_action_pressed
        
        # Fizik sistemi
        lua_globals['physics_body'] = self._lua_physics_body
        lua_globals['physics_set_velocity'] = self._lua_physics_set_velocity
        lua_globals['apply_force'] = self._lua_apply_force
        lua_globals['apply_impulse'] = self._lua_apply_impulse
        lua_globals['on_begin_contact'] = self._lua_on_begin_contact
        lua_globals['on_end_contact'] = self._lua_on_end_contact
        
        # Tilemap
        lua_globals['load_map'] = self._lua_load_map
        lua_globals['world_bounds_from_map'] = self._lua_world_bounds_from_map
        
        # Particle sistemi
        lua_globals['spawn_emitter'] = self._lua_spawn_emitter
        lua_globals['emitter_set_position'] = self._lua_emitter_set_position
        
        # Tween
        lua_globals['tween'] = self._lua_tween
        
        # UI sistemi
        lua_globals['ui_button'] = self._lua_ui_button
        lua_globals['label'] = self._lua_label
        lua_globals['panel'] = self._lua_panel
        
        # Event sistemi
        lua_globals['on'] = self._lua_on
        lua_globals['once'] = self._lua_once
        lua_globals['off'] = self._lua_off
        lua_globals['emit'] = self._lua_emit
        
        # Ses sistemi
        lua_globals['sfx'] = self._lua_sfx
        lua_globals['music_play'] = self._lua_music_play
        
        # Kaydetme sistemi
        lua_globals['save_game'] = self._lua_save_game
        lua_globals['load_game'] = self._lua_load_game
        
        # Hot reload
        lua_globals['watch_scripts'] = self._lua_watch_scripts
    
    def load_script(self, script_path: str) -> Optional[LuaScript]:
        """Lua script yükle"""
        try:
            script = LuaScript(self.lua_state, script_path)
            self.scripts[script_path] = script
            return script
        except Exception as e:
            print(f"Script yükleme hatası {script_path}: {e}")
            return None
    
    def reload_script(self, script_path: str) -> bool:
        """Script'i yeniden yükle"""
        if script_path in self.scripts:
            return self.scripts[script_path].reload()
        return False
    
    def enable_watchdog(self, script_dir: str) -> None:
        """Script dosya izlemeyi etkinleştir"""
        if not self.watchdog_enabled:
            self.observer = Observer()
            handler = ScriptFileHandler(self)
            self.observer.schedule(handler, script_dir, recursive=True)
            self.observer.start()
            self.watchdog_enabled = True
    
    def disable_watchdog(self) -> None:
        """Script dosya izlemeyi devre dışı bırak"""
        if self.watchdog_enabled and self.observer:
            self.observer.stop()
            self.observer.join()
            self.watchdog_enabled = False
    
    def on_script_modified(self, script_path: str) -> None:
        """Script dosyası değiştiğinde çağrılır"""
        if script_path in self.scripts:
            print(f"Script yenileniyor: {script_path}")
            self.reload_script(script_path)
    
    def update(self, dt: float) -> None:
        """Tüm script'leri güncelle"""
        for script in self.scripts.values():
            script.update(dt)
    
    # Lua API fonksiyonları
    def _lua_spawn_sprite(self, path: str, x: float, y: float) -> str:
        """Lua: spawn_sprite(path, x, y) -> entity_id"""
        entity = self.app.entity_manager.create_entity()
        
        # Transform component
        from .ecs import Transform, Sprite, Tag
        entity.add_component(Transform(x=x, y=y))
        
        # Sprite component
        try:
            image = self.app.resources.load_image(path)
            entity.add_component(Sprite(
                image_path=path,
                image=image,
                width=image.width,
                height=image.height
            ))
        except:
            # Placeholder sprite
            entity.add_component(Sprite(width=32, height=32))
        
        return entity.id
    
    def _lua_destroy(self, entity_id: str) -> None:
        """Lua: destroy(entity_id)"""
        self.app.entity_manager.destroy_entity(entity_id)
    
    def _lua_set_anim(self, entity_id: str, anim_name: str) -> None:
        """Lua: set_anim(entity_id, name)"""
        entity = self.app.entity_manager.get_entity(entity_id)
        if entity:
            # Animation component ekle/güncelle
            from .ecs import Sprite
            sprite = entity.get_component(Sprite)
            if sprite:
                sprite.image_path = f"assets/sprites/{anim_name}.png"
    
    def _lua_set_z(self, entity_id: str, z: float) -> None:
        """Lua: set_z(entity_id, z)"""
        entity = self.app.entity_manager.get_entity(entity_id)
        if entity:
            from .ecs import Transform
            transform = entity.get_component(Transform)
            if transform:
                transform.z = z
    
    def _lua_tag(self, entity_id: str, tag_name: str) -> None:
        """Lua: tag(entity_id, tag_name)"""
        entity = self.app.entity_manager.get_entity(entity_id)
        if entity:
            from .ecs import Tag
            entity.add_component(Tag(name=tag_name))
    
    def _lua_camera_follow(self, entity_id: str, lerp: float) -> None:
        """Lua: camera_follow(entity_id, lerp)"""
        entity = self.app.entity_manager.get_entity(entity_id)
        if entity:
            self.app.camera.follow(entity, lerp)
    
    def _lua_camera_set_zoom(self, zoom: float) -> None:
        """Lua: camera_set_zoom(zoom)"""
        self.app.camera.set_zoom(zoom)
    
    def _lua_world_to_screen(self, wx: float, wy: float) -> tuple:
        """Lua: world_to_screen(wx, wy) -> (sx, sy)"""
        return self.app.camera.world_to_screen(wx, wy)
    
    def _lua_screen_to_world(self, sx: float, sy: float) -> tuple:
        """Lua: screen_to_world(sx, sy) -> (wx, wy)"""
        return self.app.camera.screen_to_world(sx, sy)
    
    def _lua_bind(self, action: str, keys: str) -> None:
        """Lua: bind(action, keys)"""
        self.app.input_map.bind(action, keys)
    
    def _lua_action_down(self, action: str) -> bool:
        """Lua: action_down(action) -> bool"""
        return self.app.input_map.action_down(action)
    
    def _lua_action_pressed(self, action: str) -> bool:
        """Lua: action_pressed(action) -> bool"""
        return self.app.input_map.action_pressed(action)
    
    def _lua_physics_body(self, entity_id: str, config: dict) -> int:
        """Lua: physics_body(entity_id, config) -> body_id"""
        # Placeholder - gerçek fizik implementasyonu
        return 1
    
    def _lua_physics_set_velocity(self, body_id: int, vx: float, vy: float) -> None:
        """Lua: physics_set_velocity(body_id, vx, vy)"""
        pass
    
    def _lua_apply_force(self, body_id: int, fx: float, fy: float) -> None:
        """Lua: apply_force(body_id, fx, fy)"""
        pass
    
    def _lua_apply_impulse(self, body_id: int, ix: float, iy: float) -> None:
        """Lua: apply_impulse(body_id, ix, iy)"""
        pass
    
    def _lua_on_begin_contact(self, tag_a: str, tag_b: str, callback) -> None:
        """Lua: on_begin_contact(tagA, tagB, callback)"""
        pass
    
    def _lua_on_end_contact(self, tag_a: str, tag_b: str, callback) -> None:
        """Lua: on_end_contact(tagA, tagB, callback)"""
        pass
    
    def _lua_load_map(self, map_path: str) -> None:
        """Lua: load_map(map_path)"""
        pass
    
    def _lua_world_bounds_from_map(self) -> None:
        """Lua: world_bounds_from_map()"""
        pass
    
    def _lua_spawn_emitter(self, config: dict) -> int:
        """Lua: spawn_emitter(config) -> emitter_id"""
        return 1
    
    def _lua_emitter_set_position(self, emitter_id: int, x: float, y: float) -> None:
        """Lua: emitter_set_position(emitter_id, x, y)"""
        pass
    
    def _lua_tween(self, entity_id: str, properties: dict, duration: float, easing: str) -> None:
        """Lua: tween(entity_id, properties, duration, easing)"""
        entity = self.app.entity_manager.get_entity(entity_id)
        if entity:
            self.app.tween_manager.tween(entity, properties, duration, easing)
    
    def _lua_ui_button(self, config: dict) -> int:
        """Lua: ui_button(config) -> button_id"""
        return 1
    
    def _lua_label(self, config: dict) -> int:
        """Lua: label(config) -> label_id"""
        return 1
    
    def _lua_panel(self, config: dict) -> int:
        """Lua: panel(config) -> panel_id"""
        return 1
    
    def _lua_on(self, event: str, callback) -> None:
        """Lua: on(event, callback)"""
        self.app.events.on(event, callback)
    
    def _lua_once(self, event: str, callback) -> None:
        """Lua: once(event, callback)"""
        self.app.events.once(event, callback)
    
    def _lua_off(self, event: str, callback) -> None:
        """Lua: off(event, callback)"""
        self.app.events.off(event, callback)
    
    def _lua_emit(self, event: str, data=None) -> None:
        """Lua: emit(event, data)"""
        self.app.events.emit(event, data)
    
    def _lua_sfx(self, sound_path: str) -> None:
        """Lua: sfx(sound_path)"""
        pass
    
    def _lua_music_play(self, music_path: str, config: dict) -> None:
        """Lua: music_play(music_path, config)"""
        pass
    
    def _lua_save_game(self, slot: str) -> None:
        """Lua: save_game(slot)"""
        pass
    
    def _lua_load_game(self, slot: str) -> None:
        """Lua: load_game(slot)"""
        pass
    
    def _lua_watch_scripts(self, enabled: bool) -> None:
        """Lua: watch_scripts(enabled)"""
        if enabled and not self.watchdog_enabled:
            self.enable_watchdog("scripts")
        elif not enabled and self.watchdog_enabled:
            self.disable_watchdog()
