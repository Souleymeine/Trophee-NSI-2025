#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Principalement un "emaballage" ANSI

## Sources principales :
# - Séquence d'échappement ANSI : https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

import sys
from enum import Enum
from data_types import RGB, Coord
from typing import Final

# NOTE : On force une écriture brute dans la sortie standard 
# pour ne pas se préocuper du formattage ou du tampon mémoire de 'print'.
# 'stdout.write' est plus directe et adaptée dans notre contexte.

# Alias sys.stdout.write comme ctrl_seq (abréviation du terme spécifique 'control sequence' en anglais),
# plus pratique pour différencier un simple appel à 'stdout.write' d'une "séquence de contrôle".
# Pour toutes les mentions de la fonction 'ctrl_seq' (alias de stdout.write), se référer au lien github cité en en-tête.
def ctrl_seq(seq: str):
    sys.stdout.write(seq)
    sys.stdout.flush()

# CSI pour "Control Sequence Introducer", nom assez explicite.
CSI : Final[str] = "\x1B["

def reset_style():
    """Rétablie le style (gras, italique... et/ou la couleur) par défaut du terminal."""
    ctrl_seq(f"{CSI}m")

# === Curseur et déplacements ========================

def hide_cursor(): ctrl_seq(f"{CSI}?25l")
def show_cursor(): ctrl_seq(f"{CSI}?25h")

def gohome(): ctrl_seq(f"{CSI}H")

def cat_goto(coord: Coord):
    """Retoune ce que la fonction 'goto' imprimerait. Utile pour concaténer des séquences entières."""
    assert coord.x >= 1, f"x doit être supérieur ou égale à 1: {coord.x}"
    assert coord.y >= 1, f"y doit être supérieur ou égale à 1: {coord.y}"

    return f"{CSI}{coord.y};{coord.x}H"
def goto(coord: Coord):
    """Déplace le curseur aux positions x et y données. 
    à noter que (1 ; 1) ou la position d'origine ou "home" (voir 'gohome') se réfère au coin supérieur gauche du terminal."""
    assert coord.x >= 1, f"x doit être supérieur ou égale à 1: {coord.x}"
    assert coord.y >= 1, f"y doit être supérieur ou égale à 1: {coord.y}"
    
    ctrl_seq(f"{CSI}{coord.y};{coord.x}H")

def print_at(string: str, coord: Coord):
    """prints the given string to the given location in the terminal.
    Note that (0 , 0) or home positions (se 'gohome') refers to the top left hand corner of the terminal.
    The first character will be placed at the given position and the others will be placed inline like any regular 'print' call"""
    assert coord.x >= 1, f"x doit être supérieur ou égale à 1: {coord.x}"
    assert coord.y >= 1, f"y doit être supérieur ou égale à 1: {coord.y}"

    ctrl_seq(f"{CSI}{coord.y};{coord.x}H{string}")

# === Tampon ou écran ================================

def set_altbuf():
    """Active le tapon (ici "écran") secondaire du terminal"""
    ctrl_seq(f"{CSI}?1049h")
def unset_altbuf():
    """Désactive le tapon (ici "écran") secondaire du terminal"""
    ctrl_seq(f"{CSI}?1049l")

# === Styles =========================================

class ANSI_Styles(Enum):
    DEFAULT       = 0
    BOLD          = 1
    DIM           = 2
    ITALIC        = 3
    UNDERLINE     = 4
    BLINKING      = 5
    INVERSE       = 6
    HIDDEN        = 8
    STRIKETHROUGH = 9

def print_styled(string: str, style: ANSI_Styles):
    print(f"{CSI}{style._value_}m{string}")

def print_styled_at(string: str, style: ANSI_Styles, coord: Coord):
    assert coord.x >= 1, f"x doit être supérieur ou égale à 1: {coord.x}"
    assert coord.y >= 1, f"y doit être supérieur ou égale à 1: {coord.y}"
    print(f"{CSI}{coord.y};{coord.x}H{CSI}{style._value_}m{string}")

# === Couleurs =======================================

def print_bgcolor(color: RGB):
    """Sets the background color at the current cursor postition with the given r, g an b values.
    This is done by use a specific control sequences and resetting int while printing a space in the middle."""
    ctrl_seq(f"{CSI}48;2;{color.r};{color.g};{color.b}m {CSI}m")

def cat_bgcolor(color: RGB) -> str:
    """Retourne la séquence que 'print_bgcolor' imprimerait
    Utile pour concaténer des séquences entières."""
    return f"{CSI}48;2;{color.r};{color.g};{color.b}m {CSI}m"
def set_fgcolor(color: RGB):
    """Définie une couleur de texte pour tous les prochains print jusqu'à l'appelle de 'reset_bgcolor' ou la fin d'une séquence."""
    ctrl_seq(f"{CSI}38;2;{color.r};{color.g};{color.b}m")
def reset_fgcolor():
    """Rétablie la couleur de texte par défaut du terminal si la séquence d'échappement précédante n'a pas été terminée."""
    ctrl_seq(f"{CSI}39m")

def print_bgcolor_at(color: RGB, coord: Coord):
    """Identique à 'print_bgcolor' mais aux positions données au lieu de celles du curseur.
    Sert à colorier une cellule au coordonnées données."""
    assert coord.x >= 1, f"x doit être supérieur ou égale à 1: {coord.x}"
    assert coord.y >= 1, f"y doit être supérieur ou égale à 1: {coord.y}"

    ctrl_seq(f"{CSI}{coord.y};{coord.x}H{CSI}48;2;{color.r};{color.g};{color.b}m {CSI}m")


# https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking

def xterm_mouse_tracking(enabled: bool):
    ctrl_seq(f"{CSI}?1003{'h' if enabled else 'l'}")
