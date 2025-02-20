#Projet : pyscape
#Auteurs : Rabta Souleymeine, Benhassine Jilan

#Annotations permet de faire référence à une classe directement dans ses méthodes, il va remplacer le type par un string type : 'Vec3', 
#Puis Python fait le taff pour interpréter tous ça !
from __future__ import annotations 
from dataclasses import dataclass
import math
from decimal import Decimal


@dataclass
class RGB:
	r: int 
	g: int
	b: int

@dataclass
class Coord:
	"""
	Classe de données simple représentant un couple de valeur x et y.
	On peu l'utiliser comme vecteur, coordonnées, dimmensions, ou quoique ce soit qui puisse être représenté par une abscisse et une ordonnée.
	Elle seront représentées par des entiers uniquement, puique nous sommes dans la grille du terminal. 
	"""
	x : int
	y : int


class Vec3d:
	def __init__(self, x: int | float, y: int | float, z: int | float):
		self.x = x
		self.y = y
		self.z = z

	@classmethod
	def from_unit(cls, unit: int | float):
		"""Permet de construire un Vec3d à partir d'une seule valeur"""
		return cls(unit, unit, unit)
	
	def __add__(self, v: Vec3d):
		"""Additionne un autre vecteur ou un scalaire à ce vecteur.
        Args:
            other (Vec3d) : Le vecteur à additionner.

        Returns:
            Vec3d : Le résultat de l'addition.
		"""
		return Vec3d(self.x + v.x, self.y + v.y, self.z + v.z)
	
	def __neg__(self) -> Vec3d:
		"""Applique la négation à un Vec3d

		Args:
			v (Vec3d):

		Returns:
			Vec3d: Le vecteur inversé d'un vecteur initial
		"""
		return Vec3d(-self.x, -self.y, -self.z)

	def __sub__(self, v: Vec3d) -> Vec3d:
		"""Opération de soustraction du Vec3d

		Args:
			v (Vec3d): 

		Returns:
			Vec3d: Retourne la soustraction de ce Vec3d avec v
		"""
		return self + (-v)
	
	def __rsub__(self, other: Vec3d) -> Vec3d:
		"""Permet la soustraction dans l'autre sens (scalaire - vecteur).

		Args:
			v (Vec3d): 

		Returns:
			Vec3d: Retourne la soustraction de 2 Vec3d
		"""
		return other.__sub__(self)
	
	def __mul__(self, other):
		if isinstance(other, Vec3d):
			return Vec3d(self.x * other.x, self.y * other.y, self.z * other.z)
		else:
			return Vec3d(self.x * other, self.y * other, self.z * other)

	# Même chose qu'avec le __radd__ en fait l'opération par la droite !
	def __rmul__(self, other : int | float):
		"""Permet la multiplication dans l'autre sens (scalaire * vecteur).

        Args:
            other (int | float) : Le scalaire à multiplier.

        Returns:
            Vec3d : Le résultat de la multiplication.
        """
		return self.__mul__(other)
	
	def __truediv__(self, other):
		"""Opération de division du Vec3d

		Args:
			v (_type_): _description_

		Returns:
			_type_: La divison de 2 Vec3 entre eux
		"""

		# On regarde si le résultat de la division est entier pour conserver le type int
		if isinstance(other, Vec3d):
			is_division_round: bool = (
				self.x / other.x % 1 == 0
				and self.y / other.y % 1 == 0 
				and self.z / other.z % 1 == 0)
			if is_division_round:
				return Vec3d(int(self.x / other.x), int(self.y / other.y), int(self.z / other.z))
			else:
				return Vec3d(self.x / other.x, self.y / other.y, self.z / other.z)
		else:
			# https://stackoverflow.com/questions/3886402/how-to-get-numbers-after-decimal-point
			is_division_round: bool = self.x / other % 1 == 0
			if is_division_round:
				return Vec3d(int(self.x / other), int(self.y / other), int(self.z / other))
			else:
				return Vec3d(self.x / other, self.y / other, self.z / other)
	
	def normalize(self):
		"""
		Normalise un vecteur donné, c'est-à-dire le convertit en un vecteur unitaire
		(de norme 1) tout en conservant sa direction.

		Formule mathématique :
			v̂ = v / ||v||

			où :
			- v̂ est le vecteur normalisé
			- v est le vecteur d'origine
			- ||v|| est la norme du vecteur v, définie par :
			||v|| = sqrt(x² + y² + z²)

		Args:
			v (Vec3d): Le vecteur à normaliser.

		Returns:
			Vec3d: Le vecteur normalisé (unitaire).

		Raises:
			ZeroDivisionError: Si la norme du vecteur est nulle (vecteur nul).
		"""

		norm = self.norm()
		if norm == 0:
			raise ZeroDivisionError("Impossible de normaliser un vecteur nul.")
		return self / norm

	@staticmethod
	def cross(v1: Vec3d, v2: Vec3d) -> Vec3d:
		"""Calcule le produit vectoriel (cross product) entre deux vecteurs en 3D.

		Le produit vectoriel de deux vecteurs A et B donne un troisième vecteur C,
		perpendiculaire aux deux premiers

		Args:
			v1 (Vec3d): Premier vecteur.
			v2 (Vec3d): Deuxième vecteur.

		Returns:
			Vec3d: Le vecteur résultant du produit vectoriel.

		Exemple:
			>>> v1 = Vec3d(1, 0, 0)
			>>> v2 = Vec3d(0, 1, 0)
			>>> Vec3d.cross(v1, v2)
			Vec3d(0, 0, 1)

		Schéma:
			Produit vectoriel : A × B = C

                B (0,1,0)
                |      
                |      
                |______ A (1,0,0)
               / 
              /

				C (0,0,1)  ⬆
		"""

		x = v1.y * v2.z - v1.z * v2.y
		y = v1.z * v2.x - v1.x * v2.z
		z = v1.x * v2.y - v1.y * v2.x

		# On regarde si le résultat de la division est entier pour conserver le type int
		is_division_round: bool = (x % 1 == 0 and y % 1 == 0 and z % 1 == 0)
		if (is_division_round):
			return Vec3d(int(x), int(y), int(z))
		else:
			return Vec3d(x, y, z)

	def __str__(self) -> str:
		"""Retourne une représentation textuelle du vecteur.

        Returns:
            str : Représentation sous la forme 'Vec3d(x, y, z)'.
        """
		return f"Vec3d({self.x}, {self.y}, {self.z})"

	def norm(self) -> float:
		"""Calcule la norme du Vecteur ( donc sa taille )
		Ici on utilise math.sqrt directement implémenté en C
		Returns:
			_type_: Un float qui représente la norme du vecteur
		"""
		return math.sqrt(self.x**2 + self.y**2 + self.z**2)
	
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
