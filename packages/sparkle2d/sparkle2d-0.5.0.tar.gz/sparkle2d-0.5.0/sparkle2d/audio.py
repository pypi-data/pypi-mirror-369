"""
Ses sistemi - SFX/Music, groups, loop, fade in/out
"""

from typing import Dict, List, Optional, Any
import pyglet
import math


class AudioManager:
    """Ses yöneticisi"""
    
    def __init__(self):
        self.sfx_volume = 1.0
        self.music_volume = 0.7
        
        # Ses kaynakları
        self.sfx_sources: Dict[str, pyglet.media.Source] = {}
        self.music_sources: Dict[str, pyglet.media.Source] = {}
        
        # Aktif çalan sesler
        self.active_sfx: List[pyglet.media.Player] = []
        self.active_music: List[pyglet.media.Player] = []
        
        # Müzik geçişleri
        self.fade_in_duration = 1.0
        self.fade_out_duration = 1.0
        
        # Ses grupları
        self.sfx_groups: Dict[str, float] = {
            'master': 1.0,
            'ui': 1.0,
            'game': 1.0,
            'ambient': 1.0
        }
    
    def load_sfx(self, name: str, file_path: str) -> bool:
        """SFX yükle"""
        try:
            source = pyglet.media.load(file_path)
            self.sfx_sources[name] = source
            return True
        except Exception as e:
            print(f"SFX yükleme hatası {file_path}: {e}")
            return False
    
    def load_music(self, name: str, file_path: str) -> bool:
        """Müzik yükle"""
        try:
            source = pyglet.media.load(file_path)
            self.music_sources[name] = source
            return True
        except Exception as e:
            print(f"Müzik yükleme hatası {file_path}: {e}")
            return False
    
    def play_sfx(self, name: str, group: str = "game", volume: Optional[float] = None) -> Optional[pyglet.media.Player]:
        """SFX çal"""
        if name not in self.sfx_sources:
            print(f"SFX bulunamadı: {name}")
            return None
        
        try:
            # Player oluştur
            player = pyglet.media.Player()
            player.queue(self.sfx_sources[name])
            
            # Ses seviyesi ayarla
            final_volume = volume or self.sfx_volume
            if group in self.sfx_groups:
                final_volume *= self.sfx_groups[group]
            
            player.volume = final_volume
            
            # Çalmaya başla
            player.play()
            
            # Aktif listeye ekle
            self.active_sfx.append(player)
            
            # Çalma bittiğinde listeden kaldır
            def on_eos():
                if player in self.active_sfx:
                    self.active_sfx.remove(player)
            
            player.push_handlers(on_eos=on_eos)
            
            return player
            
        except Exception as e:
            print(f"SFX çalma hatası {name}: {e}")
            return None
    
    def play_music(self, name: str, loop: bool = True, fade_in: bool = True, 
                   volume: Optional[float] = None) -> Optional[pyglet.media.Player]:
        """Müzik çal"""
        if name not in self.music_sources:
            print(f"Müzik bulunamadı: {name}")
            return None
        
        try:
            # Mevcut müziği durdur
            self.stop_music(fade_out=True)
            
            # Player oluştur
            player = pyglet.media.Player()
            player.queue(self.music_sources[name])
            
            # Loop ayarla
            if loop:
                player.loop = True
            
            # Ses seviyesi ayarla
            final_volume = volume or self.music_volume
            if fade_in:
                player.volume = 0.0
                self._fade_in_music(player, final_volume)
            else:
                player.volume = final_volume
            
            # Çalmaya başla
            player.play()
            
            # Aktif listeye ekle
            self.active_music.append(player)
            
            return player
            
        except Exception as e:
            print(f"Müzik çalma hatası {name}: {e}")
            return None
    
    def stop_sfx(self, player: Optional[pyglet.media.Player] = None) -> None:
        """SFX durdur"""
        if player:
            if player in self.active_sfx:
                player.pause()
                self.active_sfx.remove(player)
        else:
            # Tüm SFX'leri durdur
            for sfx in self.active_sfx:
                sfx.pause()
            self.active_sfx.clear()
    
    def stop_music(self, fade_out: bool = False) -> None:
        """Müzik durdur"""
        if fade_out:
            # Fade out ile durdur
            for music in self.active_music:
                self._fade_out_music(music)
        else:
            # Anında durdur
            for music in self.active_music:
                music.pause()
            self.active_music.clear()
    
    def pause_music(self) -> None:
        """Müziği duraklat"""
        for music in self.active_music:
            music.pause()
    
    def resume_music(self) -> None:
        """Müziği devam ettir"""
        for music in self.active_music:
            music.play()
    
    def set_sfx_volume(self, volume: float) -> None:
        """SFX ses seviyesini ayarla"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Aktif SFX'lerin ses seviyesini güncelle
        for sfx in self.active_sfx:
            sfx.volume = self.sfx_volume
    
    def set_music_volume(self, volume: float) -> None:
        """Müzik ses seviyesini ayarla"""
        self.music_volume = max(0.0, min(1.0, volume))
        
        # Aktif müziklerin ses seviyesini güncelle
        for music in self.active_music:
            music.volume = self.music_volume
    
    def set_group_volume(self, group: str, volume: float) -> None:
        """Grup ses seviyesini ayarla"""
        self.sfx_groups[group] = max(0.0, min(1.0, volume))
    
    def _fade_in_music(self, player: pyglet.media.Player, target_volume: float) -> None:
        """Müzik fade in"""
        def fade_step(dt):
            current_volume = player.volume
            if current_volume < target_volume:
                new_volume = min(target_volume, current_volume + (target_volume / self.fade_in_duration) * dt)
                player.volume = new_volume
            else:
                player.volume = target_volume
                return False  # Schedule'ı durdur
        
        pyglet.clock.schedule(fade_step)
    
    def _fade_out_music(self, player: pyglet.media.Player) -> None:
        """Müzik fade out"""
        def fade_step(dt):
            current_volume = player.volume
            if current_volume > 0:
                new_volume = max(0.0, current_volume - (current_volume / self.fade_out_duration) * dt)
                player.volume = new_volume
            else:
                player.pause()
                if player in self.active_music:
                    self.active_music.remove(player)
                return False  # Schedule'ı durdur
        
        pyglet.clock.schedule(fade_step)
    
    def update(self, dt: float) -> None:
        """Ses yöneticisini güncelle"""
        # Ölü player'ları temizle
        self.active_sfx = [sfx for sfx in self.active_sfx if sfx.playing]
        self.active_music = [music for music in self.active_music if music.playing]
    
    def clear(self) -> None:
        """Tüm sesleri temizle"""
        self.stop_sfx()
        self.stop_music()
        self.sfx_sources.clear()
        self.music_sources.clear()
    
    def get_sfx_count(self) -> int:
        """Aktif SFX sayısını döndür"""
        return len(self.active_sfx)
    
    def get_music_count(self) -> int:
        """Aktif müzik sayısını döndür"""
        return len(self.active_music)
    
    def is_music_playing(self) -> bool:
        """Müzik çalıyor mu kontrol et"""
        return len(self.active_music) > 0 and any(music.playing for music in self.active_music)
    
    def get_current_music(self) -> Optional[str]:
        """Şu anda çalan müziği döndür"""
        for name, source in self.music_sources.items():
            for music in self.active_music:
                if music.source == source:
                    return name
        return None
