"""
MS2 - Outils de dessin communs aux animations Manim (repris de MS1 : grille, forces, cotes,
flèches de rotation, liaisons, panneau de texte, classe de base Slide/Scene ;
ajoutés pour MS2 : sections, barycentre, repère ZY, profilés UPE).
"""

from manim import *
import numpy as np

try:
    from manim_slides import Slide as _Base
except ImportError:  # sans manim-slides : simple vidéo
    class _Base(Scene):
        def next_slide(self, *args, **kwargs):
            pass


# ---------------------------------------------------------------------------
# Couleurs et tailles
# ---------------------------------------------------------------------------
C_FORCE = RED
C_FX = RED
C_FY = BLUE_C
C_BARRE = GREY_A
C_LEVIER = YELLOW
C_POS = GREEN
C_NEG = ORANGE
C_POINT = WHITE

FS_TITRE = 44
FS_TEXTE = 32
FS_EQ = 38


# ---------------------------------------------------------------------------
# Outils de dessin
# ---------------------------------------------------------------------------
class Grille:
    """Grille du poly : 1 graduation = 1 m (ou 1 kN pour les forces)."""

    def __init__(self, x0, x1, y0, y1, origine, s=1.0):
        self.x0, self.x1, self.y0, self.y1 = x0, x1, y0, y1
        self.o = np.array([origine[0], origine[1], 0.0])
        self.s = s

    def p(self, x, y):
        return self.o + self.s * np.array([x, y, 0.0])

    def mob(self):
        g = VGroup()
        for x in range(self.x0, self.x1 + 1):
            g.add(Line(self.p(x, self.y0), self.p(x, self.y1)))
        for y in range(self.y0, self.y1 + 1):
            g.add(Line(self.p(self.x0, y), self.p(self.x1, y)))
        g.set_stroke(GREY_D, width=1.5)
        return g


class Decimal(DecimalNumber):
    """DecimalNumber avec une virgule décimale (notation française)."""

    def _get_num_string(self, number):
        return super()._get_num_string(number).replace(".", ",")


def T(texte, **kw):
    """Texte (LaTeX) aligné à gauche."""
    kw.setdefault("font_size", FS_TEXTE)
    return Tex(texte, tex_environment="flushleft", **kw)


def ligne_live(prefixe, f, unite=r"\mathrm{kN\cdot m}", fs=FS_EQ, decimales=1):
    """« prefixe  valeur  unité » où la valeur est recalculée par f() à chaque image."""
    v = Decimal(f(), num_decimal_places=decimales, include_sign=True, font_size=fs)
    g = VGroup(MathTex(prefixe, font_size=fs), v,
               MathTex(unite, font_size=fs)).arrange(RIGHT, buff=0.15)

    def maj(m):
        m.set_value(f()).next_to(g[0], RIGHT, buff=0.15)
        g[2].next_to(m, RIGHT, buff=0.15)
    v.add_updater(maj)
    return g


def force(debut, fin, couleur=C_FORCE, epaisseur=7):
    return Arrow(
        debut, fin, buff=0, color=couleur, stroke_width=epaisseur,
        max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=12,
    )


def fleche_sens(centre, signe, r=0.45, couleur=None):
    """Flèche circulaire : signe > 0 -> sens trigo (positif), sinon horaire."""
    if couleur is None:
        couleur = C_POS if signe > 0 else C_NEG
    if signe > 0:
        arc = Arc(radius=r, start_angle=-PI / 4, angle=1.5 * PI, arc_center=centre)
    else:
        arc = Arc(radius=r, start_angle=5 * PI / 4, angle=-1.5 * PI, arc_center=centre)
    arc.set_stroke(couleur, width=6)
    arc.add_tip(tip_length=0.2, tip_width=0.2)
    arc.get_tip().set_color(couleur)
    return arc


