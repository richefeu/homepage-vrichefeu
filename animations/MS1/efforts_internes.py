"""
MS1 - Animations pédagogiques : efforts internes N, V, M par la méthode de la coupure (§4.2 du poly)

Scènes :
    EffortsInternesIntro   pourquoi couper ? N, V, M (traction, glissement, flexion) ; conventions de signe
    CoupureUnTroncon       exemple 1 du poly : charge q sur L, 1 tronçon, équations puis diagrammes
    CoupureDeuxTroncons    exemple 2 du poly : force F en C, 2 tronçons, x depuis le début du tronçon,
                           partie gauche puis partie droite, diagrammes (saut de V, pic de M)
    CoupureConsole         console encastrée : on isole la partie de DROITE (pas besoin des réactions),
                           N > 0 (traction), M < 0
    CoupureAstuce          effort = −[actions à gauche] = +[actions à droite] ; check-list des pièges

Vidéo  : manim -qh efforts_internes.py EffortsInternesIntro CoupureUnTroncon CoupureDeuxTroncons \
             CoupureConsole CoupureAstuce
Slides : manim-slides render -qh efforts_internes.py <scènes>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403

# ---------------------------------------------------------------------------
# 1. Introduction : que sont N, V et M ?
# ---------------------------------------------------------------------------
class EffortsInternesIntro(EIScene):
    def construct(self):
        titre = self.titre(r"Efforts internes : de quoi parle-t-on ?")
        self.play(Write(titre))
        self.repere(6)
        barre = poutre(self.X(0), self.X(6))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 6)
        P = self.charge(3.5, r"P")
        pts = VGroup(self.point(0, "A", UL), self.point(6, "B", UR))
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts), GrowArrow(P[0]), Write(P[1]))
        self.ecrire(T(r"Que se passe-t-il \textbf{à l'intérieur} de la poutre ?"))
        self.etape()

        # on coupe : sans « colle », le morceau de droite tombe
        xg = 2.2
        cut = self.coupure(xg)
        lG = MathTex("G", color=YELLOW, font_size=FS_EQ).next_to(cut, UP, buff=0.05)
        self.play(Create(cut), Write(lG))
        self.ecrire(T(r"On imagine qu'on \textbf{coupe} la poutre en un point $G$..."))
        gauche = poutre(self.X(0), self.X(xg))
        droite = poutre(self.X(xg), self.X(6))
        self.remove(barre)
        self.add(gauche, droite)
        morceau = VGroup(droite, P)
        morceau.save_state()
        self.play(Rotate(morceau, 14 * DEGREES, about_point=self.X(6)), rate_func=rate_functions.ease_in_quad,
                  run_time=1.5)
        self.ecrire(T(r"Sans rien pour les relier, le morceau de droite tomberait :\\"
                      r"à travers la coupure, la matière transmet des \textbf{efforts}."))
        self.play(Restore(morceau))
        self.etape()

        # la coupure = un encastrement : 3 efforts
        self.effacer_calculs()
        ef = self.efforts(xg)
        self.play(droite.animate.set_opacity(0.15), P.animate.set_opacity(0.15), lB.animate.set_opacity(0.15))
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in ef],
                  *[Write(e[1]) for e in ef])
        self.ecrire(T(r"La coupure agit comme un \textbf{encastrement} : 3 efforts internes."))
        self.ecrire(T(r"$N$ : effort \textbf{normal} \quad $V$ : effort \textbf{tranchant} \quad "
                      r"$M$ : moment \textbf{fléchissant}", color=C_INT))
        self.etape()

        # signification physique : 3 petits schémas
        self.tout_effacer(garder=[titre])
        centres = [np.array([-4.6, 0.6, 0]), np.array([0, 0.6, 0]), np.array([4.6, 0.6, 0])]
        textes = [r"$N$ : \textbf{traction} ($N>0$)\\ou compression ($N<0$)",
                  r"$V$ : \textbf{glissement}\\(cisaillement)", r"$M$ : \textbf{flexion}\\(la poutre se courbe)"]
        blocs = []
        for c, t in zip(centres, textes):
            g = Rectangle(width=1.3, height=0.7, color=GREY_A, fill_color=GREY_D, fill_opacity=1).move_to(c + 0.68 * LEFT)
            d = Rectangle(width=1.3, height=0.7, color=GREY_A, fill_color=GREY_D, fill_opacity=1).move_to(c + 0.68 * RIGHT)
            lab = T(t, font_size=FS_TEXTE - 2).next_to(VGroup(g, d), DOWN, buff=0.6)
            blocs.append((g, d, lab, c))
            self.play(FadeIn(g), FadeIn(d), Write(lab))
        (g1, d1, _, c1), (g2, d2, _, c2), (g3, d3, _, c3) = blocs
        fN = VGroup(force(c1 + 1.4 * RIGHT, c1 + 2.1 * RIGHT, couleur=C_INT, epaisseur=5),
                    force(c1 + 1.4 * LEFT, c1 + 2.1 * LEFT, couleur=C_INT, epaisseur=5))
        self.play(GrowArrow(fN[0]), GrowArrow(fN[1]))
        self.play(d1.animate.shift(0.25 * RIGHT), g1.animate.shift(0.25 * LEFT), fN[0].animate.shift(0.25 * RIGHT),
                  fN[1].animate.shift(0.25 * LEFT), rate_func=there_and_back, run_time=1.6)
        fV = VGroup(force(c2 + 0.68 * RIGHT + 0.4 * DOWN, c2 + 0.68 * RIGHT + 1.0 * DOWN, couleur=C_INT, epaisseur=5),
                    force(c2 + 0.68 * LEFT + 0.4 * UP, c2 + 0.68 * LEFT + 1.0 * UP, couleur=C_INT, epaisseur=5))
        self.play(GrowArrow(fV[0]), GrowArrow(fV[1]))
        self.play(d2.animate.shift(0.25 * DOWN), g2.animate.shift(0.25 * UP), rate_func=there_and_back, run_time=1.6)
        mG = fleche_sens(c3 + 1.6 * LEFT, -1, r=0.35, couleur=C_INT)
        mD = fleche_sens(c3 + 1.6 * RIGHT, +1, r=0.35, couleur=C_INT)
        self.play(Create(mG), Create(mD))
        self.play(Rotate(g3, -12 * DEGREES, about_point=c3 + 0.03 * LEFT + 0.35 * UP),
                  Rotate(d3, 12 * DEGREES, about_point=c3 + 0.03 * RIGHT + 0.35 * UP),
                  rate_func=there_and_back, run_time=1.8)
        self.etape()

        # conventions de signe
        self.tout_effacer(garder=[titre])
        sous = T(r"\textbf{Conventions} : on dessine toujours les efforts internes \textbf{positifs}",
                 color=BLUE_B).next_to(titre, DOWN, buff=0.3)
        self.play(Write(sous))
        G1, G2 = np.array([-2.2, 0.4, 0]), np.array([1.6, 0.4, 0])
        pg = poutre(G1 + 3.6 * LEFT, G1)
        pd = poutre(G2, G2 + 3.6 * RIGHT)
        self.play(Create(pg), Create(pd))
        eg = VGroup(VGroup(force(G1, G1 + 0.9 * RIGHT, couleur=C_INT, epaisseur=5),
                           MathTex("N", color=C_INT, font_size=FS_EQ).next_to(G1 + 0.9 * RIGHT, RIGHT, buff=0.08)),
                    VGroup(force(G1, G1 + 0.9 * UP, couleur=C_INT, epaisseur=5),
                           MathTex("V", color=C_INT, font_size=FS_EQ).next_to(G1 + 0.9 * UP, UP, buff=0.08)),
                    VGroup(fleche_sens(G1, +1, r=0.45, couleur=C_INT),
                           MathTex("M", color=C_INT, font_size=FS_EQ).next_to(G1, DR, buff=0.45)))
        ed = VGroup(VGroup(force(G2, G2 + 0.9 * LEFT, couleur=C_INT, epaisseur=5),
                           MathTex("N", color=C_INT, font_size=FS_EQ).next_to(G2 + 0.9 * LEFT, LEFT, buff=0.08)),
                    VGroup(force(G2, G2 + 0.9 * DOWN, couleur=C_INT, epaisseur=5),
                           MathTex("V", color=C_INT, font_size=FS_EQ).next_to(G2 + 0.9 * DOWN, DOWN, buff=0.08)),
                    VGroup(fleche_sens(G2, -1, r=0.45, couleur=C_INT),
                           MathTex("M", color=C_INT, font_size=FS_EQ).next_to(G2, UL, buff=0.45)))
        tg = T(r"partie \textbf{gauche} :\\$N \rightarrow$, \ $V \uparrow$, \ $M \curvearrowleft$").next_to(pg, DOWN, buff=1.2)
        td = T(r"partie \textbf{droite} : sens opposés\\(action -- réaction)").next_to(pd, DOWN, buff=1.2)
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in eg],
                  *[Write(e[1]) for e in eg], Write(tg))
        self.etape(0.5)
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in ed],
                  *[Write(e[1]) for e in ed], Write(td))
        n = T(r"(Dans le cours, à droite, on dessine $-N$, $-V$, $-M$ dans le sens positif : c'est la même chose.)",
              font_size=FS_TEXTE - 4, color=GREY_B).to_edge(DOWN, buff=0.5)
        self.play(Write(n))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Un tronçon : charge répartie (exemple 1 du poly)
# ---------------------------------------------------------------------------
class CoupureUnTroncon(EIScene):
    def construct(self):
        titre = self.titre(r"Méthode de la coupure : 1 tronçon")
        self.play(Write(titre))
        L = 6
        self.repere(L, largeur=9.0, xc=-0.7)
        barre = poutre(self.X(0), self.X(L))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", L)
        pts = VGroup(self.point(0, "A", UL), self.point(L, "B", UR))
        q = self.repartie(0, L, r"q")
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts))
        self.play(LaggedStart(*[GrowArrow(a) for a in q[0]], lag_ratio=0.04), Create(q[1]), Write(q[2]))
        XA = self.reaction("X", 0, r"X_A = 0")
        YA = self.reaction("Y", 0, r"Y_A = \tfrac{qL}{2}")
        YB = self.reaction("Y", L, r"Y_B = \tfrac{qL}{2}")
        self.ecrire(T(r"\textbf{1.} Actions de liaison (calculées avant) : $X_A = 0$, \ $Y_A = Y_B = qL/2$"))
        self.remplacer_liaisons([lA, lB], [XA, YA, YB])
        self.ecrire(T(r"\textbf{2.} Le chargement ne change pas de $A$ à $B$ : \textbf{un seul tronçon}, $x \in [0,\,L]$"))
        self.etape()

        # coupure en G, à x de A
        self.effacer_calculs()
        xg = 2.4
        cut = self.coupure(xg)
        lG = MathTex("G", color=YELLOW, font_size=FS_EQ).next_to(cut, UP, buff=0.05).shift(0.2 * LEFT)
        cx = self.cote_x(0, xg, "x", dy=-1.4)
        self.play(Create(cut), Write(lG), FadeIn(cx))
        self.ecrire(T(r"\textbf{3.} On coupe en $G$, à la distance $x$ du \textbf{début du tronçon}, et on garde la partie \textbf{gauche}."))
        gauche, droite = poutre(self.X(0), self.X(xg)), poutre(self.X(xg), self.X(L))
        self.remove(barre)
        self.add(gauche, droite)
        qg = self.repartie(0, xg, r"q")
        qg[2].set_opacity(0)
        self.add(qg)
        self.play(droite.animate.set_opacity(0.12), q.animate.set_opacity(0.12), YB.animate.set_opacity(0.12),
                  pts[1].animate.set_opacity(0.12))
        ef = self.efforts(xg)
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in ef],
                  *[Write(e[1]) for e in ef])
        self.ecrire(T(r"Les efforts internes $N$, $V$, $M$ sont dessinés \textbf{positifs}.", color=C_INT))
        self.etape()

        # charge sur la partie isolée
        Fq = self.charge(xg / 2, r"qx", h=1.25, couleur=YELLOW, cote_lab=LEFT)
        self.play(qg.animate.set_opacity(0.3), TransformFromCopy(qg[0], Fq[0]), Write(Fq[1]))
        self.ecrire(T(r"\textbf{Piège :} seule la charge \textbf{sur la partie isolée} compte : $q\,x$, à $x/2$ de $G$.",
                      color=C_NEG))
        self.etape()

        # PFS sur la partie gauche
        self.effacer_calculs()
        self.play(FadeOut(cx))
        self.play(Indicate(VGroup(ef[0], XA), color=YELLOW))
        self.ecrire(MathTex(r"\sum F_X = N(x) + X_A = 0 \ \Rightarrow\ N(x) = 0", font_size=self.FS_CALC))
        self.play(Indicate(VGroup(ef[1], YA, Fq), color=YELLOW))
        self.ecrire(MathTex(r"\sum F_Y = V(x) + Y_A - qx = 0 \ \Rightarrow\ V(x) = qx - \frac{qL}{2}",
                            font_size=self.FS_CALC))
        rq = T(r"Moments au point de coupure $G$ :\\$N$ et $V$ y passent (moment nul).", color=C_LEVIER,
               font_size=FS_TEXTE - 2)
        eq = self.equation(r"\sum M_{/G} =", r"M(x)", r"-x\,Y_A", r"+\frac{x}{2}\,qx", r"=0")
        self.terme(ef[2], xg, xg, 0, eq[1], rq=rq)
        self.terme(YA, xg, 0, -1, eq[2], d="x")
        self.terme(Fq, xg, xg / 2, +1, eq[3], d=r"x/2")
        self.play(Write(eq[4]))
        self.resultat(r"M(x) = -\frac{qx^2}{2} + \frac{qL}{2}\,x")
        self.etape()

        # diagrammes : application numérique
        self.effacer_calculs()
        self.play(*map(FadeOut, [ef, Fq, qg, cut, lG]))
        self.remove(gauche, droite)
        self.add(barre)
        self.play(q.animate.set_opacity(1), YB.animate.set_opacity(1), pts[1].animate.set_opacity(1))
        app = T(r"Application :\\$q = 2$ kN/m\\$L = 6$ m", font_size=FS_TEXTE - 4).move_to([5.75, -0.8, 0])
        self.play(Write(app))
        fV = lambda x: 2 * x - 6
        fM = lambda x: -x ** 2 + 6 * x
        yV, eV, yM, eM = -1.3, 0.11, -3.6, 0.15
        dV = self.diagramme([(0, L, fV)], yV, eV, r"V", C_FY)
        dM = self.diagramme([(0, L, fM)], yM, eM, r"M", C_INT)
        eqV = MathTex(r"V(x) = 2x - 6", font_size=FS_TEXTE - 2, color=C_FY).move_to([5.6, -1.6, 0])
        eqM = MathTex(r"M(x) = -x^2 + 6x", font_size=FS_TEXTE - 2, color=C_INT).move_to([5.6, -2.9, 0])
        self.play(Create(dV[0]), Write(dV[3]), Write(eqV))
        self.play(Create(dV[2]), FadeIn(dV[1]))
        self.play(Write(self.valeur_diag(0, -6, yV, eV, "-6", DL)), Write(self.valeur_diag(L, 6, yV, eV, "+6", UR)))
        self.play(Create(dM[0]), Write(dM[3]), Write(eqM))
        self.play(Create(dM[2]), FadeIn(dM[1]))
        self.etape(0.5)

        xc = ValueTracker(0.01)
        ligne = self.coupure_mobile(xc, yM - 0.2)
        pV = self.point_mobile(xc, fV, yV, eV, C_FY)
        pM = self.point_mobile(xc, fM, yM, eM, C_INT)
        P = Panneau(4.4, -3.3, gap=0.1)
        lv = P.placer(ligne_live(r"V =", lambda: fV(xc.get_value()), unite=r"\mathrm{kN}", fs=FS_TEXTE - 2))
        self.play(FadeIn(ligne), FadeIn(pV), FadeIn(pM), FadeIn(lv))
        self.play(xc.animate.set_value(3), run_time=3, rate_func=linear)
        mx = self.valeur_diag(3, 9, yM, eM, r"M_{max} = \frac{qL^2}{8} = 9~\mathrm{kN\cdot m}", UP, YELLOW)
        z = self.valeur_diag(3, 0, yV, eV, r"V = 0", UL, YELLOW)
        self.play(Write(mx), Write(z), Flash(self.D(3, 9, yM, eM), color=YELLOW))
        self.wait(0.5)
        self.play(xc.animate.set_value(L - 0.01), run_time=3, rate_func=linear)
        n = T(r"$M'(x) = -V(x)$ :\\$M$ extrémal\\là où $V = 0$", color=YELLOW,
              font_size=FS_TEXTE - 4).move_to([5.6, -2.55, 0])
        self.play(FadeOut(eqM))
        self.play(Write(n))
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. Deux tronçons : force ponctuelle (exemple 2 du poly)
# ---------------------------------------------------------------------------
class CoupureDeuxTroncons(EIScene):
    def construct(self):
        titre = self.titre(r"Méthode de la coupure : 2 tronçons")
        self.play(Write(titre))
        L, a = 6, 4
        self.repere(L, largeur=9.0, xc=-0.7)
        barre = poutre(self.X(0), self.X(L))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", L)
        pts = VGroup(self.point(0, "A", UL), self.point(a, "C", UR), self.point(L, "B", UR))
        F = self.charge(a, r"F = 6~\mathrm{kN}")
        cotes = VGroup(self.cote_x(0, a, r"a = 4~\mathrm{m}", dy=-0.95), self.cote_x(a, L, r"b = 2~\mathrm{m}", dy=-0.95))
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts), FadeIn(cotes), GrowArrow(F[0]), Write(F[1]))
        XA = self.reaction("X", 0, r"X_A = 0")
        YA = self.reaction("Y", 0, r"Y_A = 2~\mathrm{kN}")
        YB = self.reaction("Y", L, r"Y_B = 4~\mathrm{kN}")
        self.ecrire(T(r"Actions de liaison (calculées avant) : $X_A = 0$, \ $Y_A = \frac{b}{a+b}F = 2$ kN, "
                      r"\ $Y_B = \frac{a}{a+b}F = 4$ kN"))
        self.play(FadeOut(cotes))
        self.remplacer_liaisons([lA, lB], [XA, YA, YB])
        self.etape()

        # découpage en tronçons
        self.ecrire(T(r"En $C$, la force $F$ \textbf{change les équations} : 2 tronçons."))
        bT1 = BraceBetweenPoints(self.X(0, -1.25), self.X(a, -1.25), DOWN, color=BLUE_B)
        bT2 = BraceBetweenPoints(self.X(a, -1.25), self.X(L, -1.25), DOWN, color=BLUE_B)
        tT1 = MathTex(r"T_1", color=BLUE_B, font_size=FS_EQ).next_to(bT1, DOWN, buff=0.08)
        tT2 = MathTex(r"T_2", color=BLUE_B, font_size=FS_EQ).next_to(bT2, DOWN, buff=0.08)
        self.play(GrowFromCenter(bT1), GrowFromCenter(bT2), Write(tT1), Write(tT2))
        self.ecrire(T(r"Nouveau tronçon à chaque \textbf{force ponctuelle}, \textbf{appui}, \textbf{couple},"
                      r" \textbf{début ou fin de charge répartie}.", color=C_LEVIER))
        self.etape()
        self.play(*map(FadeOut, [bT1, bT2, tT1, tT2]))
        self.effacer_calculs()

        def isoler_gauche(xg):
            g, d = poutre(self.X(0), self.X(xg)), poutre(self.X(xg), self.X(L))
            self.remove(barre)
            self.add(g, d)
            return g, d

        # --- tronçon T1
        xg = 1.8
        cut = self.coupure(xg)
        lG = MathTex("G", color=YELLOW, font_size=FS_EQ).next_to(cut.get_top(), RIGHT, buff=0.12)
        cx = self.cote_x(0, xg, "x", dy=-1.4)
        self.ecrire(T(r"\textbf{Tronçon $T_1$} : coupure à $x$ de $A$, \ $x \in [0,\,4]$ ; on garde la partie gauche."))
        self.play(Create(cut), Write(lG), FadeIn(cx))
        g, d = isoler_gauche(xg)
        cache = VGroup(d, F, YB, pts[1], pts[2])
        self.play(cache.animate.set_opacity(0.12))
        ef = self.efforts(xg)
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in ef],
                  *[Write(e[1]) for e in ef])
        self.ecrire(MathTex(r"N(x) = 0 \qquad V(x) + 2 = 0 \qquad M(x) - x\times2 = 0", font_size=self.FS_CALC))
        self.resultat(r"T_1 : \ N = 0, \quad V(x) = -2~\mathrm{kN}, \quad M(x) = 2x")
        self.etape()

        # --- tronçon T2, partie gauche
        self.effacer_calculs()
        self.play(*map(FadeOut, [ef, cut, lG, cx]))
        self.remove(g, d)
        self.add(barre)
        self.play(VGroup(F, YB, pts[1], pts[2]).animate.set_opacity(1))
        x2 = 1.0
        xg = a + x2
        cut = self.coupure(xg)
        lG = MathTex("G", color=YELLOW, font_size=FS_EQ).next_to(cut.get_top(), RIGHT, buff=0.12)
        cx = self.cote_x(a, xg, "x", dy=-0.95)
        cAx = self.cote_x(0, xg, "4 + x", dy=-1.45)
        self.ecrire(T(r"\textbf{Tronçon $T_2$} : $x$ est mesuré depuis \textbf{le début du tronçon} ($C$), $x \in [0,\,2]$.",
                      color=C_NEG))
        self.play(Create(cut), Write(lG), FadeIn(cx))
        g, d = isoler_gauche(xg)
        cache = VGroup(d, YB, pts[2])
        self.play(cache.animate.set_opacity(0.12))
        ef = self.efforts(xg)
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in ef],
                  *[Write(e[1]) for e in ef])
        self.play(FadeIn(cAx))
        self.ecrire(T(r"Partie gauche : $Y_A$ \textbf{et} $F$ interviennent."))
        self.ecrire(MathTex(r"V(x) + 2 - 6 = 0 \qquad M(x) - (4+x)\times 2 + x\times 6 = 0", font_size=self.FS_CALC))
        self.resultat(r"T_2 : \ V(x) = 4~\mathrm{kN}, \quad M(x) = 8 - 4x")
        self.etape()

        # --- T2 en gardant la partie droite
        self.effacer_calculs()
        self.play(*map(FadeOut, [ef, cAx, cx]))
        self.play(cache.animate.set_opacity(1), VGroup(g, F, YA, XA, pts[0], pts[1]).animate.set_opacity(0.12))
        efd = self.efforts(xg, cote="droite")
        cd = self.cote_x(xg, L, "2 - x", dy=-1.4)
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in efd],
                  *[Write(e[1]) for e in efd], FadeIn(cd))
        self.ecrire(T(r"Plus simple : on garde la partie \textbf{droite} (longueur $2 - x$), seul $Y_B$ intervient."))
        self.ecrire(MathTex(r"-V(x) + 4 = 0 \qquad -M(x) + (2-x)\times 4 = 0", font_size=self.FS_CALC))
        self.resultat(r"V(x) = 4~\mathrm{kN}, \quad M(x) = 4(2-x) = 8 - 4x \quad \checkmark")
        self.etape()

        # --- diagrammes
        self.effacer_calculs()
        self.play(*map(FadeOut, [efd, cd, cut, lG]))
        self.remove(g, d)
        self.add(barre)
        self.play(VGroup(F, YA, XA, pts[0], pts[1], YB, pts[2]).animate.set_opacity(1))
        fV = lambda x: -2 if x < a else 4
        fM = lambda x: 2 * x if x <= a else 8 - 4 * (x - a)
        yV, eV, yM, eM = -1.3, 0.15, -3.55, 0.17
        dV = self.diagramme([(0, a, lambda x: -2), (a, L, lambda x: 4)], yV, eV, r"V", C_FY)
        dM = self.diagramme([(0, a, lambda x: 2 * x), (a, L, lambda x: 8 - 4 * (x - a))], yM, eM, r"M", C_INT)
        self.play(Create(dV[0]), Write(dV[3]))
        self.play(Create(dV[2]), FadeIn(dV[1]))
        self.play(Write(self.valeur_diag(2, -2, yV, eV, "-2", DOWN)), Write(self.valeur_diag(5, 4, yV, eV, "+4", UP)))
        saut = T(r"saut de $F = 6$ kN", color=YELLOW, font_size=FS_TEXTE - 4).next_to(self.D(a, 1, yV, eV), RIGHT, buff=0.15)
        self.play(Write(saut))
        self.play(Create(dM[0]), Write(dM[3]))
        self.play(Create(dM[2]), FadeIn(dM[1]))
        self.play(Write(self.valeur_diag(a, 8, yM, eM, r"M_{max} = 8~\mathrm{kN\cdot m}", UP, YELLOW)))
        self.etape(0.5)

        xc = ValueTracker(0.01)
        ligne = self.coupure_mobile(xc, yM - 0.2)
        pV = self.point_mobile(xc, fV, yV, eV, C_FY)
        pM = self.point_mobile(xc, fM, yM, eM, C_INT)
        P = Panneau(4.4, -1.1, gap=0.15)
        ltr = P.placer(always_redraw(lambda: MathTex("T_1" if xc.get_value() < a else "T_2", color=BLUE_B,
                                                     font_size=FS_TEXTE).move_to([4.8, -1.3, 0])))
        lv = P.placer(ligne_live(r"V =", lambda: fV(xc.get_value()), unite=r"\mathrm{kN}", fs=FS_TEXTE - 2))
        lm = P.placer(ligne_live(r"M =", lambda: fM(xc.get_value()), unite=r"\mathrm{kN\cdot m}", fs=FS_TEXTE - 2))
        self.play(FadeIn(ligne), FadeIn(pV), FadeIn(pM), FadeIn(ltr), FadeIn(lv), FadeIn(lm))
        self.play(xc.animate.set_value(L - 0.01), run_time=6, rate_func=linear)
        n = T(r"$M$ \textbf{continu},\\$V$ \textbf{saute}\\sous la force", color=YELLOW,
              font_size=FS_TEXTE - 4).move_to([5.4, -3.2, 0])
        self.play(Write(n))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. Console : on garde la partie droite
# ---------------------------------------------------------------------------
class CoupureConsole(EIScene):
    def construct(self):
        titre = self.titre(r"Méthode de la coupure : console encastrée")
        self.play(Write(titre))
        L = 4
        self.repere(L, largeur=7.5, xc=-1.4)
        barre = poutre(self.X(0), self.X(L))
        enc = self.liaison("encastrement", 0)
        pts = VGroup(self.point(0, "A", UR), self.point(L, "B", UL))
        P = self.charge(L, r"P = 5~\mathrm{kN}", h=1.3)
        H = self.charge_vec(L, 1.1 * RIGHT, r"H = 3~\mathrm{kN}", cote_lab=UP)
        H.shift(1.1 * RIGHT)
        H[1].next_to(H[0], DOWN, buff=0.1)
        c = self.cote_x(0, L, r"4~\mathrm{m}", dy=-0.95)
        self.play(FadeIn(enc), Create(barre), FadeIn(pts), FadeIn(c), GrowArrow(P[0]), Write(P[1]),
                  GrowArrow(H[0]), Write(H[1]))
        self.ecrire(T(r"Un seul tronçon ($A \to B$). Astuce : on garde la partie \textbf{droite}\\"
                      r"$\Rightarrow$ pas besoin de calculer les actions de l'encastrement !"))
        self.etape()

        xg = 1.6
        self.play(FadeOut(c))
        cut = self.coupure(xg)
        lG = MathTex("G", color=YELLOW, font_size=FS_EQ).next_to(cut.get_top(), RIGHT, buff=0.12)
        g, d = poutre(self.X(0), self.X(xg)), poutre(self.X(xg), self.X(L))
        self.remove(barre)
        self.add(g, d)
        cx = self.cote_x(0, xg, "x", dy=-1.0)
        cd = self.cote_x(xg, L, "4 - x", dy=-1.0)
        self.play(Create(cut), Write(lG), FadeIn(cx))
        self.play(VGroup(g, enc, pts[0]).animate.set_opacity(0.12), FadeIn(cd))
        efd = self.efforts(xg, cote="droite")
        self.play(*[GrowArrow(e[0]) if isinstance(e[0], Arrow) else Create(e[0]) for e in efd],
                  *[Write(e[1]) for e in efd])
        self.etape()

        self.effacer_calculs()
        self.play(Indicate(VGroup(efd[0], H), color=YELLOW))
        self.ecrire(MathTex(r"\sum F_X = -N(x) + 3 = 0 \ \Rightarrow\ N(x) = +3~\mathrm{kN}", font_size=self.FS_CALC))
        self.ecrire(T(r"$N > 0$ : la poutre est \textbf{tendue} (traction), logique : $H$ tire sur $B$.",
                      color=C_LEVIER, font_size=FS_TEXTE - 4))
        self.play(Indicate(VGroup(efd[1], P), color=YELLOW))
        self.ecrire(MathTex(r"\sum F_Y = -V(x) - 5 = 0 \ \Rightarrow\ V(x) = -5~\mathrm{kN}", font_size=self.FS_CALC))
        eq = self.equation(r"\sum M_{/G} =", r"-M(x)", r"-(4-x)\times5", r"+0", r"=0")
        self.terme(efd[2], xg, xg, 0, eq[1])
        self.terme(P, xg, L, -1, eq[2], d="4-x")
        self.terme(H, xg, L, 0, eq[3], nul=True, dir_la=RIGHT)
        self.play(Write(eq[4]))
        self.resultat(r"M(x) = -5\,(4 - x) = 5x - 20")
        self.etape()

        # diagrammes N, V, M
        self.effacer_calculs()
        self.play(*map(FadeOut, [efd, cut, lG, cx, cd]))
        self.remove(g, d)
        self.add(barre)
        self.play(VGroup(g, enc, pts[0]).animate.set_opacity(1))
        yN, eN, yV, eV, yM, eM = -0.75, 0.12, -1.85, 0.1, -2.85, 0.045
        dN = self.diagramme([(0, L, lambda x: 3)], yN, eN, r"N", C_FX)
        dV = self.diagramme([(0, L, lambda x: -5)], yV, eV, r"V", C_FY)
        dM = self.diagramme([(0, L, lambda x: 5 * x - 20)], yM, eM, r"M", C_INT)
        for dg, tex, xv, val, dirv in [(dN, "+3", 2, 3, UP), (dV, "-5", 2, -5, DOWN), (dM, r"-20", 0, -20, RIGHT)]:
            self.play(Create(dg[0]), Write(dg[3]))
            y0, ech = {id(dN): (yN, eN), id(dV): (yV, eV), id(dM): (yM, eM)}[id(dg)]
            self.play(Create(dg[2]), FadeIn(dg[1]), Write(self.valeur_diag(xv, val, y0, ech, tex, dirv)))
        P2 = Panneau(2.8, -0.6, gap=0.25)
        for t, cl in [(r"$N = 3$ kN : traction", C_FX),
                      (r"$V = -5$ kN : constant", C_FY),
                      (r"$|M|$ max à l'encastrement :\\$M(0) = -20$ kN$\cdot$m", C_INT),
                      (r"Vérif. : $C_A = +20$ kN$\cdot$m\\$= -M(0)$ \checkmark", C_POS)]:
            m = P2.placer(T(t, color=cl, font_size=FS_TEXTE - 4))
            self.play(Write(m))
        self.etape(2)


# ---------------------------------------------------------------------------
# 5. L'astuce et les pièges
# ---------------------------------------------------------------------------
class CoupureAstuce(Base):
    def construct(self):
        titre = self.titre(r"Méthode de la coupure : astuce et pièges")
        self.play(Write(titre))
        r1 = T(r"En gardant la partie \textbf{gauche} :\quad effort ($N$, $V$ ou $M$) $=$ "
               r"$\boldsymbol{-}$\,[actions extérieures à \textbf{gauche}]")
        r2 = T(r"En gardant la partie \textbf{droite} :\quad effort ($N$, $V$ ou $M$) $=$ "
               r"$\boldsymbol{+}$\,[actions extérieures à \textbf{droite}]")
        regle = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(titre, DOWN, buff=0.5)
        boite = SurroundingRectangle(regle, color=YELLOW, buff=0.2)
        self.play(Write(r1))
        self.play(Write(r2), Create(boite))
        rq = T(r"(forces comptées $+$ vers le haut / la droite, moments $+$ dans le sens $\curvearrowleft$, calculés en $G$)",
               font_size=FS_TEXTE - 6, color=GREY_B).next_to(boite, DOWN, buff=0.15)
        self.play(Write(rq))
        self.etape()

        ex = VGroup(
            T(r"Exemple : tronçon $T_2$ de la poutre à 2 tronçons ($Y_A = 2$, $F = 6$, $Y_B = 4$ kN)", color=BLUE_B),
            MathTex(r"V = -[\,Y_A - F\,] = -(2 - 6) = 4~\mathrm{kN} \qquad V = +[\,Y_B\,] = 4~\mathrm{kN}",
                    font_size=FS_EQ - 4),
            MathTex(r"M = -[\,-(4+x)\,Y_A + x\,F\,] = 8 - 4x \qquad M = +[\,(2-x)\,Y_B\,] = 8 - 4x",
                    font_size=FS_EQ - 4),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(rq, DOWN, buff=0.5)
        for m in ex:
            self.play(Write(m))
        self.etape()

        self.play(*map(FadeOut, [r1, r2, boite, rq, ex]))
        items = [
            r"Découper en \textbf{tronçons} : force ponctuelle, appui, couple, début/fin de charge répartie.",
            r"$x$ est mesuré depuis le \textbf{début du tronçon} (partie droite : longueur $\ell - x$).",
            r"Charge répartie : seulement la partie \textbf{isolée} ($q\,x$ à $x/2$ de la coupure).",
            r"Dessiner $N$, $V$, $M$ \textbf{positifs} ($-N$, $-V$, $-M$ côté droit).",
            r"$\sum M$ au \textbf{point de coupure} : $N$ et $V$ n'y ont pas de moment.",
            r"Garder le côté \textbf{le plus simple} (console : côté libre, sans réactions).",
            r"Vérifier : $M$ continu, $V$ saute de $F$ sous une force, $M'(x) = -V(x)$.",
            r"Vérifier : $M = 0$ aux extrémités libres en rotation (appui, articulation, bout libre).",
        ]
        lignes = VGroup(*[
            VGroup(MathTex(r"\checkmark", color=C_POS, font_size=FS_TEXTE), T(t, font_size=FS_TEXTE - 2))
            .arrange(RIGHT, buff=0.2) for t in items
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(titre, DOWN, buff=0.45)
        if lignes.width > 13.4:
            lignes.scale_to_fit_width(13.4)
        lignes.set_x(0)
        for l in lignes:
            self.play(FadeIn(l, shift=0.2 * RIGHT), run_time=0.6)
            self.wait(0.4)
        self.etape(2)
