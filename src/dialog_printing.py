#Projet : pyscape
#Auteurs : Rabta Souleymeine

from typing import Final, Dict 
import asyncio

# Tous les délais prédéfinies sont en millisecondes

DEFAULT_CHAR_DELAY : Final[int] = 32
PUNCTUATION_DELAYS : Final[Dict[str, int]] = {
	',' : 700,
	':' : 900,
	';' : 1100,
	'.' : 1200,
	'!' : 1000,
	'?' : 1000,
}

async def print_dialog(text : str, speed_multiplier : float = 1, newline : bool = True):
	for char in text:
		lookup_delay : int | None = PUNCTUATION_DELAYS.get(char)
		milis_delay : int = (lookup_delay if lookup_delay else DEFAULT_CHAR_DELAY)

		print(char, end='', flush=True)
		await asyncio.sleep((milis_delay / 1000) / speed_multiplier)
	if (newline):
		print()

async def print_sized_dialog(text: str,  max_line_length: int, speed_multiplier: float = 1, newline: bool = True):
	assert max_line_length > 0, f"'max_line_length' doit être supérieur à 0 : {max_line_length}"
	current_line_length: int = 0
	
	for char in text:
		lookup_delay : int | None = PUNCTUATION_DELAYS.get(char)
		milis_delay : int = (lookup_delay if lookup_delay else DEFAULT_CHAR_DELAY)

		print(char, end='', flush=True)
		if (current_line_length < max_line_length):
			current_line_length += 1
		if char == '\n':
			current_line_length = 0
		if current_line_length >= max_line_length and char == ' ':
			current_line_length = 0
			print()
		await asyncio.sleep((milis_delay / 1000) / speed_multiplier)
	if (newline):
		print()


