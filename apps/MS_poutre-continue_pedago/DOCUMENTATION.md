# poutre-continue — Documentation IHM

## Méthode de calcul

1. **Réactions** : méthode des déplacements (éléments de poutre d'Euler-Bernoulli + barre),
   maillage d'environ 120 éléments, nœuds sur chaque liaison et chaque point de charge.
   Elle traite tous les cas : appuis multiples, encastrements, porte-à-faux, isostatique,
   section différente par travée (EI et EA par élément).
2. **Efforts N, V, M** : statique pure à partir de toutes les réactions (`computeAtX`,
   commun avec la poutre isostatique).
3. **Déformée u(x)** : déplacements nodaux du solveur, interpolés par les fonctions d'Hermite.
4. **Règle des trois moments (affichage pédagogique)** : même forme que l'application
   console `apps/poutre-continue` de MSolution :

   M₍ᵢ₋₁₎·Lᵢ/Iᵢ + 2·Mᵢ·(Lᵢ/Iᵢ + Lᵢ₊₁/Iᵢ₊₁) + Mᵢ₊₁·Lᵢ₊₁/Iᵢ₊₁ = −6·(Ωᵢᴿ/Iᵢ + Ωᵢ₊₁ᴸ/Iᵢ₊₁)

   avec Ωᴸ = (1/L)∫M₀(ξ)(L−ξ)dξ et Ωᴿ = (1/L)∫M₀(ξ)ξ dξ (M₀ : travée isolée sur deux appuis simples).
   Encastrement d'extrémité : 2·L₁·M_A + L₁·M_B = −6·Ω₁ᴸ. Si les sections diffèrent, tout est
   multiplié par I_réf = I₁ (longueurs réduites L′ = L·I_réf/I).
   Les moments affichés sont ceux du solveur ; l'application vérifie qu'ils satisfont ces équations.
   Cas non couverts par l'affichage (les résultats restent valables) : encastrement intérieur,
   couple appliqué sur un appui intérieur.

## Validation (25/10/2026)

| Cas | Attendu | Obtenu |
|---|---|---|
| 2 travées égales L, q | R = 3qL/8, 10qL/8 ; M_B = −qL²/8 | 15 / 50 / 15 kN ; −20 kN·m |
| 2 travées, P au milieu | M_B = −3PL/16 | −15 kN·m |
| Encastrée-appuyée, q | M_A = −qL²/8 | −31.25 kN·m |
| Bi-encastrée, P au milieu | M_A = M_B = −PL/8 | −10 kN·m |
| Isostatique, P au milieu | f = PL³/48EI | 0.0595 mm |
| Livre 4.5.1, 4.5.3 | trois moments à la main | identiques |

## Conventions

Mêmes conventions que la poutre isostatique : Fy vers le haut, Mz anti-horaire,
M(x) positif quand la fibre inférieure est tendue. Sauvegardes dans le navigateur sous
`msolution_continue_slots` (distinctes de la poutre isostatique).
