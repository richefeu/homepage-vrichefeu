---
layout: page
title: 'Méthodes'
---

<div class="posts">
   <ol>
   {% for post in site.categories.methods %}
     <li>
      <a href="{{ site.baseurl }}{{ post.url }}"> {{ post.title }} </a> 
      {% if post.image != 'none' %}
      <br/>
      <img src="{{ site.baseurl }}{{ post.image }}" alt="image" height="100" />
      {% endif %}
      </li>
   {% endfor %}
   </ol>
</div>
