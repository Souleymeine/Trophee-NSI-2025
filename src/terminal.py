#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Ce fichier contient des fonctions utilitaires liées au terminal

import os
import sys
from escape_sequences import gohome, hide_cursor, reset_style, set_altbuf, show_cursor, unset_altbuf


def set_fullscreen():
    if sys.platform == "win32":
        # -> https://stackoverflow.com/questions/2791839/which-is-the-easiest-way-to-simulate-keyboard-and-mouse-on-python
        import ctypes
        F11_KEYCODE = 0x7A
        ctypes.windll.user32.keybd_event(F11_KEYCODE, 0, 0, 0)      # Simule F11 (racourcie pour activer le plein écran)
        ctypes.windll.user32.keybd_event(F11_KEYCODE, 0, 0x0002, 0) # Relache la touche

def init_term():
    """Initialise le terminal pour supporter les séqunces d'échappement et les caractères spéciaux.
    Prépare également l'écran secondaire du terminal."""
    
    set_fullscreen()
    # Merci à ce post qui m'a permis de ne pas tomber dans la folie après plusieurs jours de recherches.
    # https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
    if sys.platform == "win32":
        os.system("") # Magie...

    # NOTE : l'ordre de ces fonctions n'est pas anodin. 
    # Cacher le curseur après avoir activé l'écran alternatif le réaffichera.
    set_altbuf()
    hide_cursor()
    gohome()

def reset_term():
    """Rétablie l'était du terminal initial."""
    reset_style()
    unset_altbuf()
    show_cursor()
