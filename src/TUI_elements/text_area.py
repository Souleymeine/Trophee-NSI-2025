#Projet : pyscape
#Auteurs : Rabta Souleymeine

import warnings
from typing import Final
from TUI_elements.box import Box
from data_types import Alignment, HorizontalAlignment, Vec2d, VerticalAlignment
from escape_sequences import ANSI_Styles, print_styled_at

# TODO : Les textes ne retournent pas à la ligne...
class TextArea():
	"""Permet de représenter des zones de texte contenue dans un certain cadre, visible ou non."""
	def __init__(self, text: str, style: ANSI_Styles, alignment: Alignment, box: Box):
		self.text = text
		self.style = style
		self.alignment = alignment
		self.box = box
		if (len(text) > box.dimentions.x - 2):
			warnings.warn(f"Warning: Text trop grand pour rentrer dans la la largeur: {len(text)} > {box.dimentions.x - 2} (on ne compte pas les bordures)")
	
	def draw(self):
		self.box.draw()

		BOX_TOP_LEFT_COORD: Final[Vec2d] = self.box.determine_top_left_coord()
		FIRST_CHAR_COORD: Final[Vec2d] = self.determine_first_char_coord(BOX_TOP_LEFT_COORD)
		print_styled_at(self.text, self.style, FIRST_CHAR_COORD)

	def determine_first_char_coord(self, box_top_left_coord: Vec2d):
		"""Détermine les bonnes coordonnées pour imprimer le text à partir de 'self.box' et self.alignment."""
		first_char_coord = Vec2d(0, 0)
		match self.alignment.horizontal:
			case HorizontalAlignment.LEFT:   first_char_coord.x = box_top_left_coord.x + 1
			case HorizontalAlignment.CENTER: first_char_coord.x = int(box_top_left_coord.x + self.box.dimentions.x / 2 - len(self.text)/2)
			case HorizontalAlignment.RIGHT:  first_char_coord.x = box_top_left_coord.x + self.box.dimentions.y - len(self.text) - 1
		match self.alignment.vertical:
			case VerticalAlignment.TOP:    first_char_coord.y = box_top_left_coord.y + 1
			case VerticalAlignment.MIDDLE: first_char_coord.y = int(box_top_left_coord.y + self.box.dimentions.y / 2)
			case VerticalAlignment.BOTTOM: first_char_coord.y = box_top_left_coord.y + self.box.dimentions.y - 2
		
		return first_char_coord
