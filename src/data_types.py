#Projet : pyscape
#Auteurs : Rabta Souleymeine

from dataclasses import dataclass

@dataclass
class RGB:
	r: int 
	g: int
	b: int

@dataclass
class Vec2d:
	"""
	Classe de données simple représentant un couple de valeur x et y.
	On peu l'utiliser comme vecteur, coordonnées, dimmensions, ou quoique ce soit qui puisse être représenté par une abscisse et une ordonnée.
	Elle seront représentées par des entiers uniquement, puique nous sommes dans la grille du terminal.
	"""
	x : int
	y : int

from enum import Enum

class Anchor(Enum):
	CENTER       = 0,
	TOP_LEFT     = 1,
	TOP_RIGHT    = 2,
	BOTTOM_LEFT  = 3,
	BOTTOM_RIGHT = 4,

class HorizontalAlignment(Enum):
	LEFT   = 0,
	CENTER = 1,
	RIGHT  = 2

class VerticalAlignment(Enum):
	TOP	= 0,
	MIDDLE = 1,
	BOTTOM = 2

@dataclass
class Alignment():
	horizontal: HorizontalAlignment
	vertical: VerticalAlignment