def cote(p1, p2, texte, cote_label=None, couleur=C_LEVIER, fs=FS_EQ):
    """Cote (double flèche) avec une étiquette placée à côté du milieu."""
    p1, p2 = np.array(p1), np.array(p2)
    fl = DoubleArrow(p1, p2, buff=0, color=couleur, stroke_width=4,
                     tip_length=0.18, max_tip_length_to_length_ratio=0.3)
    u = (p2 - p1) / np.linalg.norm(p2 - p1)
    if cote_label is None:
        cote_label = np.array([-u[1], u[0], 0])  # perpendiculaire, à gauche
    lab = MathTex(texte, color=couleur, font_size=fs)
    lab.next_to((p1 + p2) / 2, cote_label, buff=0.15)
    return VGroup(fl, lab)


def croix(point, couleur=C_POINT, t=0.1):
    return VGroup(
        Line(point + t * (UL), point + t * (DR)),
        Line(point + t * (UR), point + t * (DL)),
    ).set_stroke(couleur, width=4)


def ligne_action(p, direction, longueur=12, couleur=GREY_B):
    u = np.array(direction, dtype=float)
    u /= np.linalg.norm(u)
    return DashedLine(p - longueur * u, p + longueur * u,
                      color=couleur, stroke_width=2.5, dash_length=0.12)


class Panneau:
    """Empile des lignes de texte, alignées à gauche, à partir de (x, y)."""

    def __init__(self, x, y, gap=0.3):
        self.x, self.y0, self.gap = x, y, gap
        self.y = y

    def placer(self, mob, gap=None):
        mob.move_to([self.x + mob.width / 2, self.y - mob.height / 2, 0])
        self.y -= mob.height + (self.gap if gap is None else gap)
        return mob

    def reset(self):
        self.y = self.y0


class Base(_Base):
    def etape(self, t=1.0):
        """Pause : fin de diapo en mode slides, simple attente en vidéo."""
        self.wait(t)
        self.next_slide()

    def titre(self, texte):
        t = Tex(texte, font_size=FS_TITRE).to_edge(UP, buff=0.3)
        trait = Line(LEFT, RIGHT, color=BLUE_B).set_width(t.width + 0.6)
        trait.next_to(t, DOWN, buff=0.12)
        return VGroup(t, trait)

    def tout_effacer(self, garder=()):
        mobs = [m for m in self.mobjects if m not in garder]
        for m in mobs:
            m.clear_updaters()
        mobs = [m for m in mobs if any(sm.has_points() for sm in m.get_family())]
        if mobs:
            self.play(*map(FadeOut, mobs))

    def montrer_rotation(self, objets, centre, signe, angle=18 * DEGREES, run_time=1.6):
        """Fait « tourner » les objets autour du centre, puis retour."""
        grp = VGroup(*objets)
        self.play(Rotate(grp, -angle if signe < 0 else angle, about_point=centre,
                         rate_func=there_and_back), run_time=run_time)




# ---------------------------------------------------------------------------
# Liaisons (mêmes symboles que drawingTool.tex) et poutres
# Chaque symbole est un VGroup(partie_mobile, sol) ; angle en degrés comme TikZ.
# ---------------------------------------------------------------------------
C_LIAISON = GREY_A
C_REACTION = BLUE_C


def _sol(y, x0=-0.5, x1=0.5, n=6):
    g = VGroup(Line([x0, y, 0], [x1, y, 0]))
    for i in range(n):
        x = x0 + i * (x1 - x0) / (n - 1)
        g.add(Line([x, y, 0], [x - 0.2, y - 0.2, 0]))
    return g


def _placer_symbole(g, point, angle, s):
    g.set_stroke(C_LIAISON, width=3)
    g.scale(s, about_point=ORIGIN).rotate(angle * DEGREES, about_point=ORIGIN)
    g.shift(np.array(point))
    return g


def symbole_appui(point, angle=0, s=0.5):
    tri = Polygon([0, 0, 0], [0.5, -0.866, 0], [-0.5, -0.866, 0])
    roues = VGroup(*[Circle(radius=0.175).move_to([x, -1.041, 0]) for x in (-0.35, 0, 0.35)])
    return _placer_symbole(VGroup(VGroup(tri, roues), _sol(-1.216)), point, angle, s)


def symbole_articulation(point, angle=0, s=0.5):
    cercle = Circle(radius=0.5).move_to([0, -0.5, 0])
    return _placer_symbole(VGroup(VGroup(cercle), _sol(-1.0)), point, angle, s)


