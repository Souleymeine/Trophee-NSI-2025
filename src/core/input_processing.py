# Projet : pyscape
# Auteurs : Rabta Souleymeine

from multiprocessing import Queue
import sys

if sys.platform == "win32":
    import win32console
    import win32con
    from core.terminal import scale_win_console
    from core.terminal import MockPyINPUT_RECORDType
else:
    import fcntl
import signal
import os
import core.terminal as terminal
from type_def.data_types import Coord
from core.terminal import TerminalInfoProxy
from type_def.input_properties import *

def mouse(info: MouseInfo, event_queue: Queue):
    event_queue.put(info)

def key(info: KeyInfo, term_info: TerminalInfoProxy, event_queue: Queue):
    if info.char == b'e' and info.key_flag & KeyFlags.ALT:
        event_queue.put("END")
        return

    event_queue.put(info)

    # TODO : zoomer DANS la console sans l'agrandir
    if sys.platform == "win32":
        current_term_size = os.get_terminal_size()
        if (info.char == b'=' or info.char == b'+') and info.key_flag & KeyFlags.ALT:
            scale_win_console(1)
            resize(current_term_size, event_queue)
        if info.char == b'-' and info.key_flag & KeyFlags.ALT:
            scale_win_console(-1)
            resize(current_term_size, event_queue)

    # TODO : Créer un fichier contenant toutes les définitions de caractères spéciaux

def arrow(info: ArrowInfo, event_queue: Queue):
    event_queue.put(info)

def resize(terminal_size: os.terminal_size, event_queue: Queue):
    event_queue.put(terminal_size)

if sys.platform == "win32":
    def parse_windows_mouse_event(event: MockPyINPUT_RECORDType, last_click: MouseClick | None) -> MouseInfo:
        """Analyse l'évènement renvoyé par le terminal et le formatte en un objet de type 'MouseInfo'"""
        
        # Le code se réfère à ce format: https://learn.microsoft.com/fr-fr/windows/console/mouse-event-record-str

        mouse_coord = Coord(event.MousePosition.X + 1, event.MousePosition.Y + 1) # On ajoute 1 pour coller au système de coordonnées Xterm qui commence à la cellule 1, 1
        mouse_click = None
        mouse_button = None
        mouse_button_released = False
        mouse_wheel = None
        mouse_flags = 0

        if event.ControlKeyState & win32con.LEFT_CTRL_PRESSED: mouse_flags |= MouseKeyFlags.CTRL
        if event.ControlKeyState & win32con.SHIFT_PRESSED:     mouse_flags |= MouseKeyFlags.SHIFT
        if event.ControlKeyState & win32con.LEFT_ALT_PRESSED:  mouse_flags |= MouseKeyFlags.ALT
        if event.EventFlags & win32con.MOUSE_MOVED:            mouse_flags |= MouseKeyFlags.MOVE

        if event.EventFlags & win32con.MOUSE_WHEELED:
            mouse_wheel = MouseWheel(event.ButtonState >> 2**5 - 1 > 0)
        else:
            if   event.ButtonState & win32con.FROM_LEFT_1ST_BUTTON_PRESSED: mouse_button = MouseButton.LEFT
            elif event.ButtonState & win32con.RIGHTMOST_BUTTON_PRESSED:     mouse_button = MouseButton.RIGHT
            elif event.ButtonState & win32con.FROM_LEFT_2ND_BUTTON_PRESSED: mouse_button = MouseButton.MIDDLE
            elif event.ButtonState == 0 and (last_click is not None and last_click.released == False): # Aucun click enfoncé
                # On cherche le dernier click enfoncé pour trouvé le bouton correspondant
                mouse_button = last_click.button
                mouse_button_released = True
            
            if mouse_button is not None:
                mouse_click = MouseClick(mouse_button, mouse_button_released)
        
        return MouseInfo(mouse_click, mouse_wheel, mouse_coord, mouse_flags)
    def parse_windows_key_event(event: MockPyINPUT_RECORDType) -> KeyInfo:
        char = event.Char.encode()

        # \r est reçu à la place \n (sauf si CTRL + entrer), on rend les deux identiques
        if char == b'\r':
            char = b'\n'

        is_char_unmodifianle_key: bool = (char != b'\x1b' and char != b'\x7f' and char != b'\x08' and char != b'\n')

        flag: int = 0
        if is_char_unmodifianle_key:
            if event.ControlKeyState & win32con.LEFT_CTRL_PRESSED: flag |= KeyFlags.CTRL
            if event.ControlKeyState & win32con.SHIFT_PRESSED:     flag |= KeyFlags.SHIFT
            if event.ControlKeyState & win32con.LEFT_ALT_PRESSED:  flag |= KeyFlags.ALT

        if is_char_unmodifianle_key and flag & KeyFlags.CTRL:
            char = (int.from_bytes(char) + 2**6 + 2**5).to_bytes()
            if flag & KeyFlags.SHIFT:
                char = char.upper()

        return KeyInfo(char, flag)

    def parse_windows_arrow_event(event: MockPyINPUT_RECORDType) -> ArrowInfo | None:
        flag: int = 0
        if event.ControlKeyState & win32con.LEFT_CTRL_PRESSED: flag |= KeyFlags.CTRL
        if event.ControlKeyState & win32con.SHIFT_PRESSED:     flag |= KeyFlags.SHIFT
        if event.ControlKeyState & win32con.LEFT_ALT_PRESSED:  flag |= KeyFlags.ALT

        arrow: Arrows | None = None
        match event.VirtualKeyCode:
            case 37: arrow = Arrows.LEFT
            case 38: arrow = Arrows.UP
            case 39: arrow = Arrows.RIGHT
            case 40: arrow = Arrows.DOWN

        if arrow is not None:
            return ArrowInfo(arrow, flag)

