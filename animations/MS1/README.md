# Animations Manim – MS1

| Fichier | Scènes | Poly |
|---|---|---|
| `forces.py` | `DecompositionForce`, `ResultanteForces` | §1.1 |
| `moments.py` | `Intro`, `BrasDeLevier`, `ForceInclinee`, `MomentResultant`, `Couple` | §1.2–1.3 |
| `pfs.py` | `PFSPatate`, `PFSPoutreL` | §1.4 |
| `liaisons.py` | `AppuiSimple`, `Articulation`, `Encastrement`, `LiaisonsBilan` | §2 |
| `actions_liaison.py` | `ReactionsMethode`, `Isostatisme`, `ReactionsChargeRepartie`, `ReactionsForceInclineeCouple`, `ReactionsConsole`, `ReactionsPorteAFaux`, `ReactionsAppuiIncline`, `ReactionsPieges` | §2–3 |
| `efforts_internes.py` | `EffortsInternesIntro`, `CoupureUnTroncon`, `CoupureDeuxTroncons`, `CoupureConsole`, `CoupureAstuce` | §4.2 |
| `diagrammes.py` | `DiagrammeN`, `DiagrammeVPonctuelle`, `DiagrammeVRepartie`, `DiagrammeMVelo`, `DiagrammeMAires`, `DiagrammesSynthese` | §4.3 |
| `treillis.py` | `TreillisIntro`, `TreillisHyperstaticite`, `TreillisMethodeNoeuds`, `TreillisMethodeSection`, `TreillisPieges` | §5 |
| `outils_ms1.py` | outils communs (grille, forces, cotes, flèches de rotation, symboles de liaisons, classe `Base`) | — |

## Contenu

- **DecompositionForce** : F_X = F cos θ, F_Y = F sin θ, force qui tourne (signes en direct) ;
  pièges : angle par rapport à la verticale, direction donnée par une pente 3/4/5
- **ResultanteForces** : exemple du poly (3 forces), résultante, piège de l'arctan (quadrant)
- **Intro** : clé de serrage, effet de la distance, ligne d'action passant par O, M = ±F×d, N·m, signes
- **BrasDeLevier** : exemple du poly, signe (barre imaginaire OA) puis d → −4 kN·m ; OA ≠ d
- **ForceInclinee** : décomposition F_X, F_Y → −2 kN·m, vérification avec la vraie distance
- **MomentResultant** : 4 forces sur une poutre, ΣM_O ≠ ΣM_B, point P mobile
- **Couple** : +2ℓF en A, B, C, O puis point P mobile (constant)
- **PFSPatate** : 1 force (translation), 2 forces alignées (équilibre), couple (rotation malgré ΣF = 0),
  3 forces concourantes (triangle des forces fermé), énoncé du PFS
- **PFSPoutreL** : structure en L (articulation A, appui B, P = 4 kN, F = 2 kN horizontale, Q = 1 kN) :
  isoler, ΣM_A (bras de levier = hauteur 3 m ≠ AC), Y_B = 4,5 kN, X_A = −2 kN (sens réel), Y_A = 0,5 kN,
  vérification ΣM_B = 0 (3 forces à moment nul en B)
- **AppuiSimple / Articulation / Encastrement** : mouvements libres/bloqués animés,
  actions de liaison (1, 2, 3 inconnues), appui incliné à 45°
- **LiaisonsBilan** : tableau récapitulatif
- **ReactionsMethode** : la méthode en 5 étapes (articulation + appui, P = 12 kN)
- **Isostatisme** : 3 inconnues = isostatique ; 4 = hyperstatique ; 2 = mécanisme (la poutre part)
- **ReactionsChargeRepartie** : charge partielle, F_eq = q × longueur chargée au milieu de la zone
- **ReactionsForceInclineeCouple** : décomposition (pente 3/4/5), F_X sur l'axe ⇒ moment nul,
  couple « tel quel » dans ΣM et absent de ΣF, X_A négatif
