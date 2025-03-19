# Projet : pyscape
# Auteurs : Rabta Souleymeine

from enum import IntFlag
import sys
if sys.platform == "win32":
    import win32console
    from win32console import PyINPUT_RECORDType
    import win32con
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
    if sys.platform != "win32": # Les deux touches sont inversé sur POSIX
        BACKSPACE, DELETE = DELETE, BACKSPACE

    print(f"decoded: \"{char.decode('utf-8')}\", raw: {char}")

if sys.platform == "win32":
    def parse_windows_mouse_event(event: PyINPUT_RECORDType, last_click: mouse.Click | None, previouse_mouse_info: mouse.Info | None ) -> mouse.Info:
        """Analyse l'évènement renvoyé par le terminal et le formatte en un objet de type 'mouse.Info'"""
        
        mouse_coord = Coord(event.MousePosition.X + 1, event.MousePosition.Y + 1)
        mouse_click = None
        mouse_button = None
        mouse_button_released = False
        mouse_wheel = None
        mouse_flags = 0
        
        # TODO : Trouver un 'match' qui fasse l'affaire
        if event.ControlKeyState & win32con.RIGHT_CTRL_PRESSED or event.ControlKeyState & win32con.LEFT_CTRL_PRESSED:
            mouse_flags += mouse.MouseKeyFlags.CTRL
        if event.ControlKeyState & win32con.SHIFT_PRESSED:
            mouse_flags += mouse.MouseKeyFlags.SHIFT
        if event.ControlKeyState & win32con.LEFT_ALT_PRESSED:
            mouse_flags += mouse.MouseKeyFlags.ALT
        if event.EventFlags & win32con.MOUSE_MOVED:
            mouse_flags += mouse.MouseKeyFlags.MOVE

        if event.EventFlags & win32con.MOUSE_WHEELED:
            # Lorsque la molette est utilisée, la valeur avait l'air d'approcher les 2^32 et 2^31, un bitshift a fait l'affaire,
            # aucune idée de pourquoi ni comment mais ça m'a l'air d'être l'usage attendu...
            # Peut être ? https://learn.microsoft.com/fr-fr/windows/win32/api/winuser/nf-winuser-mouse_event
            mouse_wheel = mouse.Wheel(event.ButtonState >> 32 - 1)
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
        data: list[int] = [byte - 32 for byte in sequence]

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
        mouse_flags = 0

        xterm_mouse_key_flags = 0
        for flag in _XtermMouseFlags:
            if data[3] & flag:
                xterm_mouse_key_flags += flag
                # Ajoute le drapeau au nom correspondant entre _XtermMouseFlags et mouse.MouseKeyFlags
                if flag.name != None:
                    mouse_flags += mouse.MouseKeyFlags[flag.name].value

        button_flag = data[3] - xterm_mouse_key_flags
        match button_flag:
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

        return mouse.Info(mouse_click, mouse_wheel, Coord(data[-2], data[-1]), mouse_flags)

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
    sys.stdin = os.fdopen(0)
    # On initialise ici les variables dépendantes de la plateforme sujets à changement utilisées dans l'interprétation de l'entrée utilisateur
    if sys.platform == "win32":
        conin_event: PyINPUT_RECORDType
    else:
        SEQUENCE_LENGTH: Final[int] = 6

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
                    last_char = conin_event.Char.encode("utf-8")
                    # \r est reçu à la place \n (sauf si CTRL + entrer)
                    if last_char == b'\r': last_char = b'\n'
                    # b'\x00' est reçu lorsque l'on presse alt ou ctrl, ce qui est inutile puisqu'on gère ces touches avec 'conin_event'
                    if last_char != b'\x00':
                        on_key(last_char)

                if terminal.info.mouse_mode == True and conin_event.EventType == win32console.MOUSE_EVENT:
                    if last_click != None and last_click.released: # Permet de prévenir le signal "move" après le relachement du click
                        last_click = None
                        continue

                    # TODO : ça marche, mais comment ?
                    moved_cell: bool = previous_mouse_info.coord != Coord(conin_event.MousePosition.X + 1, conin_event.MousePosition.Y + 1)
                    clicked_on_cell: bool = (conin_event.ButtonState != 0 or (last_click != None and not last_click.released)) and not conin_event.EventFlags & win32con.MOUSE_MOVED

                    if moved_cell ^ clicked_on_cell:
                        current_mouse_info = parse_windows_mouse_event(conin_event, last_click, previous_mouse_info)
            else:
                last_char = terminal.unix_getch()

                if last_char == b'\x1b':
                    with Nonblocking(sys.stdin):
                        read = sys.stdin.buffer.read(SEQUENCE_LENGTH - 1)
                        if read != None:
                            byte_sequence = last_char + read
                            if len(byte_sequence) == SEQUENCE_LENGTH and byte_sequence[2] == ord('M'): # La séquence se démarque par un M majuscule
                                current_mouse_info = parse_xterm_mouse_tracking_sequence(byte_sequence, last_click)
                            else:
                                # TODO: Gérer les autres séquences comme les flèches
                                pass
                        else:
                            on_key(b'\x1b')
                else:
                    # CTRL + ESPACE renvoie \x00, on le convertie en ' ' plus classique
                    if last_char == b'\x00': last_char = b' '
                    on_key(last_char)

            if terminal.info.mouse_mode == True and current_mouse_info != None:
                previous_mouse_info = current_mouse_info
                if current_mouse_info.click != None:
                    last_click = current_mouse_info.click

                on_mouse(current_mouse_info)
                # Une fois la variable "current_mouse_info" utilisée, on la remet à None pour indiquer qu'aucun évènement n'est arrivé après celui-là.
                current_mouse_info = None

    except KeyboardInterrupt:
        pass

input_process = multiprocessing.Process(target=listen_to_input, name="InputProcess", daemon=True)
