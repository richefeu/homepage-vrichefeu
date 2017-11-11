---
layout: post
title: 'Avalanches rocheuses'
category: themes
---


Mon intérêt pour la modélisation des avalanches rocheuses date de mon arrivé au Laboratoire 3SR en septembre 2008. Le projet Européen Alcotra MASSA avait été monté en collaboration avec Pascal Villard et Dominique Daudon. Le travail initial a consisté à développer un outil DEM ayant pour particularité de tenir compte des formes complexes des blocs rocheux. Pour cela, la stratégie des Sphero-polyèdres a été adoptée et validée dans le cadre du projet Européen par comparaison avec des expériences de laboratoire menées à l’EPFL par l’équipe de Vincent Labiouse. L’identification des paramètres mécaniques de dissipation a été réalisée lors du post-doc de Guilhem Mollon pour des collisions sur substratum rigide. Une confrontation de simulations discrètes et continues a également été menée pour valider l’outil numérique et étudier l’influence d’une transition entre les pentes du chemin de propagation (Claudio Scavia et Marina Pirulli, Politecnico di Milano).

La rencontre de Pierre Plotto, chef de l’entreprise IMSRN, a permis d’initier un travail important sur la modélisation des avalanches rocheuses grâce au financement de trois thèses CIFRE. Dans la thèse de Stiven Cuervo la modélisation d’avalanches rocheuses sur topographies complexes a été développée. La thèse de Fabio Garcia (en cours) se focalise sur la modélisation continue de sols subissant de très grandes déformations (avalanches ou impact d’un bloc rigide sur un sol meuble) en développant un couplage entre les approches DEM et MPM. Plus récemment, la thèse de Bruna Garcia s’attache à définir un modèle de collision sur sols plastiques et à identifier les paramètres mécaniques sur les sites à risque.


<!--
En collaboration avec Pascal Villard. MASSA blabla

------

Un objectif de ce thème de recherche porte sur le développement d'outils de prédiction pour évaluer le danger (ou l'étudier _a posteriori_) liés aux chutes de blocs ou aux avalanches rocheuses. 

La méthode des éléments discrets est utilisée à cette fin avec des blocs dont la forme est modélisée avec la technique des sphéro-polyèdres (voir post [DEMbox](/methods/dembox)).

La phylosophie est d'accorder une très grande importance à la géométrie des blocs et du versant de propagation, et de simplifier autant que possible les loi de force. Toutefois, cette simplification ne concerne pas le bilan énergétique des collisions de sorte que les modes de dissipations soient au cœur des analyses résultant de la modélisation. 



### Identification des paramètres de collision <small>(Postdoc. Guilhem Mollon)</small>

Le premier travail qui a été réalisé a consistait à identifier 

XX
Avant de s'intéresser à un cas réel en contexte naturel, la pertinence du modèle a été évaluée en le confrontant aux résultats expérimentaux de Manzella et Labiouse (2009). Leurs expériences consistaient à mettre en place un assemblage de petites briques (d'une longueur de 3 cm et au nombre de 6000 à 10000), et de relâcher cet assemblage sur un biplan de manière à observer l'écoulement de la masse granulaire sur la pente et son dépôt sur le plan horizontal. L'estimation des paramètres de contact a été effectuée à partir d'expériences additionnelles utilisant les matériaux d'origine des expériences de Manzella et Labiouse (briques et support). Des essais de rebond de briques ont été réalisés, avec prises de vues par deux caméras rapides. Une analyse inverse des trajectoires de chute libre et de rebond a permis de définir un jeu de huit paramètres de contact (quatre paramètres pour le contact brique-pente, et quatre paramètres pour le contact inter-briques), qui ont ensuite été introduits dans la simulation de l'évènement complet. Les résultats de cette simulation (vitesses de propagation et de dépôt, forme et taille du dépôt granulaire) ont montré une excellente correspondance avec les résultats expérimentaux, et ont prouvé que le comportement collectif d'une masse granulaire en écoulement pouvait être modélisé à partir de lois de contact très simples calibrées sur des impacts isolés.
XX

### Etudes de cas réelles <small>(PhD Stiven Cuervo)</small>

TODO

### ??? <small>(PhD Bruna Da Silva Garcia)</small>

### Modélisation continue <small>(PhD Fabio Gracia)</small>
TODO

-->

