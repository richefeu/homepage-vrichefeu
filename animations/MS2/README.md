# Animations Manim – MS2

| Fichier | Scènes | Poly |
|---|---|---|
| `sections.py` | `Barycentre`, `BarycentreT`, `BarycentreEvidement`, `MomentQuadratique`, `Huygens`, `ProfilesUPE` | §1 |
| `navier.py` | `ContrainteNormale`, `DiagrammeNavier`, `NavierEnDirect`, `NavierTableau` | §2.1 |
| `admissibles.py` | `ContraintesAdmissibles`, `SolutionsRupture`, `SectionNonSymetrique`, `NavierUPE`, `ChoixProfile` | §2.2–2.5 |
| `deformee.py` | `CourbureMoment`, `ConditionsLimites`, `DeformeeConsoleRepartie`, `DeformeeConsoleForce`, `FlecheMax`, `DimensionnementFleche` | §3 |
| `outils_ms2.py` | outils communs (ceux de MS1 + sections, repère ZY, point G, profilés UPE, tableau du catalogue, diagramme de Navier) | — |

## Contenu

- **Barycentre** : rectangle (diagonales), disque, profilé en I = 1 + 2 + 3, tube = 1 − 2, symétries,
  formule Y_G = Σ S_i Y_Gi / Σ S_i construite terme à terme sur la figure du poly
- **BarycentreT** : section en T (âme 2 × 12, table 12 × 2 cm) : Y_G1 = 6, Y_G2 = 13 (piège : pas 1 cm),
  Y_G = 9,5 cm ; vérifications (S_1 = S_2 ⇒ milieu de G_1G_2, Y_G ≠ h/2)
- **BarycentreEvidement** : rectangle 10 × 12 moins un trou 6 × 4 : S_2 = −24 cm², Y_G = 5,5 cm (G descend)
- **MomentQuadratique** : règle à plat / sur chant (poutres qui fléchissent), I = ∫ y² dS (bandes et barres y²),
  calcul de b h³/12, b et h modifiés en direct (h × 2 ⇒ I × 8 ; b × 2 ⇒ I × 2), règle : 8 vs 288 cm⁴ (× 36), disque π D⁴/64
- **Huygens** : rectangle qui s'éloigne de l'axe (I = 4 + 12 d² en direct), formule du poly,
  section en T : 582 + 302 = 884 cm⁴ ; section évidée : 1470 − 182 = 1288 cm⁴
- **ProfilesUPE** : UPE 120 dessiné à l'échelle (contour réel, G à y_s), axes y/z du catalogue ≠ Y/Z du cours,
  extrait du catalogue (UPE 80 à 140) ; en C : I_y = 364 cm⁴, Y_G = 60 mm ; en U : I_z = 55,5 cm⁴, Y_G = y_s = 19,8 mm ;
  en ∩ : I_z, Y_G = 40,2 mm ; × 6,6 pour le même poids ; piège des unités (mm⁴ × 10⁴ = cm⁴)
- **ContrainteNormale** : on coupe la poutre, σ = dF/dS (MPa = N/mm²), traction σ > 0 / compression σ < 0,
  N seul (σ = N/S uniforme), M seul (poutre qui fléchit : fibres raccourcies en haut, allongées en bas, fibre neutre),
  σ = N/S − M y / I_GZ, unités (piège kN·m → N·mm)
- **DiagrammeNavier** : section en T de §1 (S = 4800 mm², I_GZ = 884·10⁴ mm⁴), N = −48 kN, M = −4 kN·m :
  N seul (−10 MPa), M seul (0,452 y), somme : σ_sup = +10,4 MPa, σ_inf = −53,0 MPa, zones tendue / comprimée,
  fibre neutre y₀ = 22,1 mm, droite σ = (−M/I) y + N/S
- **NavierEnDirect** : N et M varient, valeurs en direct : M fait tourner la droite, N la décale, fibre neutre qui
  monte, qui sort de la section (tout comprimé) ou passe sous G
- **NavierTableau** : les 9 cas du poly construits pas à pas (colonne du milieu : N seul, ligne du milieu : M seul, coins)
- **ContraintesAdmissibles** : σ_min < σ < σ_max (zones interdites) ; poutre béton 200 × 400 mm (σ_max = +2,5,
  σ_min = −25 MPa), M_crit = −40 kN·m : σ_sup = +7,5 MPa > 2,5 ⇒ fissure en haut
- **SolutionsRupture** : les 5 remèdes en direct (valeurs vertes / rouges) : q ≤ 6,7 kN/m ou ℓ ≤ 2,3 m, σ_max ≥ 7,5 MPa,
  h = 700 mm, précontrainte N = −400 kN, armatures en partie haute