def symbole_encastrement(point, angle=0, s=0.5):
    tige = Line([0, 0, 0], [0, -0.1, 0])
    return _placer_symbole(VGroup(VGroup(tige), _sol(-0.1)), point, angle, s)


def poutre(*points, couleur=GREY_B, epaisseur=10):
    """Poutre (ligne brisée épaisse) passant par les points donnés."""
    m = VMobject(stroke_color=couleur, stroke_width=epaisseur)
    m.set_points_as_corners([np.array(p) for p in points])
    return m


def moment_inconnu(centre, signe=+1, r=0.55, nom=None, couleur=C_REACTION, fs=FS_EQ):
    """Flèche courbe d'un couple (inconnu) + son nom éventuel."""
    arc = fleche_sens(centre, signe, r=r, couleur=couleur)
    if nom is None:
        return arc
    lab = MathTex(nom, color=couleur, font_size=fs).next_to(arc, UR, buff=0.02)
    return VGroup(arc, lab)


def ok_ko(libre, fs=FS_EQ):
    """Coche verte (mouvement libre) ou croix rouge (mouvement bloqué)."""
    if libre:
        return MathTex(r"\checkmark", color=C_POS, font_size=fs + 6)
    return MathTex(r"\boldsymbol{\times}", color=RED, font_size=fs + 6)


