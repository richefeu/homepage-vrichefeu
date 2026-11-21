"""
MS2 - Animations pédagogiques : déformée et flèche maximale (§3 du poly)

Scènes (dans l'ordre du cours) :
    CourbureMoment            la poutre fléchit, rayon de courbure petit là où M est grand : M = E I C,
                              C ≈ u_y'', deux intégrations successives (constantes K1, K2)
    ConditionsLimites         appui / articulation : u = 0 ; encastrement : u = 0 et u' = 0 ;
                              entre deux tronçons : pas de saut, pas de cassure
    DeformeeConsoleRepartie   exemple 1 du poly (console, charge q) : M(x), intégrations, A1 = A2 = 0,
                              u_y(x), ω(x), déformée animée
    DeformeeConsoleForce      exemple 2 du poly (console, F au milieu) : deux tronçons, continuité en C,
                              B1, B2, partie droite rectiligne
    FlecheMax                 f = −u_y, f_max des deux exemples, formulaire des 4 cas classiques,
                              application UPE 120 (13,2 mm en C, 86,9 mm en U)
    DimensionnementFleche     pourquoi limiter la flèche ; console P = 2 kN, L = 2 m, f_adm = L/200 :
                              (I_GZ)_min = 254 cm⁴ -> UPE 120 placé en C

Vidéo  : manim -qh deformee.py CourbureMoment ConditionsLimites DeformeeConsoleRepartie DeformeeConsoleForce \\
             FlecheMax DimensionnementFleche
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms2 import *  # noqa: E402,F403

C_DEF = TEAL_B          # couleur de la déformée


# Déformées normalisées (|u| max = 1, u < 0 vers le bas), x dans [0, L]
def u_console_q(L):
    return lambda x: -(x ** 4 - 4 * L * x ** 3 + 6 * L ** 2 * x ** 2) / (3 * L ** 4)


def u_console_F_bout(L):
    return lambda x: -(3 * L * x ** 2 - x ** 3) / (2 * L ** 3)


def u_console_F_milieu(L):
    def u(x):
        if x <= L / 2:
            v = (2 * x ** 3 - 3 * L * x ** 2) / 12
        else:
            xd = x - L / 2
            v = -(3 * L ** 2 * xd + L ** 3) / 24
        return v / (5 * L ** 3 / 48)
    return u


def u_appuis_F_milieu(L):
    def u(x):
        xx = min(x, L - x)
        return -(3 * L ** 2 * xx - 4 * xx ** 3) / L ** 3
    return u


def u_appuis_q(L):
    return lambda x: -16 / 5 * x * (L ** 3 - 2 * L * x ** 2 + x ** 3) / L ** 4


class DefScene(EIScene):
    YB = 1.7

    def courbe(self, u, amp, couleur=C_DEF, n=60, epaisseur=10):
        return poutre(*[self.X(x, amp * u(x)) for x in np.linspace(0, self.L, n)], couleur=couleur,
                      epaisseur=epaisseur)

    def deformable(self, u, amp, t):
        """Poutre qui se déforme quand t passe de 0 à 1."""
        return always_redraw(lambda: self.courbe(lambda x: t.get_value() * u(x), amp,
                                                 couleur=interpolate_color(GREY_B, C_DEF, t.get_value())))

    def lignes(self, *texs, fs=32, couleur=WHITE, gap=None):
        out = []
        for t in texs:
            m = MathTex(t, font_size=fs, color=couleur) if not isinstance(t, Mobject) else t
            self.ecrire(m, gap=gap)
            out.append(m)
        return out

    def axe_x(self):
        a = Arrow(self.X(0, -0.45), self.X(1.0, -0.45), buff=0, stroke_width=3, color=GREY_A,
                  max_tip_length_to_length_ratio=0.2)
        return VGroup(a, MathTex("x", font_size=30, color=GREY_A).next_to(a, RIGHT, buff=0.08))


# ---------------------------------------------------------------------------
# 1. La courbure est proportionnelle au moment
# ---------------------------------------------------------------------------
class CourbureMoment(DefScene):
    YB = 1.4

    def construct(self):
        titre = self.titre(r"Déformée : la courbure suit le moment")
        self.play(Write(titre))
        L = 6
        self.repere(L, largeur=9.0, xc=-0.3)
        u = u_appuis_q(L)
        AMP = 0.9
        t = ValueTracker(0)
        b = self.deformable(u, AMP, t)
        liaisons = VGroup(self.liaison("articulation", 0), self.liaison("appui", L))
        q = self.repartie(0, L, "q", h=0.7)
        self.play(FadeIn(b), FadeIn(liaisons), FadeIn(q))
        self.play(t.animate.set_value(1), run_time=2)
        t0 = T(r"Une poutre droite se \textbf{courbe} sous la charge (déformée amplifiée).", font_size=30)
        self.P.placer(t0)
        self.play(Write(t0))
        self.etape()

        # --- diagramme de M et cercles osculateurs
        Mf = lambda x: 0.5 * x * (L - x) / (L ** 2 / 8)          # M(x) normalisé (max 1 au milieu)
        dM = self.diagramme([(0, L, Mf)], y0=-2.9, ech=0.9, nom="M(x)", couleur=C_FORCE)
        self.play(FadeOut(t0), FadeOut(q), FadeIn(dM))

        def cercle(x, da):
            h = 1e-3
            ys = lambda xx: self.X(xx, AMP * u(xx))[1]
            xs = lambda xx: self.X(xx)[0]
            d1 = (ys(x + h) - ys(x - h)) / (xs(x + h) - xs(x - h))
            d2 = (ys(x + h) - 2 * ys(x) + ys(x - h)) / ((xs(x + h) - xs(x)) ** 2)
            R = (1 + d1 ** 2) ** 1.5 / abs(d2)
            p = self.X(x, AMP * u(x))
            n = np.array([-d1, 1, 0]) / np.sqrt(1 + d1 ** 2)
            c = p + R * n
            a0 = np.arctan2(*(p - c)[1::-1])
            arc = Arc(radius=R, start_angle=a0 - da, angle=2 * da, arc_center=c).set_stroke(YELLOW, 4)
            return VGroup(arc, Dot(p, color=YELLOW)), R

        a_mil, R1 = cercle(3.0, 0.32)
        a_cote, R2 = cercle(1.0, 0.18)
        l1 = Tex(r"$R$ petit : très courbé", font_size=26, color=YELLOW).next_to(a_mil, UP, buff=0.1)
        l2 = Tex(r"$R$ grand : peu courbé", font_size=26, color=YELLOW).next_to(a_cote, UP, buff=0.1).shift(0.3 * LEFT)
        rap = VGroup(DashedLine(self.X(3.0, AMP * u(3.0)), self.D(3.0, Mf(3.0), -2.9, 0.9)),
                     DashedLine(self.X(1.0, AMP * u(1.0)), self.D(1.0, Mf(1.0), -2.9, 0.9))).set_stroke(GREY_B, 2)
        self.play(Create(a_mil), FadeIn(l1), Create(rap[0]))
        self.play(Create(a_cote), FadeIn(l2), Create(rap[1]))
        rq = Tex(r"Courbure $\mathcal{C} = 1/R$ : grande là où $M$ est grand,\\nulle aux appuis où $M = 0$.",
                 font_size=28).to_edge(RIGHT, buff=0.3).set_y(-1.7)
        self.play(FadeIn(rq))
        self.etape()
        b.clear_updaters()
        self.tout_effacer(garder=[titre])

        # --- la relation M = E I C
        f1 = MathTex(r"M(x) = (E\,I_{GZ})\times \mathcal{C}(x)", font_size=52).move_to([0, 2.0, 0])
        c1 = SurroundingRectangle(f1, color=BLUE_B, buff=0.2)
        self.play(Write(f1), Create(c1))
        expl = VGroup(
            Tex(r"$E$ : module d'Young du \textbf{matériau} (acier $\approx 210\,000$ MPa, bois $\approx 10\,000$ MPa)",
                font_size=28),
            Tex(r"$I_{GZ}$ : moment quadratique de la \textbf{section} (§1)", font_size=28),
            Tex(r"$E\,I_{GZ}$ : \textbf{rigidité en flexion} ; plus elle est grande, moins la poutre se courbe",
                font_size=28, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(c1, DOWN, buff=0.35)
        for e in expl:
            self.play(FadeIn(e, shift=0.2 * UP))
        self.etape()
        self.play(FadeOut(expl), VGroup(f1, c1).animate.scale(0.75).to_edge(UP, buff=1.2).to_edge(LEFT, buff=0.5))

        P = Panneau(-6.6, 1.0, gap=0.3)
        l = [P.placer(m) for m in (
            T(r"Petites déformations : la courbure est la dérivée seconde de la déformée $u_y(x)$ :", font_size=28),
            MathTex(r"\mathcal{C}(x) = u_y''(x) \quad\Rightarrow\quad u_y''(x) = \frac{M(x)}{E\,I_{GZ}}", font_size=40),
            T(r"On intègre deux fois ; \textbf{chaque intégration ajoute une constante} :", font_size=28),
            MathTex(r"u_y'(x) = \frac{1}{E\,I_{GZ}}\int M(x)\,\mathrm{d}x + K_1"
                    r"\qquad u_y(x) = \int u_y'(x)\,\mathrm{d}x + K_2", font_size=36),
        )]
        for m in l:
            self.play(Write(m))
        cad = SurroundingRectangle(l[1], color=YELLOW, buff=0.12)
        self.play(Create(cad))
        self.etape()
        self.play(*map(FadeOut, l + [cad]))

        P.reset()
        g = [P.placer(m) for m in (
            T(r"Exemple : $M(x) = a x^2 + b x + c$ (charge répartie sur le tronçon)", font_size=28),
            MathTex(r"u_y''(x) = \frac{1}{E I_{GZ}}\left(a x^2 + b x + c\right)", font_size=36),
            MathTex(r"u_y'(x) = \frac{1}{E I_{GZ}}\left(a\frac{x^3}{3} + b\frac{x^2}{2} + c\,x + K_1\right)",
                    font_size=36),
            MathTex(r"u_y(x) = \frac{1}{E I_{GZ}}\left(a\frac{x^4}{12} + b\frac{x^3}{6} + c\frac{x^2}{2} + K_1 x + K_2\right)",
                    font_size=36),
        )]
        for m in g:
            self.play(Write(m))
        fin = Tex(r"$K_1$ et $K_2$ se trouvent avec les \textbf{conditions aux limites} (vidéo suivante).",
                  font_size=28, color=YELLOW).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(fin))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Conditions aux limites et de continuité
# ---------------------------------------------------------------------------
class ConditionsLimites(DefScene):
    YB = 1.2

    def tangente(self, u, amp, x, long=1.2, couleur=YELLOW):
        h = 1e-3
        p0, p1 = self.X(x - h, amp * u(x - h)), self.X(x + h, amp * u(x + h))
        d = normalize(p1 - p0)
        p = self.X(x, amp * u(x))
        return DashedLine(p - long * d, p + long * d, color=couleur, stroke_width=3)

    def construct(self):
        titre = self.titre(r"Les conditions aux limites")
        self.play(Write(titre))
        L = 6

        # --- appui simple / articulation
        self.repere(L, largeur=8.0, xc=-0.5)
        u = u_appuis_q(L)
        t = ValueTracker(0)
        b = self.deformable(u, 0.9, t)
        li = VGroup(self.liaison("articulation", 0), self.liaison("appui", L))
        self.play(FadeIn(b), FadeIn(li))
        self.play(t.animate.set_value(1), run_time=1.5)
        tg = VGroup(self.tangente(u, 0.9, 0.001), self.tangente(u, 0.9, L - 0.001))
        self.play(Create(tg))
        e1 = self.lignes(
            T(r"\textbf{Appui ou articulation} en $x_i$ : le point ne monte ni ne descend,", font_size=30),
            MathTex(r"u_y(x_i) = 0", font_size=40, color=YELLOW),
            T(r"mais la poutre peut \textbf{tourner} : la pente $u_y'(x_i)$ n'est pas nulle.", font_size=30,
              color=GREY_B),
        )
        self.etape()
        b.clear_updaters()
        self.tout_effacer(garder=[titre])

        # --- encastrement
        self.repere(L, largeur=8.0, xc=-0.5)
        u = u_console_F_bout(L)
        t = ValueTracker(0)
        b = self.deformable(u, 1.2, t)
        enc = self.liaison("encastrement", 0)
        self.play(FadeIn(b), FadeIn(enc))
        self.play(t.animate.set_value(1), run_time=1.5)
        tg = self.tangente(u, 1.2, 0.001, long=1.5)
        self.play(Create(tg))
        e2 = self.lignes(
            T(r"\textbf{Encastrement} en $x_i$ : ni déplacement, \textbf{ni rotation} :", font_size=30),
            MathTex(r"u_y(x_i) = 0 \qquad\text{et}\qquad u_y'(x_i) = 0", font_size=40, color=YELLOW),
            T(r"la déformée part \textbf{horizontalement} de l'encastrement.", font_size=30, color=GREY_B),
        )
        self.etape()
        b.clear_updaters()
        self.tout_effacer(garder=[titre])

        # --- continuité entre deux tronçons
        self.repere(L, largeur=8.0, xc=-0.5)
        xi = 3.0
        ug = lambda x: -0.15 * x ** 2 / 9
        ok_d = lambda x: ug(xi) + (-0.3 * xi / 9) * (x - xi)
        saut_d = lambda x: ok_d(x) - 0.35
        casse_d = lambda x: ug(xi) + 0.25 * (x - xi) / 3

        def tronçon(f, x0, x1, couleur):
            return poutre(*[self.X(x, 3 * f(x)) for x in np.linspace(x0, x1, 30)], couleur=couleur, epaisseur=8)
        g = tronçon(ug, 0, xi, C_DEF)
        enc = self.liaison("encastrement", 0)
        lab = VGroup(Tex(r"tronçon g", font_size=28, color=C_DEF).next_to(self.X(1.5, 0.5), UP),
                     Tex(r"tronçon d", font_size=28, color=PURPLE_B).next_to(self.X(4.5, 0.5), UP))
        pt = VGroup(croix(self.X(xi, 3 * ug(xi)), YELLOW),
                    MathTex(r"x_i", font_size=30, color=YELLOW).next_to(self.X(xi, 3 * ug(xi)), DOWN, buff=0.25))
        self.play(FadeIn(enc), Create(g), FadeIn(lab), FadeIn(pt))
        cases = [(saut_d, r"\boldsymbol{\times}\ \text{la poutre serait coupée (saut)}", C_KO_),
                 (casse_d, r"\boldsymbol{\times}\ \text{la poutre serait cassée (pente différente)}", C_KO_),
                 (ok_d, r"\checkmark\ \text{continue : même déplacement et même pente}", C_POS)]
        d_prev, m_prev = None, None
        for f, tex, col in cases:
            d = tronçon(f, xi, L, PURPLE_B)
            m = MathTex(tex, font_size=32, color=col).move_to([0, self.YB - 2.6, 0])
            if d_prev is None:
                self.play(Create(d), FadeIn(m))
            else:
                self.play(ReplacementTransform(d_prev, d), ReplacementTransform(m_prev, m))
            self.wait(0.8)
            d_prev, m_prev = d, m
        self.etape()
        self.P.y = self.YB - 3.1
        e3 = self.lignes(
            T(r"Entre deux tronçons de longueurs $\ell_g$ et $\ell_d$ (avec $x$ compté depuis le début de chaque tronçon) :",
              font_size=28),
            MathTex(r"u_{y,g}'(\ell_g) = u_{y,d}'(0) \qquad\text{et}\qquad u_{y,g}(\ell_g) = u_{y,d}(0)", font_size=38,
                    color=YELLOW),
        )
        self.etape(2)


C_KO_ = RED


# ---------------------------------------------------------------------------
# 3. Exemple 1 : console sous charge répartie
# ---------------------------------------------------------------------------
class DeformeeConsoleRepartie(DefScene):
    def construct(self):
        titre = self.titre(r"Exemple 1 : console sous charge répartie")
        self.play(Write(titre))
        L = 4
        self.repere(L, largeur=6.5, xc=-1.8)
        b0 = poutre(self.X(0), self.X(L))
        enc = self.liaison("encastrement", 0)
        q = self.repartie(0, L, "q", h=0.6)
        A = self.point(0, "A", cote=UR)
        cl = self.cote_x(0, L, r"\ell", dy=-0.95)
        ax = self.axe_x()
        self.play(Create(b0), FadeIn(enc))
        self.play(FadeIn(q), FadeIn(A), FadeIn(cl), FadeIn(ax))
        data = Tex(r"Rigidité en flexion $E\,I_{GZ}$,\\encastrée en $A$ ($x = 0$).", font_size=28,
                   color=GREY_B).to_edge(RIGHT, buff=0.3).set_y(self.YB)
        self.play(FadeIn(data))
        self.etape()

        # --- 1. M(x) par la coupure (partie droite)
        xc = 2.4
        cut = self.coupure(xc)
        res = self.charge((xc + L) / 2, r"q(\ell - x)", h=0.9, couleur=ORANGE, cote_lab=RIGHT)
        bras = cote(self.X(xc, -0.45), self.X((xc + L) / 2, -0.45), r"\tfrac{\ell - x}{2}", DOWN, fs=26)
        self.play(Create(cut), q.animate.set_opacity(0.25))
        self.play(FadeIn(res), FadeIn(bras), FadeOut(cl))
        self.lignes(
            T(r"\textbf{1.} On coupe en $x$ et on isole la partie droite :", font_size=28),
            r"M(x) = -q(\ell - x)\times\frac{\ell - x}{2} = -\frac{q}{2}\left(x^2 - 2\ell x + \ell^2\right)",
        )
        self.etape()
        self.play(FadeOut(cut), FadeOut(res), FadeOut(bras), q.animate.set_opacity(1), FadeIn(cl))
        self.effacer_calculs()

        # --- 2. deux intégrations
        self.lignes(
            T(r"\textbf{2.} On intègre deux fois (constantes $A_1$ et $A_2$) :", font_size=28),
            r"u_y''(x) = \frac{M(x)}{E I_{GZ}} = -\frac{q}{2EI_{GZ}}\left(x^2 - 2\ell x + \ell^2\right)",
            r"u_y'(x) = -\frac{q}{2EI_{GZ}}\left(\frac{x^3}{3} - \ell x^2 + \ell^2 x + A_1\right)",
            r"u_y(x) = -\frac{q}{2EI_{GZ}}\left(\frac{x^4}{12} - \frac{\ell x^3}{3} + \frac{\ell^2 x^2}{2} + A_1 x + A_2\right)",
            fs=30,
        )
        self.etape()
        self.effacer_calculs()

        # --- 3. conditions aux limites
        self.play(Indicate(enc, color=YELLOW), Indicate(A, color=YELLOW))
        self.lignes(
            T(r"\textbf{3.} Encastrement en $A$ : ni déplacement ni rotation en $x = 0$ :", font_size=28),
            r"u_y'(0) = 0 \ \Rightarrow\ -\frac{q\,A_1}{2EI_{GZ}} = 0 \ \Rightarrow\ A_1 = 0",
            r"u_y(0) = 0 \ \Rightarrow\ -\frac{q\,A_2}{2EI_{GZ}} = 0 \ \Rightarrow\ A_2 = 0",
            fs=32,
        )
        self.etape()
        self.effacer_calculs()

        # --- 4. résultats
        r = self.lignes(
            T(r"\textbf{4.} Résultat (on note $\omega(x) = u_y'(x)$ la rotation, petite : $\tan\omega \approx \omega$) :",
              font_size=28),
            r"u_y(x) = -\frac{q}{24EI_{GZ}}\left(x^4 - 4\ell x^3 + 6\ell^2 x^2\right)",
            r"\omega(x) = -\frac{q}{6EI_{GZ}}\left(x^3 - 3\ell x^2 + 3\ell^2 x\right)",
            fs=34, couleur=YELLOW,
        )
        self.play(Create(SurroundingRectangle(VGroup(r[1], r[2]), color=YELLOW, buff=0.12)))
        self.etape()
        self.effacer_calculs()
        self.play(*map(FadeOut, self.mobjects[1:]))

        # --- 5. la déformée et les rotations
        u = u_console_q(L)
        t = ValueTracker(0)
        AMP = 1.0
        b = self.deformable(u, AMP, t)
        enc, A = self.liaison("encastrement", 0), self.point(0, "A", cote=UR)
        self.play(FadeIn(b), FadeIn(enc), FadeIn(A))
        self.play(t.animate.set_value(1), run_time=2.5)
        fl = cote(self.X(L, 0) + 0.45 * RIGHT, self.X(L, -AMP) + 0.45 * RIGHT,
                  r"u_y(\ell) = -\frac{q\ell^4}{8EI_{GZ}}", RIGHT, fs=28)
        self.play(FadeIn(fl))
        om = lambda x: -(x ** 3 - 3 * L * x ** 2 + 3 * L ** 2 * x) / L ** 3
        dO = self.diagramme([(0, L, om)], y0=-1.2, ech=1.1, nom=r"\omega(x)", couleur=PURPLE_B)
        v0 = MathTex(r"\omega(0) = 0", font_size=26).next_to(self.D(0, 0, -1.2, 1.1), UP, buff=0.12).shift(0.6 * RIGHT)
        vL = MathTex(r"\omega(\ell) = -\frac{q\ell^3}{6EI_{GZ}}", font_size=26).next_to(self.D(L, -1, -1.2, 1.1),
                                                                                    RIGHT, buff=0.15)
        self.play(FadeIn(dO), FadeIn(v0), FadeIn(vL))
        rq = Tex(r"Déformée amplifiée. $x$ est compté depuis $A$ sur tout le tronçon.\\"
                 r"Rotation nulle à l'encastrement, maximale au bout libre.", font_size=26,
                 color=GREY_B).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(rq))
        self.etape(2)
        b.clear_updaters()


# ---------------------------------------------------------------------------
# 4. Exemple 2 : console avec une force au milieu
# ---------------------------------------------------------------------------
class DeformeeConsoleForce(DefScene):
    def construct(self):
        titre = self.titre(r"Exemple 2 : console avec une force au milieu")
        self.play(Write(titre))
        L = 4
        self.repere(L, largeur=6.5, xc=-1.8)
        b0 = poutre(self.X(0), self.X(L))
        enc = self.liaison("encastrement", 0)
        F = self.charge(L / 2, "F", h=1.0)
        pts = VGroup(self.point(0, "A", cote=UR), self.point(L / 2, "C", cote=DR), self.point(L, "B", cote=UR))
        cl = VGroup(self.cote_x(0, L / 2, r"\ell/2", dy=-0.95), self.cote_x(L / 2, L, r"\ell/2", dy=-0.95))
        self.play(Create(b0), FadeIn(enc))
        self.play(FadeIn(F), FadeIn(pts), FadeIn(cl))
        tr = VGroup(Tex(r"tronçon g", font_size=26, color=C_DEF).next_to(self.X(L / 4, -0.3), DOWN, buff=0.05),
                    Tex(r"tronçon d", font_size=26, color=PURPLE_B).next_to(self.X(3 * L / 4, -0.3), DOWN, buff=0.05))
        self.play(FadeIn(tr))
        data = Tex(r"Rigidité $E\,I_{GZ}$. Deux tronçons :\\$x$ compté depuis $A$ (g),\\puis depuis $C$ (d).",
                   font_size=28, color=GREY_B).to_edge(RIGHT, buff=0.3).set_y(self.YB)
        self.play(FadeIn(data))
        self.etape()

        # --- 1. moments
        self.lignes(
            T(r"\textbf{1.} Coupure dans g : à droite, $F$ à la distance $\ell/2 - x$ ;"
              r" coupure dans d : rien à droite.", font_size=28),
            r"M_g(x) = -F\left(\frac{\ell}{2} - x\right) = F x - \frac{\ell F}{2}"
            r"\qquad\qquad M_d(x) = 0",
        )
        self.etape()
        self.effacer_calculs()

        # --- 2. intégrations (deux colonnes)
        self.lignes(T(r"\textbf{2.} On intègre sur chaque tronçon (4 constantes) :", font_size=28))
        y0 = self.P.y
        gauche = VGroup(*[MathTex(t, font_size=30, color=C_DEF) for t in (
            r"u_{y,g}'' = \frac{F}{EI_{GZ}}\left(x - \frac{\ell}{2}\right)",
            r"u_{y,g}' = \frac{F}{EI_{GZ}}\left(\frac{x^2}{2} - \frac{\ell x}{2} + A_1\right)",
            r"u_{y,g} = \frac{F}{EI_{GZ}}\left(\frac{x^3}{6} - \frac{\ell x^2}{4} + A_1 x + A_2\right)")]
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        droite = VGroup(*[MathTex(t, font_size=30, color=PURPLE_B) for t in (
            r"u_{y,d}'' = 0", r"u_{y,d}' = B_1", r"u_{y,d} = B_1 x + B_2")]).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        gauche.move_to([-6.6, y0, 0], aligned_edge=UL)
        droite.move_to([2.2, y0, 0], aligned_edge=UL)
        for m in gauche:
            self.play(Write(m))
        for m in droite:
            self.play(Write(m))
        rq = T(r"pas de moment $\Rightarrow$ pas de courbure :\\le tronçon d reste \textbf{droit}.", font_size=26,
               color=PURPLE_B).next_to(droite, DOWN, buff=0.25, aligned_edge=LEFT)
        self.play(FadeIn(rq))
        self.contenu += [gauche, droite, rq]
        self.etape()
        self.effacer_calculs()

        # --- 3. conditions
        self.play(Indicate(enc, color=YELLOW))
        self.lignes(
            T(r"\textbf{3.} En $A$ (encastrement) : $u_{y,g}'(0) = 0 \Rightarrow A_1 = 0$ et"
              r" $u_{y,g}(0) = 0 \Rightarrow A_2 = 0$.", font_size=28),
        )
        self.play(Indicate(pts[1], color=YELLOW))
        self.lignes(
            T(r"En $C$ : continuité ($x = \ell/2$ pour g, $x = 0$ pour d) :", font_size=28),
            r"u_{y,g}'(\ell/2) = u_{y,d}'(0) \ \Rightarrow\ B_1 = \frac{F}{EI_{GZ}}\left(\frac{\ell^2}{8} - \frac{\ell^2}{4}\right)"
            r" = -\frac{F\ell^2}{8EI_{GZ}}",
            r"u_{y,g}(\ell/2) = u_{y,d}(0) \ \Rightarrow\ B_2 = \frac{F}{EI_{GZ}}\left(\frac{\ell^3}{48} - \frac{\ell^3}{16}\right)"
            r" = -\frac{F\ell^3}{24EI_{GZ}}",
            fs=30,
        )
        self.etape()
        self.effacer_calculs()

        # --- 4. résultats
        self.lignes(T(r"\textbf{4.} Résultat :", font_size=28))
        y0 = self.P.y
        gauche = VGroup(MathTex(r"u_{y,g}(x) = \frac{F}{12EI_{GZ}}\left(2x^3 - 3\ell x^2\right)", font_size=32),
                        MathTex(r"\omega_g(x) = \frac{F}{2EI_{GZ}}\left(x^2 - \ell x\right)", font_size=32)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([-6.6, y0, 0], aligned_edge=UL)
        droite = VGroup(MathTex(r"u_{y,d}(x) = -\frac{F}{24EI_{GZ}}\left(3\ell^2 x + \ell^3\right)", font_size=32),
                        MathTex(r"\omega_d(x) = -\frac{F\ell^2}{8EI_{GZ}}", font_size=32)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([0.6, y0, 0], aligned_edge=UL)
        gauche.set_color(C_DEF)
        droite.set_color(PURPLE_B)
        self.play(Write(gauche))
        self.play(Write(droite))
        cad = SurroundingRectangle(VGroup(gauche, droite), color=YELLOW, buff=0.15)
        self.play(Create(cad))
        rq = T(r"Rotation constante dans d : $u_{y,d}$ est linéaire (une droite).", font_size=26,
               color=GREY_B).next_to(cad, DOWN, buff=0.25)
        self.play(FadeIn(rq))
        self.contenu += [gauche, droite, cad, rq]
        self.etape()
        self.effacer_calculs()
        self.play(FadeOut(F), FadeOut(cl), FadeOut(tr), FadeOut(data), FadeOut(b0))

        # --- 5. déformée
        u = u_console_F_milieu(L)
        t = ValueTracker(0)
        AMP = 1.0
        b = self.deformable(u, AMP, t)
        self.add(b)
        self.play(FadeOut(pts[1:]))
        self.play(t.animate.set_value(1), run_time=2.5)
        xC = L / 2
        pts2 = VGroup(*[VGroup(croix(self.X(x, AMP * u(x))), MathTex(n, font_size=FS_EQ).next_to(
            self.X(x, AMP * u(x)), UR, buff=0.1)) for x, n in ((L / 2, "C"), (L, "B"))])
        self.play(FadeIn(pts2))
        pC = self.X(xC, AMP * u(xC))
        pB = self.X(L, AMP * u(L))
        tg = DashedLine(pC + 0.2 * (pC - pB), pB + 0.25 * (pB - pC), color=YELLOW, stroke_width=3)
        lab = Tex(r"tronçon d : droite\\(tangente en $C$)", font_size=26, color=YELLOW).next_to((pC + pB) / 2, DOWN,
                                                                                         buff=0.35)
        fl = cote(self.X(L, 0) + 0.45 * RIGHT, pB + 0.45 * RIGHT, r"u_{y,d}(\ell/2) = -\frac{5F\ell^3}{48EI_{GZ}}",
                  RIGHT, fs=26)
        self.play(Create(tg), FadeIn(lab))
        self.play(FadeIn(fl))
        rq = Tex(r"Attention : dans $u_{y,d}(x)$, $x$ est compté depuis $C$ : le bout libre est en $x = \ell/2$.",
                 font_size=28, color=C_NEG).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(rq))
        self.etape(2)
        b.clear_updaters()


# ---------------------------------------------------------------------------
# 5. Flèche maximale
# ---------------------------------------------------------------------------
class FlecheMax(DefScene):
    CAS = [
        ("console", "F_bout", u_console_F_bout, r"f_\text{max} = \frac{F\ell^3}{3EI_{GZ}}"),
        ("console", "q", u_console_q, r"f_\text{max} = \frac{q\ell^4}{8EI_{GZ}}"),
        ("appuis", "F_milieu", u_appuis_F_milieu, r"f_\text{max} = \frac{F\ell^3}{48EI_{GZ}}"),
        ("appuis", "q", u_appuis_q, r"f_\text{max} = \frac{5q\ell^4}{384EI_{GZ}}"),
    ]

    def petit_cas(self, xc, yb, largeur, appuis, charge, u, amp=0.4):
        self.YB = yb
        L = 4
        self.repere(L, largeur=largeur, xc=xc)
        g = VGroup(DashedLine(self.X(0), self.X(L), color=GREY_C, stroke_width=3),
                   self.courbe(u(L), amp, epaisseur=7))
        if appuis == "console":
            g.add(symbole_encastrement(self.X(0), angle=-90, s=0.7))
        else:
            g.add(symbole_articulation(self.X(0), s=0.35), symbole_appui(self.X(L), s=0.35))
        if charge == "q":
            g.add(self.repartie(0, L, "q", h=0.4))
        else:
            xF = L if charge == "F_bout" else L / 2
            g.add(self.charge(xF, "F", h=0.7))
        g.add(cote(self.X(0, -amp - 0.35), self.X(L, -amp - 0.35), r"\ell", DOWN, fs=26))
        return g

    def construct(self):
        titre = self.titre(r"La flèche maximale $f_\text{max}$")
        self.play(Write(titre))

        # --- définition sur l'exemple 1
        g = self.petit_cas(-2.5, 1.4, 6.0, "console", "q", u_console_q, amp=1.0)
        self.play(FadeIn(g))
        pB = self.X(4, -1.0)
        f = cote(self.X(4, 0) + 0.4 * RIGHT, pB + 0.4 * RIGHT, r"f_\text{max}", RIGHT)
        self.play(FadeIn(f))
        Pn = Panneau(-6.6, -0.55, gap=0.18)
        d = [Pn.placer(m) for m in (
            MathTex(r"f = -u_y \quad\text{(la flèche est comptée positive vers le bas)}", font_size=36),
            T(r"$f_\text{max}$ : là où $|u_y|$ est maximal ($u_y' = 0$, ou à une extrémité).\\"
              r"Pour une console : au bout libre.", font_size=30),
        )]
        for m in d:
            self.play(Write(m))
        self.etape()
        e = [Pn.placer(m) for m in (
            MathTex(r"\text{Exemple 1 : } f_\text{max} = -u_y(\ell) = \frac{3q\ell^4}{24EI_{GZ}}"
                    r" = \frac{q\ell^4}{8EI_{GZ}}", font_size=34, color=YELLOW),
            MathTex(r"\text{Exemple 2 : } f_\text{max} = -u_{y,d}(\ell/2) = \frac{5F\ell^3}{48EI_{GZ}}",
                    font_size=34, color=YELLOW),
        )]
        for m in e:
            self.play(Write(m))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- formulaire des cas classiques
        intro = Tex(r"Les cas courants sont déjà calculés dans des \textbf{formulaires} :", font_size=30)
        intro.to_edge(UP, buff=1.15)
        self.play(FadeIn(intro))
        pos = [(-3.8, 1.0), (2.9, 1.0), (-3.8, -2.0), (2.9, -2.0)]
        for (app, ch, u, form), (xc, yb) in zip(self.CAS, pos):
            g = self.petit_cas(xc - 0.9, yb, 3.2, app, ch, u)
            fm = MathTex(form, font_size=32, color=YELLOW).next_to(g, RIGHT, buff=0.35).set_y(yb - 0.3)
            self.play(FadeIn(g), Write(fm), run_time=1.2)
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- application numérique
        g = self.petit_cas(-3.0, 1.6, 5.0, "console", "q", u_console_q, amp=0.6)
        self.play(FadeIn(g))
        don = VGroup(
            T(r"Console en acier, $\ell = 3$ m, $q = 1$ kN/m,", font_size=28),
            T(r"\textsf{UPE\,120}, $E = 210\,000$ MPa", font_size=28),
            T(r"(unités : N et mm, donc $q = 1$ N/mm)", font_size=26, color=GREY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([1.4, 2.0, 0], aligned_edge=UL)
        self.play(FadeIn(don))
        Pn = Panneau(-6.6, -0.6, gap=0.3)
        r = [Pn.placer(m) for m in (
            MathTex(r"\text{placé en C : } I_{GZ} = \mathsf{I_y} = 364\cdot 10^4\ \mathrm{mm^4}"
                    r"\ \Rightarrow\ f_\text{max} = \frac{1\times 3000^4}{8\times 210\,000\times 364\cdot 10^4}"
                    r" = 13{,}2\ \mathrm{mm}", font_size=30),
            MathTex(r"\text{placé en U : } I_{GZ} = \mathsf{I_z} = 55{,}5\cdot 10^4\ \mathrm{mm^4}"
                    r"\ \Rightarrow\ f_\text{max} = \frac{1\times 3000^4}{8\times 210\,000\times 55{,}5\cdot 10^4}"
                    r" = 86{,}9\ \mathrm{mm}", font_size=30),
        )]
        for m in r:
            self.play(Write(m))
        concl = T(r"Même poutre, même charge : $6{,}6$ fois plus de flèche en U !", font_size=30,
                  color=YELLOW).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(concl))
        self.etape(2)


# ---------------------------------------------------------------------------
# 6. Dimensionner avec la flèche
# ---------------------------------------------------------------------------
class DimensionnementFleche(DefScene):
    def construct(self):
        titre = self.titre(r"Dimensionner avec la flèche maximale")
        self.play(Write(titre))
        raisons = VGroup(*[Tex(r"\checkmark\ " + t, font_size=30) for t in (
            r"\textbf{confort} des usagers (plancher qui « bouge », pont qui vibre)",
            r"\textbf{limites de service} : l'ELS des Eurocodes impose une flèche maximale",
            r"éviter les \textbf{désordres} : fissures des cloisons, carrelages, vitrages...",
            r"\textbf{sécurité des éléments voisins} (porte-à-faux, éléments architecturaux)",
        )]).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([0, 0.6, 0])
        for r in raisons:
            self.play(FadeIn(r, shift=0.2 * UP))
        self.etape()
        self.play(FadeOut(raisons))

        # --- l'exemple
        L = 4
        self.YB = 2.0
        self.repere(L, largeur=4.2, xc=-4.5)
        b = self.courbe(u_console_F_bout(L), 0.6)
        g = VGroup(DashedLine(self.X(0), self.X(L), color=GREY_C, stroke_width=3), b,
                   self.liaison("encastrement", 0), self.charge(L, "P", h=0.8),
                   cote(self.X(0, -0.95), self.X(L, -0.95), "L", DOWN, fs=28),
                   cote(self.X(L, 0) + 0.35 * RIGHT, self.X(L, -0.6) + 0.35 * RIGHT, r"f_\text{max}", RIGHT, fs=26))
        self.play(FadeIn(g))
        don = VGroup(
            T(r"Console en acier : $P = 2$ kN, $L = 2$ m,", font_size=26),
            T(r"$E = 210\,000$ MPa, profilé UPE \textbf{placé en C}", font_size=26),
            T(r"Exigence : $f_\text{max} \leq L/200 = 10$ mm", font_size=26, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([0.2, 2.6, 0], aligned_edge=UL)
        self.play(FadeIn(don))
        Pn = Panneau(0.2, don.get_bottom()[1] - 0.2, gap=0.2)
        l = [Pn.placer(m) for m in (
            MathTex(r"f_\text{max} = \frac{P L^3}{3EI_{GZ}}\ \Rightarrow\ (I_{GZ})_\text{min} = \frac{P L^3}{3E\,f_\text{max}}",
                    font_size=28),
            MathTex(r"(I_{GZ})_\text{min} = \frac{2000\times 2000^3}{3\times 210\,000\times 10} = 254\cdot 10^4\ \mathrm{mm^4}"
                    r" = 254\ \mathrm{cm^4}", font_size=28, color=YELLOW),
        )]
        l[1].move_to([-6.6, 0.35, 0], aligned_edge=LEFT)
        for m in l:
            self.play(Write(m))
        self.etape()

        tab = tableau_upe(largeur=10.0).move_to([0.3, -2.35, 0])
        self.play(FadeIn(tab))
        COL_IY, COL_IZ = 5, 7
        col = SurroundingRectangle(tab.get_columns()[COL_IY - 1], color=YELLOW, buff=0.03)
        txt = T(r"colonne $\mathsf{I_y}$ (placé en C) : la plus petite valeur $\geq 254$ cm$^4$", font_size=26)
        txt.move_to([-6.6, -0.4, 0], aligned_edge=LEFT)
        self.play(Create(col), FadeIn(txt))
        marques = []
        for ligne, ok in ((2, False), (3, False), (4, True)):
            cel = tab.get_cell((ligne, COL_IY), color=C_POS if ok else RED).set_stroke(width=5)
            sym = MathTex(r"\checkmark" if ok else r"\boldsymbol{\times}", font_size=34,
                          color=C_POS if ok else RED).next_to(tab, RIGHT, buff=0.15).set_y(cel.get_y())
            self.play(Create(cel), FadeIn(sym), run_time=0.7)
            marques += [cel, sym]
        self.etape()
        self.play(FadeOut(txt))
        res = VGroup(
            T(r"$\Rightarrow$ \textsf{UPE\,120} : vérification", font_size=28, color=C_POS),
            MathTex(r"f_\text{max} = \frac{2000\times 2000^3}{3\times 210\,000\times 364\cdot 10^4} = 7{,}0\ \mathrm{mm}"
                    r" \leq 10 \ \checkmark", font_size=28, color=C_POS),
        ).arrange(RIGHT, buff=0.3).move_to([0, -0.4, 0])
        self.play(Write(res))
        self.etape()
        self.play(FadeOut(res), *map(FadeOut, marques), FadeOut(col))
        colZ = SurroundingRectangle(tab.get_columns()[COL_IZ - 1], color=YELLOW, buff=0.03)
        rz = T(r"Placé en U (colonne $\mathsf{I_z}$) : toutes les valeurs sont $< 254$ cm$^4$, aucun ne convient !",
               font_size=26, color=RED).move_to([0, -0.4, 0])
        self.play(Create(colZ), FadeIn(rz))
        self.etape()
        fin = MathTex(r"\text{Vérifier aussi les contraintes (§2) : }\ \frac{|M|}{\mathsf{W_{el,y}}} = "
                      r"\frac{4\cdot 10^6}{60{,}6\cdot 10^3} = 66\ \mathrm{MPa}\ \checkmark", font_size=26,
                      color=YELLOW).move_to([0, -0.3, 0])
        self.play(FadeOut(rz), FadeOut(colZ), FadeIn(fin))
        self.etape(2)