else:
    def parse_xterm_mouse_tracking_sequence(sequence: bytes, last_click: MouseClick | None) -> MouseInfo:
        """Analyse la séquence de caractère pour l'interpréter en une classe de type mouse.Info"""

        # Convertie les caractères en valeures numériques
        data: list[int] = [byte - 32 for byte in sequence[1:]]

        # Le code se réfère à ce format : https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking

        mouse_coord = Coord(data[-2], data[-1])
        mouse_click = None
        mouse_button = None
        mouse_button_released = False
        mouse_wheel = None
        mouse_flags = 0

        xterm_mouse_key_flags = 0
        for flag in XtermMouseFlags:
            if data[0] & flag:
                xterm_mouse_key_flags += flag
                # Ajoute le drapeau au nom correspondant entre _XtermMouseFlags et mouse.MouseKeyFlags
                if flag.name != None:
                    mouse_flags += MouseKeyFlags[flag.name].value

        button_flag = data[0] - xterm_mouse_key_flags
        match button_flag:
            case 64: mouse_wheel = MouseWheel.SCROLL_UP
            case 65: mouse_wheel = MouseWheel.SCROLL_DOWN
            case 0: mouse_button = MouseButton.LEFT
            case 1: mouse_button = MouseButton.MIDDLE
            case 2: mouse_button = MouseButton.RIGHT
            case 3: # Aucun click enfoncé
                mouse_button_released = True
                # On cherche le dernier click enfoncé pour trouvé le bouton correspondant
                if last_click != None and not last_click.released:
                    mouse_button = last_click.button

        if mouse_button != None:
            mouse_click = MouseClick(mouse_button, mouse_button_released)

        return MouseInfo(mouse_click, mouse_wheel, mouse_coord, mouse_flags)
    def parse_xterm_arrow_sequence(sequence: bytes) -> ArrowInfo | None:
        arrow: Arrows | None = None
        match sequence[-1].to_bytes():
            case b'A': arrow = Arrows.UP
            case b'B': arrow = Arrows.DOWN
            case b'C': arrow = Arrows.RIGHT
            case b'D': arrow = Arrows.LEFT

        arrow_flags: int = 0
        if sequence[0].to_bytes() == b'1':
            for flag in XtermKeyFlags:
                if sequence[2] - sequence[0] & flag and flag.name is not None:
                    arrow_flags |= KeyFlags(KeyFlags[flag.name].value)

        if arrow is not None:
            return ArrowInfo(arrow, arrow_flags)

    def parse_xterm_key(char: bytes, sequence: bool) -> KeyInfo | None:
        char = b'\n' if char == b'\r' else char
        if char != b'\t' and char != b'\x1b' and char != b'\x08' and char != b'\x7f' and char != b'\n':
            if int.from_bytes(char) <= 26: # Caractères spéciaux précédents les caractères normaux, dans ce contexte : CTRL + A-Z
                offset_char = (int.from_bytes(char) + 2**6 + 2**5).to_bytes()
                flags = KeyFlags.CTRL | (KeyFlags.ALT if sequence else 0) | (KeyFlags.SHIFT if offset_char.isupper() else 0)
                return KeyInfo(offset_char, flags)
            elif 2**5 < int.from_bytes(char) < 2**7 and sequence:
                return KeyInfo(char, KeyFlags.ALT | (KeyFlags.SHIFT if char.isupper() else 0))
            elif int.from_bytes(char) > 2**7: # Pour les caractères au delà de 127 (utf-8, ex : 'ù')
                second_char = sys.stdin.buffer.read(1)
                assert second_char is not None, "Caractère innatendu"
                return KeyInfo(char + second_char, 0)

        return KeyInfo(char, KeyFlags.SHIFT if char.isupper() else 0)
    
    def is_mouse_sequence(sequence: bytes) -> bool:
        if len(sequence) != 5:
            return False
        valid_mouse_CSI: bool = (sequence[0:2] == b'[M')
        valid_coord: bool = (sequence[3] - 2**5 >= 1 and sequence[4] - 2**5 >= 1)
        valid_flags: bool = False

        flags: int = 0
        for flag in XtermMouseFlags:
            if sequence[2] - 2**5 & flag:
                flags |= flag

        for button_value in (0, 1, 2, 3, 64, 65):
            if sequence[2] - 2**5 - flags == button_value:
                valid_flags = True

        return valid_mouse_CSI and valid_flags and valid_coord
    def is_arrow_sequence(sequence: bytes) -> bool:
        if len(sequence) == 5:
            valid_CSI: bool = (sequence[0:3] == b'[1;')
            if not valid_CSI:
                return False
            valid_flag: bool = False
            for flag in XtermKeyFlags:
                if int((sequence[3] - 1).to_bytes()) & flag:
                    valid_flag = True
                    break
            return valid_CSI and valid_flag
        elif len(sequence) == 2:
            for arrow_code in b'ABCD':
                if sequence[1] == arrow_code:
                    return True
        return False
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



