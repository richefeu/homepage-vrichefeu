# poutre — Documentation IHM

Interface graphique HTML/CSS/JS pour l'analyse de poutres isostatiques.

---

## Architecture

### Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | Structure de la page, chargement des modules |
| `css/style.css` | Mise en page et thème visuel |
| `js/physics.js` | Calculs mécaniques (réactions, N/V/M, déformée) |
| `js/render.js` | Rendu SVG : schéma de la poutre, diagrammes |
| `js/ui.js` | Gestion des événements, formulaires, import/export JSON |

### Format de données JSON

Les configurations de poutre peuvent être sauvegardées et chargées via un fichier JSON.
Le fichier `SAE1.3.json` illustre le format utilisé.

---

## Fonctionnalités

- Saisie graphique de la poutre (longueur, section, liaisons, chargements)
- Calcul des réactions d'appui
- Diagrammes interactifs N(x), V(x), M(x)
- Export SVG des résultats
- Import/export de configurations JSON

---

## Conventions

Mêmes conventions physiques que l'application console `apps/poutre` :
- Longueurs en mètres, forces en Newton, moments en N·m
- Axe x horizontal (gauche → droite), axe z vertical (bas → haut)
- M(x) positif = sagging (fibre inférieure en traction)
