"""
Construit le site du cours MS1 (HTML + vidéos) dans un dossier autonome :

    site_MS1/
      index.html      page du cours (résumés + vidéos)
      videos/  vignettes/

    python3 construire_site.py                  # rendu 720p puis génération dans ./site_MS1
    python3 construire_site.py --qualite h      # rendu 1080p60
    python3 construire_site.py --sans-rendu     # réutilise les vidéos déjà rendues
    python3 construire_site.py --sortie ~/depot/MS1   # écrit ailleurs
    python3 construire_site.py --zip            # crée aussi une archive .zip
"""

import argparse
import html
import shutil
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
DOSSIERS_QUALITE = {"l": "480p15", "m": "720p30", "h": "1080p60"}

CODE = "MS1"
TITRE = "Statique et efforts internes"
SOUS_TITRE = ("Forces, moments, équilibre, actions de liaison, efforts internes dans les poutres et treillis. "
              "Un résumé et des animations pour chaque notion.")
ORIGINE = "IUT Génie Civil – Construction Durable, Université Grenoble Alpes"

# (identifiant, titre, résumé HTML, [(fichier, scène, titre, description)])
CHAPITRES = [
    ("forces", "Forces", """
<p>Une force est définie par son intensité F (en newtons), sa direction et son sens. Pour calculer, on la remplace
par ses deux composantes suivant les axes : <i class="f">F<sub>X</sub> = F cos θ</i> et <i class="f">F<sub>Y</sub> = F sin θ</i>,
où θ est l'angle mesuré depuis l'axe X dans le sens trigonométrique. Les signes viennent alors d'eux-mêmes.</p>
<p>Si l'angle est donné par rapport à la verticale, le cosinus va au côté adjacent à l'angle. Si la direction est donnée
par une pente, on utilise directement les rapports de longueurs. La résultante de plusieurs forces s'obtient
en sommant les composantes.</p>""", [
        ("forces.py", "DecompositionForce", "Décomposer une force", "Composantes, signes, angle par rapport à la verticale, pente."),
        ("forces.py", "ResultanteForces", "Résultante de plusieurs forces", "Somme des composantes et quadrant de l'angle."),
    ]),
    ("moments", "Moment d'une force", """
<p>Le moment d'une force par rapport à un point O mesure sa capacité à faire tourner :
<i class="f">M<sub>/O</sub> = ± F × d</i>, où d est la distance entre O et la ligne d'action de la force (le bras de levier).
Il s'exprime en N·m. Il est positif si la force fait tourner dans le sens trigonométrique.</p>
<p>Pour une force inclinée, on additionne les moments de ses deux composantes. Le moment résultant dépend
du point choisi, sauf pour un couple : deux forces opposées et décalées ont le même moment en tout point.</p>""", [
        ("moments.py", "Intro", "Pourquoi le moment ?", "La clé de serrage, définition et convention de signe."),
        ("moments.py", "BrasDeLevier", "Le bras de levier", "Trouver le signe, puis la distance."),
        ("moments.py", "ForceInclinee", "Force inclinée", "Moment des deux composantes."),
        ("moments.py", "MomentResultant", "Moment résultant", "Le résultat dépend du point."),
        ("moments.py", "Couple", "Couple de forces", "Le même moment en tout point."),
    ]),
    ("pfs", "Principe fondamental de la statique", """
<p>Un solide est en équilibre si la somme des forces est nulle <i class="f">ΣF<sub>X</sub> = 0, ΣF<sub>Y</sub> = 0</i>
et si la somme des moments en un point quelconque est nulle <i class="f">ΣM<sub>/A</sub> = 0</i>.
Dans le plan, cela fournit trois équations. On a intérêt à écrire l'équation de moment au point où passent
le plus d'inconnues.</p>""", [
        ("pfs.py", "PFSPatate", "L'équilibre d'un solide", "Pourquoi il faut à la fois ΣF = 0 et ΣM = 0."),
        ("pfs.py", "PFSPoutreL", "Application à une structure en L", "Bras de levier vertical et réaction négative."),
    ]),
    ("liaisons", "Liaisons", """
<p>Une liaison bloque certains mouvements. Chaque mouvement bloqué crée une action inconnue, et chaque mouvement libre
une action nulle. On dessine les inconnues dans le sens positif : le signe du résultat donne le sens réel.</p>
<table><tr><th>Liaison</th><th>Mouvements bloqués</th><th>Inconnues</th></tr>
<tr><td>Appui simple</td><td>une translation</td><td>1</td></tr>
<tr><td>Articulation</td><td>deux translations</td><td>2 (X, Y)</td></tr>
<tr><td>Encastrement</td><td>deux translations et la rotation</td><td>3 (X, Y, C)</td></tr></table>""", [
        ("liaisons.py", "AppuiSimple", "L'appui simple", "Une inconnue, perpendiculaire au support."),
        ("liaisons.py", "Articulation", "L'articulation", "Deux inconnues."),
        ("liaisons.py", "Encastrement", "L'encastrement", "Deux forces et un couple."),
        ("liaisons.py", "LiaisonsBilan", "Récapitulatif", "Les trois liaisons côte à côte."),
    ]),
    ("actions", "Actions de liaison d'une poutre", """
<p>On isole la poutre, on remplace chaque liaison par ses inconnues, puis on vérifie qu'il y en a exactement trois
(poutre isostatique). On écrit ensuite l'équation de moment au point où passent le plus d'inconnues, puis les deux
équations de forces, et on contrôle le résultat avec un moment en un autre point.</p>
<p>Une charge répartie q se remplace par une force q × longueur, placée au milieu de la zone chargée.
Un couple appliqué intervient dans l'équation de moment, mais pas dans celles des forces.</p>""", [
        ("actions_liaison.py", "ReactionsMethode", "La méthode", "Articulation, appui simple et une force."),
        ("actions_liaison.py", "Isostatisme", "Compter les inconnues", "Isostatique, hyperstatique ou mécanisme."),
        ("actions_liaison.py", "ReactionsChargeRepartie", "Charge répartie", "Force équivalente d'une charge partielle."),
        ("actions_liaison.py", "ReactionsForceInclineeCouple", "Force inclinée et couple", "Composantes et couple appliqué."),
        ("actions_liaison.py", "ReactionsConsole", "Poutre encastrée", "Le couple d'encastrement."),
        ("actions_liaison.py", "ReactionsPorteAFaux", "Porte-à-faux", "Une réaction peut être négative."),
        ("actions_liaison.py", "ReactionsAppuiIncline", "Appui incliné", "Une inconnue de direction connue."),
        ("actions_liaison.py", "ReactionsPieges", "Erreurs fréquentes", "Les points à vérifier."),
    ]),
    ("coupure", "Efforts internes", """
<p>On coupe la poutre à une abscisse x et on étudie l'équilibre d'une des deux parties. La coupure fait apparaître
trois efforts internes : l'effort normal N, l'effort tranchant V et le moment fléchissant M. L'équilibre
de la partie isolée donne N(x), V(x) et M(x).</p>
<p>Les expressions changent à chaque force ponctuelle, appui, couple, et au début ou à la fin d'une charge répartie :
la poutre se découpe en tronçons. On peut garder la partie gauche ou la partie droite, et on choisit la plus simple.</p>""", [
        ("efforts_internes.py", "EffortsInternesIntro", "N, V et M", "Ce que représentent les efforts internes."),
        ("efforts_internes.py", "CoupureUnTroncon", "Un tronçon", "Poutre sous charge répartie."),
        ("efforts_internes.py", "CoupureDeuxTroncons", "Deux tronçons", "Force ponctuelle, partie gauche ou droite."),
        ("efforts_internes.py", "CoupureConsole", "Console encastrée", "Sans calculer les réactions."),
        ("efforts_internes.py", "CoupureAstuce", "Gauche ou droite", "Choisir la partie la plus simple."),
    ]),
    ("diagrammes", "Diagrammes des efforts internes", """
<p>Les diagrammes peuvent se tracer sans écrire les équations. L'effort normal N est constant entre deux forces
parallèles à la poutre : positif si la poutre est tirée, négatif si elle est poussée. L'effort tranchant V
se construit force par force, en balayant la poutre : chaque force ponctuelle crée un saut, une charge répartie une pente.</p>
<p>Le moment fléchissant vérifie <i class="f">V = −dM/dx</i> : les aires sous le diagramme de V donnent les variations de M,
et M est extrémal là où V s'annule.</p>""", [
        ("diagrammes.py", "DiagrammeN", "Effort normal", "Traction et compression."),
        ("diagrammes.py", "DiagrammeVPonctuelle", "Effort tranchant, forces ponctuelles", "Un saut par force."),
        ("diagrammes.py", "DiagrammeVRepartie", "Effort tranchant, charge répartie", "Une pente égale à q."),
        ("diagrammes.py", "DiagrammeMVelo", "Moment fléchissant et pente", "V donne la pente de M."),
        ("diagrammes.py", "DiagrammeMAires", "Moment fléchissant et aires", "M à partir des aires sous V."),
        ("diagrammes.py", "DiagrammesSynthese", "Exemple complet", "Porte-à-faux et charge partielle."),
    ]),
    ("treillis", "Treillis", """
<p>Un treillis est formé de barres articulées à leurs extrémités et chargées aux nœuds. Chaque barre ne transmet
qu'un effort normal, de traction ou de compression. Le degré d'hyperstaticité vaut <i class="f">H = b + r − 2n</i>
(barres, inconnues de liaison, nœuds).</p>
<p>Méthode des nœuds : on écrit l'équilibre de chaque nœud, en commençant par un nœud qui n'a que deux barres inconnues.
Méthode des sections : on coupe au plus trois barres, puis on écrit l'équilibre d'une des deux parties.</p>""", [
        ("treillis.py", "TreillisIntro", "Pourquoi des triangles ?", "Hypothèses, traction et compression."),
        ("treillis.py", "TreillisHyperstaticite", "Degré d'hyperstaticité", "Compter barres, nœuds et liaisons."),
        ("treillis.py", "TreillisMethodeNoeuds", "Méthode des nœuds", "Équilibre nœud par nœud."),
        ("treillis.py", "TreillisMethodeSection", "Méthode des sections", "Couper trois barres."),
        ("treillis.py", "TreillisPieges", "Erreurs fréquentes", "Les points à vérifier."),
    ]),
]

