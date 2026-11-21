# poutre — Interface web (IHM)

Interface graphique HTML/JS pour la saisie et la visualisation de poutres isostatiques.  
Fonctionne entièrement dans le navigateur, sans serveur.

## Lancement

Ouvrir `index.html` directement dans un navigateur, ou servir le répertoire :

```bash
python3 -m http.server 8080   # puis ouvrir http://localhost:8080
```

## Structure

```
IHM/poutre/
├── index.html        # Point d'entrée
├── css/style.css     # Styles
├── js/
│   ├── physics.js    # Calculs mécaniques
│   ├── render.js     # Rendu SVG/canvas
│   └── ui.js         # Interactions utilisateur
├── logo-header.png   # Logo MSolution (en-tête)
└── Logo_IUT1.svg     # Logo IUT1
```

Voir `DOCUMENTATION.md` pour le détail de l'architecture JS et des formats de données.
