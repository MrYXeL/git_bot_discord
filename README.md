# Discord Casino Bot
Bot Discord de jeux de casino avec leaderboard.

## Description
Bot Discord de jeux de casino développé en Python. Les joueurs peuvent tenter leur chance sur différents jeux, gagner des crédits virtuels et grimper dans le classement global via un scoreboard persistant en base de données.

L'objectif de ce projet est d'apprendre à utiliser [`discord.py`][2] ainsi que de réussir un équilibrage d'aléatoire

*Projet personnel en cours de développement — nouvelles fonctionnalités à venir.*

## Fonctionnalités
- Jeux de casino : blackjack, slot machine (en cours)
- Système de crédits virtuels par joueur
- Scoreboard persistant via base de données [`SQLite`][1]

## Technologies
- [`Python 3.14`][3]
- [`discord.py`][2] — interaction avec l'API Discord
- [`SQLite`][1] — stockage des scores et données joueurs

## Installation
```
# Cloner le repo
git clone https://github.com/MrYXeL/git_bot_discord

# Installer les dépendances
pip install -r requirements.txt

# Lancer le bot
python main.py
```

## Configuration
Créer un fichier .env à la racine :
```
TOKEN=ton_token_ici
```

[1]: https://sqlite.org
[2]: discordpy.readthedocs.io/en/stable/
[3]: https://www.python.org
