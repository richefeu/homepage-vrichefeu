---
layout: page
title: 'Outils numériques'
---

Parmi les outils numériques que le développe, certains ont pris une importance particulière. Il s'agit de :

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

