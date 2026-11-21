"""
Construit un dossier autonome (HTML + vidéos) du cours MS2, à partager avec les collègues.

    python3 construire_site.py                  # rendu 480p (fichiers légers) puis génération du site
    python3 construire_site.py --qualite m      # rendu 720p (plus long, fichiers plus gros)
    python3 construire_site.py --sans-rendu     # réutilise les vidéos déjà rendues
    python3 construire_site.py --zip            # crée aussi site_MS2.zip

Le résultat est dans ./site_MS2/ : ouvrir index.html dans un navigateur (fonctionne hors ligne).
"""

import argparse
import html
import shutil
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
DOSSIERS_QUALITE = {"l": "480p15", "m": "720p30", "h": "1080p60"}

# (identifiant, titre du chapitre, référence poly, résumé HTML, [(fichier, scène, titre, description)])
CHAPITRES = [
    ("sections", "Caractéristiques des sections", "§1", """
<p>Le <b>barycentre</b> G d'une section composée de formes simples se trouve avec
<span class="f">Y<sub>G</sub> = Σ S<sub>i</sub> Y<sub>Gi</sub> / Σ S<sub>i</sub></span>, les hauteurs étant mesurées depuis le point
le plus bas de la section complète (un trou compte avec S<sub>i</sub> &lt; 0).</p>
<p>Le <b>moment quadratique</b> I<sub>GZ</sub> mesure la répartition de la matière autour de l'axe horizontal Z passant par G
(unité&nbsp;: cm<sup>4</sup> ou mm<sup>4</sup>)&nbsp;: <span class="f">b h<sup>3</sup>/12</span> pour un rectangle,
<span class="f">π D<sup>4</sup>/64</span> pour un disque.</p>
<ul>
<li>Doubler la hauteur multiplie I<sub>GZ</sub> par 8, doubler la largeur seulement par 2.</li>
<li>Théorème de Huygens&nbsp;: <span class="f">I<sub>GZ</sub> = Σ (I<sub>GiZ</sub> + d<sub>i</sub><sup>2</sup> S<sub>i</sub>)</span>,
avec d<sub>i</sub> = Y<sub>Gi</sub> − Y<sub>G</sub>.</li>
<li>Profilés&nbsp;: on lit A, y<sub>s</sub>, I<sub>y</sub>, I<sub>z</sub> dans le catalogue, dans la colonne qui correspond à l'orientation
(axes y, z du catalogue ≠ axes Y, Z du cours).</li>
</ul>""", [
        ("sections.py", "Barycentre", "Le barycentre d'une section", "Formes simples, sections composées, formule de Y_G."),
        ("sections.py", "BarycentreT", "Exemple : section en T", "Y_G = 9,5 cm, pièges et vérifications."),
        ("sections.py", "BarycentreEvidement", "Enlever de la matière", "Un trou compte négativement : Y_G = 5,5 cm."),
        ("sections.py", "MomentQuadratique", "Le moment quadratique", "Règle à plat / sur chant, b h³/12, effet de h³, disque."),
        ("sections.py", "Huygens", "Théorème de Huygens", "Transport d² S : section en T (884 cm⁴), section évidée (1288 cm⁴)."),
        ("sections.py", "ProfilesUPE", "Lire le catalogue (UPE 120)", "En C, en U, en ∩ : la bonne colonne et les unités."),
    ]),
    ("navier", "Contraintes normales : le diagramme de Navier", "§2.1", """
<p>La contrainte normale σ est une densité de force sur la section (MPa = N/mm²), positive en traction,
négative en compression&nbsp;: <span class="f">σ(x, y) = N(x)/S − M(x) y / I<sub>GZ</sub></span>
(y mesuré depuis G, vers le haut&nbsp;; M en N·mm, I<sub>GZ</sub> en mm<sup>4</sup>).</p>
<ul>
<li>N seul&nbsp;: σ uniforme = N/S. M seul&nbsp;: σ proportionnelle à y, nulle en G (fibre neutre).</li>
<li>Le diagramme de Navier est une droite&nbsp;: pente −M/I<sub>GZ</sub>, valeur N/S en G.
Les contraintes extrêmes sont en haut (y<sub>sup</sub>) et en bas (y<sub>inf</sub>) de la section.</li>
<li>Fibre neutre&nbsp;: σ(y<sub>0</sub>) = 0. Elle se déplace avec N et peut sortir de la section.</li>
<li>Allure rapide&nbsp;: M fait tourner l'axe vertical (↺ si M &gt; 0, ↻ si M &lt; 0), N le décale de N/S.</li>
</ul>""", [
        ("navier.py", "ContrainteNormale", "La contrainte normale", "σ = dF/dS, effet de N, effet de M (flexion), formule et unités."),
        ("navier.py", "DiagrammeNavier", "Le diagramme de Navier", "Section en T : N seul, M seul, superposition, fibre neutre."),
        ("navier.py", "NavierEnDirect", "Effet de N et de M", "La droite tourne avec M, se décale avec N."),
        ("navier.py", "NavierTableau", "Les 9 cas", "Allure du diagramme selon les signes de N et M."),
    ]),
    ("admissibles", "Contraintes admissibles et choix d'un profilé", "§2.2 – 2.5", """
<p>Une section résiste si toutes ses contraintes restent dans l'intervalle admissible
<span class="f">σ<sub>min</sub> &lt; σ &lt; σ<sub>max</sub></span> (σ<sub>max</sub> &gt; 0 en traction, σ<sub>min</sub> &lt; 0 en compression).
Il suffit de vérifier les fibres extrêmes, en haut (y<sub>sup</sub>) et en bas (y<sub>inf</sub>).</p>
<ul>
<li>Si une limite est dépassée&nbsp;: réduire la charge ou la portée, changer de matériau, augmenter h (I ∝ h³),
précontraindre (N &lt; 0) ou renforcer la zone tendue (armatures).</li>
<li>Section non symétrique&nbsp;: σ<sub>sup</sub> ≠ −σ<sub>inf</sub>&nbsp;; la fibre la plus éloignée de G est la plus sollicitée,
et l'orientation de la section compte.</li>
<li>Profilés&nbsp;: <span class="f">|σ| = |M| / w<sub>el,Z</sub></span> avec w<sub>el,Z</sub> = I<sub>GZ</sub> / max(−y<sub>inf</sub>, y<sub>sup</sub>)
(colonne W<sub>el,y</sub> ou W<sub>el,z</sub> selon l'orientation)&nbsp;; le signe se lit sur le dessin.</li>
<li>Choisir un profilé&nbsp;: <span class="f">(w<sub>el,Z</sub>)<sub>min</sub> = |M<sub>crit</sub>| / σ<sub>max</sub></span>,
puis la plus petite valeur supérieure dans la bonne colonne du catalogue.</li>
</ul>""", [
        ("admissibles.py", "ContraintesAdmissibles", "Contraintes admissibles", "Poutre en béton : le haut est trop tendu."),
        ("admissibles.py", "SolutionsRupture", "Éviter la rupture", "Les 5 solutions, en direct."),
        ("admissibles.py", "SectionNonSymetrique", "Section non symétrique", "Section en T, puis retournée : l'orientation compte."),
        ("admissibles.py", "NavierUPE", "UPE 120 et module de flexion", "En C et en ∩ : W_el,y, W_el,z, I_z."),
        ("admissibles.py", "ChoixProfile", "Choisir un profilé", "La méthode en 5 étapes avec le catalogue."),
    ]),
    ("deformee", "Déformée et flèche maximale", "§3", """
<p>La courbure de la poutre est proportionnelle au moment&nbsp;: <span class="f">M(x) = E I<sub>GZ</sub> × u<sub>y</sub>''(x)</span>
(E I<sub>GZ</sub>&nbsp;: rigidité en flexion). On intègre deux fois u<sub>y</sub>'' = M/(E I<sub>GZ</sub>)&nbsp;; chaque intégration
ajoute une constante, déterminée par les conditions aux limites.</p>
<ul>
<li>Appui ou articulation&nbsp;: u<sub>y</sub> = 0. Encastrement&nbsp;: u<sub>y</sub> = 0 et u<sub>y</sub>' = 0.
Entre deux tronçons&nbsp;: même déplacement et même pente.</li>
<li>Rotation&nbsp;: ω(x) = u<sub>y</sub>'(x) (petites rotations). Un tronçon sans moment reste droit.</li>
<li>Flèche&nbsp;: f = −u<sub>y</sub> (positive vers le bas)&nbsp;; f<sub>max</sub> au point où |u<sub>y</sub>| est maximal.
Console&nbsp;: <span class="f">Fℓ³/3EI</span> (force en bout), <span class="f">qℓ⁴/8EI</span> (charge répartie).</li>
<li>Dimensionner&nbsp;: isoler I<sub>GZ</sub> dans f<sub>max</sub> ≤ f<sub>adm</sub>, puis choisir le profilé dans la bonne colonne (I<sub>y</sub> ou I<sub>z</sub>).</li>
</ul>""", [
        ("deformee.py", "CourbureMoment", "Courbure et moment", "M = E I C, puis deux intégrations."),
        ("deformee.py", "ConditionsLimites", "Conditions aux limites", "Appui, encastrement, continuité entre tronçons."),
        ("deformee.py", "DeformeeConsoleRepartie", "Exemple 1 : console, charge répartie", "Déformée et rotation pas à pas."),
        ("deformee.py", "DeformeeConsoleForce", "Exemple 2 : console, force au milieu", "Deux tronçons et continuité en C."),
        ("deformee.py", "FlecheMax", "Flèche maximale", "Définition, formulaire, application à l'UPE 120."),
        ("deformee.py", "DimensionnementFleche", "Dimensionner avec la flèche", "I minimal puis choix dans le catalogue."),
    ]),
]

