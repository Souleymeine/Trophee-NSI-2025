#Projet : pyscape
#Auteurs : Rabta Souleymeine

from typing import Final
from input_properties import MouseInfo
from tui.base import Positioning, ClickableElement, ColorsOnMouse
from tui.box import Box
from data_types import Align, HorizAlign, Coord, VirtAlign
from escape_sequences import ANSI_Styles, cat_goto, print_styled_at, print_styled
from utils import split_preserve

class TextArea(ClickableElement):
    """Permet de représenter des zones de texte contenue dans un certain cadre, visible ou non."""
    def __init__(self, positioning: Positioning, text: str, style: ANSI_Styles, colors_on_mouse: ColorsOnMouse, rounded=False, alignment = Align(HorizAlign.LEFT, VirtAlign.TOP),
                 z_index: int = 0, visible: bool = True):
        self._text = text
        self._style = style
        self._colors_on_mouse = colors_on_mouse
        self._alignment = alignment
        self._box = Box(positioning, visible=visible, rounded=rounded)
        super().__init__(positioning, colors_on_mouse, z_index, visible)

    def _on_hover(self, info: MouseInfo):
        if self._colors_on_mouse.hover_fg_col is not None:
            self._box._color = self._colors_on_mouse.hover_fg_col

        self.render()
        super()._on_hover(info)
    
    def _on_click(self, info: MouseInfo):
        assert info.click is not None
        if info.click.released == False:
            if self._colors_on_mouse.click_fg_col is not None:
                self._box._color = self._colors_on_mouse.click_fg_col
        else:
            if self._colors_on_mouse.hover_fg_col is not None:
                self._box._color = self._colors_on_mouse.hover_fg_col
        self.render()
        super()._on_click(info)
    
    def _on_mouse_exit(self, info: MouseInfo):
        if self._colors_on_mouse.default_fg_col is not None:
            self._box._color = self._colors_on_mouse.default_fg_col
        self.render()
        super()._on_mouse_exit(info)

    def wrapped_text(self, first_char_pos: Coord) -> str:
        """
        Génère un texte enveloppé selon les dimensions de la boîte.

        Args:
            first_char_pos (Coord): Position du premier caractère

        Returns:
            str: Texte enveloppé avec les sauts de ligne et les positions appropriés
        """
        MAX_LENGTH = self._box.positioning.width - 2

        wrapped_text = cat_goto(first_char_pos)
        current_line_length = 0
        current_line_count = 1

        def _concat_offset_linebreak():
            """Saute une ligne et réinitialise la longueur de ligne."""
            nonlocal wrapped_text, current_line_count, current_line_length
            wrapped_text += cat_goto(Coord(first_char_pos.x, first_char_pos.y + current_line_count))
            current_line_count += 1
            current_line_length = 0

        def _concat_text(text: str):
            """Ajoute du texte à la ligne courante."""
            nonlocal wrapped_text, current_line_length
            wrapped_text += text
            current_line_length += len(text)

        for raw_line in split_preserve('\n', self._text):
            if raw_line == "\n":
                _concat_offset_linebreak()
            elif len(raw_line) < MAX_LENGTH:
                _concat_text(raw_line)    
            else:
                for word in split_preserve(' ', raw_line):
                    if len(word) >= MAX_LENGTH:
                        for char in word:
                            _concat_text(char)
                            if current_line_length == MAX_LENGTH:
                                _concat_offset_linebreak()
                        break  # On passe au mot suivant
                    elif current_line_length + len(word) > MAX_LENGTH:
                        _concat_offset_linebreak()
                        # Supprime le prochain espace s'il est en début de ligne
                        if word == " ": word = ""
                    _concat_text(word)

        return wrapped_text

    def render(self):
        """
        Dessine la boîte et le texte selon les paramètres spécifiés.
        """
        if self._visible:
            self._box.render()

            BOX_TOP_LEFT_COORD: Final[Coord] = super().top_left_coord
            FIRST_CHAR_COORD: Final[Coord] = self.determine_first_char_coord(BOX_TOP_LEFT_COORD)

            is_text_inline: bool = len(self._text) <= self._positioning.width - 2
            if is_text_inline:
                print_styled_at(self._text, self._style, FIRST_CHAR_COORD)
            else:
                margin_pos = Coord(BOX_TOP_LEFT_COORD.x + 1, BOX_TOP_LEFT_COORD.y + 1)
                print_styled(self.wrapped_text(margin_pos), self._style)

    def determine_first_char_coord(self, box_top_left_coord: Coord) -> Coord:
        """
        Détermine les coordonnées précises pour imprimer le texte.

        Args:
            box_top_left_coord (Coord): Coordonnées du coin supérieur gauche de la boîte

        Returns:
            Coord: Coordonnées du premier caractère à imprimer
        """
        first_char_coord = Coord(0, 0)
        match self._alignment.horizontal:
            case HorizAlign.LEFT:   
                first_char_coord.x = box_top_left_coord.x + 1
            case HorizAlign.CENTER: 
                first_char_coord.x = int(box_top_left_coord.x + self._positioning.width / 2 - len(self._text)/2)
            case HorizAlign.RIGHT:  
                first_char_coord.x = box_top_left_coord.x + self._positioning.width - len(self._text) - 1
        
        match self._alignment.vertical:
            case VirtAlign.TOP:    
                first_char_coord.y = box_top_left_coord.y + 1
            case VirtAlign.MIDDLE: 
                first_char_coord.y = int(box_top_left_coord.y + self._positioning.height / 2)
            case VirtAlign.BOTTOM: 
                first_char_coord.y = box_top_left_coord.y + self._positioning.height - 2
        
        return first_char_coord


