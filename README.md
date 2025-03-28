# Pyscape - Trophée NSI 2025
#### (proposition **temporaire** de nom)
"*py*" pour Python et "*scape*" pour escape, ou "escape sequence" (voir `src/escape_sequences.py`)
## Prévu
- [ ] Système de dialogue
- [ ] Boutons fonctionnels
- [ ] Simulation de fluides
- [ ] Simulation de tissu (apparamment assez simple)
- [ ] Calculatrice complète
- [ ] Moteur de rendu 3D simple et modulable
- [ ] Petit jeu 2D (platformer ou autre)

### Propositions
- Outil de bureautique (tableur, traitement de texte) ?
- Un module qui raconterait l'histoire des terminaux sous forme de "vidéo" interactive et animée directement dans le terminal

# Lancement
Il suffit de lancer `main.py` dans le dossier `src/` avec

	python -OO src/main.py

si le chemin de python est ajouté au PATH, sinon remplacer par le chemin absolu ou relatif de python.

Pour quitter : `ALT + E`

On notera l'option -OO pour "**O**ptimization", qui s'est montrée utile pour ce programme. On peut également constater une utilisation de la mémoire réduite.

Sur Windows, la seul dépendance est la librairie [pywin32](https://pypi.org/project/pywin32/) couplé à une version de Windows 10 datant d'après 2015.
Une version de python ultérieur ou égale à 3.10 est requise.
