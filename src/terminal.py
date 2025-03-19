#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Ce fichier contient des fonctions et classes utilitaires liées au terminal

import os
import sys
if sys.platform == "win32":
    import win32console
    import win32file
else:
    import termios
from data_types import EnsureSingle
from escape_sequences import gohome, hide_cursor, reset_style, set_altbuf, unset_altbuf, show_cursor, xterm_mouse_tracking


class Info(metaclass=EnsureSingle):
    def __init__(self):

        if sys.platform == "win32":
            # FIXME : BUG !!! La classe est initialisée deux fois sur windows car le processus "InputProcess" n'a pas accès au processus principale.
            # Cela se manifeste en bug que l'humanité n'était pas censée connaître.
            # Plus sérieusement la copie de cette classe ne sera pas la même sur les deux processus, d'où le fait qu'on "hardcode" certaines valeurs ici. 
            # -> https://docs.python.org/fr/3.13/library/multiprocessing.html#contexts-and-start-methods
            self._mouse_mode = True

            # MERCI : https://stackoverflow.com/questions/76154843/windows-python-detect-mouse-events-in-terminal

            # Les différents mode: https://learn.microsoft.com/fr-fr/windows/console/setconsolemode
            ENABLE_EXTENDED_FLAGS = 0x0080
            ENABLE_QUICK_EDIT_MODE = 0x0040

            self._conin = win32console.PyConsoleScreenBufferType(
                win32file.CreateFile("CONIN$", win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    win32file.FILE_SHARE_WRITE, None, win32file.OPEN_ALWAYS, 0, None)
            )

            self._conin.SetStdHandle(win32console.STD_INPUT_HANDLE)
            
            self._conin_default_mode = 487
            
            self._conin_text_mode = (self._conin_default_mode | win32console.ENABLE_PROCESSED_INPUT) & ~ENABLE_QUICK_EDIT_MODE
            self._conin_mouse_mode = win32console.ENABLE_MOUSE_INPUT | win32console.ENABLE_PROCESSED_INPUT | ENABLE_EXTENDED_FLAGS 


    @property
    def mouse_mode(self) -> bool:
        return self._mouse_mode
    @mouse_mode.setter
    def mouse_mode(self, value: bool):
        self._mouse_mode = value
        if value == True:
            if sys.platform == "win32":
                self.set_conin_mode(self.conin_mouse_mode)
            else:
                xterm_mouse_tracking(True)
            hide_cursor()
        else:
            if sys.platform == "win32":
                self.set_conin_mode(self.conin_text_mode)
            else:
                xterm_mouse_tracking(False)
            show_cursor()

    if sys.platform == "win32":
        @property
        def conin_default_mode(self) -> int:
            return self._conin_default_mode
        @property
        def conin_text_mode(self) -> int:
            return self._conin_text_mode
        @property
        def conin_mouse_mode(self) -> int:
            return self._conin_mouse_mode
    
        def set_conin_mode(self, mode: int):
            self._conin.SetConsoleMode(mode)


if sys.platform != "win32":
    # De https://gist.github.com/kgriffs/5726314
    def set_posix_echo(enabled: bool):
        """Active/Désactive l'affichage de l'entré de l'utilisateur.
        Aussi utilsé pour interpréter les touches de clavier/souris sans afficher quoique ce soit."""
        fd = sys.stdin.fileno()
        new = termios.tcgetattr(fd)
        if enabled:
            new[3] |= termios.ECHO
        else:
            new[3] &= ~termios.ECHO

        termios.tcsetattr(fd, termios.TCSANOW, new)
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

# Instance unique !
info = Info()

def init():
    """Initialise le terminal pour supporter les séqunces d'échappement et les caractères spéciaux.
    Prépare également l'écran secondaire du terminal."""
    # Merci à ce post qui m'a permis de ne pas tomber dans la folie après plusieurs jours de recherches.
    # https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    if sys.platform == "win32":
        os.system("") # Magie...
    else:
        set_posix_echo(False)

    # NOTE : l'ordre de ces fonctions n'est pas anodin. 
    # Cacher le curseur après avoir activé l'écran alternatif le réaffichera.
    set_altbuf()
    hide_cursor()
    gohome()
    info.mouse_mode = True

def reset():
    """Rétablie l'était du terminal initial."""
    reset_style()
    unset_altbuf()
    show_cursor()
    info.mouse_mode = False
    if sys.platform == "win32":
        info.set_conin_mode(info.conin_default_mode) 
    else:
        set_posix_echo(True)

