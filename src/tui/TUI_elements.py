from type_def.data_types import RGB, Anchor, Coord
from abc import ABC, abstractmethod
from escape_sequences import gohome, print_at, set_fgcolor, reset_fgcolor


class TUI_element(ABC):
    def __init__(self, position: Coord, anchor: Anchor, width: int, height: int, z_index: int = 0):
        self._position = position
        self._anchor = anchor
        self._width = width
        self._height = height
        self._z_index = z_index
        self._visible = True
        self._color = RGB(255, 255, 255)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Coord):
        if value.x < 1 or value.y < 1:
            raise ValueError("Cord has to be greater than 1")
        self._position = value

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, value: Anchor):
        if not isinstance(value, Anchor):
            raise TypeError("anchor must be of type Anchor")
        self._anchor = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value: int):
        if not isinstance(value, int):
            raise TypeError("width must be an integer")
        if value <= 0:
            raise ValueError("width must be greater than 0")
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: int):
        if not isinstance(value, int):
            raise TypeError("height must be an integer")
        if value <= 0:
            raise ValueError("height must be greater than 0")
        self._height = value

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
    def color(self):
        return self._color

    @color.setter
    def color(self, value: RGB):
        if not isinstance(value, RGB):
            raise TypeError("color must be of type RGB")
        self._color = value

    def determine_top_left_coord(self) -> Coord:
        """
        Détermine les coordonnées du coin supérieur gauche en fonction de l'ancre
        et de la position de l'élément.
        """
        match self._anchor:
            case Anchor.CENTER:
                return Coord(int(self._position.x - (self._width / 2)), int(self._position.y - (self._height / 2)))
            case Anchor.TOP_LEFT:
                return Coord(self._position.x, self._position.y)
            case Anchor.TOP_RIGHT:
                return Coord(self._position.x - self._width, self._position.y)
            case Anchor.BOTTOM_LEFT:
                return Coord(self._position.x, self._position.y - self._height)
            case Anchor.BOTTOM_RIGHT:
                return Coord(self._position.x - self._width, self._position.y - self._height)

    def render(self):
        """
        Méthode générale pour le rendu de l'élément TUI.
        Cette méthode sera appelée par le gestionnaire d'interface.
        """
        if not self._visible:
            return
        self.on_render()

    @abstractmethod
    def on_render(self):
        """
        Méthode à surcharger par les classes dérivées pour implémenter
        le rendu spécifique à chaque type d'élément.
        """
        pass

    def on_hover(self):
        """
        Méthode appelée lorsque le curseur survole l'élément.
        À surcharger par les classes dérivées si nécessaire.
        """
        pass