CSS = """
:root{--fond:#fff;--texte:#1a1a1a;--doux:#6b6b6b;--trait:#e6e6e6;--accent:#0b5c78}
@media (prefers-color-scheme:dark){:root{--fond:#121212;--texte:#e6e6e6;--doux:#9a9a9a;--trait:#2a2a2a;--accent:#7cc4dc}}
*{box-sizing:border-box}
body{margin:0;background:var(--fond);color:var(--texte);font:17px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.page{max-width:980px;margin:0 auto;padding:56px 20px 80px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
header{margin:0 0 48px}
.code{font-size:.85rem;letter-spacing:.12em;color:var(--doux)}
h1{font-size:2.2rem;font-weight:600;letter-spacing:-.01em;line-height:1.2;margin:4px 0 12px}
.intro{color:var(--doux);max-width:640px;margin:0}
.sommaire{list-style:none;padding:0;margin:0 0 24px;columns:2;column-gap:40px;counter-reset:c}
.sommaire li{counter-increment:c;padding:3px 0;break-inside:avoid}
.sommaire li::before{content:counter(c,decimal-leading-zero);color:var(--doux);font-variant-numeric:tabular-nums;margin-right:12px;font-size:.85rem}
section{border-top:1px solid var(--trait);padding-top:40px;margin-top:56px}
h2{font-size:1.45rem;font-weight:600;margin:0 0 16px}
h2 span{color:var(--doux);font-weight:400;font-variant-numeric:tabular-nums;margin-right:14px}
.resume{max-width:680px}.resume p{margin:0 0 12px}
sub{line-height:0}
.f{font-family:"STIX Two Text","Cambria Math",Georgia,serif;font-size:1.05em;white-space:nowrap}
table{border-collapse:collapse;margin:8px 0 4px;font-size:.95rem}
th{text-align:left;font-weight:600;color:var(--doux);font-size:.85rem}
td,th{padding:6px 24px 6px 0;border-bottom:1px solid var(--trait)}
.videos{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:32px 24px;margin-top:32px}
.videos video{width:100%;display:block;aspect-ratio:16/9;background:#000;border-radius:6px}
.videos h3{font-size:1rem;font-weight:600;margin:10px 0 2px}
.videos p{margin:0;color:var(--doux);font-size:.9rem}
footer{margin-top:80px;color:var(--doux);font-size:.85rem}
@media (max-width:600px){.page{padding-top:32px}h1{font-size:1.7rem}.sommaire{columns:1}}
"""


