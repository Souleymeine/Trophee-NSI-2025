#!/usr/bin/python

#Projet : pyscape
#Auteurs : Rabta Souleymeine

import os
import sys
import asyncio
from typing import Final
from TUI_elements.box import Box
from TUI_elements.text_area import TextArea
from data_types import RGB, Alignment, Anchor, HorizontalAlignment, Vec2d, VerticalAlignment
from dialog_printing import print_sized_dialog
from escape_sequences import get_bgcolor, gohome, goto, ANSI_Styles
from terminal import*

# Petit test assez sympa
def print_2d_gradient():
	termsize = os.get_terminal_size()
	term_area : Final[int] = termsize.lines * termsize.columns
	# Initialize la table en avance pour éviter les copies et réalocation en mémoire : moins lent
	cells : list = term_area * [None]
	for i in range(term_area):
		x_range = int(i % termsize.columns / termsize.columns * 255)
		y_range = int((i / termsize.columns) % termsize.lines / termsize.lines * 255)
		cells[i] = get_bgcolor(RGB(x_range, 0, y_range))
	picture: str = ''.join(cells)

	sys.stdout.write(picture)

async def main():
	init_term()

	# print_2d_gradient()

	termsize = os.get_terminal_size()

	notice_text_area = TextArea("Bienvenue !!!", ANSI_Styles.BOLD,
		Alignment(HorizontalAlignment.CENTER, VerticalAlignment.MIDDLE),
		Box(Anchor.TOP_RIGHT, Vec2d(termsize.columns, 1), Vec2d(19, 5), show=True, rounded=True, color=RGB(255, 100, 0), show_anchor=False))
	notice_text_area.draw()
	gohome()
	
	# De https://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
	notice_path = os.path.join(os.path.dirname(__file__), "../notice_aux_eleves.txt")
	with open(notice_path, "r", encoding="utf-8") as file:
		data = file.read()
		await print_sized_dialog(data, termsize.columns - notice_text_area.box.dimentions.x - 8, speed_multiplier=1.25)

	goto(Vec2d(1, termsize.lines))
	input("Appuie sur 'Entrer' pour quitter.")

	reset_term()

if __name__ == '__main__': 
	asyncio.run(main())
	# try:
	# 	asyncio.run(main())
	# except KeyboardInterrupt:
	# 	exit_gracefully()

def exit_gracefully():
	reset_term()
	sys.exit(0)

