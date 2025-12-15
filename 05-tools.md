---
layout: page
title: 'Outils numériques'
---

Les outils de simulation numérique que je développe en C++ se distinguent par leur simplicité de compilation et leur légèreté, grâce à une dépendance minimale aux librairies tierces. Conçus pour être à la fois performants et faciles à déployer, ces logiciels ont été éprouvés, améliorés et validés au fil de plusieurs travaux de thèse. 

Parmi ces outils, certains se sont révélés essentiels pour répondre à des enjeux scientifiques, parfois industriels, complexes. Il s'agit de :

<div class="posts">
  <ol>
  {% for post in site.categories.tools %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">
        {{ post.title }}
      </a>
    </li>
  {% endfor %}
</ol>
</div>

