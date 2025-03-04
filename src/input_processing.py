# Projet : pyscape
# Auteurs : Rabta Souleymeine

from enum import IntFlag
import sys
import os
import mouse
import terminal
from escape_sequences import gohome
from data_types import Coord
from typing import Final
from multiprocessing import Process

def on_mouse(info: mouse.Info):
    print(info, flush=True, end="")
    gohome()
    print("\x1b[0J", end="")

def parse_xterm_mouse_tracking_sequence(sequence: list[bytes], last_click: mouse.Click | None) -> mouse.Info:
    """Analyse la séquence de caractère pour l'interpréter en une classe de type mouse.Info"""

    # Convertie les caractères en valeures numériques
    data = [int.from_bytes(byte) - 32 for byte in sequence]

    # Le code se réfère à ce format : https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking

    class _XtermMouseFlags(IntFlag):
        SHIFT = 4
        ALT = 8
        CTRL = 16
        MOVE = 32

    mouse_click = None
    mouse_button = None
    mouse_button_released = False
    mouse_wheel = None
    mouse_key_flags = 0

    for flag in _XtermMouseFlags:
        if data[3] & flag != 0:
            mouse_key_flags += flag

    match data[3] - mouse_key_flags:
        case 0:
            mouse_button = mouse.Button.LEFT
        case 1:
            mouse_button = mouse.Button.MIDDLE
        case 2:
            mouse_button = mouse.Button.RIGHT
        case 3: # Aucun click enfoncé
            mouse_button_released = True
            if last_click != None and not last_click.released:
                mouse_button = last_click.button
        case 64:
             mouse_wheel = mouse.Wheel.SCROLL_UP
        case 65:
             mouse_wheel = mouse.Wheel.SCROLL_DOWN

    if mouse_button != None:
        mouse_click = mouse.Click(mouse_button, mouse_button_released)

    return mouse.Info(mouse_click, mouse_wheel, Coord(data[-2], data[-1]), mouse_key_flags)

def listen_to_input():
    # Nécessaire car le lancement d'un nouveau processus ferme stdin
    sys.stdin = os.fdopen(0)

    # Pour les séquences liées à xterm uniquement, cmd ou powershell n'en ont pas besoin
    SEQ_LEN: Final[int] = 6
    mouse_seq = [b''] * SEQ_LEN
    i = 0

    # On initialise les informations précédentes de la souris par des informations non valide, au cas où
    # Cette valeur sera changée à partir de la première intéraction
    previous_mouse_info: mouse.Info = mouse.Info(None, None, Coord(0, 0), -1)
    last_click: mouse.Click | None = None

    while True:
        terminal.info.last_byte = terminal.unix_getch()

        if terminal.info.mouse_mode == True:
            if sys.platform == "win32":
                pass
            else:
                mouse_seq[i] = terminal.info.last_byte
                i += 1

                if i == SEQ_LEN:
                    mouse_info = parse_xterm_mouse_tracking_sequence(mouse_seq, last_click)
                    previous_mouse_info = mouse_info
                    if mouse_info.click != None:
                        last_click = mouse_info.click
                    i = 0

                    on_mouse(mouse_info)

                    # test pour le click dans une zone de texte
                    if mouse_info.coord.x == 1 and mouse_info.coord.y and mouse_info.click != None and mouse_info.click.released:
                        terminal.info.mouse_mode = False
        else:
            # Si le dernier caractère reçu pendant la frappe est 'échap', on quitte le mode texte
            if terminal.info.last_byte == b'\x1b':
                terminal.info.mouse_mode = True

input_process = Process(target=listen_to_input)
