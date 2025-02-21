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
from escape_sequences import gohome, goto, ANSI_Styles
from terminal import*

async def main():
    init_term()

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

	# De https://stackoverflow.com/questions/7165749/open-file-in-a-relative-location-in-python
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
    
    goto(Coord(1, termsize.lines))
    input("Appuie sur 'Entrer' pour quitter.")

def exit_gracefully(signum, frame):
    reset_term()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)  # Capture CTRL+C
    asyncio.run(main())

# Enfaite ici ça dépends si on a des problèmes avec signal, parce que apparemment sur windows ça marche pas très bien.
# except KeyboardInterrupt:
# exit_gracefully()
