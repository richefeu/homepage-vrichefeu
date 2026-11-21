"""
MS1 - Animations pédagogiques : tracer les diagrammes N, V, M sans écrire les équations (§4.3 du poly)

Scènes :
    DiagrammeN              N « intuitif » : qui tire, qui pousse ; constant par tronçon ; balayage ; poteau
    DiagrammeVPonctuelle    balayage de droite à gauche : on monte / descend de la valeur des forces
    DiagrammeVRepartie      charge répartie : on descend progressivement (pente q) ; position où V = 0
    DiagrammeMVelo          M' = −V, M = 0 aux extrémités libres en rotation, astuce du vélo
    DiagrammeMAires         M(X) = −(aire à gauche) = +(aire à droite) sur le diagramme de V
    DiagrammesSynthese      poutre avec porte-à-faux et charge partielle : V puis M, pas à pas

Vidéo  : manim -qh diagrammes.py DiagrammeN DiagrammeVPonctuelle DiagrammeVRepartie DiagrammeMVelo \
             DiagrammeMAires DiagrammesSynthese
Slides : manim-slides render -qh diagrammes.py <scènes>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403

C_TRAC = RED_C       # traction
C_COMP = BLUE_C      # compression


def velo(couleur=WHITE):
    """Petit vélo tourné vers la GAUCHE, posé sur l'origine (roues tangentes à y = 0)."""
    r = 0.12
    rav = Circle(radius=r).move_to([-0.2, r, 0])
    rar = Circle(radius=r).move_to([0.2, r, 0])
    cadre = VGroup(Line([0.2, r, 0], [0.0, r, 0]), Line([0.0, r, 0], [-0.08, 0.34, 0]),
                   Line([0.2, r, 0], [0.06, 0.34, 0]), Line([-0.08, 0.34, 0], [0.06, 0.34, 0]),
                   Line([-0.2, r, 0], [-0.12, 0.42, 0]), Line([-0.12, 0.42, 0], [-0.2, 0.44, 0]),
                   Line([0.06, 0.34, 0], [0.09, 0.4, 0]))
    return VGroup(rav, rar, cadre).set_stroke(couleur, width=3)


class DiagScene(EIScene):
    """Poutre en haut à gauche, diagrammes dessous, commentaires à droite."""

    def setup_poutre(self, L, largeur=7.8, xc=-1.15):
        self.repere(L, largeur=largeur, xc=xc)
        self.com = None

    def dire(self, texte, couleur=WHITE, y=-0.35):
        # boîte de largeur fixe (≈ 4,1 unités) : retour à la ligne automatique, taille constante
        m = Tex(r"\begin{minipage}{4.8cm}\raggedright " + texte + r"\end{minipage}",
                font_size=FS_TEXTE - 4, color=couleur)
        m.move_to([2.9 + m.width / 2, y - m.height / 2, 0])
        anims = [Write(m)]
        if self.com is not None:
            anims.insert(0, FadeOut(self.com))
        self.play(*anims)
        self.com = m
        return m

    def axe(self, y0, ech, nom, couleur):
        a = Line(self.D(0, 0, y0, ech), self.D(self.L, 0, y0, ech), color=GREY_B, stroke_width=2)
        lab = MathTex(nom, color=couleur, font_size=FS_TEXTE).next_to(a, LEFT, buff=0.25)
        return VGroup(a, lab)

    def seg(self, x1, v1, x2, v2, y0, ech, couleur):
        return Line(self.D(x1, v1, y0, ech), self.D(x2, v2, y0, ech), color=couleur, stroke_width=5)

    def curseur(self, x, y_bas):
        return DashedLine(self.X(x, 0.8), [self.X(x)[0], y_bas, 0], color=YELLOW, stroke_width=3,
                          dash_length=0.1)

    def fond(self, morceaux, y0, ech, couleur, opacite=0.25, n=40):
        pts = []
        for x1, x2, f in morceaux:
            for x in np.linspace(x1, x2, n):
                pts.append(self.D(x, f(x), y0, ech))
        return Polygon(self.D(morceaux[0][0], 0, y0, ech), *pts, self.D(morceaux[-1][1], 0, y0, ech),
                       stroke_width=0, fill_color=couleur, fill_opacity=opacite)

    def courbe(self, f, x1, x2, y0, ech, couleur, n=80):
        pts = [self.D(x, f(x), y0, ech) for x in np.linspace(x1, x2, n)]
        return VMobject(stroke_color=couleur, stroke_width=5).set_points_as_corners(pts)

    def balade_velo(self, fM, dM, y0, ech, couleur, x_debut, x_fin, run_time=5):
        """Le vélo roule de x_debut vers x_fin (vers la gauche) en traçant M."""
        if getattr(self, "_velo", None) is not None:
            self.remove(self._velo)   # un seul vélo à l'écran
        t = ValueTracker(x_debut)
        trace = always_redraw(lambda: self.courbe(fM, t.get_value(), x_debut, y0, ech, couleur, n=60)
                              if x_debut - t.get_value() > 1e-3 else VMobject())

        def placer():
            x = t.get_value()
            pente = ech * dM(x) / self.s
            v = velo()
            v.rotate(np.arctan(pente), about_point=ORIGIN)
            v.shift(self.D(x, fM(x), y0, ech))
            return v
        bike = always_redraw(placer)
        self.add(trace, bike)
        self.play(t.animate.set_value(x_fin), run_time=run_time, rate_func=linear)
        trace.clear_updaters()
        bike.clear_updaters()
        self._velo = bike
        return trace, bike


