# Projet : pyscape
# Auteurs : Rabta Souleymeine

from enum import IntFlag
import sys
if sys.platform == "win32":
    import win32console
    from win32console import PyINPUT_RECORDType
    import win32con
    from ctypes import c_long
else:
    import fcntl
import multiprocessing
import os
import mouse
import terminal
from data_types import Coord
from typing import Final

def on_mouse(info: mouse.Info):
    print(info)

def on_key(char: bytes):
    if terminal.info.mouse_mode == False and char == b'\x1b':
        terminal.info.mouse_mode = True
    # TODO: Créer un fichier contenant toutes les définitions de caractères spéciaux
    BACKSPACE = b'\x08'
    DELETE    = b'\x7f'
    if sys.platform != "win32": # Les deux touches sont inversées sur Xterm
        BACKSPACE, DELETE = DELETE, BACKSPACE

    print(f"decoded: \"{char.decode('utf-8')}\", raw: {char}")

if sys.platform == "win32":
    def parse_windows_mouse_event(event: PyINPUT_RECORDType, last_click: mouse.Click | None) -> mouse.Info:
        """Analyse l'évènement renvoyé par le terminal et le formatte en un objet de type 'mouse.Info'"""
        
        # Le code se réfère à ce format: https://learn.microsoft.com/fr-fr/windows/console/mouse-event-record-str

        mouse_coord = Coord(event.MousePosition.X + 1, event.MousePosition.Y + 1) # On ajoute 1 pour coller au système de coordonnées Unix qui commence à la cellule 1, 1
        mouse_click = None
        mouse_button = None
        mouse_button_released = False
        mouse_wheel = None
        mouse_flags = 0
        
        class _Win32MouseFlags(IntFlag):
            MOVE = win32con.MOUSE_MOVED
            SHIFT = win32con.SHIFT_PRESSED
            ALT = win32con.LEFT_ALT_PRESSED
            CTRL = win32con.LEFT_CTRL_PRESSED

        cmd_mouse_key_flags = 0
        for flag in _Win32MouseFlags:
            if event.ControlKeyState & flag:
                cmd_mouse_key_flags += flag
                # Ajoute le drapeau au nom correspondant entre _CmdMouseFlags et mouse.MouseKeyFlags
                if flag.name != None:
                    mouse_flags += mouse.MouseKeyFlags[flag.name].value

        if event.EventFlags & win32con.MOUSE_WHEELED:
            mouse_wheel = mouse.Wheel(c_long(event.ButtonState).value < 0)
        else:
            if event.ButtonState & win32con.FROM_LEFT_1ST_BUTTON_PRESSED:
                mouse_button = mouse.Button.LEFT
            elif event.ButtonState & win32con.RIGHTMOST_BUTTON_PRESSED:
                mouse_button = mouse.Button.RIGHT
            elif event.ButtonState & win32con.FROM_LEFT_2ND_BUTTON_PRESSED:
                mouse_button = mouse.Button.MIDDLE
            elif event.ButtonState == 0 and (last_click != None and not last_click.released): # Aucun click enfoncé
                mouse_button = last_click.button
                mouse_button_released = True
            
            if mouse_button != None:
                mouse_click = mouse.Click(mouse_button, mouse_button_released)
        
        return mouse.Info(mouse_click, mouse_wheel, mouse_coord, mouse_flags)
else:
    def parse_xterm_mouse_tracking_sequence(sequence: bytes, last_click: mouse.Click | None) -> mouse.Info:
        """Analyse la séquence de caractère pour l'interpréter en une classe de type mouse.Info"""

        # Convertie les caractères en valeures numériques
        data: list[int] = [byte - 32 for byte in sequence[1:]]

        # Le code se réfère à ce format : https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking

        class _XtermMouseFlags(IntFlag):
            SHIFT = 4
            ALT = 8
            CTRL = 16
            MOVE = 32

        mouse_coord = Coord(data[-2], data[-1])
        mouse_click = None
        mouse_button = None
        mouse_button_released = False
        mouse_wheel = None
        mouse_flags = 0

        xterm_mouse_key_flags = 0
        for flag in _XtermMouseFlags:
            if data[0] & flag:
                xterm_mouse_key_flags += flag
                # Ajoute le drapeau au nom correspondant entre _XtermMouseFlags et mouse.MouseKeyFlags
                if flag.name != None:
                    mouse_flags += mouse.MouseKeyFlags[flag.name].value

        button_flag = data[0] - xterm_mouse_key_flags
        match button_flag:
            case 0:
                mouse_button = mouse.Button.LEFT
            case 1:
                mouse_button = mouse.Button.MIDDLE
            case 2:
                mouse_button = mouse.Button.RIGHT
            case 3: # Aucun click enfoncé
                mouse_button_released = True
                # On cherche le dernier click enfoncé pour trouvé le bouton correspondant
                if last_click != None and not last_click.released:
                    mouse_button = last_click.button
            case 64:
                mouse_wheel = mouse.Wheel.SCROLL_UP
            case 65:
                mouse_wheel = mouse.Wheel.SCROLL_DOWN

        if mouse_button != None:
            mouse_click = mouse.Click(mouse_button, mouse_button_released)

        return mouse.Info(mouse_click, mouse_wheel, mouse_coord, mouse_flags)

    # Après plusieurs jours de recherche, je suis tombé sur ce gestionnaire de contexte depuis le code source
    # du projet bpytop qui faisait exactement le comportement attendu sans processus ou timeout.
    # Pure magie pour l'instant. TODO : à démystifier
    # De : https://github.com/aristocratos/bpytop/blob/master/bpytop.py#L800
    class Nonblocking(object):
        """Set nonblocking mode for device"""
        def __init__(self, stream):
            self.stream = stream
            self.fd = self.stream.fileno()
        def __enter__(self):
            self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
        def __exit__(self, *_):
            fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)