- **SectionNonSymetrique** : section en T, M = −4 kN·m, σ_max = +30 / σ_min = −60 MPa : +20,4 / −43,0 ✓ ;
  la même section retournée : σ_sup = +43,0 > 30 ✗ (l'orientation compte)
- **NavierUPE** : UPE 120, acier S235, M = −3 kN·m : en C ±49,5 MPa, w_el = I_GZ / max(−y_inf, y_sup) = W_el,y ;
  en ∩ : σ_inf = −217,4 (W_el,z, bord le plus éloigné), σ_sup = +107,0 MPa (I_z) ⇒ 4,4 fois plus sollicité
- **ChoixProfile** : méthode en 5 étapes (M_crit = −6 kN·m, σ_adm = ±160 MPa) : (w_el)_min = 37,5 cm³ ⇒ UPE 100 en C
  (vérif. 144,9 MPa) ; placé en U, aucun UPE de l'extrait ne convient
- **CourbureMoment** : poutre sur deux appuis qui fléchit, cercles osculateurs (R petit là où M est grand) face au
  diagramme de M ; M = E I C, E (matériau) et I (section), C ≈ u'' ; deux intégrations, constantes K₁, K₂
- **ConditionsLimites** : appui / articulation (u = 0, rotation libre), encastrement (u = 0 et u' = 0, tangente
  horizontale), continuité entre tronçons (saut ✗, cassure ✗, continue ✓)
- **DeformeeConsoleRepartie** : exemple 1 du poly : coupure (partie droite), intégrations, A₁ = A₂ = 0, u_y et ω,
  déformée animée, u_y(ℓ) = −qℓ⁴/8EI, diagramme de ω(x)
- **DeformeeConsoleForce** : exemple 2 du poly : M_g et M_d = 0, intégrations sur 2 tronçons, continuité en C
  (B₁ = −Fℓ²/8EI, B₂ = −Fℓ³/24EI), déformée : tronçon d rectiligne (tangente en C), piège du x local
- **FlecheMax** : f = −u_y, f_max des deux exemples, formulaire des 4 cas classiques, application numérique :
  console UPE 120, ℓ = 3 m, q = 1 kN/m : 13,2 mm en C, 86,9 mm en U
- **DimensionnementFleche** : pourquoi limiter la flèche (confort, ELS, désordres, voisins) ; console P = 2 kN,
  L = 2 m, f_adm = L/200 : (I_GZ)_min = 254 cm⁴ ⇒ UPE 120 en C (f = 7,0 mm), aucun en U ; vérification des contraintes

## Vidéos MP4 (Chamilo)

```sh
manim -qh sections.py Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE
manim -qh navier.py   ContrainteNormale DiagrammeNavier NavierEnDirect NavierTableau
manim -qh admissibles.py ContraintesAdmissibles SolutionsRupture SectionNonSymetrique NavierUPE ChoixProfile
manim -qh deformee.py CourbureMoment ConditionsLimites DeformeeConsoleRepartie DeformeeConsoleForce FlecheMax DimensionnementFleche
# -> media/videos/<fichier>/1080p60/*.mp4   (-ql pour un aperçu rapide)
```

⚠️ Lancer les rendus **l'un après l'autre** (deux `manim` en parallèle se gênent dans le dossier Tex).
Si une scène plante, `manim` peut rester bloqué : l'arrêter avec Ctrl-C.
Le préambule LaTeX de manim ne charge pas `xcolor` : colorier avec `color=` / `tex_to_color_map`, pas `\textcolor`.

## Diaporama en cours (manim-slides)

```sh
manim-slides render -qh sections.py Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE
manim-slides present Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE
# Espace / → : étape suivante,  ← : étape précédente,  F : plein écran,  Q : quitter
```

Export HTML autonome (reveal.js) :

```sh
manim-slides convert Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE sections.html --one-file
```

Chaque `self.etape()` dans le code = une pause (fin de diapo en mode slides, 1 s d'attente en vidéo).

## Site à partager (résumé du cours + vidéos)

```sh
python3 construire_site.py              # rendu 480p de toutes les scènes + génération de site_MS2/ (≈ 18 Mo)
python3 construire_site.py --qualite m  # 720p (plus long, plus lourd)
python3 construire_site.py --sans-rendu # réutilise les vidéos déjà rendues
python3 construire_site.py --zip        # crée aussi site_MS2.zip
```

Les résumés et l'ordre des vidéos se modifient dans la liste `CHAPITRES` du script.