# ---------------------------------------------------------------------------
# Poutre horizontale en haut de l'écran, calculs en dessous
# ---------------------------------------------------------------------------
class PoutreScene(Base):
    """Outils pour une poutre horizontale en haut de l'écran, calculs en dessous."""

    YB = 1.3          # ordonnée de la poutre
    FS_CALC = FS_EQ - 4

    # --- géométrie
    def repere(self, L, largeur=9.0, xc=-0.3):
        self.L = L
        self.s = largeur / L
        self.x0 = xc - largeur / 2
        self.P = Panneau(-6.6, self.YB - 2.05, gap=0.22)
        self.contenu = []

    def X(self, x, dy=0.0):
        return np.array([self.x0 + self.s * x, self.YB + dy, 0.0])

    # --- dessin
    def point(self, x, nom, cote=UR):
        return VGroup(croix(self.X(x)), MathTex(nom, font_size=FS_EQ).next_to(self.X(x), cote, buff=0.1))

    def liaison(self, genre, x, angle=0):
        p = self.X(x)
        if genre == "appui":
            return symbole_appui(p, angle=angle, s=0.5)
        if genre == "articulation":
            return symbole_articulation(p, angle=angle, s=0.5)
        return symbole_encastrement(p, angle=-90 if x < self.L / 2 else 90, s=1.1)

    def charge(self, x, texte, h=1.3, couleur=C_FORCE, cote_lab=UP):
        a = force(self.X(x, h + 0.06), self.X(x, 0.06), couleur=couleur)
        lab = MathTex(texte, color=couleur, font_size=FS_TEXTE).next_to(a, cote_lab, buff=0.1)
        if cote_lab is not UP:
            lab.shift(0.35 * UP)
        return VGroup(a, lab)

    def charge_vec(self, x, v, texte, couleur=C_FORCE, cote_lab=UP):
        v = np.array([v[0], v[1], 0.0])
        a = force(self.X(x, 0.06) - v, self.X(x, 0.06), couleur=couleur)
        lab = MathTex(texte, color=couleur, font_size=FS_TEXTE).next_to(a.get_start(), cote_lab, buff=0.1)
        return VGroup(a, lab)

    def repartie(self, x1, x2, texte, h=0.9):
        n = max(2, int(round((x2 - x1) * self.s / 0.45)) + 1)
        fl = VGroup(*[Arrow(self.X(x, h + 0.06), self.X(x, 0.06), buff=0, color=C_FORCE, stroke_width=3,
                            max_tip_length_to_length_ratio=0.22, max_stroke_width_to_length_ratio=10)
                      for x in np.linspace(x1, x2, n)])
        ligne = Line(self.X(x1, h + 0.06), self.X(x2, h + 0.06), color=C_FORCE, stroke_width=3)
        lab = MathTex(texte, color=C_FORCE, font_size=FS_TEXTE).next_to(ligne, UP, buff=0.1)
        return VGroup(fl, ligne, lab)

    def couple(self, x, signe, texte):
        arc = fleche_sens(self.X(x), signe, r=0.42, couleur=C_FORCE)
        lab = MathTex(texte, color=C_FORCE, font_size=FS_TEXTE).next_to(arc, UP, buff=0.05)
        return VGroup(arc, lab)

    def reaction(self, genre, x, nom, signe=+1):
        p = self.X(x)
        if genre == "X":
            if x < self.L / 2:
                a = force(p + 1.0 * LEFT, p, couleur=C_REACTION)
                lab = MathTex(nom, color=C_REACTION, font_size=FS_EQ).next_to(a.get_start(), UP, buff=0.1)
            else:
                a = force(p, p + 1.0 * RIGHT, couleur=C_REACTION)
                lab = MathTex(nom, color=C_REACTION, font_size=FS_EQ).next_to(a.get_end(), UP, buff=0.1)
            return VGroup(a, lab)
        if genre == "Y":
            a = force(p + 1.0 * DOWN, p, couleur=C_REACTION)
            lab = MathTex(nom, color=C_REACTION, font_size=FS_EQ).next_to(a.get_start(), RIGHT, buff=0.1)
            return VGroup(a, lab)
        arc = fleche_sens(p, signe, r=0.6, couleur=C_REACTION)
        lab = MathTex(nom, color=C_REACTION, font_size=FS_EQ).next_to(arc, UP, buff=0.02)
        return VGroup(arc, lab)

    def cote_x(self, x1, x2, texte, dy=-1.45):
        return cote(self.X(x1, dy), self.X(x2, dy), texte, DOWN, fs=FS_TEXTE)

    # --- texte / calculs
    def ecrire(self, mob, gap=None, anim=True):
        self.P.placer(mob, gap=gap)
        self.contenu.append(mob)
        if anim:
            self.play(Write(mob))
        return mob

    def effacer_calculs(self):
        if self.contenu:
            self.play(*map(FadeOut, self.contenu))
        self.contenu = []
        self.P.reset()

    def equation(self, *parts):
        eq = MathTex(*parts, font_size=self.FS_CALC)
        self.ecrire(eq, anim=False)
        self.play(Write(eq[0]))
        return eq

    def resultat(self, tex, quoi=None):
        r = MathTex(r"\Rightarrow\ " + tex, font_size=FS_EQ)
        self.ecrire(r)
        b = SurroundingRectangle(r[0][1:], color=YELLOW, buff=0.1)
        self.play(Create(b))
        self.contenu.append(b)
        return r

    def terme(self, fl, x_pt, x_f, signe, part, d=None, nul=False, dir_la=UP, rq=None):
        """Un terme de ΣM : force en jaune, bras de levier, sens de rotation, puis on l'écrit."""
        fl.save_state()
        self.play(fl.animate.set_color(YELLOW), run_time=0.35)
        tmp = []
        if nul:
            la = ligne_action(self.X(x_f), dir_la, longueur=7)
            tmp.append(la)
            self.play(Create(la), run_time=0.7)
        elif signe != 0:
            anims = []
            if d is not None and abs(x_f - x_pt) > 1e-9:
                c = self.cote_x(x_pt, x_f, d)
                tmp.append(c)
                anims.append(FadeIn(c))
            sens = fleche_sens(self.X(x_pt), signe, r=0.38)
            tmp.append(sens)
            anims.append(Create(sens))
            self.play(*anims, run_time=0.8)
        if rq is not None:
            rq.to_edge(RIGHT, buff=0.4).set_y(self.YB - 2.05 - rq.height / 2)
            tmp.append(rq)
            self.play(FadeIn(rq))
        self.play(Write(part), run_time=0.8)
        self.wait(0.3)
        self.play(*map(FadeOut, tmp), Restore(fl), run_time=0.5)

    def remplacer_liaisons(self, liaisons, reactions):
        self.play(*map(FadeOut, liaisons))
        anims = []
        for r in reactions:
            anims += [Create(r[0]) if isinstance(r[0], Arc) else GrowArrow(r[0]), Write(r[1])]
        self.play(*anims)

    def valeur(self, reac, tex, inverser=False):
        """Remplace le nom d'une inconnue par sa valeur ; inverse la flèche si négative."""
        nouveau = MathTex(tex, color=C_REACTION if not inverser else C_NEG, font_size=FS_TEXTE)
        a = reac[0]
        if isinstance(a, Arrow) and abs(a.get_end()[1] - a.get_start()[1]) < 1e-3 and a.get_end()[0] > a.get_start()[0] \
                and reac[1].get_center()[0] < a.get_end()[0] - 0.3:
            # réaction horizontale à gauche : valeur au-dessus, à gauche du point (ne masque pas le nom du point)
            nouveau.next_to(a, UP, buff=0.12).align_to(a, RIGHT).shift(0.4 * LEFT)
        else:
            nouveau.move_to(reac[1], aligned_edge=LEFT)
        anims = [Transform(reac[1], nouveau)]
        if inverser:
            reac[0].set_color(C_NEG)
            anims.append(Rotate(reac[0], PI))
        return anims