def listen_to_input():
    # On réouvre sys.stdin car il est automatiquement fermé lors de la création d'un nouveau processus
    sys.stdin = os.fdopen(0)
    # On initialise ici les variables dépendantes de la plateforme sujets à changement utilisées dans l'interprétation de l'entrée utilisateur
    if sys.platform == "win32":
        conin_event: PyINPUT_RECORDType
    else:
        SEQUENCE_LENGTH: Final[int] = 5

    # On initialise les informations précédentes de la souris par des informations non valide, au cas où
    # Ces valeurs seront changées à partir de la première intéraction
    last_char: bytes = b''
    previous_mouse_info = mouse.Info(None, None, Coord(0, 0), -1)
    current_mouse_info: mouse.Info | None = None
    last_click: mouse.Click | None = None

    try:
        while True:
            if sys.platform == "win32":
                conin_event = terminal.info._conin.ReadConsoleInput(1)[0]

                if conin_event.EventType == win32console.KEY_EVENT and conin_event.KeyDown:
                    last_char = str.encode(conin_event.Char)
                    # \r est reçu à la place \n (sauf si CTRL + entrer), on rend les deux identiques
                    if last_char == b'\r': last_char = b'\n'
                    if last_char != b'\x00':
                        on_key(last_char)

                if terminal.info.mouse_mode == True and conin_event.EventType == win32console.MOUSE_EVENT:
                    if last_click != None and last_click.released: # Permet de prévenir le signal "move" après le relachement du click
                        last_click = None
                        continue

                    moved_cell: bool = previous_mouse_info.coord != Coord(conin_event.MousePosition.X + 1, conin_event.MousePosition.Y + 1)
                    clicked_on_cell: bool = (conin_event.ButtonState != 0 or (last_click != None and not last_click.released)) and not conin_event.EventFlags & win32con.MOUSE_MOVED

                    if moved_cell ^ clicked_on_cell:
                        current_mouse_info = parse_windows_mouse_event(conin_event, last_click)
            else:
                last_char = terminal.unix_getch()

                if last_char == b'\x1b':
                    with Nonblocking(sys.stdin):
                        read = sys.stdin.buffer.read(SEQUENCE_LENGTH)
                        if read != None:
                            read = bytes(read)
                            if len(read) == SEQUENCE_LENGTH and read[1] == ord('M'): # La séquence se démarque par un M majuscule
                                current_mouse_info = parse_xterm_mouse_tracking_sequence(read[1:], last_click)
                            else:
                                # TODO: Gérer les autres séquences comme les flèches
                                pass
                        else:
                            on_key(b'\x1b')
                elif last_char != b'\x00':
                    if int.from_bytes(last_char) >= (2**7 - 1): # Pour les caractères au delà de 127 (utf-8, ex : 'ù')
                        second_part = sys.stdin.buffer.read(1)
                        on_key(last_char + second_part)
                    else:
                        on_key(last_char)

            if terminal.info.mouse_mode == True and current_mouse_info != None:
                previous_mouse_info = current_mouse_info
                if current_mouse_info.click != None:
                    last_click = current_mouse_info.click

                on_mouse(current_mouse_info)
                # Une fois la variable "current_mouse_info" utilisée, on la remet à None pour indiquer qu'aucun évènement n'est arrivé après celui-là.
                current_mouse_info = None

    except KeyboardInterrupt:
        # Géré dans main.py
        pass

input_process = multiprocessing.Process(target=listen_to_input, name="InputProcess", daemon=True)