# ---------------------------------------------------------------------------
# 1. Effort normal N : intuitif
# ---------------------------------------------------------------------------
class DiagrammeN(DiagScene):
    def construct(self):
        titre = self.titre(r"Diagramme de l'effort normal $N(x)$ : l'intuition")
        self.play(Write(titre))

        # --- traction / compression sur un petit élément
        c1, c2 = np.array([-3.5, 0.6, 0]), np.array([3.5, 0.6, 0])
        b1 = Rectangle(width=2.4, height=0.5, color=GREY_A, fill_color=GREY_D, fill_opacity=1).move_to(c1)
        b2 = Rectangle(width=2.4, height=0.5, color=GREY_A, fill_color=GREY_D, fill_opacity=1).move_to(c2)
        t1 = VGroup(force(c1 + 1.25 * RIGHT, c1 + 2.2 * RIGHT, couleur=C_TRAC),
                    force(c1 + 1.25 * LEFT, c1 + 2.2 * LEFT, couleur=C_TRAC))
        t2 = VGroup(force(c2 + 2.2 * RIGHT, c2 + 1.25 * RIGHT, couleur=C_COMP),
                    force(c2 + 2.2 * LEFT, c2 + 1.25 * LEFT, couleur=C_COMP))
        l1 = T(r"on \textbf{tire} : la barre s'allonge\\\textbf{traction}, $N > 0$", color=C_TRAC).next_to(b1, DOWN, buff=0.6)
        l2 = T(r"on \textbf{pousse} : la barre se raccourcit\\\textbf{compression}, $N < 0$", color=C_COMP).next_to(b2, DOWN, buff=0.6)
        self.play(FadeIn(b1), FadeIn(b2))
        self.play(GrowArrow(t1[0]), GrowArrow(t1[1]))
        self.play(b1.animate.stretch(1.25, 0).set_fill(C_TRAC, 0.6), t1[0].animate.shift(0.3 * RIGHT),
                  t1[1].animate.shift(0.3 * LEFT), run_time=1.2)
        self.play(Write(l1))
        self.play(GrowArrow(t2[0]), GrowArrow(t2[1]))
        self.play(b2.animate.stretch(0.8, 0).set_fill(C_COMP, 0.6), t2[0].animate.shift(0.24 * LEFT),
                  t2[1].animate.shift(0.24 * RIGHT), run_time=1.2)
        self.play(Write(l2))
        r = T(r"Seules les forces \textbf{parallèles à la barre} créent $N$. "
              r"En MS1, $N$ est \textbf{constant par tronçon}.", color=YELLOW).to_edge(DOWN, buff=0.8)
        self.play(Write(r))
        self.etape()

        # --- exemple : poutre avec force inclinée
        self.tout_effacer(garder=[titre])
        L, xc = 6, 2
        self.setup_poutre(L)
        AC = poutre(self.X(0), self.X(xc))
        CB = poutre(self.X(xc), self.X(L))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", L)
        pts = VGroup(self.point(0, "A", DOWN), self.point(xc, "C", DL), self.point(L, "B", UR))
        FX = self.charge_vec(xc, 1.0 * RIGHT, r"F_X = 6~\mathrm{kN}", couleur=C_FX, cote_lab=UP)
        FX.shift(1.0 * RIGHT)
        FX[1].next_to(FX[0], DOWN, buff=0.1).shift(0.4 * RIGHT)
        FY = self.charge(xc, r"F_Y = 8~\mathrm{kN}", couleur=C_FY)
        FY[1].shift(0.6 * LEFT)
        self.play(Create(AC), Create(CB), FadeIn(lA), FadeIn(lB), FadeIn(pts))
        self.play(GrowArrow(FX[0]), Write(FX[1]), GrowArrow(FY[0]), Write(FY[1]))
        XA = self.reaction("X", 0, r"X_A = -6")
        XA[1].set_color(C_NEG)
        XA[0].set_color(C_NEG)
        XA[0].rotate(PI)
        self.play(FadeOut(lA), GrowArrow(XA[0]), Write(XA[1]))
        self.dire(r"Seules les forces \textbf{horizontales} comptent : $F_X$ (tire vers la droite) "
                  r"et la réaction $X_A$ (6 kN vers la gauche).")
        self.etape()

        # AC est étiré, CB est libre
        self.play(AC.animate.set_stroke(C_TRAC, width=14), Indicate(XA, color=YELLOW), Indicate(FX, color=YELLOW))
        self.play(AC.animate.stretch(1.03, 0, about_point=self.X(0)), rate_func=there_and_back, run_time=1.2)
        self.dire(r"Entre $A$ et $C$ : tiré à gauche \textbf{et} à droite $\Rightarrow$ \textbf{traction}, $N = +6$ kN.",
                  couleur=C_TRAC)
        self.etape(0.5)
        self.play(Indicate(CB, color=YELLOW))
        self.dire(r"Entre $C$ et $B$ : aucune force horizontale à droite (l'appui ne retient que verticalement) "
                  r"$\Rightarrow$ $N = 0$.")
        yN, eN = -1.6, 0.13
        ax = self.axe(yN, eN, "N", C_FX)
        self.play(Create(ax[0]), Write(ax[1]))
        diagN = VGroup(self.seg(xc, 0, xc, 6, yN, eN, C_TRAC), self.seg(xc, 6, 0, 6, yN, eN, C_TRAC),
                       self.seg(0, 6, 0, 0, yN, eN, C_TRAC))
        fondN = VGroup(self.fond([(0, xc, lambda x: 6)], yN, eN, C_TRAC), self.valeur_diag(1, 6, yN, eN, "+6~\\mathrm{kN}", UP))
        self.play(*map(Create, diagN))
        self.play(FadeIn(fondN))
        self.etape()

        # balayage : même principe que pour V
        self.dire(r"\textbf{Balayage} de droite à gauche : une force horizontale vers la \textbf{droite} "
                  r"fait \textbf{monter} $N$, vers la \textbf{gauche} le fait \textbf{descendre}.", couleur=YELLOW)
        cur = self.curseur(L, yN - 0.3)
        self.play(Create(cur))
        self.play(cur.animate.move_to([self.X(xc)[0], cur.get_center()[1], 0]), run_time=1.5)
        self.play(Indicate(FX, color=YELLOW))
        self.play(cur.animate.move_to([self.X(0)[0], cur.get_center()[1], 0]), run_time=1.5)
        self.play(Indicate(XA, color=YELLOW))
        self.dire(r"En $A$, $X_A$ (vers la gauche) fait redescendre à 0 : \checkmark", couleur=C_POS)
        self.play(FadeOut(cur))
        self.etape()

        # compression si F_X pousse vers la gauche
        FX2 = self.charge_vec(xc, 1.0 * LEFT, r"F_X = 6~\mathrm{kN}", couleur=C_FX, cote_lab=UP)
        FX2[1].next_to(FX2[0], DOWN, buff=0.1).shift(0.4 * RIGHT)
        self.play(ReplacementTransform(FX, FX2), AC.animate.set_stroke(C_COMP, width=14),
                  XA[0].animate.rotate(PI).set_color(C_REACTION), Transform(XA[1], MathTex(r"X_A = +6", color=C_REACTION,
                  font_size=FS_TEXTE).move_to(XA[1])))
        self.play(AC.animate.stretch(0.97, 0, about_point=self.X(0)), rate_func=there_and_back, run_time=1.2)
        self.dire(r"Si $F_X$ \textbf{pousse} vers la gauche : $AC$ est \textbf{comprimé}, $N = -6$ kN.", couleur=C_COMP)
        nouv = VGroup(self.seg(xc, 0, xc, -6, yN, eN, C_COMP), self.seg(xc, -6, 0, -6, yN, eN, C_COMP),
                      self.seg(0, -6, 0, 0, yN, eN, C_COMP), self.fond([(0, xc, lambda x: -6)], yN, eN, C_COMP),
                      self.valeur_diag(1, -6, yN, eN, "-6~\\mathrm{kN}", DOWN))
        self.play(FadeOut(diagN), FadeOut(fondN))
        self.play(*map(Create, nouv))
        self.etape()

        # poteau
        self.tout_effacer(garder=[titre])
        self.com = None
        base = np.array([-3.0, -3.0, 0])
        haut = base + 4.4 * UP
        pot = poutre(base, haut, epaisseur=14)
        enc = symbole_encastrement(base, s=1.4)
        P = force(haut + 1.3 * UP, haut, couleur=C_FORCE)
        lP = MathTex(r"P", color=C_FORCE, font_size=FS_EQ).next_to(P, RIGHT)
        self.play(FadeIn(enc), Create(pot), GrowArrow(P), Write(lP))
        self.play(pot.animate.set_stroke(C_COMP, width=18))
        self.play(pot.animate.stretch(0.95, 1, about_point=base), rate_func=there_and_back, run_time=1.2)
        t = T(r"Un \textbf{poteau} qui porte une charge :\\il est écrasé $\Rightarrow$ \textbf{compression}"
              r"\\$N = -P$ sur toute sa hauteur.", color=C_COMP).move_to([2.2, 0.3, 0])
        self.play(Write(t))
        t2 = T(r"Dans les poutres $N \neq 0$ parfois ;\\dans les poteaux, \textbf{toujours}.", color=YELLOW,
               font_size=FS_TEXTE - 2).next_to(t, DOWN, buff=0.6)
        self.play(Write(t2))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. V : forces ponctuelles (exemple du poly)
