---
layout: post
title: 'Matériaux granulaires à particules déformables'
category: themes
---

Cellules végétales, billes d'hydrogel, poudres pharmaceutiques ou alimentaires, grains d'argile qui gonflent à l'humidité : dans tous ces matériaux, les grains changent de forme. Les méthodes d'éléments discrets classiques, qui supposent des grains rigides, ne suffisent plus. Ce thème, le plus récent, vise à construire des modèles discrets où les grains se déforment, et à comprendre ce que cela change à l'échelle de l'assemblage.

#### Des particules « cœur-coquille »

Dans la thèse de Yohann Trivino (avec Farhang Radjaï, Komlanvi Lampoh et Jean-Yves Delenne, Montpellier), nous avons développé un modèle 2D, implémenté dans le code [l-hyphen](https://github.com/richefeu/l-hyphen), où chaque particule est une coquille faite de points matériels reliés par des liens élasto-plastiques, qui résistent à l'étirement et à la flexion, autour d'un cœur dont la rigidité représente le fluide qu'il contient. Le modèle a été vérifié sur des poutres fléchies et sur la compression d'une particule isolée.

<img src="{{ site.baseurl }}/public/img/def_modele.jpg" alt="Modèle de particule cœur-coquille" style="display: block; margin: auto; max-width: 100%;" width="480px"/>
<p style="text-align: center; font-size: 0.85em;">Une particule est une coquille de points reliés par des liens qui résistent à l'étirement (k<sub>s</sub>) et à la flexion (k<sub>b</sub>), autour d'un cœur de rigidité K<sub>Ω</sub> (gauche). Compression d'une particule sans (a) et avec (b) rigidité du cœur (droite).</p>

**Ce que l'on en retient :**

- lors de la compaction, les vides se referment surtout parce que les particules se **facettent** : elles deviennent polygonales ou allongées selon leur plasticité ;
- la porosité qui subsiste après déchargement, signature de la plasticité collective, varie de façon non monotone avec le seuil de plasticité des particules, contrairement à l'intuition ;
- le même modèle simule la rupture de tissus cellulaires, et sert à étudier des tissus végétaux (tige de maïs) à partir de leur structure réelle.

<img src="{{ site.baseurl }}/public/img/def_assemblages.jpg" alt="Compaction de particules déformables et rupture de tissus" style="display: block; margin: auto; max-width: 100%;" width="680px"/>
<p style="text-align: center; font-size: 0.85em;">Formes des particules après compaction selon la rigidité du cœur (η) et le seuil de plasticité de la coquille (γ) (gauche). Rupture en traction d'un tissu de cellules élastiques (centre) et plastiques (droite).</p>

#### Des grains qui gonflent et ramollissent

Certains grains (argiles, racines, polymères) gonflent et se ramollissent en absorbant de l'eau. Sous charge constante, un assemblage de tels grains se dilate puis se tasse, comme l'avaient montré des expériences antérieures. Avec Ilija Vego et Gioacchino Viggiani, un modèle discret volontairement simple, piloté par un seul paramètre, reproduit cette réponse dilatation-compaction.

<img src="{{ site.baseurl }}/public/img/def_gonflement.jpg" alt="Dilatation puis compaction de grains qui gonflent" style="display: block; margin: auto; max-width: 100%;" width="520px"/>
<p style="text-align: center; font-size: 0.85em;">Sous une force constante F, l'assemblage se dilate puis se compacte : expérience (a) et simulation discrète (b).</p>

#### Et aussi

- l'imagerie par tomographie de la compaction de billes d'hydrogel (voir [Micro-mécanique expérimentale]({{ site.baseurl }}{% link _posts/themes/0000-01-03-experimental.md %})) ;
- l'introduction d'éléments déformables dans le code [Rockable]({{ site.baseurl }}{% link _posts/tools/0000-01-02-rockable.md %}) (méthode des éléments discrets « compliants », travail de M. Singh Bisht).

#### Publications principales

- Y. Trivino, V. Richefeu, F. Radjaï, K. Lampoh, J.-Y. Delenne (2026). *A soft particle dynamics method based on shape degrees of freedom for core-shell particles*, Computer Physics Communications **321**, 110030. [`Online`](https://doi.org/10.1016/j.cpc.2026.110030)
- I. Vego, V. Richefeu, G. Felekis, A. Tengattini, G. Viggiani (2025). *A simple discrete approach to explore the response of swelling and softening particles*, Géotechnique Letters **15**(2). [`PDF`]({{ site.baseurl }}/public/pdf/Vego2025.pdf)
- Y. Trivino, V. Richefeu, F. Radjaï, K. Lampoh, J.-Y. Delenne (2024). *A new numerical model for the elasto-plastic behavior of cellular materials*, IS-Grenoble 2024. [`HAL`](https://hal.science/hal-04999048)
