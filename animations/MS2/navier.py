"""
MS2 - Animations pédagogiques : contraintes normales et diagramme de Navier (§2.1 du poly)

Scènes (dans l'ordre du cours) :
    ContrainteNormale   σ = dF/dS (MPa), traction / compression, effet de N (uniforme), effet de M (flexion,
                        fibres raccourcies / allongées, fibre neutre), formule σ = N/S − M y / I_GZ, unités
    DiagrammeNavier     section en T de §1, N = −48 kN, M = −4 kN·m : N seul, M seul, superposition,
                        σ_sup = +10,4 MPa, σ_inf = −53,0 MPa, fibre neutre à 22,1 mm, droite « Y = A X + B »
    NavierEnDirect      N et M varient en direct : la droite tourne (M) et se décale (N), la fibre neutre
                        se déplace et peut sortir de la section (section entièrement comprimée)
    NavierTableau       les 9 cas (signes de N et de M) : inclinaison donnée par M, décalage donné par N

Vidéo  : manim -qh navier.py ContrainteNormale DiagrammeNavier NavierEnDirect NavierTableau
Slides : manim-slides render navier.py ContrainteNormale DiagrammeNavier NavierEnDirect NavierTableau
         manim-slides present ContrainteNormale DiagrammeNavier NavierEnDirect NavierTableau
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms2 import *  # noqa: E402,F403

# Section en T de §1, en mm, coordonnées par rapport à G (Y_G = 95 mm depuis le bas)
RECTS_T = [(-10, -95, 10, 25), (-60, 25, 60, 45)]     # âme 20 x 120, table 120 x 20
S_T = 4800.0           # mm²
I_T = 884e4            # mm⁴
Y_SUP, Y_INF = 45.0, -95.0


def sigma(N_kN, M_kNm):
    """σ(y) en MPa pour N en kN, M en kN·m (y en mm)."""
    return lambda y: N_kN * 1e3 / S_T - M_kNm * 1e6 / I_T * y


# ---------------------------------------------------------------------------
# 1. Qu'est-ce qu'une contrainte normale ?
# ---------------------------------------------------------------------------
class ContrainteNormale(Base):
    def construct(self):
        titre = self.titre(r"La contrainte normale $\sigma$")
        self.play(Write(titre))

        # --- on coupe la poutre
        yb, hb = 1.0, 1.4
        gauche = Rectangle(width=6.5, height=hb).set_stroke(WHITE, 3).set_fill(GREY_D, 1)
        gauche.move_to([-6.0 + 3.25, yb, 0])
        droite = Rectangle(width=3.0, height=hb).set_stroke(WHITE, 3).set_fill(GREY_D, 1)
        droite.next_to(gauche, RIGHT, buff=0)
        axe = DashedLine([-6.4, yb, 0], [4.4, yb, 0], color=GREY_B, stroke_width=2)
        lx = MathTex("x", font_size=FS_TEXTE, color=GREY_B).next_to(axe, RIGHT, buff=0.1)
        self.play(FadeIn(gauche), FadeIn(droite), Create(axe), Write(lx))
        xc = gauche.get_right()[0]
        cut = DashedLine([xc, yb - 1.1, 0], [xc, yb + 1.1, 0], color=YELLOW, stroke_width=4)
        self.play(Create(cut))
        self.play(droite.animate.shift(2.0 * RIGHT).set_opacity(0.25), FadeOut(cut))
        t = T(r"On coupe la poutre : sur la \textbf{section}, la partie de droite exerce\\"
              r"des forces sur la partie de gauche.", font_size=30).move_to([0, -1.0, 0])
        self.play(Write(t))
        self.etape()

        # --- un petit élément de surface dS et sa force dF
        el = Line([xc, yb + 0.3, 0], [xc, yb + 0.6, 0], color=YELLOW, stroke_width=10)
        l_el = MathTex(r"\mathrm{d}S", font_size=30, color=YELLOW).next_to(el, LEFT, buff=0.15)
        dF = force([xc, yb + 0.45, 0], [xc + 1.2, yb + 0.45, 0], couleur=C_TRAC, epaisseur=5)
        l_dF = MathTex(r"\mathrm{d}F", font_size=30, color=C_TRAC).next_to(dF, UP, buff=0.08)
        self.play(FadeOut(t), Create(el), Write(l_el))
        self.play(GrowArrow(dF), Write(l_dF))
        Pn = Panneau(-6.4, -0.3, gap=0.22)
        defi = MathTex(r"\sigma = \frac{\mathrm{d}F}{\mathrm{d}S}", font_size=48)
        Pn.placer(defi)
        cadre = SurroundingRectangle(defi, color=BLUE_B, buff=0.15)
        expl = VGroup(
            T(r"\textbf{densité de force} sur la section ;", font_size=30),
            T(r"\textbf{normale} : la force est perpendiculaire à la section (suivant $x$) ;", font_size=30),
            T(r"unité : le MPa, avec $1\ \mathrm{MPa} = 1\ \mathrm{N/mm^2}$.", font_size=30, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(cadre, RIGHT, buff=0.5).align_to(cadre, UP)
        self.play(Write(defi), Create(cadre))
        for e in expl:
            self.play(FadeIn(e, shift=0.2 * UP))
        self.etape()

        # --- traction / compression
        self.play(*map(FadeOut, (expl, defi, cadre)))
        el2 = Line([xc, yb - 0.6, 0], [xc, yb - 0.3, 0], color=YELLOW, stroke_width=10)
        dF2 = force([xc + 1.2, yb - 0.45, 0], [xc, yb - 0.45, 0], couleur=C_COMP, epaisseur=5)
        l_dF2 = MathTex(r"\mathrm{d}F", font_size=30, color=C_COMP).next_to(dF2, DOWN, buff=0.08)
        self.play(Create(el2), GrowArrow(dF2), Write(l_dF2))
        tt = Tex(r"on \textbf{tire} sur la matière : \textbf{traction}, $\sigma > 0$", font_size=30, color=C_TRAC)
        tc = Tex(r"on \textbf{pousse} sur la matière : \textbf{compression}, $\sigma < 0$", font_size=30,
                 color=C_COMP)
        VGroup(tt, tc).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, -1.4, 0])
        self.play(Write(tt))
        self.play(Write(tc))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- effet de N : contrainte uniforme
        face = self.face(x=-1.0, y=0.6, h=2.4)
        fl = VGroup(*[force([-1.0, y, 0], [-1.0 + 1.0, y, 0], couleur=C_TRAC, epaisseur=4)
                      for y in np.linspace(-0.6, 1.8, 7)])
        lab = Tex(r"$N > 0$", font_size=FS_EQ, color=C_TRAC).next_to(fl, RIGHT, buff=0.3)
        self.play(FadeIn(face))
        self.play(LaggedStart(*map(GrowArrow, fl), lag_ratio=0.1), Write(lab))
        f1 = MathTex(r"\text{Effort normal seul : }\ \sigma = \frac{N}{S}", font_size=40).move_to([0, -1.6, 0])
        f1b = Tex(r"la même sur toute la section ($S$ : aire de la section, en mm$^2$)", font_size=28,
                  color=GREY_B).next_to(f1, DOWN, buff=0.2)
        self.play(Write(f1), FadeIn(f1b))
        self.etape()
        fl2 = VGroup(*[force([-1.0 + 1.0, y, 0], [-1.0, y, 0], couleur=C_COMP, epaisseur=4)
                       for y in np.linspace(-0.6, 1.8, 7)])
        lab2 = Tex(r"$N < 0$", font_size=FS_EQ, color=C_COMP).move_to(lab)
        self.play(ReplacementTransform(fl, fl2), ReplacementTransform(lab, lab2))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- effet de M : la flexion
        self.flexion()
        self.tout_effacer(garder=[titre])

        # --- la formule
        form = MathTex(r"\sigma(x, y) = \frac{N(x)}{S} - \frac{M(x)}{I_{GZ}}\times y", font_size=56)
        form.move_to([0, 1.5, 0])
        cadre = SurroundingRectangle(form, color=YELLOW, buff=0.25)
        self.play(Write(form), Create(cadre))
        unites = VGroup(
            Tex(r"$N$ en N \qquad $S$ en mm$^2$", font_size=30),
            Tex(r"$M$ en N$\cdot$mm \qquad $I_{GZ}$ en mm$^4$ \qquad $y$ en mm (depuis $G$, vers le haut)",
                font_size=30),
            Tex(r"$\Rightarrow\ \sigma$ en N/mm$^2$ = MPa", font_size=30, color=YELLOW),
            Tex(r"\textbf{Piège} : $M$ en kN$\cdot$m $\rightarrow$ multiplier par $10^6$ pour l'avoir en N$\cdot$mm !",
                font_size=30, color=C_NEG),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).next_to(cadre, DOWN, buff=0.5)
        for u in unites:
            self.play(FadeIn(u, shift=0.2 * UP))
        rq = Tex(r"$\sigma$ dépend de $y$ (la hauteur) mais pas de $z$ (la largeur).", font_size=28,
                 color=GREY_B).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(rq))
        self.etape(2)

    @staticmethod
    def face(x, y, h):
        """Bout de poutre (vu de côté) dont la face coupée est verticale en x."""
        r = Rectangle(width=3.0, height=h).set_stroke(WHITE, 3).set_fill(GREY_D, 1)
        r.move_to([x - 1.5, y, 0])
        return r

    def flexion(self):
        k = ValueTracker(0)
        KMAX = 0.13
        c = np.array([-1.5, 0.2, 0])
        Lb, hb = 3.0, 0.8

        def pt(x, y):
            kk = k.get_value()
            if abs(kk) < 1e-6:
                return c + np.array([x, y, 0])
            R = 1 / kk
            th = x / R
            return c + np.array([(R - y) * np.sin(th), R - (R - y) * np.cos(th), 0])

        def fibres():
            g = VGroup()
            for y in np.linspace(-hb, hb, 7):
                col = WHITE if abs(y) < 1e-6 else (C_COMP if y > 0 else C_TRAC)
                col = interpolate_color(GREY_B, col, k.get_value() / KMAX)
                g.add(ParametricFunction(lambda t, y=y: pt(t, y), t_range=[-Lb, Lb],
                                         stroke_width=6 if abs(y) < 1e-6 else 3, color=col))
            g.add(Line(pt(-Lb, -hb), pt(-Lb, hb), color=WHITE, stroke_width=3),
                  Line(pt(Lb, -hb), pt(Lb, hb), color=WHITE, stroke_width=3))
            return g

        poutre = always_redraw(fibres)
        couples = always_redraw(lambda: VGroup(
            fleche_sens(pt(-Lb, 0) + 0.7 * LEFT, -1, r=0.45, couleur=C_FORCE),
            fleche_sens(pt(Lb, 0) + 0.7 * RIGHT, +1, r=0.45, couleur=C_FORCE)))
        lM = always_redraw(lambda: VGroup(
            MathTex("M", color=C_FORCE, font_size=FS_EQ).move_to(pt(-Lb, 0) + 0.7 * LEFT + 0.8 * UP),
            MathTex("M", color=C_FORCE, font_size=FS_EQ).move_to(pt(Lb, 0) + 0.7 * RIGHT + 0.8 * UP)))
        self.play(FadeIn(poutre))
        t0 = Tex(r"Moment fléchissant seul ($M > 0$) : la poutre fléchit.", font_size=30).to_edge(DOWN, buff=1.2)
        self.play(FadeIn(couples), FadeIn(lM), Write(t0))
        self.play(k.animate.set_value(KMAX), run_time=2.5)
        self.etape()

        exp = VGroup(
            Tex(r"en haut : les fibres \textbf{raccourcissent} $\Rightarrow$ compression", font_size=28, color=C_COMP),
            Tex(r"en bas : les fibres \textbf{s'allongent} $\Rightarrow$ traction", font_size=28, color=C_TRAC),
            Tex(r"au milieu (en $G$) : \textbf{fibre neutre}, longueur inchangée, $\sigma = 0$", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(DOWN, buff=0.25)
        self.play(FadeOut(t0))
        for e in exp:
            self.play(FadeIn(e, shift=0.2 * UP))
        self.etape()

        # contraintes sur la face (droite) : proportionnelles à y
        xf = 4.6
        sec = Line([xf, c[1] - hb, 0], [xf, c[1] + hb, 0], color=WHITE, stroke_width=4)
        fl = VGroup()
        for y in np.linspace(-hb, hb, 9):
            if abs(y) > 1e-6:
                L = -1.1 * y / hb                      # > 0 : traction (on tire), < 0 : compression (on pousse)
                p0 = np.array([xf, c[1] + y, 0])
                if L > 0:
                    fl.add(force(p0, p0 + L * RIGHT, couleur=C_TRAC, epaisseur=4))
                else:
                    fl.add(force(p0 - L * RIGHT, p0, couleur=C_COMP, epaisseur=4))
        gpt = point_G([xf, c[1], 0], cote_label=LEFT, buff=0.15)
        ly = cote([xf - 0.35, c[1], 0], [xf - 0.35, c[1] + 0.8 * hb, 0], "y", LEFT, fs=30)
        lab = MathTex(r"\sigma = -\frac{M}{I_{GZ}}\,y", font_size=40).move_to([xf, c[1] + 2.1, 0])
        self.play(Create(sec), FadeIn(gpt))
        self.play(LaggedStart(*map(GrowArrow, fl), lag_ratio=0.08), FadeIn(ly))
        self.play(Write(lab))
        rq = Tex(r"proportionnelle à $y$\\signe $-$ : $M > 0$ et $y > 0$\\$\Rightarrow$ compression",
                 font_size=26, color=YELLOW).move_to([xf + 0.3, c[1] - hb - 0.75, 0])
        self.play(FadeIn(rq))
        self.etape()
        poutre.clear_updaters()
        couples.clear_updaters()
        lM.clear_updaters()


# ---------------------------------------------------------------------------
# Outils communs : section en T à gauche, diagramme de Navier au milieu, texte à droite
# ---------------------------------------------------------------------------
class NavierScene(Base):
    KY = 0.03                    # écran / mm
    KS = 0.035                   # écran / MPa
    YG = 0.2                     # ordonnée écran de G
    XS = -5.2                    # abscisse écran de G sur la section
    XN = -0.2                    # abscisse écran de σ = 0
    S_MIN, S_MAX = -70, 40       # étendue de l'axe σ

    def preparer(self):
        self.S = Plan((self.XS, self.YG), s=self.KY)
        self.nav = Navier((self.XN, self.YG), self.KY, self.KS, Y_INF, Y_SUP)

    def section(self):
        S = self.S
        rects = VGroup(*[S.rect(*r, C_SECTION) for r in RECTS_T])
        cotes = VGroup(
            S.cote_h(-60, 60, 54, "120", UP, fs=26),
            S.cote_v(70, 25, 45, "20", RIGHT, fs=26),
            S.cote_v(-25, -95, 25, "120", LEFT, fs=26),
            S.cote_h(-10, 10, -104, "20", DOWN, fs=26),
        )
        gG = point_G(S.p(0, 0), cote_label=LEFT, buff=0.15, fs=28)
        unite = Tex(r"(mm)", font_size=24, color=GREY_B).next_to(cotes[2], DOWN, buff=0.4)
        return rects, cotes, gG, unite

    def zones(self, f):
        """Parties tendues (bleu) et comprimées (rouge) de la section pour la répartition f(y)."""
        g = VGroup()
        A = f(0)
        B = f(1) - A
        for u0, y0, u1, y1 in RECTS_T:
            cuts = [y0, y1]
            if abs(B) > 1e-12 and y0 < -A / B < y1:
                cuts = [y0, -A / B, y1]
            for a, b in zip(cuts[:-1], cuts[1:]):
                s = f((a + b) / 2)
                if abs(s) > 1e-6:
                    g.add(self.S.rect(u0, a, u1, b, C_TRAC if s > 0 else C_COMP, opacite=0.8).set_stroke(width=0))
        return g

    def rappels(self):
        nav, S = self.nav, self.S
        return VGroup(
            rappel(S.p(60, Y_SUP), nav.p(self.S_MAX, Y_SUP)),
            rappel(S.p(10, Y_INF), nav.p(self.S_MAX, Y_INF)),
            rappel(S.p(10, 0), nav.p(self.S_MIN, 0)),
        )

    def ligne_neutre(self, y0):
        return DashedLine(self.S.p(-70, y0), self.nav.p(self.S_MAX, y0), color=WHITE, stroke_width=3,
                          dash_length=0.12)


# ---------------------------------------------------------------------------
# 2. Le diagramme de Navier pas à pas (exemple chiffré)
# ---------------------------------------------------------------------------
class DiagrammeNavier(NavierScene):
    def construct(self):
        titre = self.titre(r"Le diagramme de Navier")
        self.play(Write(titre))
        self.preparer()
        nav = self.nav
        rects, cotes, gG, unite = self.section()
        self.play(FadeIn(rects), FadeIn(cotes), FadeIn(gG), FadeIn(unite))
        axes = nav.axes(self.S_MIN, self.S_MAX)
        rap = self.rappels()
        ysup = MathTex(r"y_\text{sup} = +45", font_size=26).next_to(rap[0], UP, buff=0.05).set_x(-1.2)
        yinf = MathTex(r"y_\text{inf} = -95", font_size=26).next_to(rap[1], DOWN, buff=0.05).set_x(-0.9)
        self.play(Create(axes), Create(rap), FadeIn(ysup), FadeIn(yinf))

        Pn = Panneau(2.0, 2.6, gap=0.18)
        d = [Pn.placer(m) for m in (
            T(r"Section en T de §1 :", font_size=28, color=GREY_B),
            MathTex(r"S = 4800\ \mathrm{mm^2},\ I_{GZ} = 884\cdot 10^4\ \mathrm{mm^4}", font_size=28),
            MathTex(r"N = -48\ \mathrm{kN},\quad M = -4\ \mathrm{kN\cdot m}", font_size=30, color=C_FORCE),
        )]
        self.play(*map(FadeIn, d))
        self.etape()
        Pn.y -= 0.15
        y_etapes = Pn.y

        # --- 1. N seul
        fN = sigma(-48, 0)
        dN = nav.diagramme(fN)
        e1 = [Pn.placer(m) for m in (
            T(r"\textbf{1.} $N$ seul : $\sigma$ uniforme", font_size=28),
            MathTex(r"\frac{N}{S} = \frac{-48\,000}{4800} = -10\ \mathrm{MPa}", font_size=32),
        )]
        self.play(Write(e1[0]))
        self.play(Write(e1[1]), Create(dN[1]), LaggedStart(*map(Create, dN[0]), lag_ratio=0.05))
        self.play(FadeIn(self.zones(fN), rate_func=there_and_back), run_time=1.5)
        self.etape()

        # --- 2. M seul
        fM = sigma(0, -4)
        dM = nav.diagramme(fM)
        self.play(*map(FadeOut, e1), dN.animate.set_opacity(0.2))
        Pn.y = y_etapes
        e2 = [Pn.placer(m) for m in (
            T(r"\textbf{2.} $M$ seul : $\sigma$ proportionnelle à $y$", font_size=28),
            MathTex(r"-\frac{M}{I_{GZ}}\,y = \frac{4\cdot 10^6}{884\cdot 10^4}\,y = 0{,}452\,y", font_size=32),
            MathTex(r"y_\text{sup} : 0{,}452\times 45 = +20{,}4\ \mathrm{MPa}", font_size=30),
            MathTex(r"y_\text{inf} : 0{,}452\times (-95) = -43{,}0\ \mathrm{MPa}", font_size=30),
        )]
        for m in e2[:2]:
            self.play(Write(m))
        self.play(Create(dM[1]), LaggedStart(*map(Create, dM[0]), lag_ratio=0.05))
        self.play(Write(e2[2]), Write(e2[3]))
        self.etape()

        # --- 3. superposition
        f = sigma(-48, -4)
        dT = nav.diagramme(f)
        self.play(*map(FadeOut, e2), dM.animate.set_opacity(0.2))
        Pn.y = y_etapes
        e3 = [Pn.placer(m) for m in (
            T(r"\textbf{3.} on \textbf{additionne} : ", font_size=28),
            MathTex(r"\sigma(y) = -10 + 0{,}452\,y", font_size=34, color=YELLOW),
            MathTex(r"\sigma_\text{sup} = -10 + 20{,}4 = +10{,}4\ \mathrm{MPa}", font_size=30, color=C_TRAC),
            MathTex(r"\sigma_\text{inf} = -10 - 43{,}0 = -53{,}0\ \mathrm{MPa}", font_size=30, color=C_COMP),
        )]
        self.play(Write(e3[0]), Write(e3[1]))
        self.play(TransformFromCopy(VGroup(dN, dM), dT), run_time=2)
        self.play(FadeOut(dN), FadeOut(dM))
        v_sup = MathTex(r"+10{,}4", font_size=28, color=C_TRAC).next_to(nav.p(f(Y_SUP), Y_SUP), RIGHT, buff=0.12)
        v_inf = MathTex(r"-53{,}0", font_size=28, color=C_COMP).next_to(nav.p(f(Y_INF), Y_INF), DOWN, buff=0.12)
        self.play(Write(e3[2]), FadeIn(v_sup))
        self.play(Write(e3[3]), FadeIn(v_inf))
        z = self.zones(f)
        lt = Tex(r"tendue", font_size=26, color=WHITE).move_to(self.S.p(-32, 35))
        lc = Tex(r"comprimée", font_size=26, color=C_COMP).next_to(self.S.p(10, -60), RIGHT, buff=0.15)
        self.play(FadeIn(z), FadeIn(lt), FadeIn(lc))
        self.etape()

        # --- 4. fibre neutre
        self.play(*map(FadeOut, e3))
        Pn.y = y_etapes
        y0 = 10 / 0.452489
        e4 = [Pn.placer(m) for m in (
            T(r"\textbf{4.} fibre neutre : $\sigma = 0$", font_size=28),
            MathTex(r"-10 + 0{,}452\,y_0 = 0 \ \Rightarrow\ y_0 = 22{,}1\ \mathrm{mm}", font_size=32),
            T(r"au-dessus de $G$ (car $N < 0$)", font_size=28, color=GREY_B),
        )]
        ln = self.ligne_neutre(y0)
        lab_ln = Tex(r"fibre neutre", font_size=26).next_to(ln, UP, buff=0.05).set_x(-1.2)
        self.play(Write(e4[0]))
        self.play(Write(e4[1]), Create(ln), FadeIn(lab_ln))
        self.play(FadeIn(e4[2]))
        self.etape()

        # --- 5. une droite « Y = A X + B »
        self.play(*map(FadeOut, e4))
        Pn.y = y_etapes
        e5 = [Pn.placer(m) for m in (
            T(r"\textbf{5.} c'est une droite :", font_size=28),
            MathTex(r"\sigma = \underbrace{-\frac{M}{I_{GZ}}}_{\text{pente}}\times y"
                    r" + \underbrace{\frac{N}{S}}_{\sigma\ \text{en}\ G}", font_size=34),
        )]
        pG = Dot(nav.p(-10, 0), color=YELLOW)
        lG = MathTex(r"\sigma_G = \frac{N}{S} = -10", font_size=26, color=YELLOW).next_to(nav.p(0, 0), UR, buff=0.12)
        self.play(Write(e5[0]))
        self.play(Write(e5[1]), FadeIn(pG, scale=2), FadeIn(lG))
        self.etape()
        bilan = T(r"Traction max en $y_\text{sup}$, compression max en $y_\text{inf}$ : il suffit de calculer"
                  r"\\$\sigma$ en haut et en bas de la section pour tracer le diagramme.",
                  font_size=28, color=C_POS).to_edge(DOWN, buff=0.15).set_x(2.0)
        self.play(FadeIn(bilan))
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. N et M en direct
# ---------------------------------------------------------------------------
class NavierEnDirect(NavierScene):
    def construct(self):
        titre = self.titre(r"Diagramme de Navier : l'effet de $N$ et de $M$")
        self.play(Write(titre))
        self.preparer()
        nav = self.nav
        rects, cotes, gG, unite = self.section()
        axes = nav.axes(self.S_MIN, self.S_MAX)
        self.play(FadeIn(rects), FadeIn(cotes), FadeIn(gG), FadeIn(unite), Create(axes), Create(self.rappels()))

        N, M = ValueTracker(0), ValueTracker(0)

        def f():
            return sigma(N.get_value(), M.get_value())

        def y0():
            A, B = f()(0), f()(1) - f()(0)
            if abs(B) < 1e-9:
                return None
            y = -A / B
            return y if Y_INF < y < Y_SUP else None

        zones = always_redraw(lambda: self.zones(f()))
        diag = always_redraw(lambda: nav.diagramme(f()))
        ln = always_redraw(lambda: self.ligne_neutre(y0()) if y0() is not None else VMobject())
        self.add(zones, gG)
        self.play(FadeIn(diag))

        Pn = Panneau(1.9, 2.6, gap=0.22)
        lignes = [
            ligne_live("N =", N.get_value, r"\mathrm{kN}", fs=32, decimales=0),
            ligne_live("M =", M.get_value, r"\mathrm{kN\cdot m}", fs=32, decimales=1),
            ligne_live(r"\sigma_\text{sup} =", lambda: f()(Y_SUP), r"\mathrm{MPa}", fs=32),
            ligne_live(r"\sigma_\text{inf} =", lambda: f()(Y_INF), r"\mathrm{MPa}", fs=32),
        ]
        lignes[0].set_color(C_FORCE)
        lignes[1].set_color(C_FORCE)
        for l in lignes:
            Pn.placer(l)
        txt_y0 = always_redraw(lambda: (
            MathTex(r"\text{fibre neutre : } y_0 = " + fr(y0() + 0.0 if abs(y0()) >= 0.05 else 0.0)
                    + r"\ \mathrm{mm}", font_size=30)
            if y0() is not None else Tex(r"pas de fibre neutre dans la section", font_size=28)
        ).move_to([1.9, Pn.y - 0.2, 0], aligned_edge=LEFT))
        self.play(*map(FadeIn, lignes), FadeIn(txt_y0))
        self.add(ln)
        y_msg = Pn.y - 0.9

        def message(tex, couleur=WHITE):
            m = T(tex, font_size=28, color=couleur)
            m.move_to([1.9 + m.width / 2, y_msg - m.height / 2, 0])
            return m

        etapes = [
            ((M, -4), r"$M < 0$ : la droite \textbf{tourne}\\dans le sens horaire $\curvearrowright$\\"
                      r"(haut tendu, bas comprimé).\\$N = 0$ : fibre neutre en $G$."),
            ((M, 4), r"$M > 0$ : elle tourne dans\\l'autre sens $\curvearrowleft$\\(haut comprimé, bas tendu)."),
            ((M, -4), None),
            ((N, -48), r"$N < 0$ : la droite se \textbf{décale}\\vers la gauche de $N/S$ ;\\"
                       r"la fibre neutre \textbf{monte}."),
            ((N, -120), r"$N$ très négatif : la fibre neutre\\sort de la section, \textbf{toute}\\"
                        r"la section est comprimée !"),
            ((N, 60), r"$N > 0$ : décalage vers la droite ;\\la fibre neutre passe sous $G$."),
        ]
        msg = None
        for (tracker, v), tex in etapes:
            anims = [tracker.animate.set_value(v)]
            if msg is not None and tex is not None:
                anims.append(FadeOut(msg))
            self.play(*anims, run_time=2.5)
            if tex is not None:
                msg = message(tex, C_POS if "toute" in tex else WHITE)
                self.play(FadeIn(msg))
                self.etape()
        self.play(FadeOut(msg))
        msg = message(r"La \textbf{pente} dépend de $M$ (et de $I_{GZ}$),\\le \textbf{décalage} dépend de $N$"
                      r" (et de $S$).", YELLOW)
        self.play(FadeIn(msg))
        self.etape(2)
        for m in (zones, diag, ln, txt_y0, *[l[1] for l in lignes]):
            m.clear_updaters()


# ---------------------------------------------------------------------------
# 4. Tableau des 9 cas
# ---------------------------------------------------------------------------
class NavierTableau(Base):
    XC = (-3.0, -0.8, 1.4)        # colonnes : M < 0, M = 0, M > 0
    YC = (1.3, -0.5, -2.3)        # lignes : N < 0, N = 0, N > 0
    HY = 0.6                      # demi-hauteur de section dans une case

    def mini(self, sN, sM, c):
        """Petit diagramme de Navier (axes + droite + hachures) dans la case de centre c."""
        c = np.array([c[0], c[1], 0.0])
        f = lambda y: 0.35 * sN - 0.75 * sM * y            # y en unités écran (|y| <= HY)
        ax = VGroup(Line(c + 0.95 * LEFT, c + 0.95 * RIGHT), Line(c + (self.HY + 0.15) * DOWN,
                                                                     c + (self.HY + 0.2) * UP))
        ax.set_stroke(GREY_B, 2)
        h = VGroup()
        for y in np.linspace(-self.HY, self.HY, 9):
            s = f(y)
            if abs(s) > 0.02:
                h.add(Line(c + y * UP, c + y * UP + s * RIGHT, stroke_width=2.5, color=C_TRAC if s > 0 else C_COMP))
        d = Line(c + self.HY * DOWN + f(-self.HY) * RIGHT, c + self.HY * UP + f(self.HY) * RIGHT,
                 color=YELLOW, stroke_width=4)
        return VGroup(ax, h, d)

    def construct(self):
        titre = self.titre(r"Allure du diagramme de Navier selon les signes de $N$ et $M$")
        self.play(Write(titre))
        XC, YC = self.XC, self.YC
        ent_c = [Tex(r"$M < 0$\\$\curvearrowright$", font_size=30), Tex(r"$M = 0$", font_size=30),
                 Tex(r"$M > 0$\\$\curvearrowleft$", font_size=30)]
        ent_l = [Tex(r"$N < 0$\\$\leftarrow N/S$", font_size=30), Tex(r"$N = 0$", font_size=30),
                 Tex(r"$N > 0$\\$\rightarrow N/S$", font_size=30)]
        for e, x in zip(ent_c, XC):
            e.move_to([x, 2.45, 0])
        for e, y in zip(ent_l, YC):
            e.move_to([-5.1, y, 0])
        grille = VGroup(*[Line([-6.2, y, 0], [2.5, y, 0]) for y in (2.0, 0.4, -1.4)],
                        *[Line([x, 2.9 - 0.1, 0], [x, -3.3, 0]) for x in (-4.1, -1.9, 0.3)])
        grille.set_stroke(GREY_D, 2)
        self.play(Create(grille), *map(FadeIn, ent_c), *map(FadeIn, ent_l))

        cases = {}
        # case centrale : rien
        cases[(0, 0)] = self.mini(0, 0, (XC[1], YC[1]))
        self.play(FadeIn(cases[(0, 0)]))
        Pn = Panneau(2.75, 2.6, gap=0.25)
        t = Pn.placer(T(r"$N = 0$ et $M = 0$ :\\aucune contrainte.", font_size=28))
        self.play(Write(t))
        self.etape()

        # colonne du milieu : N décale
        t2 = Pn.placer(T(r"\textbf{$N$ décale} la droite\\de $N/S$ (contrainte en $G$).\\"
                         r"Colonne du milieu : traction\\ou compression \textbf{pure}.", font_size=28))
        for sN in (-1, 1):
            c = np.array([XC[1], YC[1 + sN], 0])
            base = Line(c + self.HY * DOWN, c + self.HY * UP, color=YELLOW, stroke_width=4)
            m = self.mini(sN, 0, c)
            fl = force(c, c + 0.35 * sN * RIGHT, couleur=C_FORCE, epaisseur=4)
            self.play(FadeIn(m[0]), Create(base))
            self.play(ReplacementTransform(base, m[2]), FadeIn(m[1]), GrowArrow(fl))
            cases[(sN, 0)] = VGroup(m, fl)
        self.play(Write(t2))
        self.etape()

        # ligne du milieu : M fait tourner
        t3 = Pn.placer(T(r"\textbf{$M$ fait tourner} l'axe vertical\\autour de $G$ : $\curvearrowleft$ si $M > 0$,"
                         r"\\$\curvearrowright$ si $M < 0$. Ligne du milieu :\\flexion \textbf{pure} ($\sigma = 0$ en $G$).",
                         font_size=28))
        for sM in (-1, 1):
            c = np.array([XC[1 + sM], YC[1], 0])
            base = Line(c + self.HY * DOWN, c + self.HY * UP, color=YELLOW, stroke_width=4)
            m = self.mini(0, sM, c)
            rot = fleche_sens(c + 0.75 * RIGHT + 0.45 * UP, sM, r=0.22, couleur=C_FORCE)
            self.play(FadeIn(m[0]), Create(base))
            self.play(ReplacementTransform(base, m[2]), FadeIn(m[1]), Create(rot))
            cases[(0, sM)] = VGroup(m, rot)
        self.play(Write(t3))
        self.etape()

        # les coins : on combine
        t4 = Pn.placer(T(r"Cas général : on \textbf{tourne}\\(signe de $M$) puis on \textbf{décale}\\"
                         r"(signe de $N$).", font_size=28, color=YELLOW))
        for sN in (-1, 1):
            for sM in (-1, 1):
                c = np.array([XC[1 + sM], YC[1 + sN], 0])
                m = self.mini(sN, sM, c)
                self.play(FadeIn(m[0]), Create(m[2]), FadeIn(m[1]), run_time=0.8)
        self.play(Write(t4))
        self.etape(2)