# ---------------------------------------------------------------------------
class DiagrammeVPonctuelle(DiagScene):
    def construct(self):
        titre = self.titre(r"Tracer $V(x)$ directement : forces ponctuelles")
        self.play(Write(titre))
        L, xc = 6, 3
        self.setup_poutre(L)
        barre = poutre(self.X(0), self.X(L))
        pts = VGroup(self.point(0, "A", UL), self.point(xc, "C", UR), self.point(L, "B", UR))
        F = self.charge(xc, r"F")
        YA = self.reaction("Y", 0, r"\tfrac{F}{2}")
        YB = self.reaction("Y", L, r"\tfrac{F}{2}")
        self.play(Create(barre), FadeIn(pts), GrowArrow(F[0]), Write(F[1]))
        self.play(GrowArrow(YA[0]), Write(YA[1]), GrowArrow(YB[0]), Write(YB[1]))
        self.dire(r"Réactions (calculées avant) : $Y_A = Y_B = F/2$.\\"
                  r"On \textbf{balaie la poutre de la droite vers la gauche}.")
        yV, eV = -1.9, 2.2
        ax = self.axe(yV, eV, "V", C_FY)
        self.play(Create(ax[0]), Write(ax[1]))
        cur = self.curseur(L + 0.15, yV - 1.4)
        self.play(Create(cur))
        self.etape()

        def aller(x, rt=1.2):
            self.play(cur.animate.set_x(self.X(x)[0]), run_time=rt)

        aller(L, 0.6)
        self.play(Indicate(YB, color=YELLOW))
        self.dire(r"En $B$ : $Y_B = F/2$ \textbf{vers le haut} $\Rightarrow$ on \textbf{monte} de $F/2$.")
        self.play(Create(self.seg(L, 0, L, 0.5, yV, eV, C_FY)))
        self.etape(0.5)
        self.dire(r"De $B$ à $C$ : aucune force $\Rightarrow$ \textbf{palier} horizontal.")
        self.play(Create(self.seg(L, 0.5, xc, 0.5, yV, eV, C_FY)), cur.animate.set_x(self.X(xc)[0]), run_time=1.5)
        self.etape(0.5)
        self.play(Indicate(F, color=YELLOW))
        self.dire(r"En $C$ : $F$ \textbf{vers le bas} $\Rightarrow$ on \textbf{descend} de $F$ : $F/2 - F = -F/2$.")
        self.play(Create(self.seg(xc, 0.5, xc, -0.5, yV, eV, C_FY)))
        self.etape(0.5)
        self.dire(r"De $C$ à $A$ : aucune force $\Rightarrow$ palier.")
        self.play(Create(self.seg(xc, -0.5, 0, -0.5, yV, eV, C_FY)), cur.animate.set_x(self.X(0)[0]), run_time=1.5)
        self.etape(0.5)
        self.play(Indicate(YA, color=YELLOW))
        self.dire(r"En $A$ : on remonte de $Y_A = F/2$ : on retombe \textbf{sur l'axe} \checkmark\\"
                  r"(sinon, il y a une erreur quelque part !)", couleur=C_POS)
        self.play(Create(self.seg(0, -0.5, 0, 0, yV, eV, C_FY)))
        self.play(FadeOut(cur), FadeIn(self.fond([(0, xc, lambda x: -0.5), (xc, L, lambda x: 0.5)], yV, eV, C_FY)),
                  Write(self.valeur_diag(4.5, 0.5, yV, eV, r"+\tfrac{F}{2}", UP)),
                  Write(self.valeur_diag(1.5, -0.5, yV, eV, r"-\tfrac{F}{2}", DOWN)))
        self.etape()
        self.dire(r"\textbf{Règle} : de droite à gauche,\\force vers le \textbf{haut} $\to$ on \textbf{monte},\\"
                  r"vers le \textbf{bas} $\to$ on \textbf{descend},\\de la valeur de la force.", couleur=YELLOW)
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. V : charge répartie (exemple du poly)
# ---------------------------------------------------------------------------
class DiagrammeVRepartie(DiagScene):
    def construct(self):
        titre = self.titre(r"Tracer $V(x)$ directement : charge répartie")
        self.play(Write(titre))
        L = 6
        self.setup_poutre(L)
        barre = poutre(self.X(0), self.X(L))
        pts = VGroup(self.point(0, "A", UL), self.point(L, "B", UR))
        q = self.repartie(0, L, r"q")
        YA = self.reaction("Y", 0, r"\tfrac{qL}{2}")
        YB = self.reaction("Y", L, r"\tfrac{qL}{2}")
        self.play(Create(barre), FadeIn(pts), LaggedStart(*[GrowArrow(a) for a in q[0]], lag_ratio=0.04),
                  Create(q[1]), Write(q[2]))
        self.play(GrowArrow(YA[0]), Write(YA[1]), GrowArrow(YB[0]), Write(YB[1]))
        yV, eV = -1.9, 2.2
        ax = self.axe(yV, eV, "V", C_FY)
        self.play(Create(ax[0]), Write(ax[1]))
        cur = self.curseur(L, yV - 1.4)
        self.play(Create(cur), Indicate(YB, color=YELLOW))
        self.dire(r"En $B$ : on \textbf{monte} de $Y_B = qL/2$.")
        self.play(Create(self.seg(L, 0, L, 0.5, yV, eV, C_FY)))
        self.etape(0.5)
        self.dire(r"De $B$ vers $A$ : la charge répartie (vers le bas) fait \textbf{descendre progressivement} :"
                  r" une \textbf{droite} de pente $q$, qui descend de $qL$ en tout.")
        self.play(Create(self.seg(L, 0.5, 0, -0.5, yV, eV, C_FY)), cur.animate.set_x(self.X(0)[0]), run_time=3,
                  rate_func=linear)
        self.etape(0.5)
        self.play(Indicate(YA, color=YELLOW))
        self.dire(r"En $A$ : on remonte de $qL/2$ : retour à 0 \checkmark", couleur=C_POS)
        self.play(Create(self.seg(0, -0.5, 0, 0, yV, eV, C_FY)), FadeOut(cur))
        self.play(FadeIn(self.fond([(0, L, lambda x: (x - L / 2) / L)], yV, eV, C_FY)),
                  Write(self.valeur_diag(L, 0.5, yV, eV, r"+\tfrac{qL}{2}", RIGHT)),
                  Write(self.valeur_diag(0, -0.5, yV, eV, r"-\tfrac{qL}{2}", LEFT)))
        self.etape()

        # où V s'annule-t-il ?
        self.dire(r"\textbf{Où $V$ s'annule-t-il ?} La pente vaut $q$ : en partant d'une valeur $V_b$,"
                  r" on atteint 0 au bout de $b = |V_b|/q$.", couleur=YELLOW)
        tri = Polygon(self.D(L, 0.5, yV, eV), self.D(L / 2, 0, yV, eV), self.D(L, 0, yV, eV),
                      color=YELLOW, stroke_width=3, fill_opacity=0.2, fill_color=YELLOW)
        cb = BraceBetweenPoints(self.D(L / 2, 0, yV, eV), self.D(L, 0, yV, eV), DOWN, color=YELLOW)
        lb = MathTex(r"b = \frac{qL/2}{q} = \frac{L}{2}", color=YELLOW, font_size=FS_TEXTE - 2).next_to(cb, DOWN, buff=0.05)
        self.play(Create(tri))
        self.play(GrowFromCenter(cb), Write(lb))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. M : relation avec V et astuce du vélo