def listen_to_input(term_info: TerminalInfoProxy, event_queue: Queue):
    # On réouvre sys.stdin car il est automatiquement fermé lors de la création d'un nouveau processus
    sys.stdin = os.fdopen(0)

    if sys.platform == "win32": # Utile uniquement dans le cas de Windows (CTRL + Scroll)
        previouse_term_size: os.terminal_size | None = None
    else:
        def sigwich_handler(signum, frame):
            resize(os.get_terminal_size(), event_queue)
        signal.signal(signal.SIGWINCH, sigwich_handler)

    # Ces valeurs seront changées à partir de la première intéraction
    previous_mouse_info: MouseInfo | None = None
    current_mouse_info: MouseInfo | None = None
    last_click: MouseClick | None = None

    current_arrow_info: ArrowInfo | None = None
    current_key_info: KeyInfo | None = None

    while True:
        if sys.platform == "win32":
            # On utilise une version simplifiée de PyINPUT_RECORDType facilement communicable entre processus, les champs restent les mêmes
            conin_event = term_info.read_conin()

            # MERCI : https://stackoverflow.com/questions/76154843/windows-python-detect-mouse-events-in-terminal
            
            if conin_event.EventType == win32console.KEY_EVENT and conin_event.KeyDown:
                if str.encode(conin_event.Char) == b'\x00':
                    current_arrow_info = parse_windows_arrow_event(conin_event)
                else:
                    current_key_info = parse_windows_key_event(conin_event)
            elif term_info.mouse_mode == True and conin_event.EventType == win32console.MOUSE_EVENT:
                # Deux évènement avec le drapeau "MOUSE_MOVED" (win32con.MOUSE_MOVED) inutiles et non désirés sont envoyés par Windows :
                # - après avoir relacher un click
                # - après avoir déplacer la souris à l'intérieur même d'une cellule
                # Les deux booléens moved_on_cell et clicked_on_cell ci dessous exlus ces cas là

                current_mouse_coord = Coord(conin_event.MousePosition.X + 1, conin_event.MousePosition.Y + 1)
                mouse_button_pressed: bool = conin_event.ButtonState != 0
                moved_for_the_first_time: bool = (previous_mouse_info is None and bool(conin_event.EventFlags & win32con.MOUSE_MOVED))

                moved_on_cell: bool = moved_for_the_first_time or (previous_mouse_info is not None and previous_mouse_info.coord != current_mouse_coord)
                clicked_on_cell: bool = (mouse_button_pressed or (last_click is not None and last_click.released == False)) and bool(conin_event.EventFlags & win32con.MOUSE_MOVED) == False
                
                # L'opérateur ^ est un "OU exclusif" (XOR)
                if moved_on_cell ^ clicked_on_cell:
                    current_mouse_info = parse_windows_mouse_event(conin_event, last_click)
            elif conin_event.EventType == win32console.WINDOW_BUFFER_SIZE_EVENT:
                term_size = os.get_terminal_size()
                if previouse_term_size != term_size or previouse_term_size is None:
                    resize(term_size, event_queue)
                    previouse_term_size = term_size
        else:
            current_char = terminal.unix_getch()

            if current_char == b'\x1b':
                with Nonblocking(sys.stdin):
                    read = sys.stdin.buffer.read(5)
                    if read != None:
                        read = bytes(read)
                        if is_mouse_sequence(read):
                            current_mouse_info = parse_xterm_mouse_tracking_sequence(read[1:], last_click)
                        elif is_arrow_sequence(read):
                            current_arrow_info = parse_xterm_arrow_sequence(read[1:])
                        elif len(read) == 1:
                            current_key_info = parse_xterm_key(read, True)
                    else:
                        current_key_info = parse_xterm_key(b'\x1b', False)
            elif current_char != b'\x00':
                # Convertie b'\x08' en b'\x7f' et b'\x7f' en b'\x08'
                current_char = b'\x08' if current_char == b'\x7f' else b'\x7f' if current_char == b'\x08' else current_char
                current_key_info = parse_xterm_key(current_char, False)

        if current_mouse_info is not None:
            previous_mouse_info = current_mouse_info
            if current_mouse_info.click is not None:
                last_click = current_mouse_info.click

            mouse(current_mouse_info, event_queue)
            current_mouse_info = None

        elif current_arrow_info is not None:
            arrow(current_arrow_info, event_queue)
            current_arrow_info = None

        elif current_key_info is not None:
            key(current_key_info, term_info, event_queue)
            current_key_info = None

