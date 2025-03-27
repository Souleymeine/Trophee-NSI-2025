#Projet : pyscape
#Auteurs : Rabta Souleymeine

from typing import Final
from tui.TUI_element import TUIElement
from tui.box import Box
from data_types import RGB, Alignment, Anchor, HorizontalAlignment, Coord, VerticalAlignment
from escape_sequences import ANSI_Styles, cat_goto, print_styled_at, print_styled
from input_properties import KeyInfo, MouseInfo
from utils import split_preserve
from event_listeners import listeners, TUIElementMouseCallbacks

class TextArea(TUIElement):
    """Permet de représenter des zones de texte contenue dans un certain cadre, visible ou non."""
    def __init__(self, position: Coord, anchor: Anchor, width: int, height: int, text: str, style: ANSI_Styles, alignment: Alignment, border_color = RGB(255, 255, 255), z_index = 0):
        """
        Initialise une zone de texte.

        Args:
            text (str): Le texte à afficher
            style (ANSI_Styles): Le style à appliquer au texte
            alignment (Alignment): L'alignement horizontal et vertical du texte
            box (Box): La boîte contenant le texte
        """
        super().__init__(position, anchor, width, height, z_index, True, 1)
        self._box = Box(position, anchor, width, height, color=border_color)
        self.text = text
        self.style = style
        self.alignment = alignment
        self.border_color = border_color
        listeners.register_mouse_callbacks(self, TUIElementMouseCallbacks(self._mouse_hover, self._mouse_exit, self._mouse_click))
        listeners.register_key(self, self._type)
        self.render()

    def _mouse_hover(self, info: MouseInfo):
        self.is_mouse_over = True
        self._box.color = RGB(int(self.border_color.r/1.25), int(self.border_color.g/1.25), int(self.border_color.b/1.25))
        self.render()
        self.on_mouse_hover()
    def _mouse_click(self, info: MouseInfo):
        assert info.click is not None
        if info.click.released == False:
            self._box.color = RGB(self.border_color.r//2, self.border_color.g//2, self.border_color.b//2)
            self.render()
            self.is_selected = True
        elif info.click.released:
            self._box.color = RGB(int(self.border_color.r/1.25), int(self.border_color.g/1.25), int(self.border_color.b/1.25))
            self.render()
        self.on_mouse_click()
    def _mouse_exit(self, info: MouseInfo):
        self._box.color = self.border_color
        self.render()
        self.on_mouse_exit()

    def _type(self, info: KeyInfo):
        pass

    @property
    def is_selected(self):
        return self._is_selected
    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    def wrapped_text(self, first_char_pos: Coord) -> str:
        """
        Génère un texte enveloppé selon les dimensions de la boîte.

        Args:
            first_char_pos (Coord): Position du premier caractère

        Returns:
            str: Texte enveloppé avec les sauts de ligne et les positions appropriés
        """
        MAX_LENGTH = self._box.width - 2

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

        for raw_line in split_preserve('\n', self.text):
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
        self._box.render()

        BOX_TOP_LEFT_COORD: Final[Coord] = self._box.determine_top_left_position()
        FIRST_CHAR_COORD: Final[Coord] = self.determine_first_char_coord(BOX_TOP_LEFT_COORD)

        is_text_inline: bool = len(self.text) <= self._box.width - 2
        if is_text_inline:
            print_styled_at(self.text, self.style, FIRST_CHAR_COORD)
        else:
            margin_pos = Coord(BOX_TOP_LEFT_COORD.x + 1, BOX_TOP_LEFT_COORD.y + 1)
            print_styled(self.wrapped_text(margin_pos), self.style)

    def determine_first_char_coord(self, box_top_left_coord: Coord) -> Coord:
        """
        Détermine les coordonnées précises pour imprimer le texte.

        Args:
            box_top_left_coord (Coord): Coordonnées du coin supérieur gauche de la boîte

        Returns:
            Coord: Coordonnées du premier caractère à imprimer
        """
        first_char_coord = Coord(0, 0)
        match self.alignment.horizontal:
            case HorizontalAlignment.LEFT:   
                first_char_coord.x = box_top_left_coord.x + 1
            case HorizontalAlignment.CENTER: 
                first_char_coord.x = int(box_top_left_coord.x + self._box.width / 2 - len(self.text)/2)
            case HorizontalAlignment.RIGHT:  
                first_char_coord.x = box_top_left_coord.x + self._box.width - len(self.text) - 1
        
        match self.alignment.vertical:
            case VerticalAlignment.TOP:    
                first_char_coord.y = box_top_left_coord.y + 1
            case VerticalAlignment.MIDDLE: 
                first_char_coord.y = int(box_top_left_coord.y + self._box.height / 2)
            case VerticalAlignment.BOTTOM: 
                first_char_coord.y = box_top_left_coord.y + self._box.height - 2
        
        return first_char_coord

    def on_render(self):
        return super().on_render()
    def on_mouse_hover(self):
        return super().on_mouse_hover()
    def on_mouse_click(self):
        return super().on_mouse_click()
    def on_mouse_exit(self):
        return super().on_mouse_exit()
