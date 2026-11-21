"""
MS1 - Animations pédagogiques : treillis isostatiques (§5 du poly)

Scènes :
    TreillisIntro            triangle indéformable, définition et hypothèses, barre = biellette (seul N),
                             tendue / comprimée
    TreillisHyperstaticite   H = b + r − 2n : exemple du poly (H = 0), barre en trop (H = 1), mécanisme (H < 0)
    TreillisMethodeNoeuds    console en bois du poly (F = 7 kN) : réactions, nœud B, nœud C, vérification en A
    TreillisMethodeSection   treillis à 6 travées du poly : coupure de 3 barres, ΣM en E, ΣF_Y, ΣF_X
    TreillisPieges           check-list des pièges et astuces

Vidéo  : manim -qh treillis.py TreillisIntro TreillisHyperstaticite TreillisMethodeNoeuds \
             TreillisMethodeSection TreillisPieges
Slides : manim-slides render -qh treillis.py <scènes>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403

C_TRAC = RED_C       # barre tendue
C_COMP = BLUE_C      # barre comprimée
C_BARRE = GREY_B


def noeud_mob(p, r=0.09):
    return Circle(radius=r, stroke_color=WHITE, stroke_width=3, fill_color=BLACK, fill_opacity=1).move_to(p)


def Tw(texte, largeur_cm=7.2, **kw):
    """Texte à largeur fixe (retour à la ligne automatique) pour les panneaux de droite."""
    kw.setdefault("font_size", FS_TEXTE - 2)
    return Tex(r"\begin{minipage}{%gcm}\raggedright " % largeur_cm + texte + r"\end{minipage}", **kw)


class Treillis:
    """Géométrie d'un treillis : nœuds {nom: (x, y)}, barres {numéro: (n1, n2)}."""

    def __init__(self, noeuds, barres, origine, s):
        self.o = np.array([origine[0], origine[1], 0.0])
        self.s = s
        self.P = {k: self.o + s * np.array([x, y, 0.0]) for k, (x, y) in noeuds.items()}
        self.barres = barres

    def p(self, k):
        return self.P[k]

    def u(self, num, depuis):
        n1, n2 = self.barres[num]
        autre = n2 if depuis == n1 else n1
        v = self.P[autre] - self.P[depuis]
        return v / np.linalg.norm(v)

    def barre(self, num, couleur=C_BARRE, ep=8):
        n1, n2 = self.barres[num]
        return Line(self.P[n1], self.P[n2], color=couleur, stroke_width=ep)

    def num(self, num, cote=1, fs=22):
        n1, n2 = self.barres[num]
        a, b = self.P[n1], self.P[n2]
        d = (b - a) / np.linalg.norm(b - a)
        perp = cote * np.array([-d[1], d[0], 0])
        c = (a + b) / 2 + 0.28 * perp
        return VGroup(Circle(radius=0.16, stroke_color=WHITE, stroke_width=2, fill_color=BLACK, fill_opacity=1).move_to(c),
                      MathTex(str(num), font_size=fs).move_to(c))

    def dessin(self, numeros=False, cotes=None):
        bars = VGroup(*[self.barre(n) for n in self.barres])
        nds = VGroup(*[noeud_mob(self.P[k]) for k in self.P])
        nums = VGroup()
        if numeros:
            cotes = cotes or {}
            nums = VGroup(*[self.num(n, cotes.get(n, 1)) for n in self.barres])
        return bars, nds, nums

    def effort(self, num, depuis, nom, l0=0.75, l1=0.75, couleur=C_INT, cote_lab=None):
        """Barre « sortante » au nœud : bout de barre + flèche qui s'éloigne du nœud (barre supposée tendue)."""
        u = self.u(num, depuis)
        p = self.P[depuis]
        bout = Line(p, p + l0 * u, color=C_BARRE, stroke_width=8)
        fl = force(p + l0 * u, p + (l0 + l1) * u, couleur=couleur, epaisseur=6)
        if cote_lab is None:
            cote_lab = u
        lab = MathTex(nom, color=couleur, font_size=FS_EQ).next_to(fl.get_end(), cote_lab, buff=0.08)
        return VGroup(bout, fl, lab)


