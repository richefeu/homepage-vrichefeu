---
layout: page
title: 'Outils numériques'
---

Je développe mes outils de simulation et de mesure en C++, avec une règle simple : **le moins de dépendances possible**. Ils se compilent sans peine, s'installent partout et s'intègrent facilement à d'autres codes. Ils sont libres, sur [GitHub](https://github.com/richefeu), et ont été éprouvés au fil de nombreuses thèses et collaborations, académiques comme industrielles.

{% assign outils = site.categories.tools | sort: 'rang' %}
{% for post in outils %}
<p><a href="{{ site.baseurl }}{{ post.url }}"><strong>{{ post.title }}</strong></a><br/>{{ post.resume }}</p>
{% endfor %}

#### Et aussi

Des outils plus spécialisés, nés d'un projet ou d'une thèse :

- [`d-tracker`](https://github.com/richefeu/d-tracker) : la version actuelle de tracker, dédiée au dispositif 1γ2ε ;
- [`PeanutVoxel`](https://github.com/richefeu/peanut) : détection des particules et des contacts dans des images de tomographie 3D ;
- [`cellyod`](https://github.com/richefeu/cellyod) : génération de tissus cellulaires végétaux (pavages de Voronoï et itérations de Lloyd), qui servent de microstructures pour la simulation mécanique ;
- [`SPICE`](https://github.com/richefeu/SPICE) : DEM 2D semi-périodique pour l'étude des interfaces granulaires (avec Cyrille Couture) ;
- [`fickle`](https://github.com/richefeu/fickle) : DEM 2D en cellule périodique, spécialisée dans l'analyse des fluctuations de déplacement ;
- [`buriedpipe`](https://github.com/richefeu/buriedpipe) : conduite enterrée dans un assemblage granulaire (DEM 2D) ;
- [`maplefloe`](https://github.com/richefeu/maplefloe) : dynamique de plaques de banquise (en développement) ;
- [`babyfem`](https://github.com/richefeu/babyfem) : une famille d'outils éléments finis 2D pédagogiques, de la grille structurée aux portiques ;
- **patatrac** : trajectographie 3D rapide des chutes de blocs (en développement, voir [Avalanches rocheuses]({{ site.baseurl }}{% link _posts/themes/0000-01-01-avalanches.md %})).
