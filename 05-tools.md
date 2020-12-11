---
layout: page
title: 'Outils numériques'
---

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

