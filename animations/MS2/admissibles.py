"""
MS2 - Animations pédagogiques : contraintes normales admissibles (§2.2 à 2.5 du poly)

Scènes (dans l'ordre du cours) :
    ContraintesAdmissibles  σ_min < σ < σ_max ; poutre béton 200 x 400 mm, M = −40 kN·m :
                            σ_sup = +7,5 MPa > σ_max = 2,5 MPa  ->  fissure en haut
    SolutionsRupture        les 5 remèdes en direct : réduire q ou ℓ, matériau plus résistant, augmenter h,
                            précontrainte (N < 0), armatures
    SectionNonSymetrique    section en T de §1, M = −4 kN·m : σ_sup ≠ −σ_inf ; la même section retournée
                            ne passe plus (σ_sup = +43 MPa > 30 MPa)
    NavierUPE               UPE 120, M = −3 kN·m, acier S235 : en C (W_el,y), en ∩ (W_el,z et I_z),
                            module de flexion élastique w_el = I_GZ / max(−y_inf, y_sup)
    ChoixProfile            méthode en 5 étapes : M_crit = −6 kN·m, σ_adm = ±160 MPa -> (w_el)_min = 37,5 cm³
                            -> UPE 100 placé en C ; placé en U, aucun profilé de l'extrait ne convient

Vidéo  : manim -qh admissibles.py ContraintesAdmissibles SolutionsRupture SectionNonSymetrique NavierUPE ChoixProfile
Slides : manim-slides render admissibles.py ContraintesAdmissibles SolutionsRupture SectionNonSymetrique NavierUPE ChoixProfile
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms2 import *  # noqa: E402,F403
from navier import RECTS_T, I_T  # noqa: E402

C_KO = RED


def verif(prefixe, f, ok, fs=30, unite=r"\mathrm{MPa}"):
    """Valeur en direct, en vert si ok() est vrai, en rouge sinon."""
    g = ligne_live(prefixe, f, unite, fs=fs, decimales=1)
    g.add_updater(lambda m: m.set_color(C_POS if ok() else C_KO))
    return g


def fmt(v):
    """Valeur signée au format français : 2.5 -> +2{,}5 ; -25 -> -25."""
    t = f"{v:+.1f}".rstrip("0").rstrip(".")
    return t.replace(".", "{,}")


class AdmScene(Base):
    """Section à gauche, diagramme de Navier avec zones interdites au milieu, texte à droite."""
    KY, KS = 0.006, 0.11          # écran / mm, écran / MPa
    YG, XS, XN = 0.0, -5.6, 0.0   # ordonnée de G, abscisse de G sur la section, abscisse de σ = 0
    S_LO, S_HI = -30, 12          # étendue de l'axe σ (MPa)
    XP = 2.0                      # début du panneau de texte

    def navier(self, y_inf, y_sup):
        return Navier((self.XN, self.YG), self.KY, self.KS, y_inf, y_sup)

    def limites(self, nav, smin, smax, y_lo, y_hi, fs=24):
        """Zones interdites (hachurées en rouge) : σ < σ_min et σ > σ_max."""
        def zone(s0, s1):
            return Polygon(nav.p(s0, y_lo), nav.p(s1, y_lo), nav.p(s1, y_hi), nav.p(s0, y_hi),
                           stroke_width=0, fill_color=RED, fill_opacity=0.15)
        lmin = Line(nav.p(smin, y_lo), nav.p(smin, y_hi), color=RED, stroke_width=4)
        lmax = Line(nav.p(smax, y_lo), nav.p(smax, y_hi), color=RED, stroke_width=4)
        tmin = MathTex(r"\sigma_\text{min} = " + fmt(smin), font_size=fs, color=RED).next_to(lmin, DOWN, buff=0.08)
        tmax = MathTex(r"\sigma_\text{max} = " + fmt(smax), font_size=fs, color=RED).next_to(lmax, DOWN, buff=0.08)
        return VGroup(zone(self.S_LO, smin), zone(smax, self.S_HI), lmin, lmax, tmin, tmax)

    def panneau(self, y=2.6, gap=0.2):
        return Panneau(self.XP, y, gap=gap)

    def ecrire(self, Pn, *mobs, anim=Write):
        out = [Pn.placer(m) for m in mobs]
        for m in out:
            self.play(anim(m))
        return out


# ---------------------------------------------------------------------------
# Section rectangulaire en béton (§2.2)
# ---------------------------------------------------------------------------
B_R = 200.0                   # mm


class RectScene(AdmScene):
    def section_rect(self, h, rouge_haut=None):
        c = np.array([self.XS, self.YG, 0])
        r = Rectangle(width=B_R * self.KY, height=h * self.KY).set_stroke(WHITE, 3).set_fill(GREY_D, 1).move_to(c)
        cb = cote(r.get_corner(DL) + 0.3 * DOWN, r.get_corner(DR) + 0.3 * DOWN, "200", DOWN, fs=26)
        ch = cote(r.get_corner(DR) + 0.3 * RIGHT, r.get_corner(UR) + 0.3 * RIGHT, fr(h, 0), RIGHT, fs=26)
        return VGroup(r, cb, ch, point_G(c, cote_label=LEFT, buff=0.15, fs=26))

    def rappels(self, h):
        x0 = self.XS + B_R * self.KY / 2
        nav = self.navier(-h / 2, h / 2)
        return VGroup(rappel([x0, self.YG + h / 2 * self.KY, 0], nav.p(self.S_HI, h / 2)),
                      rappel([x0, self.YG - h / 2 * self.KY, 0], nav.p(self.S_HI, -h / 2)),
                      rappel([x0 + 0.9, self.YG, 0], nav.p(self.S_LO, 0)))


class ContraintesAdmissibles(RectScene):
    def construct(self):
        titre = self.titre(r"Contraintes admissibles")
        self.play(Write(titre))
        H = 400.0
        nav = self.navier(-H / 2, H / 2)
        sec = self.section_rect(H)
        unite = Tex(r"(mm)", font_size=24, color=GREY_B).next_to(sec[1], DOWN, buff=0.15)
        axes = nav.axes(self.S_LO, self.S_HI, marge=25)
        self.play(FadeIn(sec), FadeIn(unite), Create(axes), Create(self.rappels(H)))

        # --- définitions
        Pn = self.panneau()
        lim = self.limites(nav, -25, 2.5, -250, 250)
        d = [Pn.placer(m) for m in (
            T(r"$\sigma_\text{max} > 0$ : ultime en \textbf{traction}", font_size=28),
            T(r"$\sigma_\text{min} < 0$ : ultime en \textbf{compression}", font_size=28),
            T(r"au-delà : rupture, dommages...", font_size=28, color=GREY_B),
            MathTex(r"\text{admissible : }\ \sigma_\text{min} < \sigma < \sigma_\text{max}", font_size=32,
                    color=YELLOW),
        )]
        self.play(Write(d[0]), FadeIn(lim[1]), Create(lim[3]), Write(lim[5]))
        self.play(Write(d[1]), FadeIn(lim[0]), Create(lim[2]), Write(lim[4]))
        self.play(FadeIn(d[2]))
        self.play(Write(d[3]))
        self.etape()
        beton = [Pn.placer(m, gap=0.25) for m in (
            T(r"Béton : $\sigma_\text{max} = +2{,}5$ MPa,\\$\sigma_\text{min} = -25$ MPa", font_size=28),
            T(r"(10 fois plus résistant en compression !)", font_size=26, color=GREY_B),
        )]
        self.play(Write(beton[0]))
        self.play(FadeIn(beton[1]))
        self.etape()

        # --- la poutre étudiée
        self.play(*map(FadeOut, d + beton))
        Pn.reset()
        e = self.ecrire(Pn,
            T(r"Section la plus sollicitée ($x_c$) :", font_size=28, color=GREY_B),
            MathTex(r"M_\text{crit} = -40\ \mathrm{kN\cdot m},\quad N = 0", font_size=32, color=C_FORCE),
            MathTex(r"I_{GZ} = \frac{200\times 400^3}{12} = 1{,}067\cdot 10^9\ \mathrm{mm^4}", font_size=28),
            MathTex(r"y_\text{sup} = +200,\quad y_\text{inf} = -200\ \mathrm{mm}", font_size=30),
        )
        self.etape()
        f = lambda y: 40e6 / (B_R * H ** 3 / 12) * y
        diag = nav.diagramme(f)
        e2 = self.ecrire(Pn,
            MathTex(r"\sigma_\text{sup} = -\frac{M}{I_{GZ}}\,y_\text{sup}", font_size=30),
            MathTex(r"= \frac{40\cdot 10^6}{1{,}067\cdot 10^9}\times 200 = +7{,}5\ \mathrm{MPa}", font_size=30),
            MathTex(r"\sigma_\text{inf} = -7{,}5\ \mathrm{MPa}", font_size=30),
        )
        self.play(Create(diag[1]), LaggedStart(*map(Create, diag[0]), lag_ratio=0.05))
        self.etape()

        # --- verdict
        ok_inf = Pn.placer(MathTex(r"\sigma_\text{inf} = -7{,}5 > -25 \ \checkmark", font_size=32, color=C_POS),
                           gap=0.25)
        ko_sup = Pn.placer(MathTex(r"\sigma_\text{sup} = 7{,}5 > 2{,}5 \ \boldsymbol{\times}", font_size=32,
                                   color=C_KO))
        self.play(Write(ok_inf))
        self.play(Write(ko_sup))
        r = sec[0]
        bande = Rectangle(width=r.width, height=r.height * (1 - 2.5 / 7.5) / 2).set_stroke(width=0)
        bande.set_fill(C_KO, 0.8).align_to(r, UP).set_x(r.get_x())
        fiss = VMobject(stroke_color=WHITE, stroke_width=4).set_points_as_corners(
            [r.get_top() + d * RIGHT + v * DOWN for d, v in ((0, 0), (0.08, 0.12), (-0.05, 0.24), (0.06, 0.36))])
        self.play(FadeIn(bande), Flash(r.get_top(), color=C_KO))
        self.play(Create(fiss))
        concl = T(r"Le haut est trop tendu : une \textbf{fissure} s'ouvrirait en haut de la poutre\\"
                  r"et se propagerait vers $G$.", font_size=28, color=C_KO).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(concl))
        self.etape(2)


# ---------------------------------------------------------------------------
# Les remèdes (en direct)
# ---------------------------------------------------------------------------
class SolutionsRupture(RectScene):
    def construct(self):
        titre = self.titre(r"Éviter la rupture : 5 solutions")
        self.play(Write(titre))
        q, L, H, SMAX, N = (ValueTracker(v) for v in (20.0, 4.0, 400.0, 2.5, 0.0))
        SMIN = -25.0

        def M():
            return -q.get_value() * L.get_value() ** 2 / 8

        def f():
            h = H.get_value()
            return lambda y: N.get_value() * 1e3 / (B_R * h) - M() * 1e6 / (B_R * h ** 3 / 12) * y

        def s_sup():
            return f()(H.get_value() / 2)

        def s_inf():
            return f()(-H.get_value() / 2)

        sec = always_redraw(lambda: self.section_rect(H.get_value()))
        diag = always_redraw(lambda: self.navier(-H.get_value() / 2, H.get_value() / 2).diagramme(f()))
        rap = always_redraw(lambda: self.rappels(H.get_value()))
        lim = always_redraw(lambda: self.limites(self.navier(-350, 350), SMIN, SMAX.get_value(), -370, 370))
        axes = self.navier(-350, 350).axes(self.S_LO, self.S_HI, marge=10)

        def bande():
            r = Rectangle(width=B_R * self.KY, height=H.get_value() * self.KY).move_to([self.XS, self.YG, 0])
            ss = s_sup()
            if ss <= SMAX.get_value():
                return VMobject()
            frac = (ss - SMAX.get_value()) / (2 * (ss - f()(0)))
            b = Rectangle(width=r.width, height=r.height * frac).set_stroke(width=0).set_fill(C_KO, 0.8)
            return b.align_to(r, UP).set_x(r.get_x())
        rupt = always_redraw(bande)
        self.play(FadeIn(sec), Create(axes), FadeIn(lim), FadeIn(rap), FadeIn(diag))
        self.add(rupt)

        Pn = self.panneau(gap=0.12)
        vals = [
            ligne_valeur("q =", q.get_value, r"\mathrm{kN/m}", fs=28),
            ligne_valeur(r"\ell =", L.get_value, r"\mathrm{m}", fs=28, decimales=2),
            ligne_valeur("h =", H.get_value, r"\mathrm{mm}", fs=28, decimales=0),
            ligne_live("N =", N.get_value, r"\mathrm{kN}", fs=28, decimales=0),
            ligne_live(r"M = -\frac{q\ell^2}{8} =", M, r"\mathrm{kN\cdot m}", fs=28),
            ligne_valeur(r"\sigma_\text{max} =", SMAX.get_value, r"\mathrm{MPa}", fs=28, couleur=RED),
            verif(r"\sigma_\text{sup} =", s_sup, lambda: s_sup() <= SMAX.get_value() + 1e-6, fs=30),
            verif(r"\sigma_\text{inf} =", s_inf, lambda: s_inf() >= SMIN, fs=30),
        ]
        for v in vals:
            Pn.placer(v)
        self.play(*map(FadeIn, vals))
        y_msg = Pn.y - 0.15
        self.etape()

        msg = None

        def message(tex):
            nonlocal msg
            m = T(tex, font_size=26, color=YELLOW)
            m.move_to([self.XP + m.width / 2, y_msg - m.height / 2, 0])
            anims = [FadeIn(m)] + ([FadeOut(msg)] if msg is not None else [])
            msg = m
            self.play(*anims)

        # 1. limiter le chargement
        message(r"\textbf{1.} Réduire la charge $q$ ou la portée $\ell$ :\\"
                r"$\sigma_\text{sup} = \dfrac{q\,\ell^2\,h}{16\,I_{GZ}}$ diminue\\($q \leq 6{,}7$ kN/m ou $\ell \leq 2{,}3$ m).")
        self.play(q.animate.set_value(6.5), run_time=3)
        self.etape()
        self.play(q.animate.set_value(20), run_time=1.2)
        self.play(L.animate.set_value(2.3), run_time=3)
        self.etape()
        self.play(L.animate.set_value(4), run_time=1.2)

        # 2. matériau plus résistant
        message(r"\textbf{2.} Matériau plus résistant en traction :\\$\sigma_\text{max} \geq 7{,}5$ MPa.")
        self.play(SMAX.animate.set_value(8), run_time=3)
        self.etape()
        self.play(SMAX.animate.set_value(2.5), run_time=1.2)

        # 3. augmenter la hauteur
        message(r"\textbf{3.} Augmenter la hauteur $h$ :\\"
                r"$\sigma_\text{sup} = \dfrac{3\,q\,\ell^2}{4\,b\,h^2}$ (car $I_{GZ} \propto h^3$) ;\\$h = 700$ mm suffit.")
        self.play(H.animate.set_value(700), run_time=3)
        self.etape()
        self.play(H.animate.set_value(400), run_time=1.2)

        # 4. précontrainte
        message(r"\textbf{4.} Précontraindre : $N < 0$ décale tout\\de $N/S$ vers la compression\\"
                r"(câble tendu, relâché après la prise).")
        self.play(N.animate.set_value(-400), run_time=3)
        self.etape()
        self.play(N.animate.set_value(0), run_time=1.2)

        # 5. armatures
        message(r"\textbf{5.} Des \textbf{armatures} en acier dans\\la zone tendue (béton armé,\\"
                r"vu dans d'autres modules).")
        r = Rectangle(width=B_R * self.KY, height=400 * self.KY).move_to([self.XS, self.YG, 0])
        arm = VGroup(*[Circle(radius=0.06).set_stroke(WHITE, 2).set_fill(GREY_A, 1)
                       .move_to(r.get_top() + 0.18 * DOWN + dx * RIGHT) for dx in (-0.4, 0, 0.4)])
        self.play(LaggedStart(*[GrowFromCenter(a) for a in arm], lag_ratio=0.3))
        self.etape()
        concl = T(r"Ici on ne dimensionne pas : on apprend à \textbf{lire} le diagramme de Navier\\"
                  r"(ce dimensionnement s'appellera l'ELU dans les Eurocodes).",
                  font_size=26, color=GREY_B).to_edge(DOWN, buff=0.15)
        self.play(FadeIn(concl))
        self.etape(2)
        for m in (sec, diag, rap, lim, rupt, *[v[1] for v in vals], vals[6], vals[7]):
            m.clear_updaters()


# ---------------------------------------------------------------------------
# Section non symétrique (§2.3) : la section en T, puis retournée
# ---------------------------------------------------------------------------
class SectionNonSymetrique(AdmScene):
    KY, KS = 0.03, 0.035
    YG, XS, XN = -0.3, -5.2, -0.2
    S_LO, S_HI = -75, 40
    XP = 1.9

    def section_T(self, sens=1):
        """sens = 1 : table en haut ; sens = -1 : section retournée (table en bas)."""
        S = Plan((self.XS, self.YG), s=self.KY)
        rects = VGroup(*[S.rect(u0, min(sens * y0, sens * y1), u1, max(sens * y0, sens * y1), C_SECTION)
                         for u0, y0, u1, y1 in RECTS_T])
        h_t = 25 * sens                       # jonction âme / table
        cotes = VGroup(
            S.cote_h(-60, 60, 54 if sens > 0 else -54, "120", UP if sens > 0 else DOWN, fs=24),
            S.cote_v(70, min(h_t, 45 * sens), max(h_t, 45 * sens), "20", RIGHT, fs=24),
            S.cote_v(-25, min(-95 * sens, h_t), max(-95 * sens, h_t), "120", LEFT, fs=24),
            S.cote_h(-10, 10, -104 * sens, "20", DOWN if sens > 0 else UP, fs=24),
        )
        return VGroup(rects, cotes, point_G(S.p(0, 0), cote_label=LEFT, buff=0.15, fs=26))

    def construct(self):
        titre = self.titre(r"Section non symétrique")
        self.play(Write(titre))
        sec = self.section_T(1)
        nav = self.navier(-95, 45)
        axes = nav.axes(self.S_LO, self.S_HI, marge=15)
        lim = self.limites(self.navier(-100, 100), -60, 30, -100, 100)
        self.play(FadeIn(sec), Create(axes))

        def rappels(y_inf, y_sup):
            S = Plan((self.XS, self.YG), s=self.KY)
            return VGroup(rappel(S.p(60, y_sup), nav.p(self.S_HI, y_sup)),
                          rappel(S.p(60, y_inf), nav.p(self.S_HI, y_inf)))
        rap = rappels(-95, 45)
        ys = VGroup(MathTex(r"y_\text{sup} = +45", font_size=26).next_to(rap[0], UP, buff=0.05).set_x(-0.9),
                    MathTex(r"y_\text{inf} = -95", font_size=26).next_to(rap[1], DOWN, buff=0.05).set_x(-0.9))
        self.play(Create(rap), FadeIn(ys))
        Pn = self.panneau()
        e = self.ecrire(Pn,
            T(r"Section en T de §1 (mm) : $G$ n'est pas\\à mi-hauteur, donc $y_\text{sup} \neq -y_\text{inf}$.",
              font_size=28),
            MathTex(r"I_{GZ} = 884\cdot 10^4\ \mathrm{mm^4}", font_size=28),
            MathTex(r"M = -4\ \mathrm{kN\cdot m},\quad N = 0", font_size=28, color=C_FORCE),
            T(r"Matériau : $\sigma_\text{max} = +30$, $\sigma_\text{min} = -60$ MPa", font_size=26, color=RED),
        )
        self.play(FadeIn(lim))
        self.etape()

        f = lambda y: 4e6 / I_T * y
        diag = nav.diagramme(f)
        e2 = self.ecrire(Pn,
            MathTex(r"-\frac{M}{I_{GZ}} = \frac{4\cdot 10^6}{884\cdot 10^4} = 0{,}452\ \mathrm{MPa/mm}", font_size=28),
            MathTex(r"\sigma_\text{sup} = 0{,}452\times 45 = +20{,}4\ \mathrm{MPa}", font_size=28),
            MathTex(r"\sigma_\text{inf} = 0{,}452\times (-95) = -43{,}0\ \mathrm{MPa}", font_size=28),
        )
        self.play(Create(diag[1]), LaggedStart(*map(Create, diag[0]), lag_ratio=0.05))
        v = self.ecrire(Pn,
            MathTex(r"-60 < -43{,}0 \quad\text{et}\quad 20{,}4 < 30 \ \checkmark", font_size=32, color=C_POS))
        rq = self.ecrire(Pn, T(r"Haut et bas différents : la fibre la plus\\\textbf{éloignée} de $G$ est la plus sollicitée.",
                               font_size=26, color=YELLOW))
        self.etape()

        # --- la même section, retournée
        self.play(*map(FadeOut, e + e2 + v + rq))
        Pn.reset()
        q = self.ecrire(Pn, T(r"Et si on \textbf{retourne} la section ?", font_size=30, color=YELLOW))
        sec2 = self.section_T(-1)
        nav2 = self.navier(-45, 95)
        f2 = f
        diag2 = nav2.diagramme(f2)
        rap2 = VGroup(rappel(Plan((self.XS, self.YG), s=self.KY).p(60, 95), nav.p(self.S_HI, 95)),
                      rappel(Plan((self.XS, self.YG), s=self.KY).p(60, -45), nav.p(self.S_HI, -45)))
        ys2 = VGroup(MathTex(r"y_\text{sup} = +95", font_size=26).next_to(rap2[0], UP, buff=0.05).set_x(-0.9),
                     MathTex(r"y_\text{inf} = -45", font_size=26).next_to(rap2[1], DOWN, buff=0.05).set_x(-0.9))
        self.play(FadeOut(sec[1]), FadeOut(ys))
        self.play(Rotate(sec[0], PI, about_point=sec[2][0].get_center()), run_time=1.5)
        self.play(FadeIn(sec2[1]), ReplacementTransform(rap, rap2), FadeIn(ys2), ReplacementTransform(diag, diag2))
        e3 = self.ecrire(Pn,
            T(r"Même $M = -4$ kN$\cdot$m, même $I_{GZ}$, mais :", font_size=28),
            MathTex(r"\sigma_\text{sup} = 0{,}452\times 95 = +43{,}0\ \mathrm{MPa}", font_size=28),
            MathTex(r"\sigma_\text{inf} = 0{,}452\times (-45) = -20{,}4\ \mathrm{MPa}", font_size=28),
            MathTex(r"43{,}0 > 30 \ \boldsymbol{\times}\quad\text{rupture en haut !}", font_size=32, color=C_KO),
        )
        self.etape()
        self.ecrire(Pn, T(r"L'\textbf{orientation} compte : la fibre la plus\\éloignée de $G$ doit être du côté\\"
                          r"qui résiste le mieux (ici la compression).", font_size=26, color=YELLOW))
        self.etape(2)


# ---------------------------------------------------------------------------
# Profilé UPE 120 (§2.4) : module de flexion élastique
# ---------------------------------------------------------------------------
class NavierUPE(AdmScene):
    KY, KS = 0.02, 0.0075
    YG, XS, XN = 0.2, -5.6, -0.8
    S_LO, S_HI = -265, 265
    XP = 1.75

    def construct(self):
        titre = self.titre(r"Profilé UPE 120 : module de flexion élastique")
        self.play(Write(titre))
        G = np.array([self.XS, self.YG, 0])
        prof = profil_upe("UPE 120", self.KY).shift(G)
        gG = point_G(G, cote_label=DR, buff=0.1, fs=26)
        aZ = axe_Z(G, demi=1.4, couleur=YELLOW)
        lZ = MathTex("Z", font_size=28, color=YELLOW).next_to(aZ.get_right(), UR, buff=0.05)
        nom = Tex(r"\textsf{UPE\,120} placé en C", font_size=30).move_to([self.XS, 2.55, 0])
        c_h = cote(G + (19.8 * self.KY + 0.35) * LEFT + 60 * self.KY * DOWN,
                   G + (19.8 * self.KY + 0.35) * LEFT + 60 * self.KY * UP, "120", LEFT, fs=26)
        c_h[1].shift(0.45 * DOWN)
        unite = Tex(r"(mm)", font_size=24, color=GREY_B).move_to([self.XS, -1.9, 0])
        self.play(DrawBorderThenFill(prof), FadeIn(gG), Create(aZ), Write(lZ), Write(nom), FadeIn(c_h),
                  FadeIn(unite))

        nav = self.navier(-60, 60)
        axes = nav.axes(self.S_LO, self.S_HI, marge=10)
        lim = self.limites(self.navier(-75, 75), -235, 235, -75, 75)
        self.play(Create(axes), FadeIn(lim))
        Pn = self.panneau(gap=0.16)
        e = self.ecrire(Pn,
            T(r"Acier S235 : $\sigma_\text{min} = -235$ et $\sigma_\text{max} = +235$ MPa", font_size=24, color=RED),
            MathTex(r"M = -3\ \mathrm{kN\cdot m},\quad N = 0", font_size=28, color=C_FORCE),
            T(r"Catalogue : $\mathsf{I_y} = 364\cdot 10^4$ mm$^4$, $h = 120$ mm", font_size=26),
        )
        f1 = lambda y: 3e6 / 364e4 * y
        d1 = nav.diagramme(f1)
        e1 = self.ecrire(Pn,
            MathTex(r"\sigma_\text{sup} = -\frac{M}{I_{GZ}}\,y_\text{sup} = \frac{3\cdot 10^6}{364\cdot 10^4}\times 60",
                    font_size=28),
            MathTex(r"\sigma_\text{sup} = +49{,}5\ \mathrm{MPa},\quad \sigma_\text{inf} = -49{,}5\ \mathrm{MPa}",
                    font_size=28),
        )
        self.play(Create(d1[1]), LaggedStart(*map(Create, d1[0]), lag_ratio=0.05))
        self.etape()

        # --- le module de flexion élastique
        self.play(*map(FadeOut, e1))
        Pn.y += sum(m.height + 0.16 for m in e1)
        w = self.ecrire(Pn,
            T(r"Plus rapide : le \textbf{module de flexion}\\\textbf{élastique} (donné par le catalogue)", font_size=26,
              color=YELLOW),
            MathTex(r"w_{\text{el},Z} = \frac{I_{GZ}}{\max(-y_\text{inf},\ y_\text{sup})}\quad (\mathrm{mm^3})",
                    font_size=30),
            MathTex(r"= \frac{364\cdot 10^4}{60} = 60{,}6\cdot 10^3\ \mathrm{mm^3} = \mathsf{W_{el,y}}",
                    font_size=28),
            MathTex(r"|\sigma| = \frac{|M|}{w_{\text{el},Z}} = \frac{3\cdot 10^6}{60{,}6\cdot 10^3} = 49{,}5\ \mathrm{MPa}",
                    font_size=28),
            T(r"Le signe se lit sur le dessin :\\$M < 0$ $\Rightarrow$ haut tendu ($+$), bas comprimé ($-$).",
              font_size=24, color=GREY_B),
        )
        v1 = VGroup(MathTex(r"+49{,}5", font_size=24, color=C_TRAC).next_to(nav.p(49.5, 60), RIGHT, buff=0.08),
                    MathTex(r"-49{,}5", font_size=24, color=C_COMP).next_to(nav.p(-49.5, -60), LEFT, buff=0.08))
        self.play(FadeIn(v1))
        self.etape()

        # --- placé en ∩
        self.play(*map(FadeOut, w + [v1, c_h]), FadeOut(d1))
        Pn.y += sum(m.height + 0.16 for m in w)
        Pn.y += e[2].height + 0.16
        self.play(FadeOut(e[2]))
        nom2 = Tex(r"\textsf{UPE\,120} placé en $\cap$", font_size=30).move_to(nom)
        self.play(Rotate(prof, -PI / 2, about_point=G), ReplacementTransform(nom, nom2), run_time=1.5)
        haut, bas = prof.get_top()[1], prof.get_bottom()[1]
        xr = prof.get_right()[0] + 0.3
        c2 = VGroup(cote([xr, bas, 0], [xr, haut, 0], "60", RIGHT, fs=26),
                    cote([xr + 0.75, G[1], 0], [xr + 0.75, haut, 0], r"19{,}8", RIGHT, fs=24, couleur=ORANGE))
        c2[0][1].shift(0.3 * DOWN)
        self.play(FadeIn(c2))
        nav2 = self.navier(-40.2, 19.8)
        e2 = self.ecrire(Pn,
            T(r"Catalogue : $\mathsf{I_z} = 55{,}5\cdot 10^4$ mm$^4$,\\$\mathsf{W_{el,z}} = 13{,}8\cdot 10^3$ mm$^3$",
              font_size=26),
            MathTex(r"y_\text{sup} = \mathsf{y_s} = 19{,}8;\ \ y_\text{inf} = 19{,}8 - 60 = -40{,}2", font_size=26),
            T(r"$\mathsf{W_{el,z}} = 55{,}5\cdot 10^4 / 40{,}2$ : valable pour\\le bord \textbf{le plus éloigné} de $G$ (le bas)",
              font_size=24, color=GREY_B),
            MathTex(r"\sigma_\text{inf} = -\frac{3\cdot 10^6}{13{,}8\cdot 10^3} = -217{,}4\ \mathrm{MPa}", font_size=28),
            MathTex(r"\sigma_\text{sup} = \frac{3\cdot 10^6}{55{,}5\cdot 10^4}\times 19{,}8 = +107{,}0\ \mathrm{MPa}",
                    font_size=26),
        )
        f2 = lambda y: 3e6 / 55.5e4 * y
        d2 = nav2.diagramme(f2)
        self.play(Create(d2[1]), LaggedStart(*map(Create, d2[0]), lag_ratio=0.05))
        v2 = VGroup(MathTex(r"+107{,}0", font_size=24, color=C_TRAC).next_to(nav2.p(107, 19.8), RIGHT, buff=0.08),
                    MathTex(r"-217{,}4", font_size=24, color=C_COMP).next_to(nav2.p(-217.4, -40.2), DOWN, buff=0.08))
        self.play(FadeIn(v2))
        self.etape()
        concl = T(r"Admissible ($217{,}4 < 235$), mais $4{,}4$ fois plus sollicité qu'en C !",
                  font_size=28, color=YELLOW).to_edge(DOWN, buff=0.2)
        self.play(FadeIn(concl))
        self.etape(2)


# ---------------------------------------------------------------------------
# Choisir un profilé (§2.5)
# ---------------------------------------------------------------------------
class ChoixProfile(Base):
    def construct(self):
        titre = self.titre(r"Choisir un profilé (contraintes normales)")
        self.play(Write(titre))
        donnees = VGroup(
            T(r"Poutre en acier, $\sigma_\text{max} = +160$ MPa, $\sigma_\text{min} = -160$ MPa, $N \approx 0$",
              font_size=28, color=RED),
            T(r"UPE placé en C, moment maximal $M_\text{crit} = -6$ kN$\cdot$m", font_size=28, color=C_FORCE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(LEFT, buff=0.4).set_y(2.35)
        self.play(FadeIn(donnees))

        etapes = [
            (r"\textbf{1.} Position $x_c$ et valeur de $M_\text{crit}$ (avec son signe)",
             r"M_\text{crit} = -6\ \mathrm{kN\cdot m} = -6\cdot 10^6\ \mathrm{N\cdot mm}"),
            (r"\textbf{2.} Quelle fibre est déterminante ?",
             r"\text{en C : symétrique et } |\sigma_\text{min}| = \sigma_\text{max} \Rightarrow \text{haut ou bas}"),
            (r"\textbf{3.} On écrit l'égalité avec la contrainte ultime",
             r"\frac{|M_\text{crit}|}{w_{\text{el},Z}} = \sigma_\text{max}"),
            (r"\textbf{4.} On en déduit le module \textbf{minimal}",
             r"(w_{\text{el},Z})_\text{min} = \frac{6\cdot 10^6}{160} = 37\,500\ \mathrm{mm^3} = 37{,}5\ \mathrm{cm^3}"),
        ]
        y = 1.45
        lignes = []
        for t, m in etapes:
            lt = T(t, font_size=28).move_to([-6.7, y, 0], aligned_edge=LEFT)
            lm = MathTex(m, font_size=30, color=YELLOW).next_to(lt, DOWN, buff=0.12, aligned_edge=LEFT).shift(0.4 * RIGHT)
            self.play(Write(lt))
            self.play(Write(lm))
            lignes += [lt, lm]
            y = lm.get_bottom()[1] - 0.35
            self.etape(0.5)
        self.etape()

        # --- étape 5 : le catalogue
        res = MathTex(r"(w_{\text{el},Z})_\text{min} = 37{,}5\ \mathrm{cm^3}", font_size=34, color=YELLOW)
        res.move_to([3.5, 2.35, 0])
        cadre = SurroundingRectangle(res, color=YELLOW, buff=0.12)
        self.play(*map(FadeOut, lignes[:-1]), ReplacementTransform(lignes[-1], res), Create(cadre))
        t5 = T(r"\textbf{5.} Dans le catalogue, colonne $\mathsf{W_{el,y}}$ (placé en C) :\\"
               r"la plus petite valeur \textbf{supérieure} à $37{,}5$ cm$^3$.", font_size=28).move_to([-6.7, 1.1, 0],
                                                                                           aligned_edge=LEFT)
        self.play(Write(t5))
        tab = tableau_upe(largeur=11.0).move_to([0.3, -1.85, 0])
        self.play(FadeIn(tab))
        COL_WY, COL_WZ = 6, 8
        col = SurroundingRectangle(tab.get_columns()[COL_WY - 1], color=YELLOW, buff=0.03)
        self.play(Create(col))
        marques = []
        for ligne, ok in ((2, False), (3, True)):
            cel = tab.get_cell((ligne, COL_WY), color=C_POS if ok else C_KO).set_stroke(width=5)
            sym = MathTex(r"\checkmark" if ok else r"\boldsymbol{\times}", font_size=34,
                          color=C_POS if ok else C_KO).next_to(tab, RIGHT, buff=0.15).set_y(cel.get_y())
            self.play(Create(cel), FadeIn(sym))
            marques += [cel, sym]
        choix = T(r"$\Rightarrow$ \textsf{UPE\,100} : $\mathsf{W_{el,y}} = 41{,}4$ cm$^3$", font_size=30,
                  color=C_POS).move_to([-6.7, 0.25, 0], aligned_edge=LEFT)
        verif_ = MathTex(r"\text{vérification : }\ \sigma = \frac{6\cdot 10^6}{41{,}4\cdot 10^3} = 144{,}9"
                         r"\ \mathrm{MPa} < 160 \ \checkmark", font_size=26, color=C_POS)
        verif_.next_to(choix, RIGHT, buff=0.4)
        self.play(Write(choix))
        self.play(Write(verif_))
        self.etape()

        # --- et placé en U ?
        self.play(*map(FadeOut, marques), FadeOut(col), FadeOut(choix), FadeOut(verif_), FadeOut(t5))
        tU = T(r"Et placé en U ? Colonne $\mathsf{W_{el,z}}$ :", font_size=28).move_to([-6.7, 1.1, 0],
                                                                                 aligned_edge=LEFT)
        colZ = SurroundingRectangle(tab.get_columns()[COL_WZ - 1], color=YELLOW, buff=0.03)
        self.play(Write(tU), Create(colZ))
        cels = VGroup(*[tab.get_cell((l, COL_WZ), color=C_KO).set_stroke(width=5) for l in (2, 3, 4, 5)])
        self.play(LaggedStart(*map(Create, cels), lag_ratio=0.3))
        conclU = T(r"toutes les valeurs sont $< 37{,}5$ cm$^3$ : \textbf{aucun} UPE de l'extrait ne convient !\\"
                   r"Bien choisir l'orientation (et la bonne colonne) avant de lire le catalogue.",
                   font_size=28, color=C_KO).move_to([-6.7, 0.35, 0], aligned_edge=LEFT)
        self.play(Write(conclU))
        self.etape(2)
