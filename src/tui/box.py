#Projet : pyscape
#Auteurs : Rabta Souleymeine

import warnings
from typing import Final
from escape_sequences import ANSI_Styles, gohome, print_at, reset_style, set_fgcolor, reset_fgcolor, set_style
from data_types import RGB, Coord
from tui.base import TUIElement, Positioning

# Historiquement, ces caractères ont été inventé pour afficher des bordures des 
# éléments d'interface directement dans le terminale, à la manière de l'ASCII art.
# On les appelles "Filets" en français ou "box-drawing characters" en anglais.
# On en profitera pour faire exactement la même chose, puisqu'il ont été créé spécialement pour ça.
# Il existe d'autres types de charactères visant à créer des interfaces utilisateurs dans le terminal
# Mais on se contentera de ceux-ci pour la classe 'Border'.
# Pour les curieux : https://en.wikipedia.org/wiki/Box-drawing_characters

FULL_HORIZONTAL_BAR : Final[str]       = '─'
FULL_VERTICAL_BAR : Final[str]         = '│'
TOP_LEFT_ROUND_CORNER : Final[str]     = '╭'
TOP_RIGHT_ROUND_CORNER : Final[str]    = '╮'
BOTTOM_LEFT_ROUND_CORNER : Final[str]  = '╰'
BOTTOM_RIGHT_ROUND_CORNER : Final[str] = '╯'
TOP_LEFT_CORNER : Final[str]           = '┌'
TOP_RIGHT_CORNER : Final[str]          = '┐'
BOTTOM_LEFT_CORNER: Final[str]         = '└'
BOTTOM_RIGHT_CORNER : Final[str]       = '┘'


# TODO : Traiter plus explicitement les cas limites pour les valeurs paire/impaires (décalage imprévu d'une cellule).

class Box(TUIElement):
    """Classe permettant de représenter une zone rectangulaire à partir de
        - Ses coordonnées
        - Son point d'encrage (à quoi correspondent les coordonnées : centre, coin supérieur gauche/droit...)
        - Ses dimensions (hauteur, largeur)
        On peut également l'afficher avec des caractères spéciaux prévus à cet effet, en choisissant sa couleur, en arrondissant les coins ou non.
        """

    def __init__(self, positioning: Positioning, rounded: bool = False, color = RGB(255, 255, 255), bold = False, show_anchor: bool = False,
                 z_index: int = 0, visible: bool = True):
        self._color = color
        self._bold = bold
        self._rounded = rounded
        self._show_anchor = show_anchor

        super().__init__(positioning, z_index=z_index, visible=visible, bg_col=None, fg_col=color)

    def render(self) -> None:
        # Ici on déterminera pour chaque cas la position du coin supérieur gauche, puisqu'il est le plus proche 
        # de l'origine du repère. (pour rappelle, les coordonnées (1 ; 1) correspondent au coin supérieur gauche du terminal)
        # On pourra ensuite aller à droite ou en bas pour compléter la forme sans avoir à utiliser des boucles
        # pour remonter dans le repère avec des pas négatifs.

        TOP_LEFT_COORD: Final[Coord] = super().top_left_coord

        if self._visible:
            set_fgcolor(self._color) # Définie la couleur de text de tous les prochains caractères imprimés.
            if self._bold:
                set_style(ANSI_Styles.BOLD)
            self.print_rows(TOP_LEFT_COORD)
            self.print_columns(TOP_LEFT_COORD)
            self.print_corners(TOP_LEFT_COORD)

            # Pour débugage ou démonstration
            if (self._show_anchor):
                gohome()
                print_at('+', Coord(self._positioning.origin.x, self._positioning.origin.y))
            
            reset_fgcolor() # Rétablie la couleur du text par défaut
            if self._bold:
                reset_style(ANSI_Styles.BOLD)

    def print_rows(self, top_left_position: Coord):
        # Leur taille est égale à la largeur du bouton - 2, l'espace manquant est occupé par un coin.
        # On note également qu'on se décale d'une cellule pour se faire, laissant donc les deux cellules dédiés aux coins intactes.
        print_at(FULL_HORIZONTAL_BAR * (self._positioning.width - 2), Coord(top_left_position.x + 1, top_left_position.y))
        print_at(FULL_HORIZONTAL_BAR * (self._positioning.width - 2), Coord(top_left_position.x + 1, top_left_position.y + self._positioning.height - 1))

    def print_columns(self, top_left_position: Coord):
        # Puisqu'on ne peut imprimer les colonnes en un seul appelle de 'print', on va descendre, à chaque itération, d'une cellule.
        # Comme pour les lignes, on laisse deux cellules intactes pour les coins, une en haut et une en bas.
        
        # Gauche
        for current_cell_ordinate in range(1, self._positioning.height):
            print_at(FULL_VERTICAL_BAR, Coord(top_left_position.x, top_left_position.y + current_cell_ordinate))
        # Droite
        for current_cell_ordinate in range(1, self._positioning.height):
            print_at(FULL_VERTICAL_BAR, Coord(top_left_position.x + self._positioning.width - 1, top_left_position.y + current_cell_ordinate))

    def print_corners(self, top_left_position: Coord):
        print_at(TOP_LEFT_ROUND_CORNER if self._rounded else TOP_LEFT_CORNER,         top_left_position)
        print_at(BOTTOM_LEFT_ROUND_CORNER if self._rounded else BOTTOM_LEFT_CORNER,   Coord(top_left_position.x, top_left_position.y + self._positioning.height - 1))
        print_at(TOP_RIGHT_ROUND_CORNER if self._rounded else TOP_RIGHT_CORNER,       Coord(top_left_position.x + self._positioning.width - 1, top_left_position.y))
        print_at(BOTTOM_RIGHT_ROUND_CORNER if self._rounded else BOTTOM_RIGHT_CORNER, Coord(top_left_position.x + self._positioning.width - 1, top_left_position.y + self._positioning.height - 1))

