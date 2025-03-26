from __future__ import annotations # Permet de référancer une classe à l'intérieur d'elle-même
from dataclasses import dataclass
from enum import Enum
from enum import IntFlag
from type_def.data_types import Coord


# ========== Souris ===========

class XtermMouseFlags(IntFlag):
    SHIFT = 4
    ALT = 8
    CTRL = 16
    MOVE = 32 
class MouseKeyFlags(IntFlag):
    """Sert de masque pour les touches de modification"""
    CTRL = 1
    SHIFT = 2
    ALT = 4
    MOVE = 8

class MouseButton(Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2
class MouseWheel(Enum):
    SCROLL_UP = 0
    SCROLL_DOWN = 1

@dataclass
class MouseClick():
    """Indique les informations relatives aux cliques, c'est-à-dire le bouton utilisé et s'il est relaché ou non"""
    button: MouseButton
    released: bool

@dataclass
class MouseInfo():
    """Indique toutes les informations accessibles à propos de la souris à un instant t"""
    click: MouseClick | None
    wheel: MouseWheel | None
    coord: Coord
    mouse_key_flag: int


# ========== Touches ==========

class XtermKeyFlags(IntFlag):
    SHIFT = 1
    ALT = 2
    CTRL = 4
class KeyFlags(IntFlag):
    CTRL = 1
    SHIFT = 2
    ALT = 4

class Arrows(Enum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3

@dataclass
class ArrowInfo:
    arrow: Arrows
    key_flag: int
@dataclass
class KeyInfo:
    char: bytes
    key_flag: int
