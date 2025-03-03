#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Ce fichier contient des fonctions utilitaires liées au terminal

import os
import sys
from escape_sequences import gohome, hide_cursor, reset_style, set_altbuf, show_cursor, unset_altbuf

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

def reset():
    """Rétablie l'était du terminal initial."""
    reset_style()
    unset_altbuf()
    show_cursor()
