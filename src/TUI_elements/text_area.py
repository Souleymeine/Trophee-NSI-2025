#Projet : pyscape
#Auteurs : Rabta Souleymeine

import re
from typing import Final
from TUI_elements.box import Box
from data_types import Alignment, HorizontalAlignment, Vec2d, VerticalAlignment
from escape_sequences import ANSI_Styles, cat_goto, goto, print_styled_at, print_styled

# TODO : Les textes ne retournent pas à la ligne...
class TextArea():
	"""Permet de représenter des zones de texte contenue dans un certain cadre, visible ou non."""
	def __init__(self, text: str, style: ANSI_Styles, alignment: Alignment, box: Box):
		self.text = text
		self.style = style
		self.alignment = alignment
		self.box = box
	


	def wrapped_text(self, first_char_pos: Vec2d) -> str:
		MAX_LENTGH = self.box.dimentions.x - 2

		wrapped_text = cat_goto(first_char_pos)
		current_line_length = 0
		current_line_count = 1

		def add_offset_linebreak():
			"""Fonction imbriquée pratique pour éviter de lourdes répétitions :
			https://stackoverflow.com/questions/11987358/why-nested-functions-can-access-variables-from-outer-functions-but-are-not-allo"""
			# nonlocal permet de référencer des variables dans le champ au dessus
			nonlocal wrapped_text, current_line_count, current_line_length
			wrapped_text += cat_goto(Vec2d(first_char_pos.x, first_char_pos.y + current_line_count))
			current_line_count += 1
			current_line_length = 0

		# De:  https://medium.com/@shemar.gordon32/how-to-split-and-keep-the-delimiter-s-d433fb697c65
		split_text = re.split(r"(?=[\n])|(?<=[\n])", self.text)
		for raw_line in split_text:
			if raw_line == "\n":
				add_offset_linebreak()
			elif len(raw_line) < MAX_LENTGH:
				wrapped_text += raw_line
				current_line_length += len(raw_line)
			else:
				for word in re.split(r"(?=[ ])|(?<=[ ])", raw_line):
					if len(word) >= MAX_LENTGH:
						for char in word:
							wrapped_text += char
							current_line_length += 1
							if current_line_length == MAX_LENTGH:
								add_offset_linebreak()
						break # On passe au mot suivant
					elif current_line_length + len(word) > MAX_LENTGH:
						add_offset_linebreak()
						# Supprime le prochain espace s'il est en début de ligne
						if word == " ":
							word = ""
					wrapped_text += word
					current_line_length += len(word)

		return wrapped_text


	def draw(self):
		self.box.draw()

		BOX_TOP_LEFT_COORD: Final[Vec2d] = self.box.determine_top_left_coord()
		FIRST_CHAR_COORD: Final[Vec2d] = self.determine_first_char_coord(BOX_TOP_LEFT_COORD)

		is_text_inline: bool = len(self.text) <= self.box.dimentions.x - 2
		if is_text_inline:
			print_styled_at(self.text, self.style, FIRST_CHAR_COORD)
		else:
			margin_pos = Vec2d(BOX_TOP_LEFT_COORD.x + 1, BOX_TOP_LEFT_COORD.y + 1)
			print_styled(self.wrapped_text(margin_pos), self.style)

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