CSS = """
:root{--fond:#f7f7f5;--carte:#fff;--texte:#1d1d1f;--doux:#5f6368;--accent:#1f6f8b;--bord:#e2e2df}
@media (prefers-color-scheme:dark){:root{--fond:#16181b;--carte:#202328;--texte:#e8e8e6;--doux:#a4a8ae;--accent:#6cc3e0;--bord:#33373d}}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--fond);color:var(--texte);line-height:1.55}
header{padding:28px 20px 12px;max-width:1150px;margin:auto}h1{margin:0 0 4px;font-size:1.7rem}header p{margin:0;color:var(--doux)}
nav{position:sticky;top:0;z-index:5;background:var(--fond);border-bottom:1px solid var(--bord)}
nav div{max-width:1150px;margin:auto;padding:8px 16px;display:flex;gap:6px;flex-wrap:wrap}
nav a{color:var(--accent);text-decoration:none;font-size:.9rem;padding:3px 9px;border:1px solid var(--bord);border-radius:14px}
main{max-width:1150px;margin:auto;padding:0 16px 60px}section{margin-top:34px}
h2{font-size:1.35rem;margin:0 0 6px}h2 small{color:var(--doux);font-weight:400;font-size:.85rem;margin-left:8px}
.resume{background:var(--carte);border:1px solid var(--bord);border-radius:10px;padding:6px 18px;margin:10px 0 16px}
.f{font-family:"Cambria Math","STIX Two Math",Georgia,serif;background:rgba(127,127,127,.12);padding:1px 6px;border-radius:4px;white-space:nowrap}
table{border-collapse:collapse;margin:8px 0 12px}td,th{border:1px solid var(--bord);padding:4px 10px;text-align:left}
.grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:16px}
.video{background:var(--carte);border:1px solid var(--bord);border-radius:10px;overflow:hidden}
.video video{width:100%;display:block;background:#000;aspect-ratio:16/9}
.video div{padding:8px 12px 12px}.video h3{margin:0 0 3px;font-size:1rem}.video p{margin:0;color:var(--doux);font-size:.88rem}
.video a{font-size:.8rem;color:var(--accent)}footer{color:var(--doux);font-size:.85rem;text-align:center;padding:20px}
"""


