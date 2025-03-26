#Projet : pyscape
#Auteurs : Rabta Souleymeine

import warnings
from typing import Final
from escape_sequences import gohome, print_at, set_fgcolor, reset_fgcolor
from data_types import RGB, Anchor, Coord
from .TUI_elements import TUI_element

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

class Box(TUI_element):
    """Classe permettant de représenter une zone rectangulaire à partir de
        - Ses coordonnées
        - Son point d'encrage (à quoi correspondent les coordonnées : centre, coin supérieur gauche/droit...)
        - Ses dimensions (hauteur, largeur)
        On peut également l'afficher avec des caractères spéciaux prévus à cet effet, en choisissant sa couleur, en arrondissant les coins ou non.
        """

    def __init__(self, position: Coord, anchor: Anchor, width: int, height: int,
        visible: bool = True, color: RGB = RGB(255, 255, 255),
        rounded: bool = False, show_anchor: bool = False, z_index: int = 0):
        """
            Initialise une boîte avec les propriétés spécifiées.

            Args:
                position: Position de la boîte
                anchor: Point d'ancrage de la boîte
                width: Largeur de la boîte
                height: Hauteur de la boîte
                visible: Si la boîte est visible
                color: Couleur de la boîte
                rounded: Si les coins sont arrondis
                show_anchor: Afficher le point d'ancrage (débogage)
                z_index: Indice Z pour l'ordre d'affichage
        """
        super().__init__(position, anchor, width, height, z_index)
        self._visible = visible
        self._color = color
        self._rounded = rounded
        self._show_anchor = show_anchor

        self._validate_properties()

    def _validate_properties(self):
        """Valide les propriétés et émet des avertissements si nécessaire."""
        import warnings

        if self._color and not self._visible:
            warnings.warn("Warning: La couleur est définie mais la boîte n'est pas visible (visible = False).")
        if self._rounded and not self._visible:
            warnings.warn("Warning: Les coins arrondis sont activés mais la boîte n'est pas visible (visible = False).")
        if self._show_anchor and not self._visible:
            warnings.warn(
                "Warning: L'affichage du point d'ancrage est activé mais la boîte n'est pas visible (visible = False).")


    def on_render(self) -> None:
        # Ici on déterminera pour chaque cas la position du coin supérieur gauche, puisqu'il est le plus proche 
        # de l'origine du repère. (pour rappelle, les coordonnées (0 ; 0) correspondent au coin supérieur gauche du terminal)
        # On pourra ensuite aller à droite ou en bas pour compléter la forme sans avoir à utiliser des boucles
        # pour remonter dans le repère avec des pas négatifs.

        TOP_LEFT_COORD: Final[Coord] = self.determine_top_left_coord() 

        if self._visible:
            set_fgcolor(self.color) # Définie la couleur d'arrière plan pour tous les prochains caractères imprimés.
            
            self.draw_rows(TOP_LEFT_COORD)
            self.draw_columns(TOP_LEFT_COORD)
            self.draw_corners(TOP_LEFT_COORD)

            # Pour débugage ou démonstration
            if (self._show_anchor):
                gohome()
                print_at('+', Coord(self.position.x, self.position.y))
            
            reset_fgcolor() # Rétablie la couleur d'arrière plan par défaut

    def determine_top_left_position(self) -> Coord:
        match self.anchor:
            case Anchor.CENTER:       return Coord(int(self.position.x - (self.width / 2)), int(self.position.y - (self.height / 2)))
            case Anchor.TOP_LEFT:     return Coord(self.position.x, self.position.y)
            case Anchor.TOP_RIGHT:    return Coord(self.position.x - self.width, self.position.y)
            case Anchor.BOTTOM_LEFT:  return Coord(self.position.x, self.position.y - self.height)
            case Anchor.BOTTOM_RIGHT: return Coord(self.position.x - self.width, self.position.y - self.height)
    
    def draw_rows(self, top_left_position: Coord):
        # Leur taille est égale à la largeur du bouton - 2, l'espace manquant est occupé par un coin.
        # On note également qu'on se décale d'une cellule pour se faire, laissant donc les deux cellules dédiés aux coins intactes.
        print_at(FULL_HORIZONTAL_BAR * (self.width - 2), Coord(top_left_position.x + 1, top_left_position.y))
        print_at(FULL_HORIZONTAL_BAR * (self.width - 2), Coord(top_left_position.x + 1, top_left_position.y + self.height - 1))

    def draw_columns(self, top_left_position: Coord):
        # Puisqu'on ne peut imprimer les colonnes en un seul appelle de 'print', on va descendre, à chaque itération, d'une cellule.
        # Comme pour les lignes, on laisse deux cellules intactes pour les coins, une en haut et une en bas.
        
        # Gauche
        for current_cell_ordinate in range(1, self.height):
            print_at(FULL_VERTICAL_BAR, Coord(top_left_position.x, top_left_position.y + current_cell_ordinate))
        # Droite
        for current_cell_ordinate in range(1, self.height):
            print_at(FULL_VERTICAL_BAR, Coord(top_left_position.x + self.width - 1, top_left_position.y + current_cell_ordinate))

    def draw_corners(self, top_left_position: Coord):
        print_at(TOP_LEFT_ROUND_CORNER if self._rounded else TOP_LEFT_CORNER,         top_left_position)
        print_at(BOTTOM_LEFT_ROUND_CORNER if self._rounded else BOTTOM_LEFT_CORNER,   Coord(top_left_position.x, top_left_position.y + self.height - 1))
        print_at(TOP_RIGHT_ROUND_CORNER if self._rounded else TOP_RIGHT_CORNER,       Coord(top_left_position.x + self.width - 1, top_left_position.y))
        print_at(BOTTOM_RIGHT_ROUND_CORNER if self._rounded else BOTTOM_RIGHT_CORNER, Coord(top_left_position.x + self.width - 1, top_left_position.y + self.height - 1))