# ---------------------------------------------------------------------------
# Efforts internes : coupure, N/V/M, diagrammes
# ---------------------------------------------------------------------------
C_INT = GREEN_C       # couleur des efforts internes


class EIScene(PoutreScene):
    """Outils propres aux efforts internes : coupure, N/V/M, diagrammes."""

    def coupure(self, x, h=0.75):
        p = self.X(x)
        return DashedLine(p + h * DOWN, p + h * UP, color=YELLOW, stroke_width=4, dash_length=0.08)

    def efforts(self, x, cote="gauche", fs=FS_TEXTE):
        """N, V, M dessinés positifs (partie gauche) ou −N, −V, −M (partie droite, notation du poly)."""
        p = self.X(x)
        pre = "" if cote == "gauche" else "-"
        if cote == "gauche":
            N = force(p, p + 0.9 * RIGHT, couleur=C_INT, epaisseur=5)
            lN = MathTex(pre + "N(x)", color=C_INT, font_size=fs).next_to(N.get_end(), RIGHT, buff=0.08)
        else:
            N = force(p + 0.9 * LEFT, p, couleur=C_INT, epaisseur=5)
            lN = MathTex(pre + "N(x)", color=C_INT, font_size=fs).next_to(N.get_start(), DOWN, buff=0.12)
        V = force(p, p + 0.9 * UP, couleur=C_INT, epaisseur=5)
        lV = MathTex(pre + "V(x)", color=C_INT, font_size=fs).next_to(V.get_end(), UP, buff=0.08)
        M = fleche_sens(p, +1, r=0.42, couleur=C_INT)
        lM = MathTex(pre + "M(x)", color=C_INT, font_size=fs).next_to(M, DR, buff=0.02)
        return VGroup(VGroup(N, lN), VGroup(V, lV), VGroup(M, lM))

    def D(self, x, val, y0, ech):
        return np.array([self.X(x)[0], y0 + ech * val, 0.0])

    def diagramme(self, morceaux, y0, ech, nom, couleur, n=40):
        """morceaux = [(x1, x2, f)] ; f(x_global) -> valeur. Axe à y0, valeurs positives vers le haut."""
        axe = Line(self.D(0, 0, y0, ech), self.D(self.L, 0, y0, ech), color=GREY_B, stroke_width=2)
        pts = []
        for x1, x2, f in morceaux:
            for x in np.linspace(x1, x2, n):
                pts.append(self.D(x, f(x), y0, ech))
        courbe = VMobject(stroke_color=couleur, stroke_width=5).set_points_as_corners(pts)
        fond = Polygon(self.D(0, 0, y0, ech), *pts, self.D(self.L, 0, y0, ech),
                       stroke_width=0, fill_color=couleur, fill_opacity=0.25)
        lab = MathTex(nom, color=couleur, font_size=FS_TEXTE).next_to(axe, LEFT, buff=0.25)
        return VGroup(axe, fond, courbe, lab)

    def valeur_diag(self, x, val, y0, ech, tex, direction=UP, couleur=WHITE):
        return MathTex(tex, font_size=FS_TEXTE - 4, color=couleur).next_to(self.D(x, val, y0, ech), direction, buff=0.08)

    def coupure_mobile(self, xc, y_bas):
        return always_redraw(lambda: DashedLine(self.X(xc.get_value(), 0.8),
                                                [self.X(xc.get_value())[0], y_bas, 0],
                                                color=YELLOW, stroke_width=3, dash_length=0.1))

    def point_mobile(self, xc, f, y0, ech, couleur):
        return always_redraw(lambda: Dot(self.D(xc.get_value(), f(xc.get_value()), y0, ech),
                                         color=couleur, radius=0.07))


