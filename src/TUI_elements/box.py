#Projet : pyscape
#Auteurs : Rabta Souleymeine

import warnings
from typing import Final
from escape_sequences import gohome, print_at, set_fgcolor, reset_fgcolor
from data_types import RGB, Anchor, Vec2d

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
class Box:
	"""Classe permettant de représenter une zone rectangulaire à partir de
		- Ses coordonnées
		- Son point d'encrage (à quoi correspondent les coordonnées : centre, coin supérieur gauche/droit...)
		- Ses dimensions (hauteur, largeur)
	On peut également l'afficher avec des caractères spéciaux prévus à cet effet, en choisissant sa couleur, en arrondissant les coins ou non.
	"""
	def __init__(self, anchor : Anchor, coord: Vec2d, dimentions : Vec2d,
			show: bool, color: RGB = RGB(255, 255, 255), rounded: bool = False, show_anchor: bool = False):
		self.anchor = anchor
		self.coord = coord
		self.dimentions = dimentions
		
		self.show = show
		self.color = color
		self.rounded = rounded
		self.show_anchor = show_anchor

		if color and not show:
			warnings.warn("Warning: La couleur pour cette instance la class 'Box' est définie mais mais elle n'est pas visible (Box.show = False).")
		if rounded and not show:
			warnings.warn("Warning: La propriété 'rounded' pour cette instance la class 'Box' est égale à 'True' mais mais elle n'est pas visible (Box.show = False).")
		if show_anchor and not show:
			warnings.warn("Warning: La propriété 'show_anchor' pour cette instance la class 'Box' est égale à 'True' mais mais elle n'est pas visible (Box.show = False).")


	def draw(self) -> None:
		# Ici on déterminera pour chaque cas la position du coin supérieur gauche, puisqu'il est le plus proche 
		# de l'origine du repère. (pour rappelle, les coordonnées (0 ; 0) correspondent au coin supérieur gauche du terminal)
		# On pourra ensuite aller à droite ou en bas pour compléter la forme sans avoir à utiliser des boucles
		# pour remonter dans le repère avec des pas négatifs.

		TOP_LEFT_COORD: Final[Vec2d] = self.determine_top_left_coord() 

		set_fgcolor(self.color) # Définie la couleur d'arrière plan pour tous les prochains caractères imprimés.
		
		self.draw_rows(TOP_LEFT_COORD)
		self.draw_columns(TOP_LEFT_COORD)
		self.draw_corners(TOP_LEFT_COORD)

		# Pour débugage ou démonstration
		if (self.show_anchor):
			gohome()
			print_at('+', Vec2d(self.coord.x, self.coord.y))
		
		reset_fgcolor() # Rétablie la couleur d'arrière plan par défaut

	def determine_top_left_coord(self) -> Vec2d:
		match self.anchor:
			case Anchor.CENTER:       return Vec2d(int(self.coord.x - (self.dimentions.x / 2)), int(self.coord.y - (self.dimentions.y / 2)))
			case Anchor.TOP_LEFT:     return Vec2d(self.coord.x, self.coord.y)
			case Anchor.TOP_RIGHT:    return Vec2d(self.coord.x - self.dimentions.x, self.coord.y)
			case Anchor.BOTTOM_LEFT:  return Vec2d(self.coord.x, self.coord.y - self.dimentions.y)
			case Anchor.BOTTOM_RIGHT: return Vec2d(self.coord.x - self.dimentions.x, self.coord.y - self.dimentions.y)
	
	def draw_rows(self, top_left_coord: Vec2d):
		# Leur taille est égale à la largeur du bouton - 2, l'espace manquant est occupé par un coin.
		# On note également qu'on se décale d'une cellule pour se faire, laissant donc les deux cellules dédiés aux coins intactes.
		print_at(FULL_HORIZONTAL_BAR * (self.dimentions.x - 2), Vec2d(top_left_coord.x + 1, top_left_coord.y))
		print_at(FULL_HORIZONTAL_BAR * (self.dimentions.x - 2), Vec2d(top_left_coord.x + 1, top_left_coord.y + self.dimentions.y - 1))

	def draw_columns(self, top_left_coord: Vec2d):
		# Puisqu'on ne peut imprimer les colonnes en un seul appelle de 'print', on va descendre, à chaque itération, d'une cellule.
		# Comme pour les lignes, on laisse deux cellules intactes pour les coins, une en haut et une en bas.
		
		# Gauche
		for current_cell_ordinate in range(1, self.dimentions.y):
			print_at(FULL_VERTICAL_BAR, Vec2d(top_left_coord.x, top_left_coord.y + current_cell_ordinate))
		# Droite
		for current_cell_ordinate in range(1, self.dimentions.y):
			print_at(FULL_VERTICAL_BAR, Vec2d(top_left_coord.x + self.dimentions.x - 1, top_left_coord.y + current_cell_ordinate))

	def draw_corners(self, top_left_coord: Vec2d):
		print_at(TOP_LEFT_ROUND_CORNER if self.rounded else TOP_LEFT_CORNER,         top_left_coord)
		print_at(BOTTOM_LEFT_ROUND_CORNER if self.rounded else BOTTOM_LEFT_CORNER,   Vec2d(top_left_coord.x, top_left_coord.y + self.dimentions.y - 1))
		print_at(TOP_RIGHT_ROUND_CORNER if self.rounded else TOP_RIGHT_CORNER,       Vec2d(top_left_coord.x + self.dimentions.x - 1, top_left_coord.y))
		print_at(BOTTOM_RIGHT_ROUND_CORNER if self.rounded else BOTTOM_RIGHT_CORNER, Vec2d(top_left_coord.x + self.dimentions.x - 1, top_left_coord.y + self.dimentions.y - 1))
