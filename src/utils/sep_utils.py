#Projet : pyscape
#Auteurs : Rabta Souleymeine

# Contient des fonctions pratiques considérées comme racourcie ne dépendant d'aucun objet ou fichier

import re

def split_preserve(sep: str, string: str) -> list[str]:
    """Similaire à str.split() mais préserve les séparateur dans la liste générées."""
    # Merci à ce post pour nous avoir permis d'utiliser la magie des "regular expressions" 
    # https://medium.com/@shemar.gordon32/how-to-split-and-keep-the-delimiter-s-d433fb697c65
    return re.split(f"(?=[{sep}])|(?<=[{sep}])", string)

