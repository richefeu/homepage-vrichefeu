"""
MS2 - Animations pédagogiques : caractéristiques géométriques des sections (§1 du poly)

Scènes (dans l'ordre du cours) :
    Barycentre           formes simples, sections composées (somme / différence), formule de Y_G
    BarycentreT          exemple chiffré : section en T (Y_G = 9,5 cm)
    BarycentreEvidement  enlever de la matière : termes négatifs (Y_G = 5,5 cm)
    MomentQuadratique    règle à plat / sur chant, I = intégrale de y² dS, b h³ / 12 (effet de h³), disque
    Huygens              transport I_GiZ + d² S : section en T (884 cm⁴), section évidée (1288 cm⁴)
    ProfilesUPE          lire le catalogue : UPE 120 en C, en U, en ∩ (bonnes colonnes, unités)

Vidéo  : manim -qh sections.py Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE
Slides : manim-slides render sections.py Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE
         manim-slides present Barycentre BarycentreT BarycentreEvidement MomentQuadratique Huygens ProfilesUPE
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms2 import *  # noqa: E402,F403

# Section en T de l'exemple (cm) : âme 2 x 12, table 12 x 2  ->  Y_G = 9,5 cm, I_GZ = 884 cm⁴
AME = (-1, 0, 1, 12)
TABLE = (-6, 12, 6, 14)
YG_T = 9.5

# Section évidée (cm) : rectangle 10 x 12 moins un trou 6 x 4 (de y = 6 à y = 10)  ->  Y_G = 5,5 cm
PLEIN = (-5, 0, 5, 12)
TROU = (-3, 6, 3, 10)
YG_E = 5.5


def section_T(P):
    return P.rect(*AME, C_ELEM[0]), P.rect(*TABLE, C_ELEM[1])


def section_evidee(P):
    plein = P.rect(*PLEIN, C_ELEM[0])
    trou = P.rect(*TROU, BLACK, opacite=1).set_stroke(C_TROU, 4)
    return plein, trou


def cotes_T(P):
    """Cotes de la section en T, à gauche et en haut (la droite reste libre pour les Y_Gi)."""
    return VGroup(
        P.cote_h(-6, 6, 14.9, "12", UP),
        P.cote_v(-6.8, 12, 14, "2", LEFT),
        P.cote_v(-2.4, 0, 12, "12", LEFT),
        P.cote_h(-1, 1, -1.0, "2", DOWN),
    )


def cotes_evidee(P):
    """Cotes de la section évidée (le trou en rouge)."""
    return VGroup(
        P.cote_h(-5, 5, -1.0, "10", DOWN),
        P.cote_v(-5.8, 0, 12, "12", LEFT),
        P.cote_h(-3, 3, 9.1, "6", UP, couleur=C_TROU, fs=28),
        P.cote_v(-2.3, 6, 10, "4", RIGHT, couleur=C_TROU, fs=28),
        P.cote_v(6.0, 10, 12, "2", RIGHT),
    )


def unite_cm():
    return Tex(r"(cotes en cm)", font_size=26, color=GREY_B).move_to([-6.0, -3.7, 0])


# ---------------------------------------------------------------------------
# 1. Barycentre : formes simples, sections composées, formule
# ---------------------------------------------------------------------------
class Barycentre(Base):
    def construct(self):
        titre = self.titre(r"Barycentre (centre de surface) d'une section")
        self.play(Write(titre))

        # --- formes simples
        rect = Rectangle(width=3.2, height=2.0).set_stroke(WHITE, 3).set_fill(C_SECTION, 0.6).move_to([-3.4, 0.5, 0])
        diags = VGroup(Line(rect.get_corner(DL), rect.get_corner(UR)),
                       Line(rect.get_corner(UL), rect.get_corner(DR))).set_stroke(GREY_A, 2)
        disque = Circle(radius=1.2).set_stroke(WHITE, 3).set_fill(C_SECTION, 0.6).move_to([3.4, 0.5, 0])
        G_r = point_G(rect.get_center(), cote_label=UP)
        G_d = point_G(disque.get_center(), cote_label=UR)
        t_r = Tex(r"Rectangle : à l'intersection\\des diagonales", font_size=FS_TEXTE).next_to(rect, DOWN, buff=0.6)
        t_d = Tex(r"Disque : en son centre", font_size=FS_TEXTE).next_to(disque, DOWN, buff=0.6).align_to(t_r, UP)
        self.play(DrawBorderThenFill(rect), DrawBorderThenFill(disque))
        self.play(Create(diags))
        self.play(FadeIn(G_r, scale=2), Write(t_r))
        self.play(FadeIn(G_d, scale=2), Write(t_d))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- sections composées : somme ou différence de formes simples
        PI_ = Plan((-3.6, -2.2), s=0.3)
        el = [PI_.rect(-5, 0, 5, 2, C_ELEM[0]), PI_.rect(-1, 2, 1, 12, C_ELEM[1]), PI_.rect(-5, 12, 5, 14, C_ELEM[2])]
        nums = VGroup(*[MathTex(str(i + 1), color=C_ELEM[i], font_size=FS_EQ).next_to(e, LEFT, buff=0.25)
                        for i, e in enumerate(el)])
        nums[1].shift(0.6 * UP)
        eq_I = Tex(r"profilé en I $=$ ", "$1$", " $+$ ", "$2$", " $+$ ", "$3$", font_size=FS_EQ)
        for i in range(3):
            eq_I[1 + 2 * i].set_color(C_ELEM[i])
        eq_I.next_to(VGroup(*el), DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(e, shift=s) for e, s in zip(el, (UP, RIGHT, DOWN))], lag_ratio=0.5),
                  run_time=2)
        self.play(Write(nums), Write(eq_I))

        PT = Plan((3.6, -2.2), s=0.3)
        ext, trou = PT.rect(-7, 0, 7, 14, C_ELEM[0]), PT.rect(-5, 2, 5, 12, C_TROU, opacite=0).set_stroke(C_TROU, 4)
        n1 = MathTex("1", color=C_ELEM[0], font_size=FS_EQ).next_to(ext, LEFT, buff=0.25).shift(0.6 * UP)
        n2 = MathTex("2", color=C_TROU, font_size=FS_EQ).move_to(PT.p(-3, 10))
        eq_T = Tex(r"tube carré $=$ ", "$1$", " $-$ ", "$2$", font_size=FS_EQ).next_to(ext, DOWN, buff=0.4)
        eq_T[1].set_color(C_ELEM[0])
        eq_T[3].set_color(C_TROU)
        self.play(FadeIn(ext), Write(n1))
        self.play(Create(trou), Write(n2))
        self.play(trou.animate.set_fill(BLACK, opacity=1), Write(eq_T))
        self.etape()

        # --- symétries
        sym = VGroup(
            DashedLine(PI_.p(0, -0.8), PI_.p(0, 14.8)), DashedLine(PI_.p(-6, 7), PI_.p(6, 7)),
            DashedLine(PT.p(0, -0.8), PT.p(0, 14.8)), DashedLine(PT.p(-8, 7), PT.p(8, 7)),
        ).set_stroke(GREY_B, 2)
        GI = point_G(PI_.p(0, 7), cote_label=UR, buff=0.1)
        GT = point_G(PT.p(0, 7), cote_label=UR, buff=0.1)
        self.play(Create(sym))
        self.play(FadeIn(GI, scale=2), FadeIn(GT, scale=2))
        t = Tex(r"Section symétrique : $G$ est sur les axes de symétrie.", font_size=FS_TEXTE, color=C_G)
        t.to_edge(DOWN, buff=0.2)
        self.play(Write(t))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- cas général : la formule (figure du poly)
        P = Plan((-3.0, -2.3), s=1.3)
        rects = [(0, 0, 2, 1), (0.75, 1, 1.25, 2.5), (1.25, 2, 2, 2.5)]
        el = [P.rect(*r, C_ELEM[i]) for i, r in enumerate(rects)]
        S = [(r[2] - r[0]) * (r[3] - r[1]) for r in rects]
        Gi = [((r[0] + r[2]) / 2, (r[1] + r[3]) / 2) for r in rects]
        uG = sum(s * g[0] for s, g in zip(S, Gi)) / sum(S)
        yG = sum(s * g[1] for s, g in zip(S, Gi)) / sum(S)
        self.play(*[DrawBorderThenFill(e) for e in el])
        sol = Line(P.p(-2.6, 0), P.p(3.0, 0), color=GREY_B, stroke_width=2)
        lab_sol = Tex(r"$Y = 0$ : point le plus bas", font_size=26, color=GREY_B).next_to(sol, DOWN, buff=0.12)
        self.play(Create(sol), FadeIn(lab_sol))

        frac = fraction([r"S_1\,Y_{G_1}", "+", r"S_2\,Y_{G_2}", "+", r"S_3\,Y_{G_3}", r"+\dots"],
                        ["S_1", "+", "S_2", "+", "S_3", r"+\dots"], fs=34)
        eq = VGroup(MathTex("Y_G", "=", font_size=34), frac).arrange(RIGHT, buff=0.2)
        eq.move_to([0, 0.9, 0]).to_edge(RIGHT, buff=0.3)
        num, den = frac[0], frac[2]
        self.play(Write(eq[0]), Create(frac[1]))
        u_cotes = (-0.3, -1.15, -2.0)
        cotes = []
        for i in range(3):
            g = point_G(P.p(*Gi[i]), nom=f"G_{i + 1}", cote_label=(DOWN, LEFT, DOWN)[i], couleur=WHITE, fs=26)
            c = P.cote_v(u_cotes[i], 0, Gi[i][1], f"Y_{{G_{i + 1}}}", LEFT, couleur=C_ELEM[i], fs=28)
            r = P.rappel(u_cotes[i], Gi[i][1], Gi[i][0], Gi[i][1])
            cotes += [c, r]
            self.play(Indicate(el[i], color=C_ELEM[i]), FadeIn(g, scale=2))
            self.play(Create(r), FadeIn(c))
            parts = [num[2 * i], den[2 * i]] + ([num[2 * i - 1], den[2 * i - 1]] if i else [])
            num[2 * i].set_color(C_ELEM[i])
            den[2 * i].set_color(C_ELEM[i])
            self.play(*map(Write, parts))
        self.play(Write(num[5]), Write(den[5]))
        self.etape()

        # --- G de la section complète
        gG = point_G(P.p(uG, yG), cote_label=UR, buff=0.1)
        cG = P.cote_v(2.6, 0, yG, "Y_G", RIGHT, couleur=C_G, fs=30)
        rG = P.rappel(uG, yG, 2.6, yG)
        self.play(FadeIn(gG, scale=2))
        self.play(Create(rG), FadeIn(cG))
        somme = MathTex(r"Y_G = \frac{\sum_i S_i \times Y_{G_i}}{\sum_i S_i}", font_size=44).move_to([eq.get_x(), -1.4, 0])
        cadre = SurroundingRectangle(somme, color=BLUE_B, buff=0.2)
        self.play(Write(somme), Create(cadre))
        self.etape()

        rq = VGroup(
            Tex(r"$S_i$ : surface de l'élément $i$ ; $Y_{G_i}$ : hauteur de son centre,", font_size=28),
            Tex(r"mesurée depuis le point le plus \textbf{bas} de la section \textbf{complète}.", font_size=28),
            Tex(r"Enlever de la matière : $S_i < 0$ (en haut \textbf{et} en bas de la fraction).",
                font_size=28, color=C_TROU),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_edge(DOWN, buff=0.15).to_edge(RIGHT, buff=0.3)
        self.play(FadeOut(lab_sol), FadeIn(rq[0]), FadeIn(rq[1]))
        self.play(FadeIn(rq[2]))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Exemple chiffré : section en T
# ---------------------------------------------------------------------------
class BarycentreT(Base):
    def construct(self):
        titre = self.titre(r"Exemple : barycentre d'une section en T")
        self.play(Write(titre))

        P = Plan((-3.9, -2.7), s=0.33)
        ame, table = section_T(P)
        self.play(DrawBorderThenFill(ame), DrawBorderThenFill(table))
        dims = cotes_T(P)
        self.play(FadeIn(dims), FadeIn(unite_cm()))
        self.etape()

        # --- découpage en 2 rectangles (les cotes restent affichées pour suivre les calculs)
        n1 = MathTex("1", color=WHITE, font_size=FS_EQ).move_to(P.p(0, 2.5))
        n2 = MathTex("2", color=WHITE, font_size=FS_EQ).move_to(P.p(-4, 13))
        self.play(table.animate.shift(0.35 * UP), run_time=0.6)
        self.play(Write(n1), Write(n2))
        self.play(table.animate.shift(0.35 * DOWN), run_time=0.6)

        sol = Line(P.p(-7.5, 0), P.p(9, 0), color=GREY_B, stroke_width=2)
        Pn = Panneau(0.0, 2.45, gap=0.22)
        t0 = Pn.placer(T(r"Hauteurs mesurées depuis le \textbf{bas} de la section.", font_size=28))
        self.play(Create(sol), Write(t0))

        # --- élément 1 : l'âme
        g1 = point_G(P.p(0, 6), nom="G_1", cote_label=DR, couleur=WHITE, fs=26, buff=0.05)
        c1 = P.cote_v(3.0, 0, 6, "Y_{G_1}", RIGHT, couleur=C_ELEM[0], fs=30)
        r1 = P.rappel(0, 6, 3.0, 6)
        self.play(Indicate(ame, color=C_ELEM[0]), FadeIn(g1, scale=2))
        self.play(Create(r1), FadeIn(c1))
        l1 = Pn.placer(MathTex(r"S_1 = 2\times 12 = 24\ \mathrm{cm^2}", font_size=34, color=C_ELEM[0]))
        l2 = Pn.placer(MathTex(r"Y_{G_1} = 12/2 = 6\ \mathrm{cm}", font_size=34, color=C_ELEM[0]))
        self.play(Write(l1))
        self.play(Write(l2))
        self.etape()

        # --- élément 2 : la table
        g2 = point_G(P.p(0, 13), nom="G_2", cote_label=LEFT, couleur=WHITE, fs=28, buff=0.3)
        c2 = P.cote_v(7.6, 0, 13, "Y_{G_2}", RIGHT, couleur=C_ELEM[1], fs=30)
        r2 = P.rappel(0, 13, 7.6, 13)
        self.play(Indicate(table, color=C_ELEM[1]), FadeIn(g2, scale=2))
        self.play(Create(r2), FadeIn(c2))
        l3 = Pn.placer(MathTex(r"S_2 = 12\times 2 = 24\ \mathrm{cm^2}", font_size=34, color=C_ELEM[1]))
        l4 = Pn.placer(MathTex(r"Y_{G_2} = 12 + 2/2 = 13\ \mathrm{cm}", font_size=34, color=C_ELEM[1]))
        self.play(Write(l3))
        self.play(Write(l4))
        piege = Tex(r"\textbf{Piège} : $Y_{G_2} \neq 1$ cm ! On part du bas de la section entière.",
                    font_size=28, color=C_NEG).to_edge(DOWN, buff=0.25).shift(1.6 * RIGHT)
        self.play(FadeIn(piege, shift=0.2 * UP))
        self.etape()

        # --- formule
        self.play(FadeOut(piege))
        f = Pn.placer(MathTex(r"Y_G = \frac{S_1 Y_{G_1} + S_2 Y_{G_2}}{S_1 + S_2}"
                              r"= \frac{24\times 6 + 24\times 13}{24 + 24}", font_size=34), gap=0.15)
        r = Pn.placer(MathTex(r"Y_G = \frac{456}{48} = 9{,}5\ \mathrm{cm}", font_size=FS_EQ))
        self.play(Write(f))
        self.play(Write(r))
        b = SurroundingRectangle(r, color=C_G, buff=0.1)
        self.play(Create(b))

        gG = point_G(P.p(0, YG_T), cote_label=UR, buff=0.15)
        cG = P.cote_v(-5.0, 0, YG_T, "Y_G", LEFT, couleur=C_G, fs=30)
        rG = P.rappel(-5.0, YG_T, 0, YG_T)
        self.play(FadeIn(gG, scale=2))
        self.play(Create(rG), FadeIn(cG))
        self.play(FadeIn(repere_zy(P.p(0, YG_T), l=0.6, fs=26)))
        self.etape()

        # --- vérifications de bon sens
        v1 = Tex(r"$S_1 = S_2$ : $G$ est au milieu de $G_1G_2$ : $\frac{6 + 13}{2} = 9{,}5$ cm \checkmark",
                 font_size=28, color=C_POS)
        v2 = Tex(r"$Y_G \neq 14/2 = 7$ cm : pas de symétrie, $G$ « monte » vers la table.",
                 font_size=28, color=C_POS)
        VGroup(v1, v2).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(DOWN, buff=0.2).shift(1.3 * RIGHT)
        self.play(FadeIn(v1))
        self.play(FadeIn(v2))
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. Enlever de la matière : termes négatifs
# ---------------------------------------------------------------------------
class BarycentreEvidement(Base):
    def construct(self):
        titre = self.titre(r"Enlever de la matière : des termes négatifs")
        self.play(Write(titre))

        P = Plan((-4.6, -2.6), s=0.32)
        plein, trou = section_evidee(P)
        self.play(DrawBorderThenFill(plein))
        dims = cotes_evidee(P)
        self.play(DrawBorderThenFill(trou))
        self.play(FadeIn(dims), FadeIn(unite_cm()))
        txt = T(r"Rectangle plein \textbf{moins} un trou :\\ le trou compte \textbf{négativement}.")
        Pn = Panneau(0.2, 2.45, gap=0.22)
        Pn.placer(txt)
        self.play(Write(txt))
        self.etape()

        # --- élément 1 : le rectangle plein (les cotes restent affichées)
        sol = Line(P.p(-6.5, 0), P.p(12, 0), color=GREY_B, stroke_width=2)
        ghost = P.rect(*PLEIN, C_ELEM[0], opacite=0).set_stroke(C_ELEM[0], 5)
        g1 = point_G(P.p(0, 6), nom="G_1", cote_label=DR, couleur=WHITE, fs=26)
        c1 = P.cote_v(8.4, 0, 6, "Y_{G_1}", RIGHT, couleur=C_ELEM[0], fs=30)
        self.play(Create(sol))
        self.play(Create(ghost), FadeIn(g1, scale=2))
        self.play(Create(P.rappel(5, 6, 8.4, 6)), FadeIn(c1))
        l1 = Pn.placer(MathTex(r"S_1 = 10\times 12 = 120\ \mathrm{cm^2},\quad Y_{G_1} = 12/2 = 6\ \mathrm{cm}",
                               font_size=32, color=C_ELEM[0]))
        self.play(Write(l1), FadeOut(ghost))

        # --- élément 2 : le trou
        g2 = point_G(P.p(0, 8), nom="G_2", cote_label=DR, couleur=C_TROU, fs=26, buff=0.05)
        c2 = P.cote_v(10.6, 0, 8, "Y_{G_2}", RIGHT, couleur=C_TROU, fs=30)
        self.play(Indicate(trou, color=C_TROU), FadeIn(g2, scale=2))
        self.play(Create(P.rappel(3, 8, 10.6, 8)), FadeIn(c2))
        l2 = Pn.placer(MathTex(r"S_2 = -\,6\times 4 = -24\ \mathrm{cm^2}", font_size=32, color=C_TROU))
        l3 = Pn.placer(MathTex(r"Y_{G_2} = 12 - 2 - 4/2 = 8\ \mathrm{cm}", font_size=32, color=C_TROU))
        self.play(Write(l2))
        self.play(Write(l3))
        self.etape()

        f = Pn.placer(MathTex(r"Y_G = \frac{120\times 6 + (-24)\times 8}{120 + (-24)} = \frac{528}{96}",
                              font_size=34), gap=0.15)
        r = Pn.placer(MathTex(r"Y_G = 5{,}5\ \mathrm{cm}", font_size=FS_EQ))
        self.play(Write(f))
        self.play(Write(r), Create(SurroundingRectangle(r, color=C_G, buff=0.1)))
        gG = point_G(P.p(0, YG_E), cote_label=LEFT, buff=0.15)
        cG = P.cote_v(6.2, 0, YG_E, "Y_G", RIGHT, couleur=C_G, fs=30)
        self.play(FadeIn(gG, scale=2), g1.animate.set_opacity(0.35))
        self.play(Create(P.rappel(0, YG_E, 6.2, YG_E)), FadeIn(cG))
        self.etape()

        v = Tex(r"Le trou est dans le haut : $G$ descend sous la mi-hauteur ($5{,}5 < 6$ cm). \checkmark",
                font_size=28, color=C_POS).to_edge(DOWN, buff=0.25).shift(1.2 * RIGHT)
        self.play(FadeIn(v))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. Moment quadratique
# ---------------------------------------------------------------------------
class MomentQuadratique(Base):
    def construct(self):
        titre = self.titre(r"Moment quadratique : la matière loin de l'axe")
        self.play(Write(titre))

        # --- la règle à plat / sur chant
        f = ValueTracker(0)
        Y0 = 1.0

        def poutre_flechie(x0, x1, amp):
            return always_redraw(lambda: ParametricFunction(
                lambda t: np.array([x0 + (x1 - x0) * t, Y0 - amp * f.get_value() * np.sin(PI * t), 0]),
                t_range=[0, 1], color=GREY_B, stroke_width=10))

        def charge(xm, amp):
            return always_redraw(lambda: force([xm, Y0 + 1.3 - amp * f.get_value(), 0],
                                               [xm, Y0 + 0.07 - amp * f.get_value(), 0]))

        cas = []
        for (x0, x1, amp, (bb, hh), nom) in ((-6.3, -1.3, 1.0, (12, 2), "à plat"),
                                             (1.3, 6.3, 1.0 / 36, (2, 12), "sur chant")):
            xm = (x0 + x1) / 2
            sec = Rectangle(width=0.12 * bb, height=0.12 * hh).set_stroke(WHITE, 3).set_fill(C_SECTION, 0.7)
            sec.move_to([xm, -1.8, 0])
            lab = Tex(nom + r" ($" + f"{bb}" + r"\times" + f"{hh}" + r"$ cm)", font_size=FS_TEXTE)
            lab.next_to(sec, DOWN, buff=0.25).set_y(-2.85)
            cas.append(VGroup(poutre_flechie(x0, x1, amp), symbole_articulation([x0, Y0, 0], s=0.4),
                              symbole_appui([x1, Y0, 0], s=0.4), charge(xm, amp), sec, lab))
        for c in cas:
            self.play(FadeIn(c))
        self.play(f.animate.set_value(1), run_time=2)
        t = Tex(r"Même section, même matière... mais pas du tout la même \textbf{rigidité} !",
                font_size=FS_TEXTE).to_edge(DOWN, buff=0.2)
        self.play(Write(t))
        self.etape()
        for c in cas:
            for m in c:
                m.clear_updaters()
        self.tout_effacer(garder=[titre])

        # --- définition : chaque bande compte avec y²
        c = np.array([-4.6, -0.5, 0])
        bS, hS, n = 2.4, 3.6, 9
        rect = Rectangle(width=bS, height=hS).set_stroke(WHITE, 3).move_to(c)
        axe = axe_Z(c, demi=bS / 2 + 0.2)
        labZ = MathTex("Z", font_size=FS_TEXTE).next_to(axe, LEFT, buff=0.1)
        gG = point_G(c, cote_label=UR)
        cb = cote(c + (hS / 2 + 0.35) * DOWN + bS / 2 * LEFT, c + (hS / 2 + 0.35) * DOWN + bS / 2 * RIGHT, "b", DOWN)
        ch = cote(c + (bS / 2 + 0.35) * RIGHT + hS / 2 * DOWN, c + (bS / 2 + 0.35) * RIGHT + hS / 2 * UP, "h", RIGHT)
        self.play(Create(rect), Create(axe), Write(labZ), FadeIn(gG), FadeIn(cb), FadeIn(ch))

        dy = hS / n
        x_bar = -1.2
        bandes, barres = VGroup(), VGroup()
        for k in range(n):
            y = -hS / 2 + dy * (k + 0.5)
            col = interpolate_color(BLUE_E, YELLOW, (2 * abs(y) / hS) ** 2)
            bandes.add(Rectangle(width=bS, height=dy).move_to(c + y * UP)
                       .set_stroke(WHITE, 1).set_fill(col, 0.85))
            L = max(0.02, 0.9 * y ** 2)
            barres.add(Rectangle(width=L, height=0.85 * dy).move_to([x_bar + L / 2, c[1] + y, 0])
                       .set_stroke(width=0).set_fill(col, 0.9))
        axe_b = Line([x_bar, c[1] - hS / 2 - 0.2, 0], [x_bar, c[1] + hS / 2 + 0.2, 0], color=GREY_B)
        lab_b = MathTex(r"y^2\,\mathrm{d}S", font_size=FS_TEXTE).next_to(axe_b, UP, buff=0.1).shift(0.6 * RIGHT)
        y_k = n - 1
        yy = -hS / 2 + dy * (y_k + 0.5)
        cy = cote(c + 0.2 * LEFT, c + 0.2 * LEFT + yy * UP, "y", LEFT, fs=30)
        ds = MathTex(r"\mathrm{d}S = b\,\mathrm{d}y", font_size=30).next_to(bandes[y_k], UP, buff=0.12)
        self.play(FadeIn(bandes[y_k]), FadeIn(cy), FadeIn(ds))
        self.etape()
        self.play(FadeOut(cy), FadeOut(ds), Create(axe_b), Write(lab_b))
        self.play(LaggedStart(*[AnimationGroup(FadeIn(bd), GrowFromEdge(br, LEFT)) for bd, br in zip(bandes, barres)],
                              lag_ratio=0.25), run_time=3)
        Pn = Panneau(2.2, 2.3, gap=0.3)
        t1 = Pn.placer(T(r"Une bande loin de l'axe $Z$\\compte beaucoup plus :\\la distance est au \textbf{carré}.",
                         font_size=30))
        self.play(Write(t1))
        defi = MathTex(r"I_{GZ} = \int_S y^2\,\mathrm{d}S", font_size=48)
        Pn.placer(defi, gap=0.4)
        cadre = SurroundingRectangle(defi, color=BLUE_B, buff=0.2)
        self.play(Write(defi), Create(cadre))
        self.etape()

        # --- calcul pour le rectangle
        self.play(FadeOut(barres), FadeOut(axe_b), FadeOut(lab_b), FadeOut(t1), FadeOut(defi), FadeOut(cadre))
        Pn = Panneau(-1.6, 2.3, gap=0.3)
        lignes = [
            r"I_{GZ} = \int_S y^2\,\mathrm{d}S = b\int_{-h/2}^{h/2} y^2\,\mathrm{d}y",
            r"= b\left[\frac{y^3}{3}\right]_{-h/2}^{h/2} = \frac{b}{3}\left(\frac{h^3}{8} + \frac{h^3}{8}\right)",
        ]
        for l in lignes:
            m = Pn.placer(MathTex(l, font_size=36))
            self.play(Write(m))
        res = Pn.placer(MathTex(r"I_{GZ} = \frac{b\,h^3}{12}", font_size=56), gap=0.3)
        res.shift(1.5 * RIGHT)
        cadre = SurroundingRectangle(res, color=YELLOW, buff=0.2)
        self.play(Write(res), Create(cadre))
        u = Tex(r"Unité : cm$^4$ ou mm$^4$ \quad ($1$ cm$^4 = 10^4$ mm$^4$)", font_size=28, color=GREY_B)
        u.next_to(cadre, DOWN, buff=0.35)
        self.play(FadeIn(u))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- effet de b et de h (en direct)
        b, h = ValueTracker(4), ValueTracker(8)
        s = 0.25
        c = np.array([-3.8, -0.6, 0])
        sec = always_redraw(lambda: Rectangle(width=s * b.get_value(), height=s * h.get_value())
                            .set_stroke(WHITE, 3).set_fill(C_SECTION, 0.7).move_to(c))
        axe = axe_Z(c, demi=1.3)
        cb = always_redraw(lambda: cote(c + (s * h.get_value() / 2 + 0.3) * DOWN + s * b.get_value() / 2 * LEFT,
                                        c + (s * h.get_value() / 2 + 0.3) * DOWN + s * b.get_value() / 2 * RIGHT,
                                        "b", DOWN))
        ch = always_redraw(lambda: cote(c + (s * b.get_value() / 2 + 0.3) * LEFT + s * h.get_value() / 2 * DOWN,
                                        c + (s * b.get_value() / 2 + 0.3) * LEFT + s * h.get_value() / 2 * UP,
                                        "h", LEFT))
        rappel_f = MathTex(r"I_{GZ} = \frac{b\,h^3}{12}", font_size=44).move_to([3.0, 2.0, 0])
        lb = ligne_valeur("b =", b.get_value, r"\mathrm{cm}", decimales=0)
        lh = ligne_valeur("h =", h.get_value, r"\mathrm{cm}", decimales=0)
        lI = ligne_valeur("I_{GZ} =", lambda: b.get_value() * h.get_value() ** 3 / 12, r"\mathrm{cm^4}",
                          couleur=YELLOW)
        for i, l in enumerate((lb, lh, lI)):
            l.move_to([1.0 + l.width / 2, 0.8 - 0.75 * i, 0])
        self.play(FadeIn(sec), Create(axe), FadeIn(cb), FadeIn(ch), Write(rappel_f))
        self.play(FadeIn(lb), FadeIn(lh), FadeIn(lI))
        self.etape()

        self.play(h.animate.set_value(16), run_time=3)
        m1 = MathTex(r"h\times 2 \ \Rightarrow\ I_{GZ}\times 8 \quad (2^3)", font_size=FS_EQ, color=C_POS)
        m1.move_to([3.0, -1.9, 0])
        self.play(Write(m1))
        self.etape()
        self.play(h.animate.set_value(8), FadeOut(m1), run_time=2)
        self.play(b.animate.set_value(8), run_time=2)
        m2 = MathTex(r"b\times 2 \ \Rightarrow\ I_{GZ}\times 2 \ \text{seulement}", font_size=FS_EQ, color=C_NEG)
        m2.move_to([3.0, -1.9, 0])
        self.play(Write(m2))
        self.etape()
        self.play(b.animate.set_value(4), FadeOut(m2), run_time=2)
        concl = Tex(r"Pour être rigide en flexion : mettre de la \textbf{hauteur} !", font_size=FS_TEXTE, color=C_G)
        concl.to_edge(DOWN, buff=0.3)
        self.play(Write(concl))
        self.etape()

        # --- retour sur la règle
        for m in (sec, cb, ch, lb[1], lh[1], lI[1]):
            m.clear_updaters()
        self.tout_effacer(garder=[titre])
        reg = VGroup(
            MathTex(r"\text{à plat : } I_{GZ} = \frac{12\times 2^3}{12} = 8\ \mathrm{cm^4}", font_size=FS_EQ),
            MathTex(r"\text{sur chant : } I_{GZ} = \frac{2\times 12^3}{12} = 288\ \mathrm{cm^4}", font_size=FS_EQ),
            MathTex(r"\frac{288}{8} = 36 \ \text{fois plus rigide sur chant !}", font_size=FS_EQ, color=C_POS),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([-2.2, 0.8, 0])
        regles = VGroup()
        for (bb, hh, y) in ((12, 2, 1.9), (2, 12, -0.9)):
            c = np.array([4.6, y, 0])
            r = Rectangle(width=0.2 * bb, height=0.2 * hh).set_stroke(WHITE, 3).set_fill(C_SECTION, 0.7).move_to(c)
            regles.add(VGroup(
                r, axe_Z(c, demi=0.2 * bb / 2 + 0.4), MathTex("Z", font_size=26).next_to(c + (0.1 * bb + 0.4) * LEFT, LEFT, 0.08),
                cote(r.get_corner(DL) + 0.3 * DOWN, r.get_corner(DR) + 0.3 * DOWN, str(bb), DOWN, fs=30),
                cote(r.get_corner(DR) + 0.3 * RIGHT, r.get_corner(UR) + 0.3 * RIGHT, str(hh), RIGHT, fs=30)))
        unite = Tex(r"(cm)", font_size=26, color=GREY_B).move_to([6.4, 3.0, 0])
        for r, sec in zip(reg[:2], regles):
            self.play(FadeIn(sec), *([FadeIn(unite)] if sec is regles[0] else []))
            self.play(Write(r))
        self.play(Write(reg[2]))
        self.etape()
        self.play(FadeOut(regles), FadeOut(unite))

        # --- le disque
        cD = np.array([4.2, -1.6, 0])
        disque = Circle(radius=1.0).set_stroke(WHITE, 3).set_fill(C_SECTION, 0.7).move_to(cD)
        cDia = cote(cD + 1.0 * LEFT + 1.25 * DOWN, cD + 1.0 * RIGHT + 1.25 * DOWN, "D", DOWN)
        fD = MathTex(r"\text{Disque : } I_{GZ} = \frac{\pi\,D^4}{64}", font_size=44).move_to([-1.8, -1.6, 0])
        self.play(DrawBorderThenFill(disque), Create(axe_Z(cD, demi=1.4)), FadeIn(point_G(cD)), FadeIn(cDia))
        self.play(Write(fD), Create(SurroundingRectangle(fD, color=YELLOW, buff=0.15)))
        self.etape(2)


# ---------------------------------------------------------------------------
# 5. Théorème de Huygens
# ---------------------------------------------------------------------------
class Huygens(Base):
    def construct(self):
        titre = self.titre(r"Sections composées : théorème de Huygens")
        self.play(Write(titre))

        # --- un rectangle qui s'éloigne de l'axe
        d = ValueTracker(0)
        s = 0.4
        c0 = np.array([-4.2, -1.4, 0])
        axe = axe_Z(c0, demi=2.6, couleur=C_G)
        labZ = MathTex(r"Z", font_size=FS_TEXTE, color=C_G).next_to(axe, LEFT, buff=0.1)
        gG = point_G(c0, cote_label=DL, buff=0.1)
        lab_axe = Tex(r"axe passant par $G$\\(section complète)", font_size=24, color=C_G).next_to(axe, DOWN, buff=0.5)
        el = always_redraw(lambda: Rectangle(width=6 * s, height=2 * s).set_stroke(WHITE, 3)
                           .set_fill(C_ELEM[1], 0.7).move_to(c0 + s * d.get_value() * UP))
        gi = always_redraw(lambda: croix(c0 + s * d.get_value() * UP, WHITE, t=0.1))
        cd = always_redraw(lambda: cote(c0 + 1.6 * RIGHT, c0 + 1.6 * RIGHT + s * max(d.get_value(), 0.05) * UP,
                                        "d", RIGHT))
        c6 = always_redraw(lambda: cote(c0 + s * d.get_value() * UP + (s + 0.3) * UP + 3 * s * LEFT,
                                        c0 + s * d.get_value() * UP + (s + 0.3) * UP + 3 * s * RIGHT, "6", UP, fs=30))
        c2 = always_redraw(lambda: cote(c0 + s * d.get_value() * UP + (3 * s + 0.3) * LEFT + s * DOWN,
                                        c0 + s * d.get_value() * UP + (3 * s + 0.3) * LEFT + s * UP, "2", LEFT, fs=30))
        unite = Tex(r"(cotes en cm)", font_size=26, color=GREY_B).move_to([-6.0, -3.7, 0])
        self.play(Create(axe), Write(labZ), FadeIn(gG), FadeIn(lab_axe))
        self.play(FadeIn(el), FadeIn(gi))
        self.play(FadeIn(c6), FadeIn(c2), FadeIn(unite))

        Pn = Panneau(0.3, 2.4, gap=0.3)
        l1 = Pn.placer(MathTex(r"\text{rectangle } 6\times 2 :\ I_{G_iZ} = \frac{6\times 2^3}{12} = 4\ \mathrm{cm^4}",
                               font_size=32))
        l1b = Pn.placer(MathTex(r"S_i = 6\times 2 = 12\ \mathrm{cm^2}", font_size=32))
        ld = ligne_valeur("d =", d.get_value, r"\mathrm{cm}")
        lI = ligne_valeur(r"I_{GZ} = 4 + d^2 \times 12 =", lambda: 4 + 12 * d.get_value() ** 2, r"\mathrm{cm^4}",
                          couleur=YELLOW)
        Pn.placer(ld)
        Pn.placer(lI)
        self.play(Write(l1), Write(l1b))
        self.play(FadeIn(ld), FadeIn(lI))
        self.etape()
        self.add(cd)
        self.play(d.animate.set_value(5), run_time=4, rate_func=linear)
        t = T(r"La matière loin de $G$ fait exploser $I_{GZ}$ :\\c'est le terme $d^2 \times S$ qui domine.",
              font_size=30, color=C_POS)
        Pn.placer(t, gap=0.4)
        self.play(Write(t))
        self.etape()
        for m in (el, gi, cd, c6, c2, ld[1], lI[1]):
            m.clear_updaters()
        self.tout_effacer(garder=[titre])

        # --- la formule (poly)
        hu = MathTex(r"\underbrace{I_{GZ}}_{\text{au barycentre}} = "
                     r"\underbrace{I_{G_iZ}}_{\substack{\text{au centre}\\ \text{de l'élément } i}} + "
                     r"\underbrace{(Y_{G_i} - Y_G)^2 \times S_i}_{\substack{\text{transport de } Y_{G_i}\\"
                     r"\text{vers } Y_G}}", font_size=44).move_to([0, 1.2, 0])
        somme = MathTex(r"I_{GZ} = \sum_i \Big( I_{G_iZ} + d_i^2 \times S_i \Big)"
                        r"\qquad d_i = Y_{G_i} - Y_G", font_size=44).move_to([0, -1.2, 0])
        cadre = SurroundingRectangle(somme, color=YELLOW, buff=0.2)
        self.play(Write(hu))
        self.etape()
        self.play(Write(somme), Create(cadre))
        rq = Tex(r"$d_i$ est au carré : son signe n'a pas d'importance.", font_size=FS_TEXTE, color=GREY_B)
        rq.next_to(cadre, DOWN, buff=0.4)
        self.play(FadeIn(rq))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- exemple : la section en T
        P = Plan((-4.4, -2.7), s=0.33)
        ame, table = section_T(P)
        axeG = axe_Z(P.p(0, YG_T), demi=2.3, couleur=C_G)
        gG = point_G(P.p(0, YG_T), cote_label=UR, buff=0.12)
        cG = P.cote_v(-5.0, 0, YG_T, "Y_G", LEFT, couleur=C_G, fs=30)
        self.play(FadeIn(ame), FadeIn(table), FadeIn(cotes_T(P)), FadeIn(unite_cm()))
        self.play(Create(axeG), FadeIn(gG), FadeIn(cG))
        Pn = Panneau(-1.0, 2.45, gap=0.2)
        l0 = Pn.placer(T(r"Section en T de l'exemple précédent :\\$Y_G = 9{,}5$ cm, $S_1 = S_2 = 24$ cm$^2$",
                         font_size=28, color=C_G))
        self.play(Write(l0))

        g1 = point_G(P.p(0, 6), nom="G_1", cote_label=DR, couleur=WHITE, fs=26, buff=0.05)
        c1 = P.cote_v(3.2, 6, YG_T, "d_1", RIGHT, couleur=C_ELEM[0], fs=30)
        self.play(Indicate(ame, color=C_ELEM[0]), FadeIn(g1, scale=2))
        self.play(Create(P.rappel(0, 6, 3.2, 6)), Create(P.rappel(1, YG_T, 3.2, YG_T)), FadeIn(c1))
        e1 = [Pn.placer(MathTex(l, font_size=32, color=C_ELEM[0])) for l in (
            r"1 :\ I_{G_1Z} = \frac{2\times 12^3}{12} = 288,\quad d_1 = 6 - 9{,}5 = -3{,}5",
            r"288 + (-3{,}5)^2 \times 24 = 288 + 294 = 582\ \mathrm{cm^4}")]
        for m in e1:
            self.play(Write(m))
        self.etape()

        g2 = point_G(P.p(0, 13), nom="G_2", cote_label=LEFT, couleur=WHITE, fs=26, buff=0.3)
        c2 = P.cote_v(7.2, YG_T, 13, "d_2", RIGHT, couleur=C_ELEM[1], fs=30)
        self.play(Indicate(table, color=C_ELEM[1]), FadeIn(g2, scale=2))
        self.play(Create(P.rappel(6, 13, 7.2, 13)), Create(P.rappel(1, YG_T, 7.2, YG_T)), FadeIn(c2))
        e2 = [Pn.placer(MathTex(l, font_size=32, color=C_ELEM[1])) for l in (
            r"2 :\ I_{G_2Z} = \frac{12\times 2^3}{12} = 8,\quad d_2 = 13 - 9{,}5 = 3{,}5",
            r"8 + 3{,}5^2 \times 24 = 8 + 294 = 302\ \mathrm{cm^4}")]
        for m in e2:
            self.play(Write(m))
        tot = Pn.placer(MathTex(r"I_{GZ} = 582 + 302 = 884\ \mathrm{cm^4}", font_size=FS_EQ), gap=0.3)
        self.play(Write(tot), Create(SurroundingRectangle(tot, color=YELLOW, buff=0.1)))
        self.etape()
        rq = Tex(r"Table : $8$ cm$^4$ « propres », mais $294$ cm$^4$ de transport !\\"
                 r"D'où les profilés en I : la matière est mise loin de $G$.",
                 font_size=28, color=C_POS).to_edge(DOWN, buff=0.2).shift(1.5 * RIGHT)
        self.play(FadeIn(rq))
        self.etape()
        self.tout_effacer(garder=[titre])

        # --- exemple : la section évidée (trou = terme négatif)
        P = Plan((-4.6, -2.6), s=0.32)
        plein, trou = section_evidee(P)
        axeG = axe_Z(P.p(0, YG_E), demi=2.2, couleur=C_G)
        gG = point_G(P.p(0, YG_E), cote_label=DL, buff=0.1)
        lab = Tex(r"$Y_G = 5{,}5$ cm", font_size=28, color=C_G).next_to(axeG.get_right(), DR, buff=0.12)
        gi = VGroup(point_G(P.p(0, 6), nom="G_1", cote_label=DR, couleur=WHITE, fs=24, buff=0.03),
                    point_G(P.p(0, 8), nom="G_2", cote_label=UR, couleur=C_TROU, fs=24, buff=0.03))
        cd2 = P.cote_v(7.5, YG_E, 8, "d_2", RIGHT, couleur=C_TROU, fs=28)
        self.play(FadeIn(plein), FadeIn(trou), FadeIn(cotes_evidee(P)), FadeIn(unite_cm()))
        self.play(Create(axeG), FadeIn(gG), FadeIn(lab), FadeIn(gi))
        self.play(Create(P.rappel(0, 8, 7.5, 8)), FadeIn(cd2))
        Pn = Panneau(-2.2, 2.45, gap=0.2)
        lignes = [
            (r"1 :\ \frac{10\times 12^3}{12} + (6 - 5{,}5)^2\times 120 = 1440 + 30 = 1470", C_ELEM[0], plein),
            (r"2 :\ -\Big(\frac{6\times 4^3}{12} + (8 - 5{,}5)^2\times 24\Big) = -(32 + 150) = -182", C_TROU, trou),
        ]
        for l, col, m in lignes:
            self.play(Indicate(m, color=col))
            self.play(Write(Pn.placer(MathTex(l, font_size=30, color=col))))
        tot = Pn.placer(MathTex(r"I_{GZ} = 1470 - 182 = 1288\ \mathrm{cm^4}", font_size=FS_EQ), gap=0.3)
        self.play(Write(tot), Create(SurroundingRectangle(tot, color=YELLOW, buff=0.1)))
        rq = Tex(r"Le trou : on retire \textbf{tout} son terme ($I_{G_iZ}$ \textbf{et} $d^2 S$).",
                 font_size=28, color=C_TROU).to_edge(DOWN, buff=0.3).shift(1.5 * RIGHT)
        self.play(FadeIn(rq))
        self.etape(2)


# ---------------------------------------------------------------------------
# 6. Profilés métalliques : lire le catalogue (UPE 120)
# ---------------------------------------------------------------------------
ORANGE_CAT = {r"$\mathsf{y}$": ORANGE, r"$\mathsf{z}$": ORANGE,
              r"$\mathsf{y\!-\!y}$": ORANGE, r"$\mathsf{z\!-\!z}$": ORANGE}


class ProfilesUPE(Base):
    NOM = "UPE 120"
    COL = dict(h=2, b=3, A=4, Iy=5, Wy=6, Iz=7, Wz=8, ys=9)   # colonnes du tableau (1 = noms)
    LIGNE = 4                                                  # ligne de l'UPE 120 (1 = en-têtes)

    def axes_catalogue(self, G, angle, l, lh=None):
        """Axes y-y et z-z du catalogue (placé en C : y horizontal vers la gauche, z vertical vers le bas).
        lh : demi-longueur de l'axe qui se retrouve horizontal (pour ne pas croiser les cotes)."""
        kw = dict(buff=0, color=ORANGE, stroke_width=2.5, max_tip_length_to_length_ratio=0.08)
        grp = VGroup()
        for nom, u0 in (("y", LEFT), ("z", DOWN)):
            u = rotate_vector(u0, angle)
            horiz = abs(u[0]) > 0.5
            L = lh if (horiz and lh is not None) else l
            a = Arrow(G - L * u, G + L * u, **kw)
            lab = MathTex(r"\mathsf{" + nom + "}", color=ORANGE, font_size=34)
            lab.move_to(a.get_end() + (0.3 * UP if horiz else 0.25 * u))
            grp.add(VGroup(a, lab))
        return VGroup(grp[0][0], grp[1][0], grp[0][1], grp[1][1])

    @staticmethod
    def demi_largeur(prof, G):
        return max(prof.get_right()[0] - G[0], G[0] - prof.get_left()[0]) + 0.2

    def axe_flexion(self, G, l):
        a = axe_Z(G, demi=l, couleur=YELLOW)
        return VGroup(a, MathTex("Z", color=YELLOW, font_size=30).next_to(a.get_right(), UL, buff=0.08))

    def construct(self):
        titre = self.titre(r"Profilés métalliques : lire le catalogue")
        self.play(Write(titre))

        # --- le profilé tel que dessiné dans le catalogue (placé en C)
        ech = 0.03
        G = np.array([-2.5, -0.4, 0])
        h, b, ys = (val(self.NOM, k) for k in ("h", "b", "ys"))
        prof = profil_upe(self.NOM, ech).shift(G)
        nom = Tex(r"\textsf{UPE\,120}", font_size=40).next_to(prof, UP, buff=1.25)
        self.play(DrawBorderThenFill(prof), Write(nom))
        dos = G[0] - ys * ech
        dims = VGroup(
            cote([dos - 0.5, G[1] - h / 2 * ech, 0], [dos - 0.5, G[1] + h / 2 * ech, 0], "h = 120", LEFT),
            cote([dos, G[1] - h / 2 * ech - 0.4, 0], [dos + b * ech, G[1] - h / 2 * ech - 0.4, 0], "b = 60", DOWN),
            cote([dos, G[1] + h / 2 * ech + 0.35, 0], [G[0], G[1] + h / 2 * ech + 0.35, 0],
                 r"\mathsf{y_s} = 19{,}8", UP, couleur=ORANGE),
            Tex(r"(cotes en mm)", font_size=26, color=GREY_B).move_to([-6.0, -3.7, 0]),
        )
        dims[0][1].shift(0.5 * DOWN)
        dims[1][1].shift(0.75 * RIGHT)
        axes = self.axes_catalogue(G, 0, 2.6)
        gG = point_G(G, cote_label=DR, buff=0.1)
        self.play(FadeIn(dims))
        self.play(Create(axes[:2]), Write(axes[2:]), FadeIn(gG))
        Pn = Panneau(1.6, 2.2, gap=0.3)
        for l in (r"$S$, $G$, $I_{GZ}$ : on ne les calcule pas,\\on les \textbf{lit} dans le catalogue\\"
                  r"(ArcelorMittal, annexe du poly).",
                  r"Attention : les axes du catalogue\\s'appellent $\mathsf{y}$ et "
                  r"$\mathsf{z}$.\\Ce ne sont \textbf{pas} nos $Y$ et $Z$ !"):
            m = Pn.placer(T(l, font_size=30, tex_to_color_map=ORANGE_CAT))
            self.play(Write(m))
            self.etape()
        aZ = self.axe_flexion(G, 1.6)
        m = Pn.placer(T(r"Notre axe $Z$ : toujours l'axe \textbf{horizontal}\\passant par $G$ (axe de flexion).",
                        font_size=30, color=YELLOW))
        self.play(Create(aZ[0]), Write(aZ[1]), Write(m))
        self.etape()

        # --- le tableau
        self.play(*[FadeOut(x) for x in self.mobjects if x not in (titre, prof, axes, gG, aZ)])
        ech2 = 0.018
        G2 = np.array([-5.0, 1.25, 0])
        tab = tableau_upe(largeur=11.0).move_to([0.6, -2.05, 0])
        lh = (prof.width * ech2 / ech) / 2 + abs(prof.get_center()[0] - G[0]) * ech2 / ech + 0.2
        new_axes = self.axes_catalogue(G2, 0, 1.45, lh)
        new_aZ = self.axe_flexion(G2, lh)
        unite = Tex(r"(mm)", font_size=26, color=GREY_B).move_to([-6.5, 3.0, 0])
        self.play(FadeIn(unite), prof.animate.scale(ech2 / ech, about_point=G).shift(G2 - G),
                  gG.animate.shift(G2 - G),
                  ReplacementTransform(axes, new_axes), ReplacementTransform(aZ, new_aZ))
        axes, aZ = new_axes, new_aZ
        self.play(FadeIn(tab))
        lig = SurroundingRectangle(tab.get_rows()[self.LIGNE - 1], color=RED, buff=0.03)
        self.play(Create(lig))
        self.etape()

        def cellules(*cles):
            return VGroup(*[tab.get_cell((self.LIGNE, self.COL[k]), color=YELLOW).set_stroke(width=5) for k in cles])

        def cote_YG(G, bas, cote_label):
            x = prof.get_right()[0] + 0.45 if cote_label is RIGHT else prof.get_left()[0] - 0.45
            return cote([x, bas, 0], [x, G[1], 0], "Y_G", cote_label, couleur=C_G, fs=30)

        def cote_hauteur(G, texte, cote_label):
            """Hauteur totale de la section, du côté opposé à Y_G ; étiquette décalée pour éviter l'axe en G."""
            x = prof.get_right()[0] + 0.45 if cote_label is RIGHT else prof.get_left()[0] - 0.45
            bas, haut = prof.get_bottom()[1], prof.get_top()[1]
            c = cote([x, bas, 0], [x, haut, 0], texte, cote_label, fs=30)
            c[1].shift(0.35 * (UP if (bas + haut) / 2 >= G[1] else DOWN))
            return c

        Pn = Panneau(-2.8, 2.55, gap=0.18)
        cas = [
            (0, r"Placé en C : $Z$ = axe $\mathsf{y\!-\!y}$ du catalogue",
             [r"I_{GZ} = \mathsf{I_y} = 364\ \mathrm{cm^4} = 364\times 10^4\ \mathrm{mm^4}",
              r"Y_G = h/2 = 120/2 = 60\ \mathrm{mm}"], ("Iy", "h")),
            (PI / 2, r"Placé en U : $Z$ = axe $\mathsf{z\!-\!z}$ du catalogue",
             [r"I_{GZ} = \mathsf{I_z} = 55{,}5\ \mathrm{cm^4} = 55{,}5\times 10^4\ \mathrm{mm^4}",
              r"Y_G = \mathsf{y_s} = 19{,}8\ \mathrm{mm}\ \ (\text{depuis le dos de l'âme})"], ("Iz", "ys")),
            (3 * PI / 2, r"Placé en $\cap$ : toujours l'axe $\mathsf{z\!-\!z}$",
             [r"I_{GZ} = \mathsf{I_z} = 55{,}5\ \mathrm{cm^4}",
              r"Y_G = b - \mathsf{y_s} = 60 - 19{,}8 = 40{,}2\ \mathrm{mm}"], ("Iz", "b", "ys")),
        ]
        angle = 0
        tmp = []
        for a, titre_cas, lignes, cles in cas:
            if tmp:
                self.play(*map(FadeOut, tmp))
                Pn.reset()
                tmp = []
            if a != angle:
                lh = self.demi_largeur(prof.copy().rotate(a - angle, about_point=G2), G2)
                new_axes = self.axes_catalogue(G2, a, 1.45, lh)
                new_aZ = self.axe_flexion(G2, lh)
                self.play(Rotate(prof, a - angle, about_point=G2), ReplacementTransform(axes, new_axes),
                          ReplacementTransform(aZ, new_aZ), run_time=1.5)
                axes, aZ, angle = new_axes, new_aZ, a
            t = Pn.placer(T(titre_cas, font_size=30, tex_to_color_map=ORANGE_CAT))
            self.play(Write(t))
            cel = cellules(*cles)
            self.play(Create(cel))
            cote_label = LEFT if a == PI / 2 else RIGHT
            cY = cote_YG(G2, prof.get_bottom()[1], cote_label)
            cH = cote_hauteur(G2, "120" if a == 0 else "60", RIGHT if cote_label is LEFT else LEFT)
            self.play(FadeIn(cY), FadeIn(cH))
            tmp += [t, cel, cY, cH]
            for l in lignes:
                m = Pn.placer(MathTex(l, font_size=32))
                self.play(Write(m))
                tmp.append(m)
            self.etape()

        # --- bilan
        self.play(*map(FadeOut, tmp))
        Pn.reset()
        bilan = [
            T(r"Même profilé, même surface $A = 15{,}4$ cm$^2$ (même poids)...", font_size=30),
            MathTex(r"\text{en C : } 364\ \mathrm{cm^4} \quad\text{contre}\quad \text{en U : } 55{,}5\ \mathrm{cm^4}"
                    r"\quad\Rightarrow\ \times 6{,}6\ !", font_size=34, color=C_POS),
            T(r"\textbf{Piège} : catalogue en mm$^4\times 10^4$, c'est-à-dire en cm$^4$.", font_size=30,
              color=C_NEG),
        ]
        for m in bilan:
            Pn.placer(m)
            self.play(Write(m))
        self.etape(2)
