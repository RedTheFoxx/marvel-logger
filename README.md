# marvel-logger

## Qui suis-je ?

Conçu pour la collecte et la visualisation des statistiques Marvel Rivals d'un joueur, récupérées sur [Tracker.gg](https://tracker.gg/marvel-rivals), j'existe à des fins d'expérimentation. Les prochaines itérations permettront de réaliser des études corrélant statistiques de matches avec des notes de qualité de jeu.

## Commandes

| Commande | Description |
|----------|-------------|
| `/stats <pseudo>` | Overview du profil : rang, stats principales, rôles et top 3 héros (saison courante, plateforme IGN). |
| `/register <pseudo>` | Lie votre compte Discord à un pseudo Tracker.gg (jusqu'à 3 pseudos). Le profil doit exister sur Tracker.gg. |
| `/match [pseudo]` | Affiche les 5 derniers matchs classés puis un menu pour consulter le scoreboard détaillé. Sans pseudo : utilise le premier pseudo lié via `/register`. |
| `/feels [pseudo]` | Note le ressenti (1–10) de vos derniers matchs classés de la saison courante. Affiche un graphique de vos notes et un menu pour noter les matchs non encore évalués. Nécessite un pseudo lié via `/register` (le vôtre uniquement). Sans pseudo : utilise le premier pseudo lié. |
