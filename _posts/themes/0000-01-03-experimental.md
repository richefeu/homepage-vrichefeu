---
layout: post
title: 'Micro-mécanique expérimentale'
category: themes
mathjax: true
---

Les simulations discrètes ne valent que si on peut les confronter à ce qui se passe réellement à l'échelle des grains. Depuis mon arrivée au laboratoire 3SR, je mène donc aussi des expériences où chaque grain est suivi individuellement, en collaboration avec Gaël Combe et Cino Viggiani.

#### Suivre chaque grain

Le dispositif \\(1\gamma2\varepsilon\\) du laboratoire sollicite un assemblage de rouleaux, analogue 2D d'un sol granulaire, selon des chemins de chargement aussi complexes que l'on veut. Des photographies très haute résolution sont prises tout au long de l'essai. L'outil [Tracker]({{ site.baseurl }}{% link _posts/tools/0000-01-01-tracker.md %}), développé pour ces essais, mesure le déplacement et la rotation de chacun des grains sans en perdre un seul.

<img src="{{ site.baseurl }}/public/img/exp_1g2e_forces.jpg" alt="Assemblage de grains 2D et réseau de forces de contact" style="display: block; margin: auto; max-width: 100%;" width="680px"/>
<p style="text-align: center; font-size: 0.85em;">Assemblage de rouleaux de Schneebeli dans le dispositif 1γ2ε (gauche) et réseau des forces de contact déduit des images (droite, épaisseur des traits proportionnelle à la force normale).</p>

**Ce que l'on en retient :**

- **Fluctuations.** Même quand l'échantillon se déforme de façon homogène, chaque grain s'écarte du mouvement moyen. Ces fluctuations ont des propriétés statistiques proches de celles de la turbulence des fluides, alors que leur origine physique est tout autre : les grains s'excluent mutuellement. Avec Allbens Atman, ces mesures ont permis la validation expérimentale d'une loi d'échelle prédite par Constantino Tsallis.
- **Forces de contact.** Peut-on « voir » les forces entre les grains à partir de leurs seuls mouvements ? Dans la thèse de Mathias Tolomeo (co-encadrée avec Jean-Noël Roux), nous avons combiné les mesures d'images et des calculs par éléments discrets pour reconstruire le réseau des forces de contact.

#### En cours : des grains qui s'écrasent

Que devient un empilement quand ses grains, au lieu d'être rigides, se déforment jusqu'à combler les vides ? Kamilia Ayed (LMGC, Montpellier) a comprimé près de 400 billes d'hydrogel millimétriques dans un microtomographe à rayons X, en collaboration avec Serge Mora, Saeid Nezamabadi et Jean-Yves Delenne. Une méthode de traitement d'images dédiée, baptisée *peanut*, retrouve chaque bille et chacun de ses contacts, même lorsque les billes très déformées se confondent sur les images.

<img src="{{ site.baseurl }}/public/img/exp_hydrogel.jpg" alt="Compaction de billes d'hydrogel imagée par tomographie" style="display: block; margin: auto; max-width: 100%;" width="680px"/>
<p style="text-align: center; font-size: 0.85em;">L'échantillon de billes d'hydrogel (gauche) et les billes identifiées une à une à différents niveaux de compaction Φ (droite).</p>

On suit ainsi la forme des billes, leurs surfaces de contact et le réseau de contacts, qui change nettement de nature vers 80 % de compacité. Ces travaux sont en cours de publication.

#### En cours : le frottement des contacts sous faible charge

La loi de Coulomb suppose un coefficient de frottement constant, quelle que soit la force qui presse deux surfaces l'une contre l'autre. Mais qu'en est-il quand cette force devient très faible, comme entre des grains presque déchargés ?

Avec Luc Sibille, nous avons conçu un dispositif simple et peu coûteux : un contrepoids allège la pièce supérieure pour mesurer le frottement sous des forces normales quasi nulles, et un capteur relié à une carte Arduino enregistre l'effort de glissement. Des essais à la boîte de Casagrande complètent la gamme vers les fortes charges.

<img src="{{ site.baseurl }}/public/img/exp_frottement.jpg" alt="Dispositif de mesure du frottement sous faible charge" style="display: block; margin: auto; max-width: 100%;" width="560px"/>
<p style="text-align: center; font-size: 0.85em;">Principe du dispositif (gauche) : la force normale est réglée par une masse ajoutée ou un contrepoids ; l'effort tangentiel T est appliqué progressivement. Le dispositif réalisé (droite).</p>

Premiers résultats : la loi de Coulomb reste une bonne approximation sous charge modérée ou forte, mais le frottement augmente nettement quand la force normale devient faible. Une loi de frottement qui en tient compte, introduite dans un code DEM, modifie le déclenchement de la rupture diffuse lorsque le matériau est entraîné vers de faibles pressions, une situation proche de la liquéfaction des sols. Ces travaux sont en cours de publication.

#### Publications principales

- V. Richefeu, G. Combe, G. Viggiani (2012). *An experimental assessment of displacement fluctuations in a 2D granular material subjected to shear*, Géotechnique Letters **2**, pp. 113-118. [`PDF`]({{ site.baseurl }}/public/pdf/Fluct_GeoLetters.pdf)
- G. Combe, V. Richefeu, M. Stasiak, A.P.F. Atman (2015). *Experimental validation of a nonextensive scaling law in confined granular media*, Physical Review Letters **115**, 238301. [`PDF`]({{ site.baseurl }}/public/pdf/PRL2015.pdf)
- M. Tolomeo, V. Richefeu, G. Combe, J.-N. Roux, G. Viggiani (2020). *An assessment of discrete element approaches to infer intergranular forces from experiments on 2D granular media*, International Journal of Solids and Structures **187**, pp. 48-57. [`PDF`]({{ site.baseurl }}/public/pdf/Tolomeo_accepted_IJSS.pdf)
- V. Richefeu, G. Combe (2020). *The Particle Image Tracking technique: an accurate optical method for measuring individual kinematics of rigid particles*, Strain. [`PDF`]({{ site.baseurl }}/public/pdf/Tracker.pdf)
