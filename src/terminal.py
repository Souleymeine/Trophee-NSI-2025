#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Ce fichier contient des fonctions et classes utilitaires liées au terminal

import os
import sys
if sys.platform == "win32":
    import msvcrt
else:
    import termios
import warnings

from data_types import Singleton
from escape_sequences import gohome, hide_cursor, reset_style, set_altbuf, show_cursor, unset_altbuf, xterm_mouse_tracking

class _Info(metaclass=Singleton):
    def _disable_win_echo(self):
        if sys.platform == "win32":
            while self.mouse_mode:
                self.last_byte = msvcrt.getwch()
        else:
            warnings.warn("La méthode '_disable_win_echo' devrait être appelée sur windows uniquement!")

    # De https://gist.github.com/kgriffs/5726314
    def _set_posix_echo(self, enabled: bool):
        """Active/Désactive l'affichage de l'entré de l'utilisateur.
        Aussi utilsé pour interpréter les touches de clavier/souris sans afficher quoique ce soit."""
        fd = sys.stdin.fileno()
        new = termios.tcgetattr(fd)
        if enabled:
            new[3] |= termios.ECHO
        else:
            new[3] &= ~termios.ECHO

        termios.tcsetattr(fd, termios.TCSANOW, new)

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
                # La fonction s'éxecutera jusqu'à ce que mouse_mode = False
                Thread(target=self._disable_win_echo).start()
            else:
                self._set_posix_echo(False)
                xterm_mouse_tracking(True)
                hide_cursor()
        else:
            # la fonction _disable_win_echo se terminera automatiquement si self._mouse_mode = False
            if sys.platform != "win32":
                self._set_posix_echo(True)
                xterm_mouse_tracking(False)
                show_cursor()

# Instance unique !
info = _Info()

def unix_getch() -> bytes:
    """Retourne le dernier octet de stdin sous les systèmes POSIX"""
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
