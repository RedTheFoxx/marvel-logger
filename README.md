# marvel-logger

Bot Discord qui affiche les statistiques Marvel Rivals d'un joueur, récupérées sur [Tracker.gg](https://tracker.gg/marvel-rivals).

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Copiez `.env.example` vers `.env` et renseignez `DISCORD_TOKEN` (et optionnellement `DISCORD_GUILD_ID`).

## Lancement

```bash
python app.py
```

## Commandes

| Commande | Description |
|----------|-------------|
| `/stats <pseudo>` | Overview du profil : rang, stats principales, rôles et top 3 héros (saison courante, plateforme IGN). |