# ---------------------------------------------------------------------------
# MS2 : sections (rectangles en cm, barycentre, repère ZY), profilés UPE
# ---------------------------------------------------------------------------
C_SECTION = BLUE_D
C_G = YELLOW
C_ELEM = [TEAL_C, PURPLE_B, GOLD_C, MAROON_B]    # couleurs des éléments 1, 2, 3...
C_TROU = RED_C


def fr(x, n=1):
    """Nombre au format français pour MathTex : 9.5 -> 9{,}5 (virgule sans espace)."""
    return f"{x:.{n}f}".replace(".", "{,}")


class Plan:
    """Plan d'une section : coordonnées (u, y) en cm, u vers la droite de l'écran, y vers le haut."""

    def __init__(self, origine, s=0.3):
        self.o = np.array([origine[0], origine[1], 0.0])
        self.s = s

    def p(self, u, y):
        return self.o + self.s * np.array([u, y, 0.0])

    def rect(self, u0, y0, u1, y1, couleur=C_SECTION, opacite=0.6):
        r = Polygon(self.p(u0, y0), self.p(u1, y0), self.p(u1, y1), self.p(u0, y1))
        return r.set_stroke(WHITE, width=3).set_fill(couleur, opacity=opacite)

    def cote_v(self, u, y0, y1, texte, cote_label=LEFT, couleur=C_LEVIER, fs=FS_TEXTE):
        return cote(self.p(u, y0), self.p(u, y1), texte, cote_label, couleur=couleur, fs=fs)

    def cote_h(self, u0, u1, y, texte, cote_label=DOWN, couleur=C_LEVIER, fs=FS_TEXTE):
        return cote(self.p(u0, y), self.p(u1, y), texte, cote_label, couleur=couleur, fs=fs)

    def rappel(self, u0, y0, u1, y1):
        return rappel(self.p(u0, y0), self.p(u1, y1))


def rappel(p1, p2, couleur=GREY_B):
    """Ligne de rappel (fine, pointillée) pour les cotes."""
    return DashedLine(np.array(p1), np.array(p2), color=couleur, stroke_width=2, dash_length=0.08)


def repere_zy(point, l=0.9, couleur=GREY_A, fs=FS_TEXTE):
    """Repère de section du poly : Z horizontal vers la gauche, Y vertical vers le haut."""
    p = np.array(point)
    kw = dict(buff=0, color=couleur, stroke_width=3, max_tip_length_to_length_ratio=0.15)
    z = Arrow(p + l * RIGHT, p + l * LEFT, **kw)
    y = Arrow(p + l * DOWN, p + l * UP, **kw)
    lz = MathTex("Z", font_size=fs, color=couleur).next_to(z.get_end(), LEFT, buff=0.08)
    ly = MathTex("Y", font_size=fs, color=couleur).next_to(y.get_end(), UP, buff=0.08)
    return VGroup(z, y, lz, ly)


def point_G(point, nom="G", cote_label=UR, couleur=C_G, fs=FS_TEXTE, buff=0.08):
    """Croix + nom (G, G_1...)."""
    return VGroup(croix(np.array(point), couleur, t=0.12),
                  MathTex(nom, color=couleur, font_size=fs).next_to(np.array(point), cote_label, buff=buff))


