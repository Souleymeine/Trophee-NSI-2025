# Projet : pyscape
# Auteurs : Rabta Souleymeine

from enum import IntFlag
import sys
if sys.platform == "win32":
    import win32console
    from win32console import PyINPUT_RECORDType
    import win32con
import os
import mouse
import terminal
from escape_sequences import gohome
from data_types import Coord
from typing import Final
from multiprocessing import Process
import time


def on_mouse(info: mouse.Info):
    print(info, flush=True, end="")
    gohome()
    print("\x1b[0J", end="")

def on_key(char: bytes):
    print(char, end="", flush=True)

if sys.platform == "win32":
    def parse_windows_mouse_event(event: PyINPUT_RECORDType, last_click: mouse.Click | None) -> mouse.Info:
        """Analyse l'évènement renvoyé par le terminal et le formatte en un objet de type 'mouse.Info'"""
        mouse_click = None
        mouse_button = None
        mouse_button_released = False
        mouse_wheel = None
        mouse_key_flags = 0
        
        if event.EventFlags & win32con.MOUSE_WHEELED:
            # Lorsque la molette est utilisée, la valeur avait l'air d'approcher les 2^32 et 2^31, un bitshift a fait l'affaire,
            # aucune idée de pourquoi ni comment mais ça m'a l'air d'être l'usage attendu...
            # Peut être ? https://learn.microsoft.com/fr-fr/windows/win32/api/winuser/nf-winuser-mouse_event
            mouse_wheel = mouse.Wheel(event.ButtonState >> 32 - 1)
        else:
            if event.ButtonState & 1:
                mouse_button = mouse.Button.LEFT
            elif event.ButtonState & 2:
                mouse_button = mouse.Button.RIGHT
            elif event.ButtonState & 4:
                mouse_button = mouse.Button.MIDDLE
            elif event.ButtonState == 0 and (last_click != None and not last_click.released): # Aucun click enfoncé
                mouse_button = last_click.button
                mouse_button_released = True
            
            if mouse_button != None:
                mouse_click = mouse.Click(mouse_button, mouse_button_released)
        
        return mouse.Info(mouse_click, mouse_wheel, Coord(event.MousePosition.X + 1, event.MousePosition.Y + 1), event.ControlKeyState)
else:
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

    # On initialise ici les variables dépendantes de la plateforme sujets à changement utilisées dans l'interprétation de l'entrée utilisateur
    if sys.platform == "win32":
        conin_event: PyINPUT_RECORDType
    else:
        TIME_THRESHOLD: Final[int] = 1 # miliseconds
        SEQ_LEN: Final[int] = 6
        mouse_seq = [b''] * SEQ_LEN
        i = 0

    # On initialise les informations précédentes de la souris par des informations non valide, au cas où
    # Cette valeur sera changée à partir de la première intéraction
    previous_mouse_info = mouse.Info(None, None, Coord(0, 0), -1)
    current_mouse_info: mouse.Info | None = None
    last_click: mouse.Click | None = None
    time_since_last_char = 0

    while True:
        if sys.platform == "win32":
            conin_event = terminal.info._conin.ReadConsoleInput(1)[0]

            if conin_event.EventType == win32console.KEY_EVENT and conin_event.KeyDown:
                encoded_char: bytes = conin_event.Char.encode("utf-8")
                terminal.info.last_byte = encoded_char
                if encoded_char != b'\x1b':
                    on_key(encoded_char)

            if terminal.info.mouse_mode == True and conin_event.EventType == win32console.MOUSE_EVENT:
                if last_click != None and last_click.released: # Permet de prévenir le signal "move" après le relachement du click
                    last_click = None
                    continue
                current_mouse_info = parse_windows_mouse_event(conin_event, last_click)
        else:
            if terminal.info.mouse_mode == True:
                time_since_last_char = time.time()

            terminal.info.last_byte = terminal.unix_getch()

            if terminal.info.mouse_mode == True:
                mouse_seq[i] = terminal.info.last_byte
                
                # TIME_THRESHOLD permet de déterminer si l'utilisateur rentre manuellement du texte ou non
                # On observe le format pour définir si la séquence est valide
                wrong_format: bool = (
                    (i != 0 and time.time() - time_since_last_char >= TIME_THRESHOLD / 1000)
                    or (i == 0 and mouse_seq[i] != b'\x1b') 
                    or (i == 1 and mouse_seq[i] != b'[') 
                    or (i == 2 and mouse_seq[i] != b'M')
                )

                if wrong_format:
                    on_key(mouse_seq[i])
                    i = 0
                    time_since_last_char = 0

                i += 1

                if i == SEQ_LEN:
                    current_mouse_info = parse_xterm_mouse_tracking_sequence(mouse_seq, last_click)
                    i = 0
                    time_since_last_char = 0

        if terminal.info.mouse_mode == True and current_mouse_info != None:
            previous_mouse_info = current_mouse_info
            if current_mouse_info.click != None:
                last_click = current_mouse_info.click

            on_mouse(current_mouse_info)

            # test pour le click dans une zone de texte
            if current_mouse_info.coord.x == 1 and current_mouse_info.coord.y == 1 and current_mouse_info.click != None and current_mouse_info.click.released:
                terminal.info.mouse_mode = False

            # Une fois la variable "current_mouse_info" utilisée, on la remet à None pour indiquer 
            # qu'aucun évènement n'est arrivé après celui-là, sauf au cas contraire (voire le code au dessus)
            current_mouse_info = None

        elif terminal.info.mouse_mode == False:
            if terminal.info.last_byte == b'\x1b':
                # Si le dernier caractère reçu pendant la frappe est 'échap', on quitte le mode texte
                terminal.info.mouse_mode = True
            elif sys.platform != "win32":
                # Windows envoie déjà un signal, en amont, comme on sait s'il vient du clavier ou de la souris
                on_key(terminal.info.last_byte)


input_process = Process(target=listen_to_input, name="InputProcess")
