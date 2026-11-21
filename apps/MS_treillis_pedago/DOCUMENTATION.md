# treillis — Documentation IHM

## Méthode

Méthode des déplacements, comme l'application console `apps/treillis` de MSolution :
- **treillis** : éléments barre (2 DDL/nœud), N = EA/L·Δℓ ; un encastrement agit comme une articulation ;
- **portique** : éléments poutre-colonne (3 DDL/nœud), K = Tᵀ·k·T ;
- réactions R = K·U − F ; mécanisme détecté par un pivot nul.

Degré d'hyperstaticité : h = b + r − 2n (treillis), h = 3b + r − 3n − c + f (portique),
c étant le nombre de rotules en bout de barre et f le nombre de nœuds dont toutes les barres sont articulées.

### Ajouts du 25/10/2026

- **Rotules en extrémité de barre** (portique) : condensation statique de la rotation libérée
  (k′ = k_ff − k_fR·k_RR⁻¹·k_Rf) ; la rotation propre de la barre est recalculée pour la déformée.
  Un nœud dont toutes les barres sont articulées perd son degré de liberté de rotation.
- **Matériau par section** : E, masse volumique ρ, contrainte limite f (valeurs indicatives :
  acier S235, aluminium, béton C25 en compression, bois C24 en flexion, ou valeurs saisies).
- **Charges réparties uniformes** sur les barres (portique, composantes globales par mètre de barre) et
  **poids propre** ρ·g·A (réparti sur les barres en portique, moitié à chaque nœud en treillis).
  Forces nodales équivalentes d'une barre bi-encastrée ; N, V, M exacts le long de la barre ;
  déformée exacte (Hermite + solution particulière), sans maillage supplémentaire.
- **Contrainte maximale** σ_max = |N|/A + |M|_max·v/I et taux σ_max/f.
- Exemples 11 et 12 : portiques sous charge répartie (encastré ; traverse articulée).
- Exemples 13 et 14 : presse de flexion IUT (bâti + poutre béton, F + poids propre ; éprouvette en treillis de Howe).

Affichages pédagogiques : barres colorées (traction / compression / effort nul), équilibre de chaque
nœud (ΣFx, ΣFy chiffrés, treillis), contrainte σ = N/A, flambement d'Euler N_cr = π²·E·I_min/L²
(barre bi-articulée), diagrammes N, V, M le long des barres (portique ; M côté fibres tendues).

Conventions : N > 0 en traction ; V, M en début et fin de barre, repère local de n1 vers n2 ;
M > 0 tend les fibres à droite du sens de parcours. Charges aux nœuds, et charges réparties
uniformes sur les barres en portique.

## Validation (25/10/2026)

| Cas | Attendu | Obtenu |
|---|---|---|
| Triangle (tests/treillis_triangle) | N_AC = N_BC = −7.071, N_AB = 5 kN | identique |
| Potence | N_AC = −15, N_BC = 18.03 kN | identique |
| Warren (exos/warren_truss) | R = 20 / 20 kN, équilibre des nœuds | résidu ~1e−11 N |
| Console IPE 300 (exos/console_IPE) | M_A = 150 kN·m, v = −25.7 mm | 150, −25.6 mm |
| Poutre bi-appuyée (tests/bi_appuye) | v = −0.339 mm, M = 12 kN·m | identique |
| Cadre sans diagonale | mécanisme | détecté |
| Console, q uniforme | v = −qL⁴/8EI = −1.429 mm | identique |
| Portique à traverse bi-articulée, q | M = qL²/8, poteaux M = 0, h = 1 | identique |
| Treillis décrit en portique tout articulé | = treillis, h = 0 | identique |
| Poids propre (treillis) | ΣR = ρ·g·A·ΣL | identique |
| Portique encastré, q sur la traverse | coin (qL²/12)·2/(2+k) = 9,70 (sans déf. axiale) | 9,685 ; mi-portée 10,315 |
| Presse IUT, F = 50 kN (presse.tex §5) | h = 0 ; 25 / 20 / 7,5 / 25 / 12,5 | identique, δv = 1,682 mm comme avec des bielles |
| Éprouvette Howe n = 6, F = 100 kN | FL/4z = 180,7 ; (F/2)/sin θ = 78,3 kN | identique |

## Sauvegardes

Clés `msolution_treillis_*` (distinctes des applications poutre), export `msolution_treillis.json`.