# ---------------------------------------------------------------------------
# 1. Introduction
# ---------------------------------------------------------------------------
class TreillisIntro(Base):
    def construct(self):
        titre = self.titre(r"Treillis : pourquoi des triangles ?")
        self.play(Write(titre))

        # rectangle articulé : déformable
        s = 2.2
        o1 = np.array([-5.2, -1.2, 0])
        dx = ValueTracker(0.0)
        pts = lambda: [o1, o1 + s * RIGHT, o1 + s * RIGHT + s * UP + dx.get_value() * RIGHT,
                       o1 + s * UP + dx.get_value() * RIGHT]
        rect = always_redraw(lambda: VGroup(
            *[Line(pts()[i], pts()[(i + 1) % 4], color=C_BARRE, stroke_width=8) for i in range(4)],
            *[noeud_mob(p) for p in pts()]))
        F1 = always_redraw(lambda: force(pts()[3] + 1.1 * LEFT, pts()[3], couleur=C_FORCE))
        sol1 = VGroup(symbole_articulation(o1, s=0.4), symbole_articulation(o1 + s * RIGHT, s=0.4))
        o2 = np.array([1.6, -1.2, 0])
        tri_pts = [o2, o2 + s * RIGHT, o2 + s / 2 * RIGHT + s * UP]
        tri = VGroup(*[Line(tri_pts[i], tri_pts[(i + 1) % 3], color=C_BARRE, stroke_width=8) for i in range(3)],
                     *[noeud_mob(p) for p in tri_pts])
        sol2 = VGroup(symbole_articulation(o2, s=0.4), symbole_articulation(o2 + s * RIGHT, s=0.4))
        F2 = force(tri_pts[2] + 1.1 * LEFT, tri_pts[2], couleur=C_FORCE)
        self.add(rect)
        self.play(FadeIn(sol1), FadeIn(rect), FadeIn(tri), FadeIn(sol2))
        self.play(FadeIn(F1), GrowArrow(F2))
        self.play(dx.animate.set_value(1.1), run_time=2, rate_func=rate_functions.ease_in_quad)
        l1 = T(r"Rectangle articulé :\\\textbf{déformable}", color=C_NEG).next_to(sol1, DOWN, buff=0.4).shift(0.6 * RIGHT)
        self.play(Wiggle(tri, scale_value=1.01, rotation_angle=0.003 * TAU))
        l2 = T(r"Triangle articulé :\\\textbf{indéformable}", color=C_POS).next_to(sol2, DOWN, buff=0.4)
        self.play(Write(l1), Write(l2))
        self.etape()

        # définition et hypothèses
        self.tout_effacer(garder=[titre])
        d = T(r"\textbf{Treillis} : barres assemblées à leurs extrémités par des \textbf{articulations},"
              r" formant des triangles $\Rightarrow$ structure légère et économique.").next_to(titre, DOWN, buff=0.5)
        self.play(Write(d))
        hyp = VGroup(*[T(t) for t in [
            r"\textbf{Hypothèses :}",
            r"$\bullet$ barres \textbf{droites}, dont les axes \textbf{concourent aux nœuds}",
            r"$\bullet$ barres \textbf{articulées} à leurs extrémités",
            r"$\bullet$ chargement appliqué \textbf{aux nœuds}",
            r"$\bullet$ poids propre négligé (ou ramené aux nœuds)",
        ]]).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(d, DOWN, buff=0.5).align_to(d, LEFT)
        for h in hyp:
            self.play(FadeIn(h, shift=0.2 * RIGHT), run_time=0.7)
        self.etape()

        # une barre = une biellette : seulement N
        self.tout_effacer(garder=[titre])
        A, B = np.array([-4.5, 0.8, 0]), np.array([-0.5, 0.8, 0])
        bar = Line(A, B, color=C_BARRE, stroke_width=10)
        reac = VGroup(
            VGroup(force(A + 1.0 * LEFT, A + 0.12 * LEFT, couleur=C_REACTION), MathTex("X_A", color=C_REACTION, font_size=FS_EQ).next_to(A + 1.0 * LEFT, UP, buff=0.1)),
            VGroup(force(A + 0.12 * UP, A + 1.0 * UP, couleur=C_REACTION), MathTex("Y_A", color=C_REACTION, font_size=FS_EQ).next_to(A + 1.0 * UP, UP, buff=0.1)),
            VGroup(force(B + 0.12 * RIGHT, B + 1.0 * RIGHT, couleur=C_REACTION), MathTex("X_B", color=C_REACTION, font_size=FS_EQ).next_to(B + 1.0 * RIGHT, UP, buff=0.1)),
            VGroup(force(B + 0.12 * UP, B + 1.0 * UP, couleur=C_REACTION), MathTex("Y_B", color=C_REACTION, font_size=FS_EQ).next_to(B + 1.0 * UP, UP, buff=0.1)),
        )
        self.play(Create(bar), FadeIn(noeud_mob(A)), FadeIn(noeud_mob(B)))
        self.play(*[GrowArrow(r[0]) for r in reac], *[Write(r[1]) for r in reac])
        P = Panneau(1.2, 1.8, gap=0.25)
        e0 = P.placer(T(r"Une barre articulée, chargée\\seulement à ses extrémités :"))
        e1 = P.placer(MathTex(r"\sum M_{/B} = -Y_A\,\ell = 0 \Rightarrow Y_A = 0", font_size=FS_EQ - 4))
        e2 = P.placer(MathTex(r"\sum F_Y = 0 \Rightarrow Y_B = 0", font_size=FS_EQ - 4))
        e3 = P.placer(MathTex(r"\sum F_X = 0 \Rightarrow X_B = -X_A", font_size=FS_EQ - 4))
        for e in (e0, e1, e2, e3):
            self.play(Write(e))
        self.play(FadeOut(reac[1]), FadeOut(reac[3]))
        e4 = P.placer(T(r"$\Rightarrow$ deux forces \textbf{opposées},\\le long de l'axe : seul effort\\"
                        r"interne, l'\textbf{effort normal} $N$.", color=YELLOW))
        self.play(Write(e4))
        self.etape()

        # tendue / comprimée
        self.tout_effacer(garder=[titre])
        y1, y2 = 1.0, -1.6
        b1 = Line([-4, y1, 0], [0, y1, 0], color=C_TRAC, stroke_width=12)
        b2 = Line([-4, y2, 0], [0, y2, 0], color=C_COMP, stroke_width=12)
        t1 = VGroup(force([-4.1, y1, 0], [-5.1, y1, 0], couleur=C_TRAC), force([0.1, y1, 0], [1.1, y1, 0], couleur=C_TRAC))
        t2 = VGroup(force([-5.1, y2, 0], [-4.1, y2, 0], couleur=C_COMP), force([1.1, y2, 0], [0.1, y2, 0], couleur=C_COMP))
        l1 = T(r"$N > 0$ : barre \textbf{TENDUE}\\(elle tire sur ses nœuds)", color=C_TRAC).move_to([4.2, y1, 0])
        l2 = T(r"$N < 0$ : barre \textbf{COMPRIMÉE}\\(elle pousse sur ses nœuds)", color=C_COMP).move_to([4.2, y2, 0])
        self.play(Create(b1), GrowArrow(t1[0]), GrowArrow(t1[1]))
        self.play(b1.animate.stretch(1.08, 0), t1[0].animate.shift(0.16 * LEFT), t1[1].animate.shift(0.16 * RIGHT),
                  rate_func=there_and_back, run_time=1.3)
        self.play(Write(l1))
        self.play(Create(b2), GrowArrow(t2[0]), GrowArrow(t2[1]))
        self.play(b2.animate.stretch(0.92, 0), t2[0].animate.shift(0.16 * RIGHT), t2[1].animate.shift(0.16 * LEFT),
                  rate_func=there_and_back, run_time=1.3)
        self.play(Write(l2))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Degré d'hyperstaticité