def ligne_valeur(prefixe, f, unite, fs=FS_EQ, decimales=1, couleur=WHITE):
    """« prefixe  valeur  unité » (sans signe +) où la valeur est recalculée par f() à chaque image."""
    v = Decimal(f(), num_decimal_places=decimales, font_size=fs, color=couleur)
    g = VGroup(MathTex(prefixe, font_size=fs, color=couleur), v,
               MathTex(unite, font_size=fs, color=couleur)).arrange(RIGHT, buff=0.15)

    def maj(m):
        m.set_value(f()).next_to(g[0], RIGHT, buff=0.15)
        g[2].next_to(m, RIGHT, buff=0.15)
    v.add_updater(maj)
    return g


def axe_Z(point, demi=3.0, couleur=GREY_B):
    """Axe horizontal (trait mixte façon dessin technique) passant par un point."""
    p = np.array(point)
    return DashedLine(p + demi * LEFT, p + demi * RIGHT, color=couleur, stroke_width=2,
                      dash_length=0.2, dashed_ratio=0.7)


def fraction(num, den, fs=FS_EQ):
    """Fraction « à la main » : num et den sont des listes de morceaux MathTex (on peut les colorier un par un)."""
    n = MathTex(*num, font_size=fs)
    d = MathTex(*den, font_size=fs)
    barre = Line(LEFT, RIGHT, stroke_width=2.5).set_width(max(n.width, d.width) + 0.2)
    n.next_to(barre, UP, buff=0.12)
    d.next_to(barre, DOWN, buff=0.12)
    return VGroup(n, barre, d)


# --- profilés UPE (extrait du catalogue ArcelorMittal, annexe B du poly)
#     h, b, tw, tf, r, ys en mm ; A en cm² ; I en cm⁴ ; W_el en cm³
UPE = {
    "UPE 80":  dict(h="80",  b="50", tw="4,0", tf="7,0", r="10", A="10,1", Iy="107", Wy="26,8", Iz="25,5", Wz="8,0",  ys="18,2"),
    "UPE 100": dict(h="100", b="55", tw="4,5", tf="7,5", r="10", A="12,5", Iy="207", Wy="41,4", Iz="38,3", Wz="10,6", ys="19,1"),
    "UPE 120": dict(h="120", b="60", tw="5,0", tf="8,0", r="12", A="15,4", Iy="364", Wy="60,6", Iz="55,5", Wz="13,8", ys="19,8"),
    "UPE 140": dict(h="140", b="65", tw="5,0", tf="9,0", r="12", A="18,4", Iy="600", Wy="85,6", Iz="78,8", Wz="18,2", ys="21,7"),
}

ENTETES_UPE = {
    "h": r"h", "b": r"b", "A": r"A", "Iy": r"\mathsf{I_y}", "Wy": r"\mathsf{W_{el,y}}",
    "Iz": r"\mathsf{I_z}", "Wz": r"\mathsf{W_{el,z}}", "ys": r"\mathsf{y_s}",
}
UNITES_UPE = {"h": "mm", "b": "mm", "A": "cm^2", "Iy": "cm^4", "Wy": "cm^3", "Iz": "cm^4", "Wz": "cm^3", "ys": "mm"}


def val(nom, cle):
    """Valeur numérique d'une case du catalogue."""
    return float(UPE[nom][cle].replace(",", "."))


def contour_upe(nom, n=10):
    """Contour (mm) d'un UPE placé en C comme dans le catalogue : âme à gauche (u = 0), mi-hauteur en y = 0."""
    h, b, tw, tf, r = (val(nom, k) for k in ("h", "b", "tw", "tf", "r"))
    pts = [(0, -h / 2), (b, -h / 2), (b, -h / 2 + tf)]
    c = (tw + r, -h / 2 + tf + r)
    pts += [(c[0] + r * np.cos(a), c[1] + r * np.sin(a)) for a in np.linspace(-PI / 2, -PI, n)]
    c = (tw + r, h / 2 - tf - r)
    pts += [(c[0] + r * np.cos(a), c[1] + r * np.sin(a)) for a in np.linspace(PI, PI / 2, n)]
    pts += [(b, h / 2 - tf), (b, h / 2), (0, h / 2)]
    return np.array(pts)


