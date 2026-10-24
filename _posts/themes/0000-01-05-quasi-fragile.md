---
layout: post
title: 'Matériaux quasi-fragiles'
category: themes
---

Le béton ou les roches ne cassent pas d'un coup : une multitude de micro-fissures apparaît avant qu'une fissure franche ne se forme. Pour suivre ce processus, j'utilise la [méthode des éléments sur réseau]({{ site.baseurl }}/04-methods/) (LEM) : le matériau est représenté par un réseau d'éléments qui se rompent un à un, et sa mésostructure (granulats, matrice, interfaces, vides) est décrite explicitement. Ce thème est né de deux collaborations, avec Yann Malécot et avec Frédéric Dufour.

#### Le béton sous chargements extrêmes

Comment réagit une enceinte de réacteur ou un barrage à l'impact d'un projectile ? Le béton y subit des compressions triaxiales très intenses, que les essais en vraie grandeur ne permettent guère d'explorer car ils sont coûteux et difficiles à instrumenter.

Dans la thèse d'Ewa Piotrowska (co-encadrée avec Yann Malécot), des simulations LEM dynamiques en 2D, à l'échelle des granulats, ont permis d'étudier l'effet de confinements extrêmes (jusqu'à 650 MPa) et celui de la mésostructure : forme et taille des granulats, proportion de vides.

#### D'où vient la longueur interne du matériau ?

Les modèles d'endommagement utilisés en ingénierie ont besoin d'une « longueur interne » pour donner des résultats indépendants du maillage. Mais quelle valeur lui donner, et à quoi correspond-elle physiquement ?

Dans la thèse de Huu Phuoc Bui (co-encadrée avec Frédéric Dufour), des essais de traction simulés en LEM, en suivant les ruptures lien par lien, ont permis de relier la largeur de la zone de fissuration (*fracture process zone*) à la mésostructure.

<img src="{{ site.baseurl }}/public/img/qf_fissures_lem.jpg" alt="Fissuration simulée par la méthode des éléments sur réseau" style="display: block; margin: auto; max-width: 100%;" width="680px"/>
<p style="text-align: center; font-size: 0.85em;">Fissures simulées dans des éprouvettes entaillées pour quatre tailles d'inclusions (rouge : inclusions, gris : matrice). Les éléments rompus apparaissent en noir (macro-fissure) et en bleu (micro-fissures).</p>

**Ce que l'on en retient :**

- sur de grandes éprouvettes, la zone de fissuration est proportionnelle à la taille maximale des granulats ;
- l'espacement entre les inclusions caractérise mieux le matériau que leur taille ;
- cette zone dépend aussi de la géométrie de l'éprouvette : ce n'est donc pas une propriété intrinsèque du matériau, une mise en garde utile pour qui veut calibrer un modèle non local.

Un couplage « bord à bord » entre éléments finis (à grande échelle) et LEM (là où la fissure se développe) a également été proposé, pour simuler de grandes structures à un coût raisonnable.

#### Publication principale

- H.P. Bui, V. Richefeu, F. Dufour (2021). *Microstructural dimension involved in the damage of concrete-like materials: an examination by the lattice element method*, International Journal of Damage Mechanics. [`PDF`]({{ site.baseurl }}/public/pdf/IJDM_HPBui_2021.pdf)