# ---------------------------------------------------------------------------
class TreillisHyperstaticite(Base):
    def construct(self):
        titre = self.titre(r"Treillis : degré d'hyperstaticité")
        self.play(Write(titre))
        f = MathTex(r"H = b + r - 2\,n", font_size=FS_EQ + 10).next_to(titre, DOWN, buff=0.35)
        bf = SurroundingRectangle(f, color=YELLOW, buff=0.15)
        self.play(Write(f), Create(bf))
        leg = T(r"$b$ : nombre de \textbf{barres} \quad $r$ : inconnues de liaison (\textbf{réactions}) \quad"
                r" $n$ : nombre de \textbf{nœuds}", font_size=FS_TEXTE - 2).next_to(bf, DOWN, buff=0.25)
        self.play(Write(leg))
        self.etape()

        tr = Treillis({"A": (0, 0), "C": (3, 0), "D": (3, 3), "E": (6, 3), "B": (6, 0)},
                      {1: ("A", "C"), 2: ("C", "B"), 3: ("A", "D"), 4: ("D", "E"), 5: ("D", "C"), 6: ("D", "B"), 7: ("E", "B")},
                      origine=(-6.0, -3.0), s=0.75)
        bars, nds, _ = tr.dessin()
        sA = symbole_appui(tr.p("A"), s=0.4)
        sB = symbole_articulation(tr.p("B"), s=0.4)
        F = force(tr.p("D") + 0.9 * UP, tr.p("D") + 0.1 * UP, couleur=C_FORCE)
        lA = MathTex("A", font_size=FS_EQ).next_to(tr.p("A"), LEFT, buff=0.2)
        lB = MathTex("B", font_size=FS_EQ).next_to(tr.p("B"), RIGHT, buff=0.2)
        self.play(Create(bars), FadeIn(nds), FadeIn(sA), FadeIn(sB), GrowArrow(F), Write(lA), Write(lB))

        P = Panneau(0.6, -0.2, gap=0.22)
        # comptage des barres
        cb = Integer(0, font_size=FS_EQ)
        lb = VGroup(MathTex("b =", font_size=FS_EQ), cb).arrange(RIGHT, buff=0.15)
        P.placer(lb)
        self.play(FadeIn(lb))
        for i, b in enumerate(bars):
            self.play(b.animate.set_color(YELLOW), cb.animate.set_value(i + 1), run_time=0.35)
        self.play(bars.animate.set_color(C_BARRE), run_time=0.3)
        cn = Integer(0, font_size=FS_EQ)
        ln = VGroup(MathTex("n =", font_size=FS_EQ), cn).arrange(RIGHT, buff=0.15)
        P.placer(ln)
        self.play(FadeIn(ln))
        for i, n in enumerate(nds):
            self.play(Indicate(n, color=YELLOW, scale_factor=1.8), cn.animate.set_value(i + 1), run_time=0.35)
        lr = P.placer(MathTex(r"r = 1 + 2 = 3", font_size=FS_EQ))
        lr2 = T(r"(appui en $A$, articulation en $B$)", font_size=FS_TEXTE - 4, color=GREY_B).next_to(lr, RIGHT, buff=0.2)
        self.play(Indicate(sA, color=YELLOW), Indicate(sB, color=YELLOW), Write(lr), Write(lr2))
        lh = P.placer(MathTex(r"H = 7 + 3 - 2\times5 = 0", font_size=FS_EQ))
        self.play(Write(lh))
        iso = P.placer(T(r"$H = 0$ : \textbf{isostatique} \checkmark", color=C_POS))
        self.play(Write(iso))
        self.etape()

        # barre en plus : hyperstatique
        b8 = Line(tr.p("C"), tr.p("E"), color=C_NEG, stroke_width=8)
        self.play(*map(FadeOut, [lb, ln, lr, lr2, lh, iso]))
        P = Panneau(0.6, -0.2, gap=0.22)
        self.play(Create(b8))
        h1 = P.placer(MathTex(r"b = 8 \Rightarrow H = 8 + 3 - 10 = 1", font_size=FS_EQ))
        h2 = P.placer(T(r"$H > 0$ : \textbf{hyperstatique}\\(une barre de trop : le PFS ne suffit plus)", color=C_NEG))
        self.play(Write(h1))
        self.play(Write(h2))
        self.etape()

        # barre en moins : mécanisme
        self.play(*map(FadeOut, [h1, h2, b8, bars, nds, sA, sB, F, lA, lB]))
        o = np.array([-5.2, -3.0, 0])
        s = 2.4
        dx = ValueTracker(0.0)
        pts = lambda: [o, o + s * RIGHT, o + s * RIGHT + s * UP + dx.get_value() * RIGHT, o + s * UP + dx.get_value() * RIGHT]
        cadre = always_redraw(lambda: VGroup(
            Line(pts()[0], pts()[3], color=C_BARRE, stroke_width=8), Line(pts()[3], pts()[2], color=C_BARRE, stroke_width=8),
            Line(pts()[2], pts()[1], color=C_BARRE, stroke_width=8), *[noeud_mob(p) for p in pts()]))
        sols = VGroup(symbole_articulation(o, s=0.4), symbole_articulation(o + s * RIGHT, s=0.4))
        self.add(cadre)
        self.play(FadeIn(cadre), FadeIn(sols))
        P = Panneau(0.6, -0.2, gap=0.22)
        m1 = P.placer(MathTex(r"b = 3,\ r = 4,\ n = 4", font_size=FS_EQ))
        m1b = P.placer(MathTex(r"H = 3 + 4 - 8 = -1", font_size=FS_EQ))
        self.play(Write(m1))
        self.play(Write(m1b))
        Fm = always_redraw(lambda: force(pts()[3] + 1.0 * LEFT, pts()[3], couleur=C_FORCE))
        self.add(Fm)
        self.play(dx.animate.set_value(1.2), run_time=2, rate_func=rate_functions.ease_in_quad)
        m2 = P.placer(T(r"$H < 0$ : \textbf{mécanisme} (la structure bouge !)", color=RED))
        self.play(Write(m2))
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. Méthode des nœuds (console en bois du poly)
# ---------------------------------------------------------------------------
class TreillisMethodeNoeuds(Base):
    def construct(self):
        titre = self.titre(r"Treillis : méthode des nœuds")
        self.play(Write(titre))
        tr = Treillis({"C": (0, 0), "A": (0, 4), "B": (4, 4)}, {1: ("A", "B"), 2: ("B", "C"), 3: ("A", "C")},
                      origine=(-5.6, -2.6), s=0.95)
        bars, nds, nums = tr.dessin(numeros=True, cotes={1: 1, 2: 1, 3: 1})
        sA = symbole_articulation(tr.p("A"), angle=-90, s=0.4)
        sC = symbole_appui(tr.p("C"), angle=-90, s=0.4)
        labs = VGroup(MathTex("A", font_size=FS_EQ).next_to(tr.p("A"), DR, buff=0.12),
                      MathTex("B", font_size=FS_EQ).next_to(tr.p("B"), UR, buff=0.12),
                      MathTex("C", font_size=FS_EQ).next_to(tr.p("C"), RIGHT, buff=0.2))
        F = VGroup(force(tr.p("B") + 0.1 * DOWN, tr.p("B") + 1.6 * DOWN, couleur=C_FORCE),
                   MathTex(r"F = 7~\mathrm{kN}", color=C_FORCE, font_size=FS_TEXTE).next_to(tr.p("B") + 1.6 * DOWN, RIGHT, buff=0.1))
        ang = VGroup(Arc(radius=0.9, start_angle=PI / 2, angle=-PI / 4, arc_center=tr.p("C"), color=C_LEVIER),
                     MathTex(r"45^\circ", color=C_LEVIER, font_size=FS_TEXTE - 4).move_to(tr.p("C") + 1.2 * np.array([0.38, 0.92, 0])))
        self.play(Create(bars), FadeIn(nds), FadeIn(nums), FadeIn(sA), FadeIn(sC), Write(labs))
        self.play(GrowArrow(F[0]), Write(F[1]), Create(ang[0]), Write(ang[1]))
        P = Panneau(0.2, 2.4, gap=0.22)
        self.contenu = []

        def ecrire(m, gap=None):
            P.placer(m, gap=gap)
            self.contenu.append(m)
            self.play(Write(m))
            return m

        def effacer():
            self.play(*map(FadeOut, self.contenu))
            self.contenu = []
            P.reset()

        ecrire(Tw(r"\textbf{0.} Isostatique ? \ $b = 3$, $n = 3$, $r = 3$ (2 en $A$, 1 en $C$)"))
        ecrire(MathTex(r"H = 3 + 3 - 2\times3 = 0 \quad \text{isostatique} \checkmark", font_size=FS_EQ - 8, color=C_POS))
        self.etape()

        # réactions
        ecrire(Tw(r"\textbf{1.} Réactions (pas toujours indispensable) :"))
        XC = VGroup(force(tr.p("C") + 1.0 * LEFT, tr.p("C") + 0.1 * LEFT, couleur=C_REACTION),
                    MathTex("X_C", color=C_REACTION, font_size=FS_EQ).next_to(tr.p("C") + 1.0 * LEFT, UP, buff=0.08))
        XA = VGroup(force(tr.p("A") + 1.0 * LEFT, tr.p("A") + 0.1 * LEFT, couleur=C_REACTION),
                    MathTex("X_A", color=C_REACTION, font_size=FS_EQ).next_to(tr.p("A") + 1.0 * LEFT, DOWN, buff=0.08))
        YA = VGroup(force(tr.p("A") + 0.1 * UP, tr.p("A") + 1.0 * UP, couleur=C_REACTION),
                    MathTex("Y_A", color=C_REACTION, font_size=FS_EQ).next_to(tr.p("A") + 1.0 * UP, RIGHT, buff=0.08))
        self.play(FadeOut(sA), FadeOut(sC), *[GrowArrow(r[0]) for r in (XC, XA, YA)], *[Write(r[1]) for r in (XC, XA, YA)])
        ecrire(MathTex(r"\sum F_Y = 0 \Rightarrow Y_A = F = 7~\mathrm{kN}", font_size=FS_EQ - 8))
        ecrire(MathTex(r"\sum M_{/A} = 4X_C - 4F = 0 \Rightarrow X_C = 7~\mathrm{kN}", font_size=FS_EQ - 8))
        ecrire(MathTex(r"\sum F_X = 0 \Rightarrow X_A = -X_C = -7~\mathrm{kN}", font_size=FS_EQ - 8))
        self.etape()

        # nœud B
        effacer()
        ecrire(Tw(r"\textbf{2.} On isole un nœud avec \textbf{2 barres} seulement (2 équations) : le nœud $B$."))
        fantome = VGroup(*[DashedLine(tr.p(tr.barres[n][0]), tr.p(tr.barres[n][1]), color=GREY_D) for n in (1, 2, 3)])
        self.play(FadeOut(bars), FadeOut(nums), FadeIn(fantome), VGroup(XC, XA, YA).animate.set_opacity(0.15),
                  ang.animate.set_opacity(0.2))
        e1 = tr.effort(1, "B", "N_1", cote_lab=UP)
        e2 = tr.effort(2, "B", "N_2", cote_lab=LEFT)
        self.play(Create(e1[0]), Create(e2[0]))
        ecrire(Tw(r"\textbf{3.} Efforts dans les barres dessinés \textbf{sortants} (barres supposées \textbf{tendues})."))
        self.play(GrowArrow(e1[1]), GrowArrow(e2[1]), Write(e1[2]), Write(e2[2]))
        ecrire(Tw(r"\textbf{4.} On ajoute les charges appliquées au nœud : $F$."))
        self.play(Indicate(F, color=YELLOW))
        self.etape()
        ecrire(Tw(r"\textbf{5.} Équilibre du nœud ($N_2$ est à $45^\circ$) :"))
        ecrire(MathTex(r"\sum F_Y = -F - N_2\sin45^\circ = 0 \Rightarrow N_2 = -F\sqrt2",
                       font_size=FS_EQ - 8))
        ecrire(MathTex(r"\sum F_X = -N_1 - N_2\cos45^\circ = 0 \Rightarrow N_1 = F", font_size=FS_EQ - 8))
        self.etape()
        ecrire(Tw(r"$N_1 = 7$ kN, \ $N_2 = -7\sqrt2 \approx -9{,}9$ kN.\\\textbf{6.} Conclure : $N_1 > 0$ \textbf{tendue}, \ $N_2 < 0$ \textbf{comprimée}."))
        b1 = tr.barre(1, C_TRAC, 10)
        b2 = tr.barre(2, C_COMP, 10)
        self.play(FadeOut(e1), FadeOut(e2), Create(b1), Create(b2))
        self.etape()

        # nœud C
        effacer()
        ecrire(Tw(r"On recommence au nœud voisin $C$ ($N_2$ est connu, il reste $N_3$) :"))
        self.play(XC.animate.set_opacity(1))
        e2c = tr.effort(2, "C", "N_2", cote_lab=RIGHT)
        e3c = tr.effort(3, "C", "N_3", cote_lab=LEFT)
        self.play(Create(e2c[0]), Create(e3c[0]), GrowArrow(e2c[1]), GrowArrow(e3c[1]), Write(e2c[2]), Write(e3c[2]))
        ecrire(MathTex(r"\sum F_Y = N_3 + N_2\sin45^\circ = 0 \Rightarrow N_3 = +7~\mathrm{kN}", font_size=FS_EQ - 8))
        ecrire(MathTex(r"\sum F_X = X_C + N_2\cos45^\circ = 7 - 7 = 0 \quad \checkmark", font_size=FS_EQ - 8, color=C_POS))
        b3 = tr.barre(3, C_TRAC, 10)
        self.play(FadeOut(e2c), FadeOut(e3c), Create(b3))
        ecrire(Tw(r"$N_3 > 0$ : barre 3 \textbf{tendue}."))
        self.etape()

        # vérification en A + bilan
        effacer()
        self.play(VGroup(XA, YA).animate.set_opacity(1))
        ecrire(Tw(r"Vérification au nœud $A$ :"))
        ecrire(MathTex(r"X_A + N_1 = -7 + 7 = 0 \qquad Y_A - N_3 = 7 - 7 = 0 \quad \checkmark", font_size=FS_EQ - 8,
                       color=C_POS))
        ecrire(Tw(r"Une barre a le \textbf{même} $N$ (valeur et signe) à ses deux extrémités.", color=YELLOW))
        vals = VGroup(
            MathTex(r"N_1 = +7", color=C_TRAC, font_size=FS_TEXTE).next_to((tr.p("A") + tr.p("B")) / 2, UP, buff=0.15),
            MathTex(r"N_2 \approx -9{,}9", color=C_COMP, font_size=FS_TEXTE).move_to((tr.p("B") + tr.p("C")) / 2 + 0.55 * np.array([0.7, -0.7, 0])),
            MathTex(r"N_3 = +7", color=C_TRAC, font_size=FS_TEXTE).next_to((tr.p("A") + tr.p("C")) / 2, RIGHT, buff=0.15),
        )
        self.play(FadeOut(fantome), *map(Write, vals))
        leg = VGroup(T(r"rouge : tendue", color=C_TRAC, font_size=FS_TEXTE - 4),
                     T(r"bleu : comprimée", color=C_COMP, font_size=FS_TEXTE - 4)).arrange(RIGHT, buff=0.6)
        leg.to_edge(DOWN, buff=0.3).set_x(-3.5)
        self.play(Write(leg))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. Méthode de la section (coupure de 3 barres)
