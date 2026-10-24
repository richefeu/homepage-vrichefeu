---
layout: post
title: 'Avalanches rocheuses'
category: themes
---

Où s'arrêtera un bloc qui se détache d'une falaise ? Avec quelle énergie atteindra-t-il une route ou un ouvrage de protection ? Pour répondre à ces questions, je développe depuis mon arrivée au laboratoire 3SR (2008) des outils de simulation qui prennent en compte la forme réelle des blocs, en collaboration étroite avec Pascal Villard et Dominique Daudon.

#### Des blocs à la forme réaliste

Tout a commencé avec le projet européen Alcotra MASSA. Le code [Rockable]({{ site.baseurl }}{% link _posts/tools/0000-01-02-rockable.md %}) décrit les blocs par des sphéro-polyèdres, ce qui permet de représenter des formes quelconques. Il a été validé par des expériences de laboratoire menées à l'EPFL (équipe de Vincent Labiouse). Les paramètres de dissipation aux impacts ont été identifiés pendant le post-doctorat de Guilhem Mollon, et une comparaison avec des approches continues a été menée avec Claudio Scavia et Marina Pirulli.

<img src="{{ site.baseurl }}/public/img/ava_simulation.jpg" alt="Avalanche rocheuse simulée" style="display: block; margin: auto; max-width: 100%;" width="460px"/>
<p style="text-align: center; font-size: 0.85em;">Avalanche de blocs simulée sur une pente plane (gauche) et sur une pente ondulée (droite), colorée par la vitesse des blocs.</p>

#### Du laboratoire au terrain

La rencontre avec Pierre Plotto, dirigeant de l'entreprise IMSRN, a lancé trois thèses CIFRE :

- **Stiven Cuervo** : simulation d'avalanches rocheuses sur des topographies réelles complexes ;
- **Fabio Gracia** : couplage entre éléments discrets et méthode des points matériels (MPM), pour les sols qui subissent de très grandes déformations, comme l'impact d'un bloc sur un sol meuble ;
- **Bruna Garcia** : modèle de collision sur sols meubles et identification des paramètres sur des sites à risque, confrontée à des lâchers de blocs en vraie grandeur.

<img src="{{ site.baseurl }}/public/img/ava_blocs.jpg" alt="Blocs réels et leurs modèles numériques" style="display: block; margin: auto; max-width: 100%;" width="520px"/>
<p style="text-align: center; font-size: 0.85em;">Blocs photographiés sur le site d'essais de chute en vraie grandeur (haut) et leurs jumeaux numériques reconstruits par photogrammétrie (bas).</p>

Ces travaux ont aussi servi à analyser des événements réels, comme l'éboulement déclenché du mont Néron (2011) ou la rupture d'un barrage filtrant au Japon, et ont fait l'objet d'un ouvrage chez ISTE-Wiley (*Modeling Gravity Hazards from Rockfalls to Landslides*, 2016).

#### patatrac : la trajectographie pour l'ingénierie

Une simulation discrète complète est riche mais coûteuse. Pour l'étude d'un site, l'ingénieur a besoin de milliers de trajectoires calculées en quelques secondes. C'est l'objet de **patatrac** (*Patatrac !*, le bruit d'un caillou qui dévale la pente), un outil de trajectographie 3D en cours de développement, écrit en C++ sans dépendance :

- terrains réels (modèles numériques de terrain, maillages issus de photogrammétrie), découpés en zones aux propriétés propres ;
- lois de rebond déterministes, stochastiques, ou **apprises par un réseau de neurones** sur des milliers d'impacts simulés avec Rockable : la finesse des simulations discrètes au service d'un outil rapide ;
- calculs Monte-Carlo parallèles, cartes d'aléa (passages, arrêts, énergies, hauteurs) lisibles dans un SIG, et ouvrages de protection (écrans, filets, merlons) ;
- une interface graphique pour placer les points de départ et les ouvrages, et visualiser les résultats.

<img src="{{ site.baseurl }}/public/img/ava_patatrac.jpg" alt="Interface de patatrac" style="display: block; margin: auto; max-width: 100%;" width="680px"/>
<p style="text-align: center; font-size: 0.85em;">L'interface de patatrac : terrain coloré par la proportion de trajectoires qui y passent, pour 4000 blocs lâchés depuis plusieurs points.</p>

L'outil est validé sur des cas à solution analytique et confronté, sur une carrière, aux arrêts de blocs mesurés et aux simulations Rockable.

#### Publications principales

- V. Richefeu, G. Mollon, D. Daudon, P. Villard (2012). *Dissipative contacts and realistic block shapes for modeling rock avalanches*, Engineering Geology **149-150**, pp. 78-92. [`PDF`]({{ site.baseurl }}/public/pdf/Richefeu_et_al_2012.pdf)
- G. Mollon, V. Richefeu, P. Villard, D. Daudon (2015). *Discrete modelling of rock avalanches: sensitivity to block and slope geometries*, Granular Matter **17**(5), pp. 645-666. [`PDF`]({{ site.baseurl }}/public/pdf/GRMA2015.pdf)
- B. Garcia, V. Richefeu, J. Baroth, D. Daudon, P. Villard (2020). *Collision of shaped boulders with sand substrate investigated by experimental, stochastic and discrete approaches*, JGR Earth Surface **125**(11). [`PDF`]({{ site.baseurl }}/public/pdf/Garcia2020.pdf)
- B. Garcia, P. Villard, V. Richefeu, D. Daudon (2022). *Comparison of full-scale rockfall tests with 3D complex-shaped discrete element simulations*, Engineering Geology **310**, 106855. [`PDF`]({{ site.baseurl }}/public/pdf/C2ROP_EngGeol2022.pdf)
