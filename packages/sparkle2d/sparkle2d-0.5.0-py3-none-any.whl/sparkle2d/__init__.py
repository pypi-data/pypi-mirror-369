"""
Sparkle2D - Lua script destekli 2D oyun motoru
"""

__version__ = "0.5.0"
__author__ = "Baba"

from .app import App
from .scene import Scene, SceneManager
from .camera import Camera2D
from .inputmap import InputMap
from .resources import ResourceManager
from .animation import Animation, Animator
from .particles import ParticleEmitter
from .physics import PhysicsWorld
from .tilemap import Tilemap
from .ui import UIElement, Button, Label, Panel
from .tween import Tween, TweenManager
from .audio import AudioManager
from .events import EventBus
from .scripting import ScriptingEngine
from .ecs import Entity, Component, System

__all__ = [
    "App",
    "Scene", 
    "SceneManager",
    "Camera2D",
    "InputMap",
    "ResourceManager",
    "Animation",
    "Animator", 
    "ParticleEmitter",
    "PhysicsWorld",
    "Tilemap",
    "UIElement",
    "Button",
    "Label",
    "Panel",
    "Tween",
    "TweenManager",
    "AudioManager",
    "EventBus",
    "ScriptingEngine",
    "Entity",
    "Component",
    "System"
]
