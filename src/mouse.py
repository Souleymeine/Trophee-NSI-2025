from __future__ import annotations # Permet de référancer une classe à l'intérieur d'elle-même
from dataclasses import dataclass
from enum import Enum
from enum import IntFlag
from data_types import Coord


class Button(Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2
class Wheel(Enum):
    SCROLL_UP = 0
    SCROLL_DOWN = 1

class MouseKeyFlags(IntFlag):
    """Sert de masque pour les touches de modification"""
    NONE = 0
    CTRL = 1
    SHIFT = 2
    ALT = 4
    MOVE = 8

@dataclass
class Click():
    """Indique les informations relatives aux cliques, c'est-à-dire le bouton utilisé et s'il est relaché ou non"""
    button: Button
    released: bool

@dataclass
class Info():
    """Indique toutes les informations accessibles à propos de la souris à un instant t"""
    click: Click | None
    wheel: Wheel | None
    coord: Coord
    mouse_key_flag: int
