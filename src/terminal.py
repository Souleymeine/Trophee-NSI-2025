#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Ce fichier contient des fonctions et classes utilitaires liées au terminal

import os
import sys
if sys.platform == "win32":
    import msvcrt
    import win32console
    import win32file
    import win32con
else:
    import termios
import warnings

from data_types import Singleton
from escape_sequences import gohome, hide_cursor, reset_style, set_altbuf, show_cursor, unset_altbuf, xterm_mouse_tracking

class _Info(metaclass=Singleton):
    def __init__(self):
        self._mouse_mode = True
        self._last_byte = b''

        if sys.platform == "win32":
            # MERCI : https://stackoverflow.com/questions/76154843/windows-python-detect-mouse-events-in-terminal

            ENABLE_EXTENDED_FLAGS = 0x0080
            ENABLE_QUICK_EDIT_MODE = 0x0040

            self._conin = win32console.PyConsoleScreenBufferType(
                win32file.CreateFile("CONIN$", win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    win32file.FILE_SHARE_WRITE, None, win32file.OPEN_ALWAYS, 0, None)
            )
            self._conin.SetStdHandle(win32console.STD_INPUT_HANDLE)

            self._win_conin_default_mode = self._conin.GetConsoleMode()
            self._win_conin_text_mode = self._win_conin_default_mode & ~ENABLE_QUICK_EDIT_MODE
            self._win_conin_mouse_mode = (self._win_conin_text_mode | win32console.ENABLE_MOUSE_INPUT | win32console.ENABLE_PROCESSED_INPUT | ENABLE_EXTENDED_FLAGS)

    @property
    def last_byte(self) -> bytes:
        return self._last_byte
    @last_byte.setter
    def last_byte(self, value: bytes):
        self._last_byte = value

    @property
    def mouse_mode(self) -> bool:
        return self._mouse_mode
    @mouse_mode.setter
    def mouse_mode(self, value: bool):
        self._mouse_mode = value
        if value == True:
            if sys.platform == "win32":
                # le drapeau pour le mode souris désactive automatiquement l'écho
                self.set_win_stdin_mode(self.win_stdin_mouse_mode)
            else:
                self.set_posix_echo(False)
                xterm_mouse_tracking(True)
                hide_cursor()
        else:
            if sys.platform == "win32":
                self.set_win_stdin_mode(self.win_stdin_text_mode)
            else:
                self.set_posix_echo(True)
                xterm_mouse_tracking(False)
                show_cursor()

    @property
    def win_stdin_default_mode(self) -> int:
        return self._win_conin_default_mode
    @property
    def win_stdin_text_mode(self) -> int:
        return self._win_conin_text_mode
    @property
    def win_stdin_mouse_mode(self) -> int:
        return self._win_conin_mouse_mode
    
    def set_win_stdin_mode(self, mode: int):
        if sys.platform == "win32":
            self._conin.SetConsoleMode(mode)
        else:
            warnings.warn("'set_win_stdin_mode' est une fonction exclusive à Windows.")

    # De https://gist.github.com/kgriffs/5726314
    def set_posix_echo(self, enabled: bool):
        """Active/Désactive l'affichage de l'entré de l'utilisateur.
        Aussi utilsé pour interpréter les touches de clavier/souris sans afficher quoique ce soit."""
        if sys.platform != "win32":
            fd = sys.stdin.fileno()
            new = termios.tcgetattr(fd)
            if enabled:
                new[3] |= termios.ECHO
            else:
                new[3] &= ~termios.ECHO

            termios.tcsetattr(fd, termios.TCSANOW, new)
        else:
            warnings.warn("La méthode '_set_posix_echo' devrait être appelée sous les systèmes POSIX uniquement!")

# Instance unique !
info = _Info()

def unix_getch() -> bytes:
    """Retourne le dernier octet de stdin sous les systèmes POSIX"""
    if sys.platform != "win32":
        # https://stackoverflow.com/questions/3523174/raw-input-without-pressing-enter
        fd: int = sys.stdin.fileno()
        orig = termios.tcgetattr(fd)

        new = termios.tcgetattr(fd)
        new[3] &= ~termios.ICANON
        new[6][termios.VMIN] = 1
        new[6][termios.VTIME] = 0

        try:
            termios.tcsetattr(fd, termios.TCSAFLUSH, new)
            return sys.stdin.buffer.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, orig)
    else:
        warnings.warn("La méthode 'unix_getch' devrait être appelée sous les systèmes POSIX uniquement!")
        return b'unix_getch : Mauvaise plateforme (windows)'

def init():
    """Initialise le terminal pour supporter les séqunces d'échappement et les caractères spéciaux.
    Prépare également l'écran secondaire du terminal."""
    
    # Merci à ce post qui m'a permis de ne pas tomber dans la folie après plusieurs jours de recherches.
    # https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    if sys.platform == "win32":
        os.system("") # Magie...

    # NOTE : l'ordre de ces fonctions n'est pas anodin. 
    # Cacher le curseur après avoir activé l'écran alternatif le réaffichera.
    set_altbuf()
    hide_cursor()
    gohome()
    info.mouse_mode = True
    info.last_byte = b''

def reset():
    """Rétablie l'était du terminal initial."""
    reset_style()
    unset_altbuf()
    show_cursor()
    info.mouse_mode = False
    if sys.platform == "win32":
        info.set_win_stdin_mode(info.win_stdin_default_mode)