def rendre(fichier, scene, qualite):
    cmd = [sys.executable, "-m", "manim", f"-q{qualite}", "--disable_caching", fichier, scene]
    print(f"  rendu {fichier} {scene} ...", flush=True)
    try:
        r = subprocess.run(cmd, cwd=ICI, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print(f"  !! {scene} : délai dépassé")
        return False
    if r.returncode != 0:
        print(f"  !! {scene} : échec\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
        return False
    return True


def vignette(video, image):
    try:
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(video)], capture_output=True, text=True).stdout.strip())
    except ValueError:
        d = 4.0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{0.6 * d:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", "scale=640:-1", str(image)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qualite", choices="lmh", default="l", help="l = 480p (défaut, fichiers légers), m = 720p, h = 1080p60")
    ap.add_argument("--sans-rendu", action="store_true", help="ne pas relancer manim, utiliser les vidéos existantes")
    ap.add_argument("--sortie", default="site_MS2", help="dossier de sortie (défaut : site_MS2)")
    ap.add_argument("--zip", action="store_true", help="créer aussi une archive .zip du dossier")
    a = ap.parse_args()

    sortie = ICI / a.sortie
    (sortie / "videos").mkdir(parents=True, exist_ok=True)
    (sortie / "vignettes").mkdir(exist_ok=True)
    rep_q = DOSSIERS_QUALITE[a.qualite]
    manquantes = []

    sections, nav = [], []
    for ident, titre, ref, resume, videos in CHAPITRES:
        print(f"== {titre}")
        cartes = []
        for fichier, scene, t, desc in videos:
            src = ICI / "media" / "videos" / Path(fichier).stem / rep_q / f"{scene}.mp4"
            if not a.sans_rendu:
                rendre(fichier, scene, a.qualite)
            if not src.exists():
                manquantes.append(f"{fichier} {scene}")
                continue
            # remux sans réencodage, index en tête (+faststart) : lecture immédiate en streaming, notamment sur téléphone
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c", "copy", "-movflags", "+faststart",
                            str(sortie / "videos" / f"{scene}.mp4")], check=True)
            vignette(src, sortie / "vignettes" / f"{scene}.jpg")
            cartes.append(f"""<article class="video">
<video controls playsinline preload="none" poster="vignettes/{scene}.jpg"><source src="videos/{scene}.mp4" type="video/mp4"></video>
<div><h3>{html.escape(t)}</h3><p>{html.escape(desc)}</p><a href="videos/{scene}.mp4" download>Télécharger</a></div></article>""")
        nav.append(f'<a href="#{ident}">{html.escape(titre)}</a>')
        sections.append(f"""<section id="{ident}"><h2>{html.escape(titre)}<small>{ref}</small></h2>
<div class="resume">{resume}</div><div class="grille">{''.join(cartes)}</div></section>""")

    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>MS2 — cours animé</title><style>{CSS}</style></head>
<body><header><h1>MS2 — Résistance des matériaux : sections, contraintes, flèches</h1>
<p>Résumé du cours et animations (IUT GCCD, BUT). Chaque vidéo se lit dans la page ou se télécharge.</p></header>
<nav><div>{''.join(nav)}</div></nav><main>{''.join(sections)}</main>
<footer>Animations réalisées avec Manim (manim.community).</footer></body></html>"""
    (sortie / "index.html").write_text(page, encoding="utf-8")

    taille = sum(f.stat().st_size for f in sortie.rglob("*") if f.is_file()) / 1e6
    print(f"\nSite écrit dans {sortie}  ({taille:.0f} Mo)")
    if manquantes:
        print("Vidéos manquantes :", ", ".join(manquantes))
    if a.zip:
        arch = shutil.make_archive(str(sortie), "zip", root_dir=sortie.parent, base_dir=sortie.name)
        print("Archive :", arch)


if __name__ == "__main__":
    main()
