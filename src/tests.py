#Projet : pyscape
#Auteurs : Rabta Souleymeine

import os
import sys
import asyncio
from escape_sequences import cat_bgcolor
from data_types import RGB
from typing import Final, Dict 

# Tous les délais prédéfinies sont en millisecondes

DEFAULT_CHAR_DELAY : Final[int] = 32
PUNCTUATION_DELAYS : Final[Dict[str, int]] = {
    ',' : 700,
    ':' : 900,
    ';' : 1100,
    '.' : 1200,
    '!' : 1000,
    '?' : 1000,
}

async def print_dialog(text : str, speed_multiplier : float = 1, newline : bool = True):
    for char in text:
        lookup_delay : int | None = PUNCTUATION_DELAYS.get(char)
        milis_delay : int = (lookup_delay if lookup_delay else DEFAULT_CHAR_DELAY)

        print(char, end='', flush=True)
        await asyncio.sleep((milis_delay / 1000) / speed_multiplier)
    if (newline):
        print()

async def print_sized_dialog(text: str,  max_line_length: int, speed_multiplier: float = 1, newline: bool = True):
    assert max_line_length > 0, f"'max_line_length' doit être supérieur à 0 : {max_line_length}"
    current_line_length: int = 0
    
    for char in text:
        lookup_delay : int | None = PUNCTUATION_DELAYS.get(char)
        milis_delay : int = (lookup_delay if lookup_delay else DEFAULT_CHAR_DELAY)

        print(char, end='', flush=True)
        if (current_line_length < max_line_length):
            current_line_length += 1
        if char == '\n':
            current_line_length = 0
        if current_line_length >= max_line_length and char == ' ':
            current_line_length = 0
            print()
        await asyncio.sleep((milis_delay / 1000) / speed_multiplier)
    if (newline):
        print()

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

