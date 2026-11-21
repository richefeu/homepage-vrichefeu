"""
MS1 - Animations pédagogiques : moment d'une force (méthode du bras de levier)

Scènes (dans l'ordre du cours) :
    Intro             pourquoi le moment ? (clé de serrage), M = ± F × d, unités, signes
    BrasDeLevier      méthode en 2 étapes : signe (barre imaginaire OA) puis distance d
    ForceInclinee     d pas évident -> décomposition en F_X et F_Y
    MomentResultant   somme des moments, le résultat dépend du point choisi
    Couple            couple de forces : même moment quel que soit le point

Vidéo  : manim -qh moments.py Intro BrasDeLevier ForceInclinee MomentResultant Couple
Slides : manim-slides render moments.py Intro BrasDeLevier ForceInclinee MomentResultant Couple
         manim-slides present Intro BrasDeLevier ForceInclinee MomentResultant Couple
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403


# ---------------------------------------------------------------------------
# 1. Introduction : la clé de serrage
# ---------------------------------------------------------------------------
class Intro(Base):
    def construct(self):
        titre = self.titre(r"Le moment : l'effet de rotation d'une force")
        self.play(Write(titre))

        # --- écrou + clé
        c = np.array([-4.5, -0.6, 0])
        ecrou = RegularPolygon(6, radius=0.38, color=GREY_B, fill_opacity=0.6).move_to(c)
        tete = Circle(radius=0.6, color=GREY_A, stroke_width=10).move_to(c)
        manche = RoundedRectangle(corner_radius=0.15, width=6.6, height=0.36,
                                  color=GREY_A, fill_color=GREY_D, fill_opacity=1)
        manche.next_to(tete, RIGHT, buff=-0.05)
        cle = VGroup(manche, tete)
        centre = Dot(c, color=YELLOW)
        lab_O = MathTex("O", font_size=FS_EQ).next_to(c, DOWN + LEFT, buff=0.5)
        self.play(FadeIn(ecrou), FadeIn(cle), FadeIn(centre), Write(lab_O))

        txt = Tex(r"On veut desserrer l'écrou : on pousse sur le manche de la clé.",
                  font_size=FS_TEXTE).move_to([0, 2.4, 0])
        self.play(Write(txt))
        self.etape()

        y_haut = manche.get_top()[1]

        def appui(x, longueur=1.6):
            return force([x, y_haut + longueur, 0], [x, y_haut, 0])

        # --- force près de l'écrou
        x1 = c[0] + 1.4
        F1 = appui(x1)
        lab_F1 = MathTex(r"\vec F", color=C_FORCE, font_size=FS_EQ).next_to(F1, LEFT)
        d1 = cote([c[0], -1.55, 0], [x1, -1.55, 0], r"d_1", DOWN)
        self.play(GrowArrow(F1), Write(lab_F1))
        self.play(FadeIn(d1))
        self.montrer_rotation([cle, F1, lab_F1], c, -1, angle=6 * DEGREES)
        t1 = Tex(r"Près de l'écrou : ça tourne à peine...", font_size=FS_TEXTE)
        t1.move_to([0, 1.7, 0])
        self.play(Write(t1))
        self.etape()

        # --- même force, loin de l'écrou
        x2 = c[0] + 6.4
        F2 = appui(x2)
        lab_F2 = MathTex(r"\vec F", color=C_FORCE, font_size=FS_EQ).next_to(F2, LEFT)
        d2 = cote([c[0], -2.35, 0], [x2, -2.35, 0], r"d_2", DOWN)
        self.play(FadeOut(t1), ReplacementTransform(F1, F2),
                  ReplacementTransform(lab_F1, lab_F2))
        self.play(FadeIn(d2))
        self.montrer_rotation([cle, F2, lab_F2], c, -1, angle=25 * DEGREES)
        t2 = Tex(r"Même force, plus loin : l'effet de rotation est bien plus grand !",
                 font_size=FS_TEXTE).move_to([0, 1.7, 0])
        self.play(Write(t2))
        self.etape()

        # --- force dirigée vers l'écrou
        xm = manche.get_right()[0]
        F3 = force([xm + 1.6, c[1], 0], [xm, c[1], 0])
        lab_F3 = MathTex(r"\vec F", color=C_FORCE, font_size=FS_EQ).next_to(F3, UP)
        la = ligne_action(F3.get_end(), LEFT, longueur=7.5)
        self.play(FadeOut(t2), FadeOut(d1), FadeOut(d2),
                  ReplacementTransform(F2, F3), ReplacementTransform(lab_F2, lab_F3))
        self.play(Create(la))
        self.play(Wiggle(VGroup(cle, F3)), run_time=1.2)
        t3 = Tex(r"La ligne d'action passe par $O$ : aucun effet de rotation, $M=0$.",
                 font_size=FS_TEXTE).move_to([0, 1.7, 0])
        self.play(Write(t3))
        self.etape()

        # --- définition
        self.tout_effacer(garder=[titre])
        defi = MathTex(r"M_{/O}(\vec F) \;=\; \pm\; d \times F", font_size=60)
        defi.move_to([0, 1.5, 0])
        cadre = SurroundingRectangle(defi, color=BLUE_B, buff=0.25)
        expl = VGroup(
            Tex(r"$F$ : intensité de la force (N)", font_size=FS_TEXTE),
            Tex(r"$d$ : \textbf{distance de levier} (m), entre $O$ et la "
                r"\textbf{ligne d'action}", font_size=FS_TEXTE),
            Tex(r"Unité : le newton-mètre N$\cdot$m \quad (surtout pas des N/m !)",
                font_size=FS_TEXTE, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(cadre, DOWN, buff=0.5)
        self.play(Write(defi), Create(cadre))
        for e in expl:
            self.play(FadeIn(e, shift=0.2 * UP))
        self.etape()

        # --- convention de signe
        self.play(FadeOut(expl))
        p_pos = np.array([-3, -1.5, 0])
        p_neg = np.array([3, -1.5, 0])
        s_pos = fleche_sens(p_pos, +1, r=0.7)
        s_neg = fleche_sens(p_neg, -1, r=0.7)
        l_pos = Tex(r"sens trigonométrique $\curvearrowleft$\\moment \textbf{positif}",
                    font_size=FS_TEXTE, color=C_POS).next_to(s_pos, DOWN)
        l_neg = Tex(r"sens horaire $\curvearrowright$\\moment \textbf{négatif}",
                    font_size=FS_TEXTE, color=C_NEG).next_to(s_neg, DOWN)
        self.play(Create(s_pos), Write(l_pos))
        self.play(Create(s_neg), Write(l_neg))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Méthode du bras de levier (exemple du poly)
# ---------------------------------------------------------------------------
class BrasDeLevier(Base):
    def construct(self):
        titre = self.titre(r"Méthode du bras de levier")
        self.play(Write(titre))

        G = Grille(0, 4, 0, 3, origine=(-6.0, -2.6), s=1.3)
        O, A = G.p(0, 0), G.p(2, 2)
        grille = G.mob()
        echelle = Tex(r"1 graduation = 1 m ou 1 kN", font_size=26, color=GREY_B)
        echelle.next_to(grille, DOWN, buff=0.45)
        dotO = Dot(O)
        labO = MathTex("O", font_size=FS_EQ).next_to(O, LEFT, buff=0.7)
        dotA = Dot(A)
        labA = MathTex("A", font_size=FS_EQ).next_to(A, UL, buff=0.1)
        F = force(A, G.p(4, 2))
        labF = MathTex(r"\vec F", color=C_FORCE, font_size=FS_EQ).next_to(F, UP, buff=0.1)
        self.play(Create(grille), FadeIn(echelle))
        self.play(FadeIn(dotO, labO, dotA, labA), GrowArrow(F), Write(labF))

        P = Panneau(1.0, 2.3)
        q = P.placer(T(r"Calculer $M_{/O}(\vec F)$, avec $F = 2$ kN."))
        self.play(Write(q))
        self.etape()

        # --- étape 1 : le signe
        e1 = P.placer(Tex(r"\textbf{Étape 1 : le signe}", font_size=FS_TEXTE,
                          color=BLUE_B), gap=0.15)
        e1b = P.placer(T(r"On imagine une barre rigide $OA$,\\articulée en $O$..."))
        self.play(Write(e1))
        barre = Line(O, A, color=C_BARRE, stroke_width=8)
        self.play(Write(e1b), Create(barre))
        self.etape()
        self.montrer_rotation([barre, F, labF, dotA, labA], O, -1, angle=20 * DEGREES)
        sens = fleche_sens(O, -1, r=0.55)
        e1c = P.placer(T(r"$\vec F$ la fait tourner dans le sens\\horaire "
                         r"$\curvearrowright$ : moment \textbf{négatif}", color=C_NEG))
        self.play(Create(sens), Write(e1c))
        self.etape()

        # --- étape 2 : la distance de levier
        e2 = P.placer(Tex(r"\textbf{Étape 2 : la distance de levier}", font_size=FS_TEXTE,
                          color=BLUE_B), gap=0.15)
        e2b = P.placer(Tex(r"distance entre $O$ et la \textbf{ligne d'action}",
                           font_size=FS_TEXTE))
        la = ligne_action(A, RIGHT, longueur=4)
        self.play(Write(e2))
        self.play(Write(e2b), Create(la))
        H = G.p(0, 2)
        perp = Line(O, H)
        angle_droit = RightAngle(Line(H, O), Line(H, A), length=0.22, quadrant=(1, 1),
                                 color=C_LEVIER)
        d = cote(O + 0.35 * LEFT, H + 0.35 * LEFT, r"d", LEFT)
        self.play(FadeIn(d), Create(angle_droit))
        self.etape()

        # --- résultat
        res = MathTex(r"M_{/O}(\vec F) = -\,d \times F", font_size=FS_EQ)
        res2 = MathTex(r"= -2~\mathrm{m} \times 2~\mathrm{kN} = -4~\mathrm{kN\cdot m}",
                       font_size=FS_EQ)
        P.placer(res, gap=0.15)
        P.placer(res2)
        res2.shift(0.6 * RIGHT)
        boite = SurroundingRectangle(VGroup(res, res2), color=YELLOW, buff=0.15)
        self.play(Write(res))
        self.play(Write(res2), Create(boite))
        self.etape()

        # --- attention : OA ≠ d, on peut glisser la force sur sa ligne d'action
        self.play(*map(FadeOut, [q, e1, e1b, e1c, e2, e2b, res, res2, boite]))
        P.reset()
        a1 = P.placer(Tex(r"\textbf{Attention :} $OA \neq d$ !", font_size=FS_TEXTE,
                          color=YELLOW))
        self.play(Write(a1))

        xa = ValueTracker(2.0)
        pA = lambda: G.p(xa.get_value(), 2)
        barre.add_updater(lambda m: m.put_start_and_end_on(O, pA()))
        dotA.add_updater(lambda m: m.move_to(pA()))
        labA.add_updater(lambda m: m.next_to(pA(), UL, buff=0.1))
        F.add_updater(lambda m: m.put_start_and_end_on(pA(), pA() + 2 * G.s * RIGHT))
        labF.add_updater(lambda m: m.next_to(F, UP, buff=0.1))

        l_OA = VGroup(MathTex(r"OA =", font_size=FS_EQ),
                      Decimal(np.sqrt(8), num_decimal_places=2, font_size=FS_EQ),
                      MathTex(r"\mathrm{m}", font_size=FS_EQ)).arrange(RIGHT, buff=0.15)
        l_OA[1].add_updater(lambda m: m.set_value(np.hypot(xa.get_value(), 2)))
        l_d = MathTex(r"d = 2{,}00~\mathrm{m}", font_size=FS_EQ, color=C_LEVIER)
        l_M = MathTex(r"M_{/O}(\vec F) = -4~\mathrm{kN\cdot m}", font_size=FS_EQ)
        for m in (l_OA, l_d, l_M):
            P.placer(m, gap=0.2)
        self.play(FadeIn(l_OA), FadeIn(l_d), FadeIn(l_M))
        self.etape()

        a2 = P.placer(T(r"On fait glisser $\vec F$ sur sa ligne d'action :\\"
                        r"$OA$ change, mais \textbf{ni $d$ ni le moment} !"), gap=0.1)
        a2.shift(0.3 * DOWN)
        self.play(Write(a2))
        self.play(xa.animate.set_value(0.3), run_time=2.5)
        self.play(xa.animate.set_value(3.0), run_time=3)
        self.play(xa.animate.set_value(2.0), run_time=1.5)
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. Force inclinée : décomposition
# ---------------------------------------------------------------------------
class ForceInclinee(Base):
    def construct(self):
        titre = self.titre(r"Force inclinée : on décompose !")
        self.play(Write(titre))

        G = Grille(-2, 4, 0, 3, origine=(-5.1, -2.6), s=0.9)
        O, A = G.p(0, 0), G.p(2, 2)
        grille = G.mob()
        dotO = Dot(O)
        labO = MathTex("O", font_size=FS_EQ).next_to(O, DR, buff=0.45)
        dotA = Dot(A)
        labA = MathTex("A", font_size=FS_EQ).next_to(A, UL, buff=0.1)
        F = force(A, G.p(4, 3), couleur=WHITE)
        labF = MathTex(r"\vec F", font_size=FS_EQ).next_to(F.get_end(), RIGHT, buff=0.1)
        self.play(Create(grille))
        self.play(FadeIn(dotO, labO, dotA, labA), GrowArrow(F), Write(labF))

        P = Panneau(-0.9, 2.4, gap=0.25)
        q = P.placer(Tex(r"Calculer $M_{/O}(\vec F)$", font_size=FS_TEXTE))
        self.play(Write(q))

        # --- ligne d'action : d difficile à lire
        la = Line(G.p(-2.4, -0.2), G.p(4.4, 3.2), color=GREY_B, stroke_width=2.5)
        la = DashedLine(la.get_start(), la.get_end(), color=GREY_B, stroke_width=2.5)
        Hp = G.p(-0.4, 0.8)
        perp = DashedLine(O, Hp, color=C_LEVIER, stroke_width=4)
        d_lab = MathTex(r"d\,?", color=C_LEVIER, font_size=FS_EQ).next_to(perp, RIGHT, buff=0.05)
        self.play(Create(la))
        self.play(Create(perp), Write(d_lab))
        t1 = P.placer(Tex(r"La distance $d$ n'est pas facile à lire...", font_size=FS_TEXTE))
        self.play(Write(t1))
        self.etape()

        # --- décomposition
        t2 = P.placer(Tex(r"On décompose : $\vec F = \vec F_X + \vec F_Y$", font_size=FS_TEXTE))
        t2b = P.placer(MathTex(r"F_X = 2~\mathrm{kN} \qquad F_Y = 1~\mathrm{kN}",
                               font_size=FS_EQ))
        t2b[0][0:2].set_color(C_FX)
        t2b[0][6:8].set_color(C_FY)
        FX = force(A, G.p(4, 2), couleur=C_FX)
        FY = force(A, G.p(2, 3), couleur=C_FY)
        labFX = MathTex(r"\vec F_X", color=C_FX, font_size=FS_EQ).next_to(FX.get_end(), DOWN, buff=0.1)
        labFY = MathTex(r"\vec F_Y", color=C_FY, font_size=FS_EQ).next_to(FY.get_end(), LEFT, buff=0.1)
        self.play(FadeOut(la), FadeOut(perp), FadeOut(d_lab), Write(t2))
        self.play(F.animate.set_opacity(0.25), labF.animate.set_opacity(0.25),
                  GrowArrow(FX), GrowArrow(FY), Write(labFX), Write(labFY))
        self.play(Write(t2b))
        self.etape()

        # --- moment de F_X
        barre = Line(O, A, color=C_BARRE, stroke_width=8)
        self.play(Create(barre), FY.animate.set_opacity(0.2), labFY.animate.set_opacity(0.2))
        self.montrer_rotation([barre, FX, labFX, dotA, labA], O, -1)
        sX = fleche_sens(O, -1, r=0.45)
        laX = DashedLine(G.p(-2, 2), G.p(4.4, 2), color=GREY_B, stroke_width=2.5, dash_length=0.12)
        dY = cote(G.p(0, 0) + 0.3 * LEFT, G.p(0, 2) + 0.3 * LEFT, r"d_Y", LEFT)
        self.play(Create(sX), Create(laX), FadeIn(dY))
        mX = P.placer(MathTex(r"M_{/O}(\vec F_X) = -\,d_Y F_X = -2\times 2 = -4~\mathrm{kN\cdot m}",
                              font_size=FS_EQ - 6))
        mX[0][0:8].set_color(C_FX)
        self.play(Write(mX))
        self.etape()

        # --- moment de F_Y
        self.play(FadeOut(sX), FadeOut(laX), FadeOut(dY),
                  FX.animate.set_opacity(0.2), labFX.animate.set_opacity(0.2),
                  FY.animate.set_opacity(1), labFY.animate.set_opacity(1))
        self.montrer_rotation([barre, FY, labFY, dotA, labA], O, +1)
        sY = fleche_sens(O, +1, r=0.45)
        laY = DashedLine(G.p(2, -0.2), G.p(2, 3.4), color=GREY_B, stroke_width=2.5, dash_length=0.12)
        dX = cote(G.p(0, 0.5), G.p(2, 0.5), r"d_X", DOWN)
        self.play(Create(sY), Create(laY), FadeIn(dX))
        mY = P.placer(MathTex(r"M_{/O}(\vec F_Y) = +\,d_X F_Y = +2\times 1 = +2~\mathrm{kN\cdot m}",
                              font_size=FS_EQ - 6))
        mY[0][0:8].set_color(C_FY)
        self.play(Write(mY))
        self.etape()

        # --- somme
        self.play(FadeOut(sY), FadeOut(laY), FadeOut(dX), FadeOut(barre),
                  FX.animate.set_opacity(1), labFX.animate.set_opacity(1))
        tot = P.placer(MathTex(r"M_{/O}(\vec F) = -4 + 2 = -2~\mathrm{kN\cdot m}",
                               font_size=FS_EQ))
        boite = SurroundingRectangle(tot, color=YELLOW, buff=0.15)
        self.play(Write(tot), Create(boite))
        self.etape()

        # --- vérification avec la vraie distance de levier
        self.play(FadeOut(FX), FadeOut(FY), FadeOut(labFX), FadeOut(labFY),
                  F.animate.set_opacity(1), labF.animate.set_opacity(1))
        self.play(Create(la), Create(perp))
        ad = RightAngle(Line(Hp, O), Line(Hp, A), length=0.2, quadrant=(1, 1), color=C_LEVIER)
        d_lab2 = MathTex(r"d", color=C_LEVIER, font_size=FS_EQ).next_to(perp, RIGHT, buff=0.05)
        self.play(Create(ad), Write(d_lab2))
        v = P.placer(T(r"Vérification : $d = \frac{2}{\sqrt5} \approx 0{,}89$ m, "
                         r"$F=\sqrt5 \approx 2{,}24$ kN\\"
                         r"$-\,d\times F = -\frac{2}{\sqrt5}\times\sqrt5 = -2~\mathrm{kN\cdot m}$ \checkmark",
                         font_size=FS_TEXTE - 2), gap=0.1)
        self.play(Write(v))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. Moment résultant : le point de calcul compte !
# ---------------------------------------------------------------------------
class MomentResultant(Base):
    def construct(self):
        titre = self.titre(r"Moment résultant d'un système de forces")
        self.play(Write(titre))

        s = 1.35
        x0, yb = -5.0, 0.9            # abscisse de x = 0, ordonnée de la poutre
        k = 0.55                       # longueur de flèche par kN
        X = lambda x: np.array([x0 + s * x, yb, 0.0])
        poutre = Rectangle(width=6 * s, height=0.22, color=GREY_A,
                           fill_color=GREY_D, fill_opacity=1).move_to(X(3))
        e = 0.11  # demi-épaisseur

        # (abscisse, Fx, Fy) en kN
        forces = [(2, 0, -3), (5, 0, -2), (6, 0, 1), (6, 2, 0)]
        noms = [r"\vec F_1", r"\vec F_2", r"\vec F_3", r"\vec F_4"]
        intens = ["3", "2", "1", "2"]
        fl = []
        for (x, fx, fy), nom, val in zip(forces, noms, intens):
            if fy < 0:
                a = force(X(x) + (e + k * (-fy)) * UP, X(x) + e * UP)
                lab = MathTex(nom, "=" + val + r"~\mathrm{kN}", font_size=FS_TEXTE).next_to(a, UP, buff=0.1)
            elif fy > 0:
                a = force(X(x) + (e + k * fy + 0.1) * DOWN, X(x) + e * DOWN)
                lab = MathTex(nom, "=" + val + r"~\mathrm{kN}", font_size=FS_TEXTE).next_to(a, LEFT, buff=0.1)
            else:
                a = force(X(x), X(x) + k * fx * RIGHT)
                lab = MathTex(nom, "=" + val + r"~\mathrm{kN}", font_size=FS_TEXTE).next_to(a, UP, buff=0.15)
            fl.append(VGroup(a, lab))

        def point(x, nom):
            return VGroup(Dot(X(x), color=YELLOW, radius=0.07),
                          MathTex(nom, color=YELLOW, font_size=FS_EQ).next_to(X(x), UP, buff=0.2).shift(0.25 * LEFT))

        # graduations
        grad = VGroup(*[VGroup(Line(X(i) + 1.0 * DOWN + 0.06 * UP, X(i) + 1.0 * DOWN + 0.06 * DOWN),
                               MathTex(str(i), font_size=24, color=GREY_B).next_to(X(i) + 1.0 * DOWN, DOWN, buff=0.08))
                        for i in range(7)]).set_color(GREY_B)
        axe = Line(X(0) + 1.0 * DOWN, X(6) + 1.0 * DOWN, color=GREY_B, stroke_width=1.5)
        unite = MathTex(r"x~(\mathrm{m})", font_size=24, color=GREY_B).next_to(axe, RIGHT, buff=0.15).shift(0.0 * DOWN)

        self.play(FadeIn(poutre), Create(axe), FadeIn(grad), FadeIn(unite))
        self.play(*[GrowArrow(f[0]) for f in fl], *[Write(f[1]) for f in fl])
        self.etape()

        # --- au point O
        pO = point(0, "O")
        self.play(FadeIn(pO))
        eqO = MathTex(r"\sum M_{/O}", "=", r"-3\times2", r"-2\times5", r"+1\times6", r"+0",
                      r"=", r"-10~\mathrm{kN\cdot m}", font_size=FS_EQ)
        eqO.move_to([0, -2.0, 0])
        self.play(Write(eqO[0:2]))
        signes = [-1, -1, +1, 0]
        for i, ((x, fx, fy), sg) in enumerate(zip(forces, signes)):
            self.calcul_terme(fl[i], X(0), X(x), sg, eqO[2 + i], fy == 0)
        self.play(Write(eqO[6:]))
        self.play(Circumscribe(eqO[7], color=YELLOW))
        n4 = Tex(r"$\vec F_4$ : sa ligne d'action passe par le point $\Rightarrow$ moment nul",
                 font_size=FS_TEXTE - 4, color=GREY_B).next_to(eqO, DOWN, buff=0.35)
        self.play(FadeIn(n4))
        self.etape()

        # --- au point B
        pB = point(4, "B")
        self.play(FadeOut(n4), eqO.animate.shift(0.5 * UP), FadeIn(pB))
        eqB = MathTex(r"\sum M_{/B}", "=", r"+3\times2", r"-2\times1", r"+1\times2", r"+0",
                      r"=", r"+6~\mathrm{kN\cdot m}", font_size=FS_EQ)
        eqB.next_to(eqO, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(Write(eqB[0:2]))
        signes = [+1, -1, +1, 0]
        for i, ((x, fx, fy), sg) in enumerate(zip(forces, signes)):
            self.calcul_terme(fl[i], X(4), X(x), sg, eqB[2 + i], fy == 0, rapide=True)
        self.play(Write(eqB[6:]))
        self.play(Circumscribe(eqB[7], color=YELLOW))
        self.etape()

        # --- un point P quelconque : le résultat varie
        self.play(FadeOut(eqO), FadeOut(eqB), FadeOut(pO), FadeOut(pB))
        xp = ValueTracker(0.0)
        pP = always_redraw(lambda: VGroup(
            Dot(X(xp.get_value()), color=YELLOW, radius=0.07),
            MathTex("P", color=YELLOW, font_size=FS_EQ).next_to(X(xp.get_value()), UP, buff=0.2).shift(0.25 * LEFT)))
        ligne = ligne_live(r"\sum M_{/P} =", lambda: -10 + 4 * xp.get_value(), fs=FS_EQ + 6)
        ligne.move_to([0, -1.8, 0])
        self.play(FadeIn(pP), FadeIn(ligne))
        self.play(xp.animate.set_value(6), run_time=5, rate_func=linear)
        self.play(xp.animate.set_value(2.5), run_time=2.5)
        concl = Tex(r"Le moment résultant \textbf{dépend du point} de calcul :\\"
                    r"il faut \textbf{toujours} préciser ce point !",
                    font_size=FS_TEXTE, color=YELLOW).next_to(ligne, DOWN, buff=0.5)
        self.play(Write(concl))
        self.etape(2)

    def calcul_terme(self, fgrp, p_calc, p_app, signe, terme, nul, rapide=False):
        rt = 0.6 if rapide else 1.0
        fgrp.save_state()
        self.play(fgrp.animate.set_color(YELLOW), run_time=0.4 * rt)
        anims = []
        if nul:
            la = ligne_action(p_app, RIGHT, longueur=8)
            self.play(Create(la), run_time=rt)
            self.play(Write(terme), run_time=rt)
            self.play(FadeOut(la), Restore(fgrp), run_time=0.5 * rt)
            return
        y_c = p_calc[1] - 1.65
        c = cote([p_calc[0], y_c, 0], [p_app[0], y_c, 0], "", DOWN)
        sens = fleche_sens(p_calc, signe, r=0.35)
        self.play(FadeIn(c), Create(sens), run_time=rt)
        self.play(Write(terme), run_time=rt)
        self.play(FadeOut(c), FadeOut(sens), Restore(fgrp), run_time=0.5 * rt)


# ---------------------------------------------------------------------------
# 5. Couple de forces (exemple du poly)
# ---------------------------------------------------------------------------
class Couple(Base):
    def construct(self):
        titre = self.titre(r"Moment engendré par un couple de forces")
        self.play(Write(titre))

        G = Grille(0, 9, 0, 6, origine=(-6.0, -3.0), s=0.6)
        grille = G.mob()
        O = G.p(0, 0)
        A, B, C = G.p(2, 3), G.p(5, 3), G.p(8, 3)
        FA = force(A, G.p(2, 1), couleur=C_FY)
        FC = force(C, G.p(8, 5), couleur=C_FY)
        labFA = MathTex(r"\vec F_A", color=C_FY, font_size=FS_EQ).next_to(FA.get_end(), RIGHT, buff=0.1)
        labFC = MathTex(r"\vec F_C", color=C_FY, font_size=FS_EQ).next_to(FC.get_end(), RIGHT, buff=0.1)
        pts = VGroup(croix(A), croix(B), croix(C), Dot(O),
                     MathTex("A", font_size=FS_EQ).next_to(A, UL, buff=0.1),
                     MathTex("B", font_size=FS_EQ).next_to(B, UR, buff=0.1),
                     MathTex("C", font_size=FS_EQ).next_to(C, DR, buff=0.1),
                     MathTex("O", font_size=FS_EQ).next_to(O, DL, buff=0.45))
        c1 = cote(G.p(2, 0.5), G.p(5, 0.5), r"\ell", UP)
        c2 = cote(G.p(5, 0.5), G.p(8, 0.5), r"\ell", UP)
        self.play(Create(grille))
        self.play(FadeIn(pts), GrowArrow(FA), GrowArrow(FC), Write(labFA), Write(labFC),
                  FadeIn(c1), FadeIn(c2))
        P = Panneau(-0.2, 2.5, gap=0.3)
        q = P.placer(T(r"Deux forces parallèles, de sens opposés,\\"
                       r"même intensité $F$."))
        self.play(Write(q))
        self.etape()

        # --- calculs aux points A, B, C, O
        lignes = [
            (A, r"\sum M_{/A} = 0\,F + 2\ell F = +2\ell F", [0, +1]),
            (B, r"\sum M_{/B} = +\ell F + \ell F = +2\ell F", [+1, +1]),
            (C, r"\sum M_{/C} = +2\ell F + 0\,F = +2\ell F", [+1, 0]),
            (O, r"\sum M_{/O} = -X_A F + (X_A+2\ell)F = +2\ell F", [-1, +1]),
        ]
        eqs = VGroup()
        for pt, tex, sg in lignes:
            marque = Circle(radius=0.2, color=YELLOW, stroke_width=5).move_to(pt)
            sens = VGroup(*[fleche_sens(pt, s_, r=0.38 + 0.18 * i) for i, s_ in enumerate(sg) if s_ != 0])
            self.play(Create(marque), Create(sens))
            eq = P.placer(MathTex(tex, font_size=FS_EQ - 4), gap=0.25)
            self.play(Write(eq))
            self.play(FadeOut(marque), FadeOut(sens))
            eqs.add(eq)
            self.etape(0.5)

        concl = P.placer(Tex(r"Le même résultat en tout point !", font_size=FS_TEXTE,
                             color=YELLOW))
        self.play(Write(concl), *[Indicate(e[0][-4:], color=YELLOW) for e in eqs])
        self.etape()

        # --- point P quelconque, valeurs numériques
        self.play(FadeOut(eqs), FadeOut(concl), FadeOut(q))
        P.reset()
        num = P.placer(MathTex(r"\ell = 3~\mathrm{m},\quad F = 2~\mathrm{kN}", font_size=FS_EQ))
        self.play(Write(num))

        xp, yp = ValueTracker(0.0), ValueTracker(0.0)
        pPt = lambda: G.p(xp.get_value(), yp.get_value())
        mP = always_redraw(lambda: VGroup(
            Dot(pPt(), color=YELLOW),
            MathTex("P", color=YELLOW, font_size=FS_EQ).next_to(pPt(), UR, buff=0.05)))

        lA = P.placer(ligne_live(r"M_{/P}(\vec F_A) =", lambda: -2 * (2 - xp.get_value())))
        lC = P.placer(ligne_live(r"M_{/P}(\vec F_C) =", lambda: 2 * (8 - xp.get_value())))
        lS = P.placer(ligne_live(r"\sum M_{/P} =", lambda: -2 * (2 - xp.get_value()) + 2 * (8 - xp.get_value())))
        bS = SurroundingRectangle(lS, color=YELLOW, buff=0.12)
        self.play(FadeIn(mP), FadeIn(lA), FadeIn(lC), FadeIn(lS), Create(bS))
        self.etape(0.5)
        for (x, y) in [(5, 5), (9, 1), (3, 6), (1, 2)]:
            self.play(xp.animate.set_value(x), yp.animate.set_value(y), run_time=2)
        self.etape()

        # --- conclusion
        self.play(*map(FadeOut, [num, lA, lC, lS, bS]))
        P.reset()
        r1 = P.placer(Tex(r"Un \textbf{couple} ne dépend pas du point de calcul.",
                          font_size=FS_TEXTE))
        r2 = P.placer(MathTex(r"C = \pm\, F \times (\text{distance entre les forces})",
                              font_size=FS_EQ))
        r3 = P.placer(MathTex(r"C = +\,2\ell F", font_size=FS_EQ + 6, color=YELLOW))
        r4 = P.placer(Tex(r"et $\sum \vec F = \vec 0$ : il ne fait que tourner.",
                          font_size=FS_TEXTE))
        r3.shift(1.0 * RIGHT)
        sens = fleche_sens(B, +1, r=0.9)
        self.play(Write(r1))
        self.play(Write(r2))
        self.play(Write(r3), Create(sens))
        self.play(Write(r4))
        self.etape(2)
