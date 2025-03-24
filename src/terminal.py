#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Ce fichier contient des fonctions et classes utilitaires liées au terminal

import sys
from typing import cast
if sys.platform == "win32":
    import win32file
    import win32console
    from win32console import PyConsoleScreenBufferType
else:
    import termios
    import tty
from data_types import EnsureSingle
from escape_sequences import gohome, hide_cursor, reset_style, set_altbuf, unset_altbuf, show_cursor, xterm_mouse_tracking
from multiprocessing.managers import BaseManager, BaseProxy


if sys.platform == "win32":
    class MockPyCOORD:
        def __init__(self, X = 0, Y = 0):
            self.X = X
            self.Y = Y
    class MockPyINPUT_RECORDType():
        """Classe utilisée pour remplacer l'objet PyINPUT_RECORDType qui n'est pas transferrable via BaseManager"""
        def __init__(self, EventType = 0, KeyDown: int | bool = False, Char = "", ControlKeyState = 0, VirtualKeyCode = 0, ButtonState = 0, EventFlags = 0, MousePosition = MockPyCOORD()):
            self.EventType = EventType
            self.KeyDown = KeyDown
            self.Char = Char
            self.ControlKeyState = ControlKeyState
            self.VirtualKeyCode = VirtualKeyCode
            self.ButtonState = ButtonState
            self.EventFlags = EventFlags
            self.MousePosition = MousePosition
else:
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

class Info(metaclass=EnsureSingle):
    def __init__(self):
        if sys.platform == "win32":
            # Les différents mode: https://learn.microsoft.com/fr-fr/windows/console/setconsolemode
            ENABLE_QUICK_EDIT_MODE = 0x0040
            ENABLE_EXTENDED_FLAGS  = 0x0080

            self._conin = PyConsoleScreenBufferType(
                win32file.CreateFile("CONIN$", win32file.GENERIC_READ | win32file.GENERIC_WRITE, 
                win32file.FILE_SHARE_WRITE, None, win32file.OPEN_ALWAYS, 0, None)
            )
            self._conin.SetStdHandle(win32console.STD_INPUT_HANDLE)
            
            self._conin_default_mode = self._conin.GetConsoleMode()
            self._conin_text_mode = (self._conin_default_mode & ~ENABLE_QUICK_EDIT_MODE & ~win32console.ENABLE_PROCESSED_INPUT) | ENABLE_EXTENDED_FLAGS
            self._conin_mouse_mode = (win32console.ENABLE_MOUSE_INPUT | win32console.ENABLE_PROCESSED_INPUT | ENABLE_EXTENDED_FLAGS) & ~win32console.ENABLE_PROCESSED_INPUT
        else:
            self._default_tty_mode = termios.tcgetattr(0)

    def get_mouse_mode(self) -> bool:
        return self._mouse_mode
    def set_mouse_mode(self, value: bool):
        self._mouse_mode = value
        if value == True:
            if sys.platform == "win32":
                self.set_conin_mode(self.get_conin_mouse_mode())
            else:
                xterm_mouse_tracking(True)
            hide_cursor()
        else:
            if sys.platform == "win32":
                self.set_conin_mode(self.get_conin_text_mode())
            else:
                xterm_mouse_tracking(False)
            show_cursor()

    if sys.platform == "win32":
        def read_conin(self) -> MockPyINPUT_RECORDType:
            """Lis l'entrée de la console et retorune une version simplifiée de la classe PyINPUT_RECORDType facilement communicable entre processus qui représente notre entrée.
            Passer l'objet de manière brute résulte en une erreur de sérialisation."""

            event = self._conin.ReadConsoleInput(1)[0]

            result = MockPyINPUT_RECORDType()

            result.EventType = event.EventType
            # Extrait les informations utiles relativement au contexte et les convertie en dictionnaire
            if event.EventType == win32console.KEY_EVENT:
                result.KeyDown = event.KeyDown
                result.Char = event.Char
                result.VirtualKeyCode = event.VirtualKeyCode
                result.ControlKeyState = event.ControlKeyState
            elif event.EventType == win32console.MOUSE_EVENT:
                result.MousePosition = MockPyCOORD(event.MousePosition.X, event.MousePosition.Y)
                result.ButtonState = event.ButtonState
                result.ControlKeyState = event.ControlKeyState
                result.EventFlags = event.EventFlags

            return result
        
        def get_conin_default_mode(self) -> int:
            return self._conin_default_mode
        def get_conin_text_mode(self) -> int:
            return self._conin_text_mode
        def get_conin_mouse_mode(self) -> int:
            return self._conin_mouse_mode

        def set_conin_mode(self, mode: int):
            assert self._conin is not None
            self._conin.SetConsoleMode(mode)
    else:
        def  get_tty_default_mode(self):
            return self._default_tty_mode

# Voir https://docs.python.org/3/library/multiprocessing.html#customized-managers
class TerminalInfoProxy(BaseProxy):
    # On définit les getter de la classe Info comme des propriété dans le proxy:
    # On les rend donc constante sans accéder aux propriétés de la classe de base

    @property
    def mouse_mode(self) -> bool:
        return cast(bool, self._callmethod('get_mouse_mode'))
    @mouse_mode.setter
    def mouse_mode(self, value: bool):
        return self._callmethod('set_mouse_mode', (value,))

    if sys.platform == "win32":
        @property
        def conin_default_mode(self) -> int:
            return cast(int, self._callmethod('get_conin_default_mode'))
        @property
        def conin_text_mode(self) -> int:
            return cast(int, self._callmethod('get_conin_text_mode'))
        @property
        def conin_mouse_mode(self) -> int:
            return cast(int, self._callmethod('get_conin_mouse_mode'))

        def set_conin_mode(self, mode):
            return self._callmethod('set_conin_mode', (mode,))

        def read_conin(self) -> MockPyINPUT_RECORDType:
            return cast(MockPyINPUT_RECORDType, self._callmethod('read_conin'))
    else:
        @property
        def tty_default_mode(self):
            return self._callmethod('get_tty_default_mode')

class TerminalInfoManager(BaseManager):
    pass

def init(term_info: TerminalInfoProxy):
    """Prépare l'écran secondaire du terminal."""
    if sys.platform != "win32":
        set_posix_echo(False)
        tty.setraw(sys.stdin.fileno())

    # NOTE : l'ordre de ces fonctions n'est pas anodin. 
    # Cacher le curseur après avoir activé l'écran alternatif le réaffichera.
    set_altbuf()
    hide_cursor()
    gohome()

    term_info.mouse_mode = True

def reset(term_info: TerminalInfoProxy):
    """Rétablie l'était initial du terminal."""
    reset_style()
    unset_altbuf()
    show_cursor()
    term_info.mouse_mode = False
    if sys.platform == "win32":
        term_info.set_conin_mode(term_info.conin_default_mode)
    else:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, term_info.tty_default_mode) # type: ignore
        set_posix_echo(True)

