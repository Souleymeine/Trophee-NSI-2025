#Projet : pyscape
#Auteurs : Rabta Souleymeine

from types import NoneType
from typing import Final
from input_properties import MouseButton, MouseInfo
from tui.base import Positioning, ClickableElement, ColorsOnMouse
from tui.box import Box
from data_types import RGB, Coord
from escape_sequences import ANSI_Styles, cat_bgcolor, goto, print_at, print_bgcolor, print_bgcolor_at, print_styled_at, reset_bgcolor, set_bgcolor

class Button(ClickableElement):
    """Permet de représenter des zones de texte contenue dans un certain cadre, visible ou non."""
    def __init__(self, positioning: Positioning, label: str, style: ANSI_Styles, colors_on_mouse: ColorsOnMouse, rounded=False, bold_border = True,
                 z_index: int = 0, visible: bool = True):
        self._label = label
        self._style = style
        self._colors_on_mouse = colors_on_mouse
        self._box = Box(positioning, visible=visible, rounded=rounded, bold=bold_border)
        super().__init__(positioning, colors_on_mouse, z_index, visible)

    def _on_hover(self, info: MouseInfo):
        if self._colors_on_mouse.hover_bg_col is not None and self.is_mouse_over == False:
            self.fill_bg_cells(self._colors_on_mouse.hover_bg_col)

        super()._on_hover(info)
    
    def _on_click(self, info: MouseInfo):
        assert info.click is not None
        if info.click.released == False and self._colors_on_mouse.click_bg_col is not None and info.click.button == MouseButton.LEFT:
            self.fill_bg_cells(self._colors_on_mouse.click_bg_col)
        elif self._colors_on_mouse.hover_bg_col is not None:
            self.fill_bg_cells(self._colors_on_mouse.hover_bg_col)

        super()._on_click(info)
    
    def _on_mouse_exit(self, info: MouseInfo):
        self.fill_bg_cells(None)
        super()._on_mouse_exit(info)

    def render(self):
        """
        Dessine la boîte et le texte selon les paramètres spécifiés et affiche le text
        """
        if self._visible:
            self._box.render()

        self.print_label()

    def print_label(self, color: RGB | NoneType = None):
        BOX_TOP_LEFT_COORD: Final[Coord] = super().top_left_coord
        FIRST_CHAR_COORD: Final[Coord] = self.determine_first_char_coord(BOX_TOP_LEFT_COORD)

        if color is not None:
            print_styled_at(f"\x1b[48;2;{color.r};{color.g};{color.b}m{self._label}\x1b[m", self._style, FIRST_CHAR_COORD)
        else:
            print_styled_at(self._label, self._style, FIRST_CHAR_COORD)


    def determine_first_char_coord(self, box_top_left_coord: Coord) -> Coord:
        return Coord(
            int(box_top_left_coord.x + self._positioning.width / 2 - len(self._label)/2),
            int(box_top_left_coord.y + self._positioning.height / 2)
        )
    
    def fill_bg_cells(self, color: RGB | NoneType):
        """Remplie l'arrière plan du boutton avec la couleur spécifiée. Le texte est réafiché après."""
        for x in range(super().top_left_coord.x + 1, super().top_left_coord.x + self.positioning.width - 1):
            for y in range(super().top_left_coord.y + 1, super().top_left_coord.y + self.positioning.height - 1):
                if type(color) == NoneType:
                    print_at(' ', Coord(x, y))
                else:
                    print_bgcolor_at(color, Coord(x, y))   

        self.print_label(color)