- **ReactionsConsole** : encastrement (X, Y, C) ; encastrement à droite ⇒ C négatif
- **ReactionsPorteAFaux** : plongeoir du poly, Y_A < 0 (l'articulation retient), effet de levier
- **ReactionsAppuiIncline** : 1 inconnue R_B de direction connue, X_A ≠ 0 avec des charges verticales
- **ReactionsPieges** : check-list des pièges
- **EffortsInternesIntro** : on coupe la poutre, N / V / M (traction, glissement, flexion), conventions de signe
- **CoupureUnTroncon** : exemple 1 du poly (q sur L) : coupure, qx à x/2, PFS, diagrammes V et M, M max = qL²/8
- **CoupureDeuxTroncons** : exemple 2 du poly (F en C, a = 4, b = 2, F = 6 kN) : tronçons, x depuis le début
  du tronçon, partie gauche puis partie droite, diagrammes (saut de V, pic de M)
- **CoupureConsole** : console avec P et H, partie droite (sans réactions), N = +3 (traction), M(0) = −20 kN·m
- **CoupureAstuce** : effort = −[gauche] = +[droite], check-list des pièges
- **DiagrammeN** : N intuitif (on tire = traction, on pousse = compression), constant par tronçon,
  exemple avec F_X (traction puis compression), balayage, poteau (N = −P)
- **DiagrammeVPonctuelle** : balayage de droite à gauche (exemple du poly, F au milieu), retour à 0
- **DiagrammeVRepartie** : q sur L, descente progressive de pente q, position où V = 0 (b = |V_b|/q)
- **DiagrammeMVelo** : V = −M', M = 0 aux extrémités libres, astuce du vélo (F au milieu, puis q)
- **DiagrammeMAires** : M(X) = −(aire à gauche) = +(aire à droite) ; M_max = qL²/8 par l'aire du triangle
- **TreillisIntro** : triangle indéformable vs rectangle, hypothèses, barre = biellette (seul N), tendue / comprimée
- **TreillisHyperstaticite** : H = b + r − 2n (exemple du poly, H = 0), barre en trop (H = 1), mécanisme (H = −1)
- **TreillisMethodeNoeuds** : console en bois du poly (F = 7 kN) : nœud B (N₁ = 7, N₂ ≈ −9,9 kN), nœud C (N₃ = 7), vérif. en A
- **TreillisMethodeSection** : treillis à 6 travées du poly : coupure des barres 10-11-12, ΣM en E, N₁₂ = −4F,
  N₁₁ = −F/√2, N₁₀ = 9F/2
- **TreillisPieges** : check-list des pièges et astuces
- **DiagrammesSynthese** : porte-à-faux + charge partielle (q = 3 kN/m, P = 3 kN) : V puis M pas à pas

## Vidéos MP4 (Chamilo)

```sh
manim -qh moments.py  Intro BrasDeLevier ForceInclinee MomentResultant Couple
manim -qh pfs.py      PFSPatate PFSPoutreL
manim -qh liaisons.py AppuiSimple Articulation Encastrement LiaisonsBilan
manim -qh forces.py   DecompositionForce ResultanteForces
manim -qh actions_liaison.py ReactionsMethode Isostatisme ReactionsChargeRepartie \
    ReactionsForceInclineeCouple ReactionsConsole ReactionsPorteAFaux ReactionsAppuiIncline ReactionsPieges
manim -qh efforts_internes.py EffortsInternesIntro CoupureUnTroncon CoupureDeuxTroncons CoupureConsole CoupureAstuce
manim -qh treillis.py TreillisIntro TreillisHyperstaticite TreillisMethodeNoeuds TreillisMethodeSection TreillisPieges
manim -qh diagrammes.py DiagrammeN DiagrammeVPonctuelle DiagrammeVRepartie DiagrammeMVelo DiagrammeMAires DiagrammesSynthese
# -> media/videos/<fichier>/1080p60/*.mp4   (-ql pour un aperçu rapide)
```

⚠️ Lancer les rendus **l'un après l'autre** (deux `manim` en parallèle se gênent dans le dossier Tex).
Si une scène plante, `manim` peut rester bloqué : l'arrêter avec Ctrl-C.

## Diaporama en cours (manim-slides)

```sh
manim-slides render -qh pfs.py PFSPatate PFSPoutreL
manim-slides present PFSPatate PFSPoutreL
# Espace / → : étape suivante,  ← : étape précédente,  F : plein écran,  Q : quitter
```

Export HTML autonome (reveal.js) :

```sh
manim-slides convert PFSPatate PFSPoutreL pfs.html --one-file
```

Chaque `self.etape()` dans le code = une pause (fin de diapo en mode slides, 1 s d'attente en vidéo).

## Site web (résumé du cours + vidéos)

```sh
python3 construire_site.py                   # rendu 720p de toutes les scènes + génération dans site_MS1/
python3 construire_site.py --qualite h       # 1080p60 (plus long, plus lourd)
python3 construire_site.py --sans-rendu      # réutilise les vidéos déjà rendues
python3 construire_site.py --sortie ~/depot/MS1   # écrit dans un autre dossier
python3 construire_site.py --zip             # crée aussi une archive .zip
```

`site_MS1/` contient `index.html` (résumés et vidéos, mode sombre automatique), `videos/` et `vignettes/`.
Il fonctionne hors ligne. Les résumés et l'ordre des vidéos se modifient dans la liste `CHAPITRES` du script.