def profil_upe(nom, echelle=0.03, couleur=C_SECTION):
    """Section d'UPE (placée en C) dont le barycentre G est à l'origine ; echelle en unités Manim par mm."""
    pts = contour_upe(nom)
    pts[:, 0] -= val(nom, "ys")                     # G est à y_s du dos de l'âme
    m = Polygon(*[echelle * np.array([u, y, 0.0]) for u, y in pts])
    return m.set_stroke(WHITE, width=3).set_fill(couleur, opacity=0.7)


def tableau_upe(cles=("h", "b", "A", "Iy", "Wy", "Iz", "Wz", "ys"), largeur=12.5, fs=30):
    """Extrait simplifié du catalogue : une ligne par profilé, une colonne par grandeur (avec unité)."""
    lignes = [[UPE[nom][k].replace(",", "{,}") for k in cles] for nom in UPE]
    t = MathTable(
        lignes,
        row_labels=[Tex(r"\textsf{" + nom.replace(" ", r"\,") + "}", font_size=fs) for nom in UPE],
        col_labels=[VGroup(MathTex(ENTETES_UPE[k], font_size=fs),
                           MathTex(r"(\mathrm{" + UNITES_UPE[k] + "})", font_size=fs - 8, color=GREY_B)
                           ).arrange(DOWN, buff=0.08) for k in cles],
        include_outer_lines=True,
        element_to_mobject_config={"font_size": fs},
        line_config={"stroke_width": 1.5, "color": GREY_C},
        h_buff=0.5, v_buff=0.3,
    )
    return t.scale_to_fit_width(largeur)


# ---------------------------------------------------------------------------
# MS2 : contraintes normales, diagramme de Navier
# ---------------------------------------------------------------------------
C_TRAC = BLUE_C      # traction (σ > 0)
C_COMP = RED_C       # compression (σ < 0)


class Navier:
    """Diagramme de Navier : y vertical (mm, même échelle que la section), σ horizontal (MPa).
    origine = point écran de (σ = 0, y = 0), c'est-à-dire à la hauteur de G."""

    def __init__(self, origine, ky, ks, y_inf, y_sup):
        self.o = np.array([origine[0], origine[1], 0.0])
        self.ky, self.ks, self.y_inf, self.y_sup = ky, ks, y_inf, y_sup

    def p(self, sig, y):
        return self.o + np.array([self.ks * sig, self.ky * y, 0.0])

    def axes(self, s_min, s_max, marge=12, fs=28):
        kw = dict(buff=0, color=GREY_A, stroke_width=2.5)
        ax_s = Arrow(self.p(s_min, 0), self.p(s_max, 0), max_tip_length_to_length_ratio=0.05, **kw)
        ax_y = Arrow(self.p(0, self.y_inf - marge), self.p(0, self.y_sup + 2 * marge),
                     max_tip_length_to_length_ratio=0.06, **kw)
        ls = MathTex(r"\sigma\ (\mathrm{MPa})", font_size=fs, color=GREY_A).next_to(ax_s.get_end(), DOWN, buff=0.12)
        ly = MathTex(r"y\ (\mathrm{mm})", font_size=fs, color=GREY_A).next_to(ax_y.get_end(), UP, buff=0.08)
        return VGroup(ax_s, ax_y, ls, ly)

    def droite(self, f, couleur=YELLOW):
        return Line(self.p(f(self.y_inf), self.y_inf), self.p(f(self.y_sup), self.y_sup),
                    color=couleur, stroke_width=5)

    def hachures(self, f, n=15):
        g = VGroup()
        for y in np.linspace(self.y_inf, self.y_sup, n):
            s = f(y)
            if abs(s * self.ks) > 0.02:
                g.add(Line(self.p(0, y), self.p(s, y), stroke_width=3, color=C_TRAC if s > 0 else C_COMP))
        return g

    def diagramme(self, f, couleur=YELLOW):
        return VGroup(self.hachures(f), self.droite(f, couleur))