# ---------------------------------------------------------------------------
class DiagrammeMVelo(DiagScene):
    def construct(self):
        titre = self.titre(r"Tracer $M(x)$ directement : l'astuce du vélo")
        self.play(Write(titre))
        rel = MathTex(r"V(x) = -M'(x)", font_size=FS_EQ + 8).next_to(titre, DOWN, buff=0.5)
        b = SurroundingRectangle(rel, color=YELLOW, buff=0.2)
        self.play(Write(rel), Create(b))
        p = VGroup(
            T(r"\textbf{1.} Extrémité \textbf{libre en rotation} (appui, articulation, bout libre) : $M = 0$."),
            T(r"\textbf{2.} En roulant \textbf{de droite à gauche}, $V$ est \textbf{la pente} de la route :"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(b, DOWN, buff=0.5)
        for m in p:
            self.play(Write(m))
        cas = VGroup()
        for i, (txt, ang) in enumerate([(r"$V = 0$ : plat", 0), (r"$V > 0$ : \textbf{montée}", -25),
                                        (r"$V < 0$ : \textbf{descente}", 25)]):
            c = np.array([-4.5 + 4.5 * i, -2.0, 0])
            route = Line(c + 1.0 * LEFT, c + 1.0 * RIGHT, color=GREY_B).rotate(ang * DEGREES, about_point=c)
            v = velo().rotate(ang * DEGREES, about_point=ORIGIN).shift(c)
            fl = Arrow(c + 0.6 * RIGHT + 0.6 * DOWN, c + 0.6 * LEFT + 0.6 * DOWN, buff=0, color=GREY_B,
                       stroke_width=3, max_tip_length_to_length_ratio=0.2).rotate(ang * DEGREES, about_point=c)
            l = T(txt, font_size=FS_TEXTE - 2).next_to(c, DOWN, buff=0.9)
            cas.add(VGroup(route, v, fl, l))
        for c in cas:
            self.play(FadeIn(c))
        self.etape()

        # exemple 1 : force ponctuelle
        self.tout_effacer(garder=[titre])
        L, xc = 6, 3
        self.setup_poutre(L)
        barre = poutre(self.X(0), self.X(L))
        pts = VGroup(self.point(0, "A", UL), self.point(xc, "C", UR), self.point(L, "B", UR))
        F = self.charge(xc, r"F")
        YA, YB = self.reaction("Y", 0, r"\tfrac{F}{2}"), self.reaction("Y", L, r"\tfrac{F}{2}")
        yV, eV, yM, eM = -1.25, 1.6, -3.7, 0.95
        fV = lambda x: -0.5 if x < xc else 0.5
        fM = lambda x: 0.5 * x if x <= xc else 0.5 * (L - x)
        dM = lambda x: 0.5 if x < xc else -0.5
        dV = VGroup(self.axe(yV, eV, "V", C_FY), self.seg(L, 0, L, 0.5, yV, eV, C_FY), self.seg(L, 0.5, xc, 0.5, yV, eV, C_FY),
                    self.seg(xc, 0.5, xc, -0.5, yV, eV, C_FY), self.seg(xc, -0.5, 0, -0.5, yV, eV, C_FY),
                    self.seg(0, -0.5, 0, 0, yV, eV, C_FY),
                    self.fond([(0, xc, lambda x: -0.5), (xc, L, lambda x: 0.5)], yV, eV, C_FY))
        self.play(Create(barre), FadeIn(pts), GrowArrow(F[0]), Write(F[1]), FadeIn(YA), FadeIn(YB))
        self.play(FadeIn(dV))
        axM = self.axe(yM, eM, "M", C_INT)
        self.play(Create(axM[0]), Write(axM[1]))
        self.dire(r"En $B$ (appui) : $M = 0$. Le vélo part de $B$ vers la gauche.")
        self.etape(0.5)
        self.dire(r"De $B$ à $C$ : $V = +F/2 > 0$ $\Rightarrow$ \textbf{montée} régulière (droite).")
        self.balade_velo(fM, dM, yM, eM, C_INT, L, xc, run_time=3)
        mC = self.valeur_diag(xc, 1.5, yM, eM, r"M_C = \tfrac{F}{2}\times\tfrac{L}{2} = \tfrac{FL}{4}", RIGHT, YELLOW)
        mC.shift(0.35 * RIGHT)
        self.play(Write(mC))
        self.etape(0.5)
        self.dire(r"De $C$ à $A$ : $V = -F/2 < 0$ $\Rightarrow$ \textbf{descente}... et on arrive bien à $M = 0$ en $A$ \checkmark")
        tr, bk = self.balade_velo(fM, dM, yM, eM, C_INT, xc, 0, run_time=3)
        self.play(FadeOut(bk), FadeIn(self.fond([(0, L, fM)], yM, eM, C_INT)))
        self.dire(r"Le maximum de $M$ est là où $V$ \textbf{change de signe} (sommet de la route).", couleur=YELLOW)
        self.etape()

        # exemple 2 : charge répartie
        self.tout_effacer(garder=[titre])
        self.com = None
        barre = poutre(self.X(0), self.X(L))
        pts = VGroup(self.point(0, "A", UL), self.point(L, "B", UR))
        q = self.repartie(0, L, r"q")
        YA, YB = self.reaction("Y", 0, r"\tfrac{qL}{2}"), self.reaction("Y", L, r"\tfrac{qL}{2}")
        fV = lambda x: (x - L / 2) / L
        fM = lambda x: x * (L - x) / (2 * L)
        dM = lambda x: (L - 2 * x) / (2 * L)
        eM = 1.1 / (L / 8)
        dV = VGroup(self.axe(yV, eV, "V", C_FY), self.seg(L, 0, L, 0.5, yV, eV, C_FY), self.seg(L, 0.5, 0, -0.5, yV, eV, C_FY),
                    self.seg(0, -0.5, 0, 0, yV, eV, C_FY), self.fond([(0, L, fV)], yV, eV, C_FY))
        self.play(Create(barre), FadeIn(pts), FadeIn(q), FadeIn(YA), FadeIn(YB))
        self.play(FadeIn(dV))
        axM = self.axe(yM, eM, "M", C_INT)
        self.play(Create(axM[0]), Write(axM[1]))
        self.dire(r"$V$ diminue de $B$ vers $A$ : la montée est \textbf{de moins en moins raide}, "
                  r"plate au milieu ($V = 0$), puis la descente s'accentue : une \textbf{parabole}.")
        tr, bk = self.balade_velo(fM, dM, yM, eM, C_INT, L, 0, run_time=6)
        self.play(FadeOut(bk), FadeIn(self.fond([(0, L, fM)], yM, eM, C_INT)),
                  Write(self.valeur_diag(L / 2, L / 8, yM, eM, r"M_{max} = \tfrac{qL^2}{8}", UP, YELLOW)))
        self.etape(2)


# ---------------------------------------------------------------------------
# 5. M par les aires
# ---------------------------------------------------------------------------
class DiagrammeMAires(DiagScene):
    def construct(self):
        titre = self.titre(r"Valeurs de $M$ : les aires sous $V(x)$")
        self.play(Write(titre))
        f1 = MathTex(r"M(X) = -\big(\text{aire à gauche de } X\big) = +\big(\text{aire à droite de } X\big)",
                     font_size=FS_EQ).next_to(titre, DOWN, buff=0.4)
        b = SurroundingRectangle(f1, color=YELLOW, buff=0.15)
        self.play(Write(f1), Create(b))
        self.etape()
        self.play(FadeOut(f1), FadeOut(b))

        L, a = 6, 4
        self.setup_poutre(L)
        barre = poutre(self.X(0), self.X(L))
        pts = VGroup(self.point(0, "A", UL), self.point(a, "C", UR), self.point(L, "B", UR))
        F = self.charge(a, r"F = 6~\mathrm{kN}")
        YA, YB = self.reaction("Y", 0, r"2~\mathrm{kN}"), self.reaction("Y", L, r"4~\mathrm{kN}")
        yV, eV, yM, eM = -1.35, 0.17, -3.65, 0.13
        dV = VGroup(self.axe(yV, eV, "V", C_FY), self.seg(L, 0, L, 4, yV, eV, C_FY), self.seg(L, 4, a, 4, yV, eV, C_FY),
                    self.seg(a, 4, a, -2, yV, eV, C_FY), self.seg(a, -2, 0, -2, yV, eV, C_FY), self.seg(0, -2, 0, 0, yV, eV, C_FY))
        self.play(Create(barre), FadeIn(pts), GrowArrow(F[0]), Write(F[1]), FadeIn(YA), FadeIn(YB))
        self.play(FadeIn(dV), Write(self.valeur_diag(5, 4, yV, eV, "+4", UP)), Write(self.valeur_diag(2, -2, yV, eV, "-2", DOWN)))
        axM = self.axe(yM, eM, "M", C_INT)
        self.play(Create(axM[0]), Write(axM[1]))

        # M en C
        cur = self.curseur(a, yM - 0.2)
        self.play(Create(cur))
        droite = self.fond([(a, L, lambda x: 4)], yV, eV, YELLOW, opacite=0.5)
        self.play(FadeIn(droite))
        self.dire(r"En $C$ : aire à \textbf{droite} = rectangle $4 \times 2 = 8$\\$\Rightarrow M_C = +8$ kN$\cdot$m")
        self.play(Create(Dot(self.D(a, 8, yM, eM), color=YELLOW)),
                  Write(self.valeur_diag(a, 8, yM, eM, "M_C = 8", UP, YELLOW)))
        self.etape(0.5)
        gauche = self.fond([(0, a, lambda x: -2)], yV, eV, ORANGE, opacite=0.5)
        self.play(FadeOut(droite), FadeIn(gauche))
        self.dire(r"Vérification avec la \textbf{gauche} : aire $= -2 \times 4 = -8$\\$\Rightarrow M_C = -(-8) = +8$ \checkmark",
                  couleur=C_POS)
        self.etape()
        self.play(FadeOut(gauche))

        # M en X = 5
        self.play(cur.animate.set_x(self.X(5)[0]))
        d2 = self.fond([(5, L, lambda x: 4)], yV, eV, YELLOW, opacite=0.5)
        self.play(FadeIn(d2))
        self.dire(r"En $x = 5$ m : aire à droite $= 4 \times 1 = 4$ $\Rightarrow M = 4$ kN$\cdot$m")
        self.play(Create(Dot(self.D(5, 4, yM, eM), color=YELLOW)))
        self.etape(0.5)
        self.play(FadeOut(d2), FadeOut(cur))
        courbe = self.courbe(lambda x: 2 * x if x <= a else 8 - 4 * (x - a), 0, L, yM, eM, C_INT)
        self.dire(r"Avec $M = 0$ aux appuis, il suffit de \textbf{relier les points} (droites car $V$ constant).")
        self.play(Create(courbe))
        self.play(FadeIn(self.fond([(0, a, lambda x: 2 * x), (a, L, lambda x: 8 - 4 * (x - a))], yM, eM, C_INT)))
        self.etape()

        # charge répartie : aire du triangle
        self.tout_effacer(garder=[titre])
        self.com = None
        barre = poutre(self.X(0), self.X(L))
        q = self.repartie(0, L, r"q")
        YA, YB = self.reaction("Y", 0, r"\tfrac{qL}{2}"), self.reaction("Y", L, r"\tfrac{qL}{2}")
        eV2 = 2.2
        fV = lambda x: (x - L / 2) / L
        dV = VGroup(self.axe(yV, eV2, "V", C_FY), self.seg(L, 0, L, 0.5, yV, eV2, C_FY), self.seg(L, 0.5, 0, -0.5, yV, eV2, C_FY),
                    self.seg(0, -0.5, 0, 0, yV, eV2, C_FY))
        self.play(Create(barre), FadeIn(q), FadeIn(YA), FadeIn(YB), FadeIn(dV))
        tri = self.fond([(L / 2, L, fV)], yV, eV2, YELLOW, opacite=0.5)
        self.play(FadeIn(tri))
        self.dire(r"$M_{max}$ (où $V = 0$) = aire du \textbf{triangle} à droite :\\"
                  r"$\frac{1}{2}\times\frac{qL}{2}\times\frac{L}{2} = \frac{qL^2}{8}$ \checkmark", couleur=YELLOW)
        self.etape(2)


# ---------------------------------------------------------------------------
# 6. Synthèse : porte-à-faux + charge partielle
# ---------------------------------------------------------------------------
class DiagrammesSynthese(DiagScene):
    def construct(self):
        titre = self.titre(r"Synthèse : tracer $V$ puis $M$ pas à pas")
        self.play(Write(titre))
        L = 8
        self.setup_poutre(L)
        barre = poutre(self.X(0), self.X(L))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 6)
        pts = VGroup(self.point(0, "A", UL), self.point(4, "D", DOWN), self.point(6, "B", UR), self.point(L, "C", UR))
        q = self.repartie(0, 4, r"q = 3~\mathrm{kN/m}")
        P = self.charge(L, r"P = 3~\mathrm{kN}")
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts))
        self.play(LaggedStart(*[GrowArrow(a) for a in q[0]], lag_ratio=0.05), Create(q[1]), Write(q[2]),
                  GrowArrow(P[0]), Write(P[1]))
        YA, YB = self.reaction("Y", 0, r"7~\mathrm{kN}"), self.reaction("Y", 6, r"8~\mathrm{kN}")
        self.play(FadeOut(lA), FadeOut(lB), GrowArrow(YA[0]), Write(YA[1]), GrowArrow(YB[0]), Write(YB[1]))
        self.dire(r"Réactions (calculées avant) : $Y_A = 7$ kN, $Y_B = 8$ kN.\\Pas de force horizontale : $N = 0$.")
        self.etape()

        # V
        yV, eV, yM, eM = -1.3, 0.16, -3.25, 0.12
        ax = self.axe(yV, eV, "V", C_FY)
        self.play(Create(ax[0]), Write(ax[1]))
        cur = self.curseur(L + 0.1, yV - 1.3)
        self.play(Create(cur))
        etapes = [
            (L, [self.seg(L, 0, L, -3, yV, eV, C_FY)], P, r"En $C$ : $P$ vers le bas $\Rightarrow$ on descend de 3 : $V = -3$."),
            (6, [self.seg(L, -3, 6, -3, yV, eV, C_FY)], None, r"De $C$ à $B$ : palier à $-3$."),
            (6, [self.seg(6, -3, 6, 5, yV, eV, C_FY)], YB, r"En $B$ : $Y_B = 8$ vers le haut $\Rightarrow$ on monte de 8 : $V = +5$."),
            (4, [self.seg(6, 5, 4, 5, yV, eV, C_FY)], None, r"De $B$ à $D$ : palier à $+5$."),
            (0, [self.seg(4, 5, 0, -7, yV, eV, C_FY)], q, r"De $D$ à $A$ : $q$ fait descendre de $3 \times 4 = 12$ : de $+5$ à $-7$."),
            (0, [self.seg(0, -7, 0, 0, yV, eV, C_FY)], YA, r"En $A$ : on remonte de 7 : retour à 0 \checkmark"),
        ]
        for x, segs, fl, txt in etapes:
            anims = [cur.animate.set_x(self.X(x)[0])] if abs(cur.get_x() - self.X(x)[0]) > 1e-3 else []
            if fl is not None:
                self.play(Indicate(fl, color=YELLOW))
            self.dire(txt, couleur=C_POS if "checkmark" in txt else WHITE)
            self.play(*map(Create, segs), *anims, run_time=1.4)
            self.wait(0.3)
        x0 = 4 - 5 / 3
        fV = lambda x: 5 - 3 * (4 - x) if x <= 4 else (5 if x <= 6 else -3)
        self.play(FadeOut(cur), FadeIn(self.fond([(0, 4, fV), (4, 6, lambda x: 5), (6, L, lambda x: -3)], yV, eV, C_FY)),
                  Write(self.valeur_diag(7, -3, yV, eV, "-3", DOWN)), Write(self.valeur_diag(5, 5, yV, eV, "+5", UP)),
                  Write(self.valeur_diag(0, -7, yV, eV, "-7", LEFT)))
        z = Dot(self.D(x0, 0, yV, eV), color=YELLOW)
        cb = BraceBetweenPoints(self.D(x0, 0, yV, eV), self.D(4, 0, yV, eV), UP, color=YELLOW)
        lz = MathTex(r"\tfrac{5}{3}", color=YELLOW, font_size=FS_TEXTE - 4).next_to(cb, UP, buff=0.05)
        self.dire(r"$V = 0$ à $\frac{|V_D|}{q} = \frac{5}{3}$ m à gauche de $D$.", couleur=YELLOW)
        self.play(FadeIn(z), GrowFromCenter(cb), Write(lz))
        self.etape()

        # M
        axM = self.axe(yM, eM, "M", C_INT)
        self.play(Create(axM[0]), Write(axM[1]))

        def fM(x):
            if x <= 4:
                return 7 * x - 1.5 * x ** 2
            if x <= 6:
                return 24 - 5 * x
            return -3 * (L - x)

        def dM(x):
            if x <= 4:
                return 7 - 3 * x
            return -5 if x <= 6 else 3
        self.dire(r"En $C$ (bout libre) et en $A$ (articulation) : $M = 0$.")
        self.play(FadeIn(Dot(self.D(L, 0, yM, eM), color=C_INT)), FadeIn(Dot(self.D(0, 0, yM, eM), color=C_INT)))
        self.dire(r"$C \to B$ : $V = -3$, \textbf{descente}. Aire à droite de $B$ : $-3\times2$ $\Rightarrow$ $M_B = -6$.")
        self.balade_velo(fM, dM, yM, eM, C_INT, L, 6, run_time=2.5)
        self.play(Write(self.valeur_diag(6, -6, yM, eM, "-6", DOWN, YELLOW)))
        self.etape(0.5)
        self.dire(r"$B \to D$ : $V = +5$, \textbf{montée}. $M_D = -6 + 5\times2 = 4$.")
        self.balade_velo(fM, dM, yM, eM, C_INT, 6, 4, run_time=2.5)
        self.play(Write(self.valeur_diag(4, 4, yM, eM, "4", UR, YELLOW)))
        self.etape(0.5)
        self.dire(r"$D \to A$ : $V$ passe de $+5$ à $-7$ : montée de plus en plus douce, sommet où $V = 0$, puis descente"
                  r" (parabole). $M_{max} = 4 + \frac{1}{2}\times 5 \times \frac{5}{3} \approx 8{,}17$.")
        tr, bk = self.balade_velo(fM, dM, yM, eM, C_INT, 4, 0, run_time=4)
        self.play(FadeOut(bk), Write(self.valeur_diag(x0, fM(x0), yM, eM, r"8{,}17", UP, YELLOW)))
        self.play(FadeIn(self.fond([(0, L, fM)], yM, eM, C_INT)))
        self.dire(r"On arrive bien à $M = 0$ en $A$ \checkmark\\Moment \textbf{négatif} sur l'appui $B$"
                  r" à cause du porte-à-faux.", couleur=C_POS)
        self.etape(2)