# ---------------------------------------------------------------------------
class TreillisMethodeSection(Base):
    def construct(self):
        titre = self.titre(r"Treillis : méthode de la section (coupure de 3 barres)")
        self.play(Write(titre))
        noeuds = {}
        for i in range(7):
            noeuds[f"b{i}"] = (2 * i, 0)
            noeuds[f"h{i}"] = (2 * i, 2)
        barres = {}
        k = 1
        for i in range(6):
            barres[f"inf{i}"] = (f"b{i}", f"b{i+1}")
            barres[f"sup{i}"] = (f"h{i}", f"h{i+1}")
        for i in range(7):
            barres[f"v{i}"] = (f"b{i}", f"h{i}")
        for i in range(3):
            barres[f"d{i}"] = (f"b{i}", f"h{i+1}")
        for i in range(3, 6):
            barres[f"d{i}"] = (f"b{i+1}", f"h{i}")
        tr = Treillis(noeuds, barres, origine=(-5.7, 0.15), s=0.95)
        bars, nds, _ = tr.dessin()
        sA = symbole_articulation(tr.p("b0"), s=0.35)
        sB = symbole_appui(tr.p("b6"), s=0.35)
        charges = VGroup(*[force(tr.p(f"h{i}") + 0.8 * UP, tr.p(f"h{i}") + 0.1 * UP, couleur=C_FORCE) for i in range(1, 6)])
        lF = VGroup(*[MathTex("F", color=C_FORCE, font_size=FS_TEXTE).next_to(c.get_start(), RIGHT, buff=0.05) for c in charges])
        lA = MathTex("A", font_size=FS_EQ).next_to(tr.p("b0"), LEFT, buff=0.25)
        nums = VGroup(*[VGroup(Circle(radius=0.18, stroke_color=WHITE, stroke_width=2, fill_color=BLACK, fill_opacity=1),
                               MathTex(t, font_size=20)).move_to(p) for t, p in
                        [("10", tr.p("b2") + 0.95 * RIGHT + 0.3 * DOWN), ("11", (tr.p("b2") + tr.p("h3")) / 2 + 0.3 * RIGHT + 0.15 * DOWN),
                         ("12", tr.p("h2") + 0.95 * RIGHT + 0.3 * UP)]])
        lc = MathTex(r"\ell", font_size=FS_TEXTE, color=C_LEVIER).next_to(tr.p("h0") + 0.95 * DOWN, LEFT, buff=0.1)
        self.play(Create(bars), FadeIn(nds), FadeIn(sA), FadeIn(sB), Write(lA))
        self.play(*map(GrowArrow, charges), Write(lF), FadeIn(nums), Write(lc))
        P = Panneau(-6.6, -1.15, gap=0.2)
        self.contenu = []

        def ecrire(m, gap=None):
            P.placer(m, gap=gap)
            self.contenu.append(m)
            self.play(Write(m))
            return m

        ecrire(T(r"Treillis long : on veut $N_{10}$, $N_{11}$, $N_{12}$ \textbf{sans} passer par tous les nœuds."))
        ecrire(T(r"On coupe \textbf{toute} la structure en traversant \textbf{au plus 3 barres}, et on garde un côté (ici la gauche)."))
        xcut = tr.p("b2")[0] + 0.95
        cut = DashedLine([xcut, -0.5, 0], [xcut, 2.6, 0], color=YELLOW, stroke_width=4)
        self.play(Create(cut))
        self.etape()

        # on garde la gauche
        droite = VGroup(*[b for n, b in zip(barres, bars) if tr.P[barres[n][0]][0] > xcut + 0.01 or tr.P[barres[n][1]][0] > xcut + 0.01],
                        *[nd for k_, nd in zip(noeuds, nds) if tr.P[k_][0] > xcut], sB, charges[2:], lF[2:])
        coupees = VGroup(*[b for n, b in zip(barres, bars) if n in ("inf2", "sup2", "d2")])
        self.play(droite.animate.set_opacity(0.1), coupees.animate.set_opacity(0.1))
        tronc = VGroup(Line(tr.p("b2"), [xcut, tr.p("b2")[1], 0], color=C_BARRE, stroke_width=8),
                       Line(tr.p("h2"), [xcut, tr.p("h2")[1], 0], color=C_BARRE, stroke_width=8),
                       Line(tr.p("b2"), tr.p("b2") + 0.95 * np.array([0.5, 0.5, 0]), color=C_BARRE, stroke_width=8))
        self.play(Create(tronc))
        XA = VGroup(force(tr.p("b0") + 0.9 * LEFT, tr.p("b0") + 0.1 * LEFT, couleur=C_REACTION),
                    MathTex("X_A = 0", color=C_REACTION, font_size=FS_TEXTE).next_to(tr.p("b0") + 0.9 * LEFT, UP, buff=0.05))
        YA = VGroup(force(tr.p("b0") + 0.9 * DOWN, tr.p("b0") + 0.1 * DOWN, couleur=C_REACTION),
                    MathTex(r"Y_A = \tfrac{5F}{2}", color=C_REACTION, font_size=FS_TEXTE).next_to(tr.p("b0") + 0.9 * DOWN, RIGHT, buff=0.05))
        self.play(FadeOut(sA), FadeOut(lA), GrowArrow(XA[0]), Write(XA[1]), GrowArrow(YA[0]), Write(YA[1]))
        u11 = np.array([1, 1, 0]) / np.sqrt(2)
        p10, p12 = np.array([xcut, tr.p("b2")[1], 0]), np.array([xcut, tr.p("h2")[1], 0])
        p11 = tr.p("b2") + 0.95 * np.array([0.5, 0.5, 0])
        N10 = VGroup(force(p10, p10 + 0.9 * RIGHT, couleur=C_INT), MathTex("N_{10}", color=C_INT, font_size=FS_TEXTE).next_to(p10 + 0.9 * RIGHT, DOWN, buff=0.05))
        N11 = VGroup(force(p11, p11 + 0.9 * u11, couleur=C_INT), MathTex("N_{11}", color=C_INT, font_size=FS_TEXTE).next_to(p11 + 0.9 * u11, RIGHT, buff=0.05))
        N12 = VGroup(force(p12, p12 + 0.9 * RIGHT, couleur=C_INT), MathTex("N_{12}", color=C_INT, font_size=FS_TEXTE).next_to(p12 + 0.9 * RIGHT, UP, buff=0.05))
        self.play(*[GrowArrow(n[0]) for n in (N10, N11, N12)], *[Write(n[1]) for n in (N10, N11, N12)])
        self.play(*map(FadeOut, self.contenu))
        self.contenu = []
        P.reset()
        ecrire(T(r"Partie gauche : réactions connues ($X_A = 0$, $Y_A = 5F/2$), 3 inconnues $N_{10}$, $N_{11}$, $N_{12}$"
                 r" (dessinées \textbf{sortantes}) $\Rightarrow$ 3 équations du PFS."))
        self.etape()

        # ΣM en E
        E = tr.p("b2")
        dE = Dot(E, color=YELLOW, radius=0.09)
        lE = MathTex("E", color=YELLOW, font_size=FS_EQ).next_to(E, DL, buff=0.08)
        self.play(FadeIn(dE), Write(lE), Indicate(VGroup(N10, N11), color=YELLOW))
        ecrire(T(r"$\sum M$ en $E$, \textbf{intersection des barres 10 et 11} : leurs moments sont nuls, seule $N_{12}$ reste !",
                 color=YELLOW))
        eqE = ecrire(MathTex(r"\sum M_{/E} = -2\ell\,Y_A + \ell F - \ell\,N_{12} = 0 \Rightarrow N_{12} = -4F", font_size=FS_EQ - 4))
        self.etape()
        # on fait de la place : on garde seulement l'équation en E
        self.play(*[FadeOut(m) for m in self.contenu if m is not eqE])
        self.contenu = [eqE]
        P.reset()
        self.play(eqE.animate.move_to([P.x + eqE.width / 2, P.y - eqE.height / 2, 0]))
        P.y -= eqE.height + P.gap
        ecrire(MathTex(r"\sum F_Y = Y_A - 2F + \frac{N_{11}}{\sqrt2} = 0 \Rightarrow N_{11} = -\frac{F}{\sqrt2}", font_size=FS_EQ - 4))
        ecrire(MathTex(r"\sum F_X = X_A + N_{10} + \frac{N_{11}}{\sqrt2} + N_{12} = 0 \Rightarrow N_{10} = \frac{9F}{2}",
                       font_size=FS_EQ - 4))
        self.etape()
        self.play(*map(FadeOut, self.contenu))
        self.contenu = []
        P.reset()
        self.play(tronc[0].animate.set_color(C_TRAC), tronc[1].animate.set_color(C_COMP), tronc[2].animate.set_color(C_COMP))
        ecrire(T(r"$N_{10} = +\frac{9F}{2}$ : \textbf{tendue} (membrure inférieure) \qquad "
                 r"$N_{12} = -4F$ : \textbf{comprimée} (membrure supérieure)"))
        ecrire(T(r"$N_{11} = -\frac{F}{\sqrt2}$ : diagonale \textbf{comprimée}."))
        ecrire(T(r"Remarque : $\sum M_{/H} = 0$, avec $H$ intersection des barres 11 et 12, donne directement $N_{10}$.",
                 color=GREY_B, font_size=FS_TEXTE - 4))
        self.etape(2)