def page_html(titre, corps, description=""):
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{html.escape(description)}">
<title>{html.escape(titre)}</title><style>{CSS}</style></head>
<body><div class="page">{corps}</div></body></html>
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
                    "-vf", "scale=640:-1", "-q:v", "4", str(image)])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qualite", choices="lmh", default="m", help="l = 480p, m = 720p (défaut), h = 1080p60")
    ap.add_argument("--sans-rendu", action="store_true", help="ne pas relancer manim, utiliser les vidéos existantes")
    ap.add_argument("--sortie", default=f"site_{CODE}", help=f"dossier de sortie (défaut : site_{CODE})")
    ap.add_argument("--zip", action="store_true", help="créer aussi une archive .zip du dossier")
    a = ap.parse_args()

    sortie = (ICI / a.sortie).expanduser().resolve()
    for sous in ("videos", "vignettes"):
        shutil.rmtree(sortie / sous, ignore_errors=True)
        (sortie / sous).mkdir(parents=True)
    rep_q = DOSSIERS_QUALITE[a.qualite]
    manquantes, sections, sommaire, n_videos = [], [], [], 0

    for i, (ident, titre, resume, videos) in enumerate(CHAPITRES, 1):
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
            n_videos += 1
            cartes.append(f"""<figure style="margin:0">
<video controls playsinline preload="none" poster="vignettes/{scene}.jpg"><source src="videos/{scene}.mp4" type="video/mp4"></video>
<h3>{html.escape(t)}</h3><p>{html.escape(desc)}</p></figure>""")
        sommaire.append(f'<li><a href="#{ident}">{html.escape(titre)}</a></li>')
        sections.append(f"""<section id="{ident}"><h2><span>{i:02d}</span>{html.escape(titre)}</h2>
<div class="resume">{resume}</div><div class="videos">{''.join(cartes)}</div></section>""")

    corps = f"""<header><div class="code">{CODE}</div><h1>{TITRE}</h1><p class="intro">{SOUS_TITRE}</p></header>
<ol class="sommaire">{''.join(sommaire)}</ol>
{''.join(sections)}
<footer>{ORIGINE}. Animations réalisées avec Manim.</footer>"""
    (sortie / "index.html").write_text(page_html(f"{CODE} — {TITRE}", corps, SOUS_TITRE), encoding="utf-8")

    taille = sum(f.stat().st_size for f in sortie.rglob("*") if f.is_file()) / 1e6
    print(f"\nCours écrit dans {sortie}  ({n_videos} vidéos, {taille:.0f} Mo)")
    if manquantes:
        print("Vidéos manquantes :", ", ".join(manquantes))
    if a.zip:
        arch = shutil.make_archive(str(sortie), "zip", root_dir=sortie.parent, base_dir=sortie.name)
        print("Archive :", arch)


if __name__ == "__main__":
    main()
