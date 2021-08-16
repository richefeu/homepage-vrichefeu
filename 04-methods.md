---
layout: page
title: 'Méthodes numériques'
---

Cette page donne une liste non-exhaustive des méthodes que j'utilise et développe dans mes recherches. Les descriptions sont assez sommaires.
Pour des aspects techniques sur différentes méthodes, voir [Computational Discrete Mechanics](https://richefeu.gitbook.io/cdm/) 

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/DEM_icon.png" alt="DEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p> Il s'agit ici de la méthode classique des éléments discrets. Le principal code que je maintiens est tri-dimensionnel avec des éléments en forme de sphéro-polyèdres (<i>R</i>-shapes). Il s'agit ici de la méthode pour laquelle mon expertise est la plus grande. Plus d'informations peuvent être trouvées dans la page dédiée au code de calcul <a href="{{ site.baseurl }}{% link _posts/tools/0000-01-02-rockable.md %}">Rockable</a>.</p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/LEM_icon.png" alt="LEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>La méthode des éléments sur réseau (LEM, Lattice Element Method) consiste à partitionner un milieu continu par un réseaux d'éléments interconnectés. Ces éléments sont dans la version la plus simple des ressorts ne pouvant transmettre qu'une force axiale élastique. Le réseau est régulier ou non, et la résolution numérique peut être statique ou dynamique (dans ce dernier cas, des masses doivent être attribuées aux nœuds de jonction entre les éléments). La possibilité de supprimer/désactiver un élément lorsque qu'il se rompt permet le développement de fissures diffuses ou concentrées, néanmoins une dépendance au maillage persiste.</p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/LBM_icon.png" alt="LBM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>La méthode de Boltzmann sur réseau (LBM, Lattice Boltzmann Method) est une méthode de dynamique des fluides. Elle résoud l'équation discrète de Boltzmann pour simuler le comportement de fluides au moyen d'un schéma de collision-propagation. Il exist différentes méthodes de résolution (BGK, MRT...), mais le principe général du procédé de collision et de propagation permet de reproduire des comportements complexes de fluides. Dans sa forme la plus simple, les équation de Navier-Stokes sont satisfaites même si elle ne font pas explicitement partie de la modélisation.
Il existe différentes solutions de modélisation pour obtenir une séparation de phases (même composants liquide/gaz ou multicomposant huile/eau).
</p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/FEM_Thumb.png" alt="FEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>La méthode des éléments finis (FEM, Finite Element Method), qu'il n'est plus nécessaire de présenter, est utilisée dans mes recherches essentiellement dans sa forme la plus simple. Il s'agit essentiellement de calculs en élasticité linéaire en petites déformations.</p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/FEMxDEM_icon.png" alt="FEMxDEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>
 Les méthodes numériques à double échelle constituent un outil efficace pour représenter simultanément la nature complexe des géomatériaux et traiter les problèmes d'ingénierie à l'échelle réelle, tels que l'excavation ou la pression, à un coût numérique raisonnable. Dans cette approche, une loi constitutive numérique basée sur des simulations DEM est intégrée dans une formulation FEM standard. Il est ainsi possible de considérer que le modèle constitutif, utilisé à chaque point de Gauss, résulte d'une homogénéisation numérique à grand nombre de degrés de liberté, plutôt que d'une relation mathématique. 
 </p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/MPM_Thumb.png" alt="MPM" width="150px"/>
</div>
<div style="width:80%;float:left;">
<p>
La méthode des points matériels (MPM, Material Point Method) est une méthode numérique pour la résolution de problèmes de mécanique des continuums qui a évolué à partir de la méthode des particules dans les cellules (PIC, Particle-In-Cell). La méthode résout la forme variationnelle de la conservation de la quantité de mouvement en discrétisant le continuum en points matériels et en utilisant une grille eulérienne de fond. La conservation de la masse pendant les simulations est satisfaite puisque la masse reste inchangée.
Une grille soujacente et fixe est utilisée pour projeter les informations portées par les points matériels et résoudre les équations du mouvement. Les solutions obtenues aux nœuds du maillage sont utilisées pour mettre à jour les informations portées par les points matériels. Cette interpolation/extrapolation entre le maillage fixe et les points matériels se fait à l'aide de fonctions de forme. Les points matériels peuvent traverser les éléments du maillage fixe, et les perturbations associées peuvent être significativement réduite au moyen de différentes techniques. 
</p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/MPM+DEM_icon.png" alt="MPM+DEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>
 Le code MPM utilisé pour mes études est une implémentation MPM améliorée qui comprend des caractéristiques telles que le fractionnement des points matériels une fois que la déformation des volumes individuels devient trop importante, l'utilisation de conditions limites de type DEM basées sur le chevauchement entre le volume du point matériel et la limite et l'utilisation de fonctions de forme d'ordre supérieur pour réduire les erreurs liées aux instabilités de croisement de cellules. Il est ainsi possible d'utiliser des modèles de contact et de frottement aux interfaces de zones rigides.
 </p>
</div>
</div>

<hr>

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/(MPM+DEM)xDEM_icon.png" alt="(MPM+DEM)xDEM" width="200px"/>
</div>
<div style="width:80%;float:left;">
 <p>Couplage...</p>
</div>
</div>



