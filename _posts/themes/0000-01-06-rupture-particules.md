---
layout: post
title: 'Matériaux granulaires avec rupture des particules'
category: themes
---

Quand les grains se cassent, un matériau granulaire change de nature : de nouveaux grains apparaissent, les vides se réorganisent et le matériau peut se tasser de façon spectaculaire. Modéliser cette rupture, grain par grain, reste un défi. J'y contribue en développant dans le code [Rockable]({{ site.baseurl }}{% link _posts/tools/0000-01-02-rockable.md %}) des particules **cassables**, faites d'éléments rigides liés entre eux.

#### Une couche compressible pour les tunnels profonds

À grande profondeur, la roche autour d'un tunnel peut se refermer lentement et surcharger le revêtement en béton. Pour l'Andra, une solution consiste à intercaler, côté roche, une couche de petits tubes creux en argile cuite : en se cassant, ils absorbent la déformation du terrain tout en limitant les efforts transmis au béton.

Dans la thèse CIFRE de Marta Stasiak (co-encadrée avec Gaël Combe, directeur, Pascal Villard et Jacques Desrues), nous avons construit un modèle 3D de ce matériau :

<img src="{{ site.baseurl }}/public/img/rupt_tube.jpg" alt="Tube réel et son modèle discret" style="display: block; margin: auto; max-width: 100%;" width="420px"/>
<p style="text-align: center; font-size: 0.85em;">Un tube d'argile cuite et son clone numérique, fait de 24 secteurs rigides collés.</p>

- chaque tube est un assemblage de 24 secteurs rigides (sphéro-polyèdres) collés entre eux, qui se séparent en traction ;
- la résistance des tubes et sa variabilité sont calibrées sur des essais d'écrasement de tubes isolés ;
- des milliers de tubes sont ensuite comprimés en œdomètre, comme lors des essais de laboratoire.

<img src="{{ site.baseurl }}/public/img/rupt_oedometre.jpg" alt="Simulation d'œdomètre et tubes cassés" style="display: block; margin: auto; max-width: 100%;" width="620px"/>
<p style="text-align: center; font-size: 0.85em;">Assemblage de tubes simulé dans l'œdomètre (gauche) et tubes réels cassés après compression (droite).</p>

**Ce que l'on en retient :** la très forte compressibilité vient de la rupture des grains, qui libère le vide intérieur des tubes. En séparant les deux porosités (à l'intérieur des tubes et entre eux), nous avons proposé un modèle simple qui prédit le tassement en fonction de la part de grains cassés, une base pour le dimensionnement en ingénierie.

#### Fragmentation à l'impact

Avec l'équipe de Montpellier (thèse de Duc-Chung Vu, CEA), une particule est représentée par un assemblage de cellules polyédriques dont les faces communes se rompent selon le critère de Griffith. Les simulations d'impact révèlent trois régimes selon l'énergie apportée : rebond élastique, endommagement sans fragmentation, puis fragmentation.

<img src="{{ site.baseurl }}/public/img/rupt_impact.jpg" alt="Particule cassable à l'impact" style="display: block; margin: auto; max-width: 100%;" width="620px"/>
<p style="text-align: center; font-size: 0.85em;">Particule modélisée par des cellules polyédriques (gauche) et exemples de rupture après impact (centre, droite).</p>

 Les formes des fragments obtenus sont très proches de celles mesurées en laboratoire et sur des échantillons lunaires.

#### Travaux en cours

- passage d'un milieu continu quasi-fragile à un empilement de fragments (avec l'Andra) ;
- modèle simplifié, inspiré de l'échelle des grains, pour les matériaux faits de particules creuses écrasables ;
- particules déformables et cassables dans Rockable (méthode des éléments discrets « compliants »), appliquées notamment à la rupture du bois.

#### Publications principales

- M. Stasiak, G. Combe, V. Richefeu, G. Armand, J. Zghondi (2022). *High compression of granular assemblies of brittle hollow tubular particles: investigation through a 3D discrete element model*, Computational Particle Mechanics. [`PDF`]({{ site.baseurl }}/public/pdf/CPMStasiak2021.pdf)
- M. Stasiak, V. Richefeu, G. Combe, J. Zghondi, G. Armand (2021). *High compressibility caused by particle breakage: a DEM investigation*, Powders & Grains 2021. [`PDF`]({{ site.baseurl }}/public/pdf/PG2021_Stasiak.pdf)
- D.-C. Vu, L. Amarsid, J.-Y. Delenne, V. Richefeu, F. Radjaï (2024). *Particle fracture regimes from impact simulations*, Physical Review E **109**, 044907. [`PDF`]({{ site.baseurl }}/public/pdf/ChungFracture.pdf)
