---
layout: page
title: 'Méthodes numériques'
---

Pour des aspects techniques sur différentes méthodes, voir [Computational Discrete Mechanics](https://richefeu.gitbook.io/cdm/) 

<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/DEM_icon.png" alt="DEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p> Il s'agit ici de la méthode classique des éléments discrets. Le principal code que je maintiens est tri-dimensionnel avec des éléments en forme de sphéro-polyèdres (<i>R</i>-shapes). Il s'agit ici de la méthode pour laquelle mon expertise est la plus grande. Plus d'informations peuvent être trouvées dans la page dédiée au code de calcul <a href="{{ site.baseurl }}{% link _posts/tools/0000-01-02-rockable.md %}">Rockable</a>.</p>
</div>
</div>


<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/LEM_icon.png" alt="LEM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>La méthode des éléments sur réseau (LEM, Lattice Element Method) consiste à partitionner un milieu continu par un réseaux d'éléments interconnectés. Ces éléments sont dans la version la plus simple des ressorts ne pouvant transmettre qu'une force axiale élastique. Le réseau est régulier ou non, et la résolution numérique peut être statique ou dynamique (dans ce dernier cas, des masses doivent être attribuées aux noeuds de jonction entre les éléments). La possibilité de supprimer/désactiver un élément lorsque qu'il se rompt permet le développement de fissures diffuses ou concentrées, néanmoins une dépendance au maillage persiste.</p>
</div>
</div>


<div style="width:100%;height:200px">
<div style="width:20%;float:left;">
 <img src="{{ site.baseurl }}/public/img/LBM_icon.png" alt="LBM" width="150px"/>
</div>
<div style="width:80%;float:left;">
 <p>Lattice Boltzmann Method ...</p>
</div>
</div>





