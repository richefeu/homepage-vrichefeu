# treillis — Interface web (IHM)

Interface graphique HTML/JS pour l'étude des structures planes de barres :
**treillis** (nœuds articulés, effort normal seul) et **portiques** (nœuds rigides, N, V, M).
Saisie par tableaux ou au clic sur le schéma. Fonctionne entièrement dans le navigateur.

## Lancement

```bash
python3 -m http.server 8080   # puis ouvrir http://localhost:8080
```

## Structure

```
MS_treillis_pedago/
├── index.html
├── css/style.css          # styles communs aux applications MSolution + outils d'édition
├── js/
│   ├── physics.js         # sections (commun avec les applications poutre)
│   ├── truss.js           # solveur treillis/portique, degré, flambement, équilibre des nœuds
│   ├── render.js          # utilitaires SVG (identique dans les trois applications)
│   ├── render_truss.js    # schéma 2D, déformée, diagrammes N/V/M sur les barres
│   └── ui.js              # saisie, édition au clic, sauvegardes, exemples
├── logo-header.png
└── Logo_IUT1.svg
```
