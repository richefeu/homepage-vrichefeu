"""
MS1 - Animations pédagogiques : décomposition des forces suivant X et Y

Scènes :
    DecompositionForce   F_X = F cos θ, F_Y = F sin θ ; rotation de la force (signes automatiques) ;
                         pièges : angle par rapport à la verticale, direction donnée par une pente
    ResultanteForces     exemple du poly (3 forces) : composantes, résultante, intensité,
                         angle (piège du quadrant avec arctan)

Vidéo  : manim -qh forces.py DecompositionForce ResultanteForces
Slides : manim-slides render -qh forces.py DecompositionForce ResultanteForces
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403


def axes(O, gauche=3.0, droite=3.0, bas=2.5, haut=2.5, fs=FS_EQ):
    ax = VGroup(
        Arrow(O + gauche * LEFT, O + droite * RIGHT, buff=0, stroke_width=2.5, color=GREY_B,
              max_tip_length_to_length_ratio=0.04),
        Arrow(O + bas * DOWN, O + haut * UP, buff=0, stroke_width=2.5, color=GREY_B,
              max_tip_length_to_length_ratio=0.05),
    )
    labs = VGroup(MathTex(r"\vec X", font_size=fs, color=GREY_B).next_to(ax[0].get_end(), DOWN, buff=0.1),
                  MathTex(r"\vec Y", font_size=fs, color=GREY_B).next_to(ax[1].get_end(), LEFT, buff=0.1))
    return VGroup(ax, labs)


def fleche_ou_rien(debut, fin, couleur, epaisseur=7):
    """Flèche, ou rien du tout si elle est trop courte (évite les flèches dégénérées)."""
    if np.linalg.norm(np.array(fin) - np.array(debut)) < 0.06:
        # segment invisible plutôt qu'un objet vide (sinon FadeOut/become plantent)
        return Line(debut, np.array(debut) + 0.01 * RIGHT, stroke_opacity=0)
    return force(debut, fin, couleur=couleur, epaisseur=epaisseur)


# ---------------------------------------------------------------------------
# 1. Décomposition d'une force
# ---------------------------------------------------------------------------
class DecompositionForce(Base):
    def construct(self):
        titre = self.titre(r"Décomposition d'une force suivant $X$ et $Y$")
        self.play(Write(titre))

        O = np.array([-3.8, -0.6, 0])
        k = 0.55                       # longueur de flèche par kN
        Fv = 5.0                        # intensité (kN)
        rep = axes(O, gauche=3.0, droite=3.2, bas=2.9, haut=3.0)
        self.play(FadeIn(rep))

        th = ValueTracker(35 * DEGREES)
        tip = lambda: O + k * Fv * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0])
        F = always_redraw(lambda: force(O, tip(), couleur=WHITE))
        lF = always_redraw(lambda: MathTex(r"\vec F", font_size=FS_EQ).next_to(
            tip(), np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0]), buff=0.1))
        arc = always_redraw(lambda: Arc(radius=0.75, start_angle=0, angle=th.get_value(), arc_center=O,
                                        color=C_LEVIER, stroke_width=3))
        lth = always_redraw(lambda: MathTex(r"\theta", color=C_LEVIER, font_size=FS_EQ).move_to(
            O + 1.05 * np.array([np.cos(th.get_value() / 2), np.sin(th.get_value() / 2), 0])))
        self.play(GrowArrow(F), Write(lF))
        self.add(F, lF)
        self.play(Create(arc), Write(lth))
        self.add(arc, lth)

        P = Panneau(0.4, 2.4, gap=0.28)
        d1 = P.placer(T(r"Une force est définie par :"))
        d2 = P.placer(T(r"\textbf{intensité} $F$ (N), \textbf{inclinaison} $\theta$\\"
                        r"par rapport à $\vec X$, et \textbf{sens}."))
        self.play(Write(d1))
        self.play(Write(d2))
        self.etape()

        # --- projections
        pX = lambda: O + np.array([tip()[0] - O[0], 0, 0])
        pY = lambda: O + np.array([0, tip()[1] - O[1], 0])
        proj = always_redraw(lambda: VGroup(
            DashedLine(tip(), pX(), color=GREY_B, stroke_width=2),
            DashedLine(tip(), pY(), color=GREY_B, stroke_width=2)))
        FX = always_redraw(lambda: fleche_ou_rien(O, pX(), C_FX))
        FY = always_redraw(lambda: fleche_ou_rien(O, pY(), C_FY))
        lFX = always_redraw(lambda: MathTex(r"\vec F_X", color=C_FX, font_size=FS_EQ).next_to(
            pX(), DOWN if tip()[1] >= O[1] else UP, buff=0.12))
        lFY = always_redraw(lambda: MathTex(r"\vec F_Y", color=C_FY, font_size=FS_EQ).next_to(
            pY(), LEFT if tip()[0] >= O[0] else RIGHT, buff=0.12))
        self.play(Create(proj))
        self.add(proj)
        self.play(GrowArrow(FX), GrowArrow(FY))
        self.add(FX, FY)
        self.play(Write(lFX), Write(lFY))
        self.add(lFX, lFY)

        d3 = P.placer(T(r"On \textbf{projette} sur les axes : $\vec F = \vec F_X + \vec F_Y$"))
        self.play(Write(d3))
        tri = P.placer(T(r"Dans le triangle rectangle :\\"
                         r"$\cos\theta = \dfrac{F_X}{F}$, \quad $\sin\theta = \dfrac{F_Y}{F}$"))
        self.play(Write(tri))
        formule = P.placer(MathTex(r"F_X = F\cos\theta \qquad F_Y = F\sin\theta", font_size=FS_EQ + 4))
        formule.shift(0.4 * RIGHT)
        bf = SurroundingRectangle(formule, color=YELLOW, buff=0.18)
        self.play(Write(formule), Create(bf))
        inv = P.placer(T(r"et inversement : $F = \sqrt{F_X^2 + F_Y^2}$"), gap=0.2)
        inv.shift(0.15 * DOWN)
        self.play(Write(inv))
        self.etape()

        # --- la force tourne : les signes viennent tout seuls
        self.play(*map(FadeOut, [d1, d2, d3, tri, inv]),
                  VGroup(formule, bf).animate.move_to([3.6, 2.2, 0]))
        P = Panneau(0.4, 1.2, gap=0.25)
        r0 = P.placer(MathTex(r"F = 5~\mathrm{kN}", font_size=FS_EQ))
        thd = Decimal(35, num_decimal_places=0, font_size=FS_EQ)
        lt = VGroup(MathTex(r"\theta =", font_size=FS_EQ), thd, MathTex(r"^\circ", font_size=FS_EQ))
        lt.arrange(RIGHT, buff=0.12)
        thd.add_updater(lambda m: m.set_value(th.get_value() / DEGREES).next_to(lt[0], RIGHT, buff=0.12))
        lt[2].add_updater(lambda m: m.next_to(thd, RIGHT, buff=0.05).align_to(thd, UP))
        P.placer(lt)
        lX = P.placer(ligne_live(r"F_X = 5\cos\theta =", lambda: Fv * np.cos(th.get_value()),
                                 unite=r"\mathrm{kN}", decimales=2))
        lY = P.placer(ligne_live(r"F_Y = 5\sin\theta =", lambda: Fv * np.sin(th.get_value()),
                                 unite=r"\mathrm{kN}", decimales=2))
        lX[0].set_color(C_FX)
        lY[0].set_color(C_FY)
        self.play(FadeIn(r0), FadeIn(lt), FadeIn(lX), FadeIn(lY))
        self.etape(0.5)
        for cible in (150, 240, 315, 35):
            self.play(th.animate.set_value(cible * DEGREES), run_time=2.5)
            self.wait(0.6)
        sg = P.placer(T(r"Avec $\theta$ mesuré depuis $\vec X$ (sens $\curvearrowleft$),\\"
                        r"les \textbf{signes} sortent tout seuls.", color=YELLOW))
        self.play(Write(sg))
        self.etape()

        # --- piège 1 : angle donné par rapport à la verticale
        self.tout_effacer(garder=[titre])
        sous = T(r"\textbf{Piège 1 :} l'angle est donné par rapport à la \textbf{verticale}",
                 color=C_NEG).next_to(titre, DOWN, buff=0.3)
        self.play(Write(sous))
        O2 = np.array([-4.2, 0.9, 0])
        beta = 30 * DEGREES
        k2 = 0.5
        F2 = 6.0
        u = np.array([np.sin(beta), -np.cos(beta), 0])
        bout = O2 + k2 * F2 * u
        verticale = DashedLine(O2, O2 + 3.4 * DOWN, color=GREY_B)
        fl = force(O2, bout, couleur=WHITE)
        lfl = MathTex(r"F = 6~\mathrm{kN}", font_size=FS_TEXTE).next_to(bout, RIGHT, buff=0.1)
        arcb = Arc(radius=1.1, start_angle=-PI / 2, angle=beta, arc_center=O2, color=C_LEVIER, stroke_width=3)
        lb = MathTex(r"\beta = 30^\circ", color=C_LEVIER, font_size=FS_TEXTE).move_to(
            O2 + 1.5 * np.array([np.sin(beta / 2), -np.cos(beta / 2), 0]) + 0.45 * RIGHT)
        self.play(Create(verticale), GrowArrow(fl), Write(lfl))
        self.play(Create(arcb), Write(lb))
        cX = force(O2, O2 + np.array([bout[0] - O2[0], 0, 0]), couleur=C_FX)
        cY = force(O2, O2 + np.array([0, bout[1] - O2[1], 0]), couleur=C_FY)
        cY.shift(0.0 * LEFT)
        lcX = MathTex(r"\vec F_X", color=C_FX, font_size=FS_EQ).next_to(cX, UP, buff=0.1)
        lcY = MathTex(r"\vec F_Y", color=C_FY, font_size=FS_EQ).next_to(cY, LEFT, buff=0.1)
        proj2 = VGroup(DashedLine(bout, cX.get_end(), color=GREY_B, stroke_width=2),
                       DashedLine(bout, cY.get_end(), color=GREY_B, stroke_width=2))
        self.play(Create(proj2), GrowArrow(cX), GrowArrow(cY), Write(lcX), Write(lcY))
        P = Panneau(0.0, 1.8, gap=0.3)
        m1 = P.placer(T(r"Côté \textbf{adjacent} à l'angle $\to$ $\cos$\\"
                        r"Côté \textbf{opposé} à l'angle $\to$ $\sin$"))
        self.play(Write(m1))
        self.play(Indicate(VGroup(cY, lcY), color=YELLOW), Indicate(arcb, color=YELLOW))
        m2 = P.placer(MathTex(r"F_X = +F\sin\beta = +6\times\sin 30^\circ = +3~\mathrm{kN}", font_size=FS_EQ - 4))
        m3 = P.placer(MathTex(r"F_Y = -F\cos\beta = -6\times\cos 30^\circ \approx -5{,}20~\mathrm{kN}",
                              font_size=FS_EQ - 4))
        m2[0][0:2].set_color(C_FX)
        m3[0][0:2].set_color(C_FY)
        self.play(Write(m2))
        self.play(Write(m3))
        m4 = P.placer(T(r"Le \textbf{signe} se lit sur le dessin :\\"
                        r"$\vec F_X$ vers la droite ($+$), $\vec F_Y$ vers le bas ($-$).", color=GREY_B))
        self.play(Write(m4))
        self.etape()

        # --- piège 2 : direction donnée par une pente
        self.tout_effacer(garder=[titre])
        sous = T(r"\textbf{Piège 2 :} la direction est donnée par une \textbf{pente} (pas d'angle)",
                 color=C_NEG).next_to(titre, DOWN, buff=0.3)
        self.play(Write(sous))
        O3 = np.array([-5.6, -2.6, 0])
        v = np.array([4, 3, 0]) / 5
        k3 = 0.42
        F3 = 10.0
        bout = O3 + k3 * F3 * v
        fl = force(O3, bout, couleur=WHITE)
        lfl = MathTex(r"F = 10~\mathrm{kN}", font_size=FS_TEXTE).next_to(bout, UP, buff=0.12)
        petit = VGroup(Line(O3 + 0.9 * RIGHT + 0.25 * DOWN, O3 + 0.9 * RIGHT + 0.25 * DOWN + 1.6 * RIGHT),
                       Line(O3 + 2.5 * RIGHT + 0.25 * DOWN, O3 + 2.5 * RIGHT + 0.25 * DOWN + 1.2 * UP),
                       Line(O3 + 0.9 * RIGHT + 0.25 * DOWN, O3 + 2.5 * RIGHT + 0.95 * UP)).set_stroke(C_LEVIER, 3)
        l4 = MathTex("4", color=C_LEVIER, font_size=FS_TEXTE).next_to(petit[0], DOWN, buff=0.08)
        l3 = MathTex("3", color=C_LEVIER, font_size=FS_TEXTE).next_to(petit[1], RIGHT, buff=0.08)
        l5 = MathTex("5", color=C_LEVIER, font_size=FS_TEXTE).next_to(petit[2].get_center(), UL, buff=0.05)
        self.play(GrowArrow(fl), Write(lfl))
        self.play(Create(petit), Write(l4), Write(l3))
        P = Panneau(0.0, 1.8, gap=0.3)
        p1 = P.placer(T(r"Pente « 3 pour 4 » : l'hypoténuse vaut\\"
                        r"$\sqrt{3^2+4^2} = 5$ (Pythagore)."))
        self.play(Write(p1), Write(l5))
        self.etape(0.5)
        cX = force(O3, O3 + np.array([bout[0] - O3[0], 0, 0]), couleur=C_FX)
        cY = force(cX.get_end(), bout, couleur=C_FY)
        self.play(GrowArrow(cX), GrowArrow(cY))
        p2 = P.placer(T(r"Triangles semblables : on applique les rapports."))
        p3 = P.placer(MathTex(r"F_X = F\times\frac{4}{5} = 8~\mathrm{kN}", font_size=FS_EQ - 2), gap=0.12)
        p3b = P.placer(MathTex(r"F_Y = F\times\frac{3}{5} = 6~\mathrm{kN}", font_size=FS_EQ - 2))
        self.play(Write(p2))
        self.play(Write(p3))
        self.play(Write(p3b))
        p4 = P.placer(T(r"Pas besoin de calculer l'angle !", color=YELLOW))
        self.play(Write(p4))
        p5 = P.placer(T(r"(Et si on calcule un angle : calculatrice en \textbf{degrés} !)",
                        font_size=FS_TEXTE - 4, color=GREY_B))
        self.play(Write(p5))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Résultante de plusieurs forces (exemple du poly)
# ---------------------------------------------------------------------------
class ResultanteForces(Base):
    def construct(self):
        titre = self.titre(r"Résultante d'un système de forces")
        self.play(Write(titre))

        O = np.array([-4.3, -0.9, 0])
        k = 0.24
        donnees = [(5, 30, r"\vec F_1", RED), (8, 90, r"\vec F_2", BLUE_C), (10, -135, r"\vec F_3", GREEN_C)]
        vecs = [F * np.array([np.cos(a * DEGREES), np.sin(a * DEGREES), 0]) for F, a, _, _ in donnees]
        rep = axes(O, gauche=2.6, droite=2.6, bas=2.6, haut=2.6)
        self.play(FadeIn(rep))
        fls = VGroup()
        for (F, a, nom, c), v in zip(donnees, vecs):
            u = v / np.linalg.norm(v)
            ar = force(O, O + k * v, couleur=c)
            lab = MathTex(nom, color=c, font_size=FS_EQ).next_to(ar.get_end(), u, buff=0.1)
            fls.add(VGroup(ar, lab))
        self.play(*[GrowArrow(f[0]) for f in fls], *[Write(f[1]) for f in fls])
        P = Panneau(0.0, 2.4, gap=0.22)
        q = P.placer(T(r"$F_1 = 5$ kN à $30^\circ$, \ $F_2 = 8$ kN à $90^\circ$,\\$F_3 = 10$ kN à $-135^\circ$"))
        self.play(Write(q))
        self.etape()

        # --- composantes
        lignes = [
            r"\vec F_1 = \begin{pmatrix} 5\cos 30^\circ \\ 5\sin 30^\circ \end{pmatrix} \approx \begin{pmatrix} 4{,}33 \\ 2{,}50 \end{pmatrix}",
            r"\vec F_2 = \begin{pmatrix} 8\cos 90^\circ \\ 8\sin 90^\circ \end{pmatrix} = \begin{pmatrix} 0 \\ 8 \end{pmatrix}",
            r"\vec F_3 = \begin{pmatrix} 10\cos(-135^\circ) \\ 10\sin(-135^\circ) \end{pmatrix} \approx \begin{pmatrix} -7{,}07 \\ -7{,}07 \end{pmatrix}",
        ]
        eqs = VGroup()
        for f, tex, (_, _, _, c) in zip(fls, lignes, donnees):
            e = MathTex(tex, font_size=FS_EQ - 8)
            e[0][0:3].set_color(c)
            P.placer(e, gap=0.15)
            self.play(Indicate(f, color=YELLOW), Write(e))
            eqs.add(e)
        self.etape()

        # --- somme : bout à bout
        pos = O.copy()
        chaine = VGroup()
        for (F, a, nom, c), v in zip(donnees, vecs):
            chaine.add(force(pos, pos + k * v, couleur=c, epaisseur=5))
            pos = pos + k * v
        for f, ch in zip(fls, chaine):
            self.play(TransformFromCopy(f[0], ch), run_time=0.9)
        R = sum(vecs)
        fR = force(O, O + k * R, couleur=YELLOW, epaisseur=8)
        lR = MathTex(r"\vec F", color=YELLOW, font_size=FS_EQ).next_to(fR.get_end(), UL, buff=0.05)
        self.play(GrowArrow(fR), Write(lR))
        som = P.placer(MathTex(r"\vec F = \sum \vec F_i \approx \begin{pmatrix} 4{,}33 + 0 - 7{,}07 \\ 2{,}50 + 8 - 7{,}07 \end{pmatrix}"
                               r"= \begin{pmatrix} -2{,}74 \\ 3{,}43 \end{pmatrix}~\mathrm{kN}", font_size=FS_EQ - 8))
        self.play(Write(som))
        self.etape()

        # --- intensité et angle : le piège du quadrant
        self.play(FadeOut(eqs), FadeOut(q), FadeOut(chaine), FadeOut(fls),
                  som.animate.move_to([som.width / 2, 2.2, 0]))
        P = Panneau(0.0, 1.3, gap=0.28)
        n = P.placer(MathTex(r"F = \sqrt{(-2{,}74)^2 + 3{,}43^2} \approx 4{,}39~\mathrm{kN}", font_size=FS_EQ - 4))
        self.play(Write(n))
        a1 = P.placer(MathTex(r"\arctan\frac{3{,}43}{-2{,}74} \approx -51{,}4^\circ \quad \text{??}",
                              font_size=FS_EQ - 4, color=C_NEG))
        self.play(Write(a1))
        faux = DashedLine(O, O + 2.2 * np.array([np.cos(-51.4 * DEGREES), np.sin(-51.4 * DEGREES), 0]),
                          color=C_NEG)
        self.play(Create(faux))
        a2 = P.placer(T(r"\textbf{Piège :} $\arctan$ donne un angle entre\\$-90^\circ$ et $+90^\circ$ seulement. "
                        r"Ici $F_X < 0$ et $F_Y > 0$ :\\la force est vers le \textbf{haut-gauche}."))
        self.play(Write(a2))
        arc = Arc(radius=0.7, start_angle=0, angle=128.6 * DEGREES, arc_center=O, color=C_LEVIER, stroke_width=3)
        la = MathTex(r"\alpha", color=C_LEVIER, font_size=FS_EQ).move_to(O + 1.0 * np.array([np.cos(64 * DEGREES), np.sin(64 * DEGREES), 0]))
        a3 = P.placer(MathTex(r"\alpha = 180^\circ - 51{,}4^\circ \approx 128{,}6^\circ", font_size=FS_EQ, color=YELLOW))
        self.play(FadeOut(faux), Create(arc), Write(la))
        self.play(Write(a3), Circumscribe(a3, color=YELLOW))
        a4 = P.placer(T(r"Toujours \textbf{vérifier sur le dessin}\\dans quel quadrant est la force.",
                        color=GREY_B))
        self.play(Write(a4))
        self.etape(2)
