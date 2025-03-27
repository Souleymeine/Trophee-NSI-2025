from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import NoneType
from type_def.data_types import Coord, Anchor, RGB
from type_def.input_properties import MouseInfo
from core.event_listeners import listeners, MouseCallbacks

@dataclass
class Positioning:
    origin: Coord
    anchor: Anchor
    width: int
    height: int

class TUIElement(ABC):
    def __init__(self, positioning: Positioning, z_index: int = 0, visible: bool = True, fg_col: RGB | NoneType = None, bg_col: RGB | NoneType = None):
        self._positioning = positioning
        self._z_index = z_index
        self._visible = visible
        self._fg_col = fg_col
        self._bg_col = bg_col
        if self._visible:
            self.render()
    
    @property
    def positioning(self):
        return self._positioning
    @positioning.setter
    def positioning(self, value: Positioning):
        if not isinstance(value, Positioning):
            raise TypeError("height must be a 'Positioning'")
        self._positioning = value

    @property
    def z_index(self):
        return self._z_index
    @z_index.setter
    def z_index(self, value: int):
        if not isinstance(value, int):
            raise TypeError("z_index must be an integer")
        self._z_index = value

    @property
    def visible(self):
        return self._visible
    @visible.setter
    def visible(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("visible must be a boolean")
        self._visible = value

    @property
    def foreground_color(self):
        return self._fg_col
    @foreground_color.setter
    def foreground_color(self, value: RGB):
        if not isinstance(value, RGB):
            raise TypeError("color must be of type RGB")
        self._fg_col = value

    @property
    def background_color(self):
        return self._bg_col
    @background_color.setter
    def background_color(self, value: RGB):
        if not isinstance(value, RGB):
            raise TypeError("color must be of type RGB")
        self._bg_col = value

    @property
    def top_left_coord(self) -> Coord:
        """Détermine les coordonnées du coin supérieur gauche en fonction de l'ancrage et de la position de l'élément."""
        match self._positioning.anchor:
            case Anchor.CENTER:
                return Coord(int(self._positioning.origin.x - (self._positioning.width / 2)), int(self._positioning.origin.y - (self._positioning.height / 2)))
            case Anchor.TOP_LEFT:
                return Coord(self._positioning.origin.x, self._positioning.origin.y)
            case Anchor.TOP_RIGHT:
                return Coord(self._positioning.origin.x - self._positioning.width, self._positioning.origin.y)
            case Anchor.BOTTOM_LEFT:
                return Coord(self._positioning.origin.x, self._positioning.origin.y - self._positioning.height)
            case Anchor.BOTTOM_RIGHT:
                return Coord(self._positioning.origin.x - self._positioning.width, self._positioning.origin.y - self._positioning.height)

    @abstractmethod
    def render(self):
        """
        Imprime l'élément dans sur l'écran.
        Méthode abstraite à implémenter.
        """
        pass


@dataclass
class ColorsOnMouse:
    default_fg_col: RGB | NoneType = None
    default_bg_col: RGB | NoneType = None
    hover_fg_col: RGB | NoneType = None
    hover_bg_col: RGB | NoneType = None
    click_fg_col: RGB | NoneType = None
    click_bg_col: RGB | NoneType = None


class ClickableElement(TUIElement):
    def __init__(self, positioning: Positioning, colors_on_mouse: ColorsOnMouse,
                 z_index: int = 0, visible: bool = True):
        super().__init__(positioning, z_index, visible, colors_on_mouse.hover_fg_col, colors_on_mouse.default_bg_col)
        self._is_mouse_over = False
        listeners.register_mouse_callbacks(self, MouseCallbacks(self._on_hover, self._on_click, self._on_mouse_exit))

    @property
    def is_mouse_over(self):
        return self._is_mouse_over
    @is_mouse_over.setter
    def is_mouse_over(self, value: bool):
        self._is_mouse_over = value

    def render(self):
        return super().render()

    # Comportement par défaut

    @abstractmethod
    def _on_hover(self, info: MouseInfo):
        """Méthode abstraite à implémenter.
        Appelée lorsque la souris survol l'élément."""
        self.on_hover(info)
        self.is_mouse_over = True
        pass
    @abstractmethod
    def _on_click(self, info: MouseInfo):
        """Méthode abstraite à implémenter.
        Appelée lorsque un click est effectué sur l'élément."""
        self.on_click(info)
        pass
    @abstractmethod
    def _on_mouse_exit(self, info: MouseInfo):
        """Méthode abstraite à implémenter.
        Appelée lorsque la souris souris ne survol plus l'élement."""
        self.on_mouse_exit(info)
        pass

    # Comportement définie par surcharge, appellé après le comportement par défaut

    def on_hover(self, info: MouseInfo):
        """Appellée après le comportement par défaut de l'élément"""
        pass
    def on_click(self, info: MouseInfo):
        """Appellée après le comportement par défaut de l'élément"""
        pass
    def on_mouse_exit(self, info: MouseInfo):
        """Appellée après le comportement par défaut de l'élément"""
        pass
