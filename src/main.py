#!/usr/bin/python

# Projet : pyscape
# Auteurs : Rabta Souleymeine

import signal
import os
import sys
import asyncio
from TUI_elements.box import Box
from TUI_elements.text_area import TextArea
from data_types import (
    RGB,
    Alignment,
    Anchor,
    HorizontalAlignment,
    Coord,
    VerticalAlignment,
)
from data_types import RGB, Alignment, Anchor, HorizontalAlignment, Coord, VerticalAlignment
<<<<<<< HEAD
from tests import print_sized_dialog
from escape_sequences import cat_bgcolor, gohome, goto, ANSI_Styles
from terminal import *

||||||| parent of 0ac05a5 (Déplace les tests dans tests.py)
from dialog_printing import print_sized_dialog
from escape_sequences import cat_bgcolor, gohome, goto, ANSI_Styles
from terminal import*
=======
from escape_sequences import gohome, goto, ANSI_Styles
from terminal import*
>>>>>>> 0ac05a5 (Déplace les tests dans tests.py)

<<<<<<< HEAD
# Petit test assez sympa
def print_2d_gradient():
    termsize = os.get_terminal_size()
    term_area: Final[int] = termsize.lines * termsize.columns
    # Initialize la table en avance pour éviter les copies et réalocation en mémoire : moins lent
    cells: list = term_area * [None]
    for i in range(term_area):
        x_range = int(i % termsize.columns / termsize.columns * 255)
        y_range = int((i / termsize.columns) % termsize.lines / termsize.lines * 255)
        cells[i] = cat_bgcolor(RGB(x_range, 0, y_range))
    picture: str = "".join(cells)

    sys.stdout.write(picture)

||||||| parent of 0ac05a5 (Déplace les tests dans tests.py)
# Petit test assez sympa
def print_2d_gradient():
	termsize = os.get_terminal_size()
	term_area : Final[int] = termsize.lines * termsize.columns
	# Initialize la table en avance pour éviter les copies et réalocation en mémoire : moins lent
	cells : list = term_area * [None]
	for i in range(term_area):
		x_range = int(i % termsize.columns / termsize.columns * 255)
		y_range = int((i / termsize.columns) % termsize.lines / termsize.lines * 255)
		cells[i] = cat_bgcolor(RGB(x_range, 0, y_range))
	picture: str = ''.join(cells)

	sys.stdout.write(picture)
=======
>>>>>>> 0ac05a5 (Déplace les tests dans tests.py)

async def main():
    init_term()

<<<<<<< HEAD
    # print_2d_gradient()

    termsize = os.get_terminal_size()
||||||| parent of 0ac05a5 (Déplace les tests dans tests.py)
	# print_2d_gradient()

	termsize = os.get_terminal_size()
=======
>>>>>>> 0ac05a5 (Déplace les tests dans tests.py)

<<<<<<< HEAD
    # # De https://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
    notice_path = os.path.join(os.path.dirname(__file__), "../notice_aux_eleves.txt")
    # with open(notice_path, "r", encoding="utf-8") as file:
    # 	data = file.read()
    # 	await print_sized_dialog(data, termsize.columns - notice_text_area.box.dimentions.x - 8, speed_multiplier=1.25)

    with open(notice_path, "r", encoding="utf-") as file:
        data = file.read()
        # await print_sized_dialog(data, termsize.columns - notice_text_area.box.dimentions.x - 8, speed_multiplier=1.25)
        notice_text_area = TextArea(
            data,
            ANSI_Styles.BOLD,
            Alignment(HorizontalAlignment.CENTER, VerticalAlignment.MIDDLE),
            Box(
                Anchor.TOP_LEFT,
                Coord(1, 1),
                Coord(60, 35),
                show=True,
                rounded=True,
                color=RGB(255, 100, 0),
                show_anchor=True,
            ),
        )
||||||| parent of 0ac05a5 (Déplace les tests dans tests.py)
	# # De https://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
	notice_path = os.path.join(os.path.dirname(__file__), "../notice_aux_eleves.txt")
	# with open(notice_path, "r", encoding="utf-8") as file:
	# 	data = file.read()
	# 	await print_sized_dialog(data, termsize.columns - notice_text_area.box.dimentions.x - 8, speed_multiplier=1.25)

	with open(notice_path, "r", encoding="utf-") as file:
		data = file.read()
		# await print_sized_dialog(data, termsize.columns - notice_text_area.box.dimentions.x - 8, speed_multiplier=1.25)
		notice_text_area = TextArea(data, 
			ANSI_Styles.BOLD,
			Alignment(HorizontalAlignment.CENTER, VerticalAlignment.MIDDLE),
			Box(Anchor.TOP_LEFT, Coord(1, 1), Coord(60, 35), show=True, rounded=True, color=RGB(255, 100, 0), show_anchor=True))
	
	for i in range(termsize.columns - notice_text_area.box.dimentions.x):
		notice_text_area.box.dimentions.x += 1
		notice_text_area.draw()
		await asyncio.sleep(0.05)
		gohome()
		sys.stdout.write("\x1b[2J")
=======
	# # De https://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
	notice_path = os.path.join(os.path.dirname(__file__), "../notice_aux_eleves.txt")
	with open(notice_path, "r", encoding="utf-8") as file:
		data = file.read()

	notice_text_area = TextArea(data, ANSI_Styles.BOLD,
						  Alignment(HorizontalAlignment.CENTER, VerticalAlignment.MIDDLE),
						  Box(Anchor.TOP_LEFT, Coord(1, 1), Coord(60, 35), show=True, rounded=True, color=RGB(255, 100, 0), show_anchor=True))
	
	termsize = os.get_terminal_size()

	for _ in range(termsize.columns - notice_text_area.box.dimentions.x):
		notice_text_area.box.dimentions.x += 1
		notice_text_area.draw()
		await asyncio.sleep(0.05)
		gohome()
		sys.stdout.write("\x1b[2J")
>>>>>>> 0ac05a5 (Déplace les tests dans tests.py)

    for _ in range(termsize.columns - notice_text_area.box.dimentions.x):
        notice_text_area.box.dimentions.x += 1
        notice_text_area.draw()
        await asyncio.sleep(0.05)
        gohome()
        sys.stdout.write("\x1b[2J")

    notice_text_area.draw()

    goto(Coord(1, termsize.lines))
    input("Appuie sur 'Entrer' pour quitter.")

    reset_term()

<<<<<<< HEAD

def exit_gracefully(signum, frame):
    reset_term()
    sys.exit(0)
||||||| parent of 0ac05a5 (Déplace les tests dans tests.py)

	goto(Coord(1, termsize.lines))
	input("Appuie sur 'Entrer' pour quitter.")
=======
	goto(Coord(1, termsize.lines))
	input("Appuie sur 'Entrer' pour quitter.")
>>>>>>> 0ac05a5 (Déplace les tests dans tests.py)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)  # Capture CTRL+C

    asyncio.run(main())

# Enfaite ici ça dépends si on a des problèmes avec signal, parce que apparemment sur windows ça marche pas très bien.
# except KeyboardInterrupt:
# exit_gracefully()
