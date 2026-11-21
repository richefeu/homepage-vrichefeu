# poutre-continue — Interface web (IHM)

Interface graphique HTML/JS pour l'étude des poutres continues (hyperstatiques) :
appuis multiples, encastrements, porte-à-faux, section différente par travée.
Fonctionne entièrement dans le navigateur, sans serveur.

## Lancement

Ouvrir `index.html` directement dans un navigateur, ou servir le répertoire :

```bash
python3 -m http.server 8080   # puis ouvrir http://localhost:8080
```

## Structure

```
MS_poutre-continue_pedago/
├── index.html          # Point d'entrée
├── css/style.css       # Styles (mêmes que la poutre isostatique + carte Clapeyron)
├── js/
│   ├── physics.js      # Sections, statique, N/V/M, contraintes (commun avec la poutre isostatique)
│   ├── continuous.js   # Travées, solveur de rigidité, règle des trois moments
│   ├── render.js       # Rendu SVG (identique à la poutre isostatique)
│   └── ui.js           # Interactions, sauvegardes, exemples
├── logo-header.png     # Logo MSolution (en-tête)
└── Logo_IUT1.svg       # Logo IUT1
```

Voir `DOCUMENTATION.md` pour la méthode de calcul.