# ---------------------------------------------------------------------------
# 5. Pièges et astuces
# ---------------------------------------------------------------------------
class TreillisPieges(Base):
    def construct(self):
        titre = self.titre(r"Treillis : pièges et astuces")
        self.play(Write(titre))
        items = [
            r"Vérifier d'abord que $H = b + r - 2n = 0$ (isostatique).",
            r"Méthode des nœuds : commencer par un nœud à \textbf{2 barres inconnues} (seulement 2 équations).",
            r"Dessiner les efforts \textbf{sortants} du nœud (barres supposées \textbf{tendues}).",
            r"Conclure : $N > 0$ tendue, \ $N < 0$ comprimée, \ $N = 0$ non sollicitée.",
            r"Une barre a le \textbf{même} $N$ à ses deux extrémités : la flèche change de sens d'un nœud à l'autre.",
            r"On peut projeter sur deux axes \textbf{quelconques} (non colinéaires) pour simplifier.",
            r"Commencer loin des appuis permet de ne pas dépendre d'une erreur sur les réactions.",
            r"Méthode de la section : couper \textbf{au plus 3 barres}, $\sum M$ à l'intersection de 2 d'entre elles.",
            r"Astuce : nœud non chargé à 2 barres non alignées $\Rightarrow$ les 2 barres ont $N = 0$.",
        ]
        lignes = VGroup(*[
            VGroup(MathTex(r"\checkmark", color=C_POS, font_size=FS_TEXTE), T(t, font_size=FS_TEXTE - 2))
            .arrange(RIGHT, buff=0.2) for t in items
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.24).next_to(titre, DOWN, buff=0.4)
        if lignes.width > 13.4:
            lignes.scale_to_fit_width(13.4)
        if lignes.height > 6.6:
            lignes.scale_to_fit_height(6.6).next_to(titre, DOWN, buff=0.3)
        lignes.set_x(0)
        for l in lignes:
            self.play(FadeIn(l, shift=0.2 * RIGHT), run_time=0.6)
            self.wait(0.4)
        self.etape(2)
