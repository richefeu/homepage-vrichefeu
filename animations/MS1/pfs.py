"""
MS1 - Animations pédagogiques : Principe Fondamental de la Statique (PFS)

Scènes :
    PFSPatate     pourquoi ΣF = 0 ET ΣM = 0 : une force, deux forces, un couple,
                  trois forces concourantes, énoncé du PFS
    PFSPoutreL    application sur une structure en L (articulation + appui) :
                  isoler, inconnues, ΣM_A, ΣF_X, ΣF_Y, vérification avec ΣM_B

Vidéo  : manim -qh pfs.py PFSPatate PFSPoutreL
Slides : manim-slides render -qh pfs.py PFSPatate PFSPoutreL
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403


# ---------------------------------------------------------------------------
# 1. Le PFS sur une « patate »
# ---------------------------------------------------------------------------
class PFSPatate(Base):
    C = np.array([-3.1, -0.5, 0.0])   # centre de la patate
    AX = 1.3                           # étirement horizontal

    def rayon(self, t):
        return 1.55 + 0.22 * np.sin(2 * t) + 0.12 * np.cos(3 * t)

    def bord(self, phi):
        """Point du contour dans la direction phi (radians) depuis le centre."""
        t = np.arctan2(self.AX * np.sin(phi), np.cos(phi))
        r = self.rayon(t)
        return self.C + r * np.array([self.AX * np.cos(t), np.sin(t), 0])

    def patate(self):
        ts = np.linspace(0, TAU, 60, endpoint=False)
        pts = [self.C + self.rayon(t) * np.array([self.AX * np.cos(t), np.sin(t), 0]) for t in ts]
        m = VMobject().set_points_smoothly(pts + [pts[0]])
        m.set_stroke(BLUE_B, width=4).set_fill(BLUE_E, opacity=0.6)
        return m

    def poussee(self, phi, F, nom=r"\vec F"):
        """Force qui pousse sur le bord (pointe sur le contour), direction F."""
        p = self.bord(phi)
        F = np.array([F[0], F[1], 0.0])
        a = force(p - F, p)
        lab = MathTex(nom, color=C_FORCE, font_size=FS_EQ).next_to(a.get_start(), UP, buff=0.1)
        return VGroup(a, lab)

    def construct(self):
        titre = self.titre(r"Principe Fondamental de la Statique (PFS)")
        self.play(Write(titre))

        pat = self.patate()
        nom = T(r"un solide quelconque\\(une « patate »)", color=BLUE_B).next_to(pat, DOWN, buff=0.3)
        self.play(DrawBorderThenFill(pat), FadeIn(nom))
        P = Panneau(1.2, 2.4)
        q = P.placer(T(r"\textbf{Question :} à quelles conditions\\un solide reste-t-il immobile ?"))
        self.play(Write(q))
        self.etape()

        # --- 1. une seule force
        self.play(FadeOut(nom))
        f1 = self.poussee(PI, (1.6, 0))
        self.play(GrowArrow(f1[0]), Write(f1[1]))
        t1 = P.placer(T(r"\textbf{1.} Une seule force : le solide part\\en translation."))
        grp = VGroup(pat, f1)
        grp.save_state()
        self.play(grp.animate.shift(2.2 * RIGHT), rate_func=rate_functions.ease_in_quad, run_time=1.5)
        self.play(Write(t1))
        r1 = P.placer(MathTex(r"\Rightarrow\ \text{il faut } \sum \vec F = \vec 0", font_size=FS_EQ,
                              color=YELLOW))
        self.play(Write(r1))
        self.play(Restore(grp))
        self.etape()

        # --- 2. deux forces opposées, alignées
        f2 = self.poussee(0, (-1.6, 0), nom=r"-\vec F")
        la = ligne_action(self.C, RIGHT, longueur=4.2)
        t2 = P.placer(T(r"\textbf{2.} Deux forces opposées, \textbf{alignées} :\\"
                        r"$\sum \vec F = \vec 0$, rien ne bouge."))
        self.play(GrowArrow(f2[0]), Write(f2[1]))
        self.play(Create(la))
        self.play(Wiggle(VGroup(pat, f1, f2), scale_value=1.02, rotation_angle=0.005 * TAU))
        self.play(Write(t2))
        self.etape()

        # --- 3. deux forces opposées, non alignées : un couple
        phiG, phiD = 155 * DEGREES, -25 * DEGREES
        g3 = self.poussee(phiG, (1.6, 0))
        d3 = self.poussee(phiD, (-1.6, 0), nom=r"-\vec F")
        self.play(FadeOut(la), ReplacementTransform(f1, g3), ReplacementTransform(f2, d3))
        yG, yD = self.bord(phiG)[1], self.bord(phiD)[1]
        laG = ligne_action(self.bord(phiG), RIGHT, longueur=4.5)
        laD = ligne_action(self.bord(phiD), RIGHT, longueur=4.5)
        xc = self.C[0] - 2.9
        dd = cote([xc, yD, 0], [xc, yG, 0], r"d", LEFT)
        self.play(Create(laG), Create(laD), FadeIn(dd))
        t3 = P.placer(T(r"\textbf{3.} Opposées mais \textbf{décalées} :\\"
                        r"$\sum \vec F = \vec 0$... et pourtant ça tourne !"))
        self.play(Write(t3))
        grp = VGroup(pat, g3, d3)
        grp.save_state()
        self.play(FadeOut(laG), FadeOut(laD), FadeOut(dd))
        self.play(Rotate(grp, -50 * DEGREES, about_point=self.C),
                  rate_func=rate_functions.ease_in_quad, run_time=1.8)
        r3 = P.placer(MathTex(r"\Rightarrow\ \text{il faut aussi } \sum M = 0", font_size=FS_EQ,
                              color=YELLOW))
        self.play(Write(r3))
        self.play(Restore(grp))
        self.etape()

        # --- 4. trois forces concourantes
        self.play(*map(FadeOut, [g3, d3, t1, r1, t2, t3, r3]))
        P.reset()
        P.placer(q)
        K = self.C + np.array([0.3, 0.2, 0])
        vecs = [0.8 * np.array(v) for v in [(1.7, 0.7, 0), (-1.3, 1.3, 0), (-0.4, -2.0, 0)]]
        noms = [r"\vec F_1", r"\vec F_2", r"\vec F_3"]
        couls = [RED, BLUE_C, GREEN_C]
        fs = VGroup()
        las = VGroup()
        for v, n, c in zip(vecs, noms, couls):
            u = v / np.linalg.norm(v)
            # point d'application : sur la ligne d'action passant par K, près du bord
            p = K + 1.0 * u
            a = force(p, p + v, couleur=c)
            lab = MathTex(n, color=c, font_size=FS_EQ).next_to(a.get_end(), u, buff=0.1)
            fs.add(VGroup(a, lab))
            las.add(ligne_action(p, u, longueur=3.3))
        t4 = P.placer(T(r"\textbf{4.} Trois forces bien choisies :\\le solide reste immobile."))
        self.play(*[GrowArrow(f[0]) for f in fs], *[Write(f[1]) for f in fs])
        self.play(Write(t4))
        self.etape()

        # somme vectorielle : on met les flèches bout à bout
        t5 = P.placer(T(r"Bout à bout, les forces forment\\un triangle fermé : $\sum \vec F = \vec 0$"))
        o = np.array([2.6, -2.6, 0])
        cop = VGroup()
        pos = o.copy()
        for f, v, c in zip(fs, vecs, couls):
            cop.add(force(pos, pos + 0.9 * v, couleur=c))
            pos = pos + 0.9 * v
        self.play(Write(t5))
        for f, a in zip(fs, cop):
            self.play(TransformFromCopy(f[0], a), run_time=1)
        self.etape()

        dotK = Dot(K, color=YELLOW)
        labK = MathTex("K", color=YELLOW, font_size=FS_EQ).next_to(K, DL, buff=0.1)
        t6 = P.placer(T(r"Les lignes d'action se coupent en $K$ :\\$\sum M_{/K} = 0$"))
        self.play(Create(las), FadeIn(dotK), Write(labK))
        self.play(Write(t6))
        self.etape()

        # --- énoncé
        self.tout_effacer(garder=[titre])
        P = Panneau(-6.2, 2.3, gap=0.35)
        e0 = P.placer(T(r"Un solide est en \textbf{équilibre statique} si :"))
        e1 = P.placer(T(r"\textbf{Résultante statique :}\quad"
                        r"$\displaystyle\sum \vec F_i = \vec 0 \;\Longrightarrow\; "
                        r"\sum F_{X,i} = 0 \ \text{ et } \ \sum F_{Y,i} = 0$"))
        e2 = P.placer(T(r"\textbf{Moment statique} en un point $A$ \textbf{quelconque} :\quad"
                        r"$\displaystyle\sum M_{/A}(\vec F_i) + \sum C_j = 0$"))
        boite = SurroundingRectangle(VGroup(e1, e2), color=YELLOW, buff=0.25)
        e3 = P.placer(T(r"En 2D : \textbf{3 équations} $\Rightarrow$ au plus 3 inconnues.",
                        color=BLUE_B), gap=0.25)
        e3.shift(0.3 * DOWN)
        e4 = P.placer(T(r"Astuce : écrire $\sum M$ au point où passent \textbf{le plus d'inconnues}\\"
                        r"(leur moment y est nul $\Rightarrow$ moins de calculs)."))
        e4.shift(0.3 * DOWN)
        self.play(Write(e0))
        self.play(Write(e1))
        self.play(Write(e2), Create(boite))
        self.etape()
        self.play(Write(e3))
        self.play(Write(e4))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Le PFS sur une structure en L
# ---------------------------------------------------------------------------
class PFSPoutreL(Base):
    def construct(self):
        titre = self.titre(r"Application du PFS : structure en L")
        self.play(Write(titre))

        G = Grille(0, 4, 0, 3, origine=(-5.2, -1.5), s=0.85)
        A, D, B, C = G.p(0, 0), G.p(2, 0), G.p(4, 0), G.p(4, 3)
        str_L = poutre(A, B, C)
        artA = symbole_articulation(A, s=0.5)
        appB = symbole_appui(B, s=0.5)
        pts = VGroup(*[croix(p) for p in (A, D, B, C)])
        labs = VGroup(MathTex("A", font_size=FS_EQ).next_to(A, UR, buff=0.12),
                      MathTex("D", font_size=FS_EQ).next_to(D, DOWN, buff=0.15),
                      MathTex("B", font_size=FS_EQ).next_to(B, DR, buff=0.12),
                      MathTex("C", font_size=FS_EQ).next_to(C, UL, buff=0.12))
        fP = force(D + 1.2 * UP, D)
        lP = MathTex(r"P = 4~\mathrm{kN}", color=C_FORCE, font_size=FS_TEXTE).next_to(fP, UP, buff=0.1)
        fF = force(C, C + 1.2 * RIGHT)
        lF = MathTex(r"F = 2~\mathrm{kN}", color=C_FORCE, font_size=FS_TEXTE).next_to(fF, DOWN, buff=0.1).shift(0.25 * RIGHT)
        fQ = force(C + 0.9 * UP, C)
        lQ = MathTex(r"Q = 1~\mathrm{kN}", color=C_FORCE, font_size=FS_TEXTE).next_to(fQ, UP, buff=0.1)
        charges = VGroup(VGroup(fP, lP), VGroup(fF, lF), VGroup(fQ, lQ))
        c_AD = cote(G.p(0, -1.0), G.p(2, -1.0), r"2~\mathrm{m}", DOWN, fs=FS_TEXTE)
        c_DB = cote(G.p(2, -1.0), G.p(4, -1.0), r"2~\mathrm{m}", DOWN, fs=FS_TEXTE)
        c_BC = cote(G.p(4.6, 0), G.p(4.6, 3), r"3~\mathrm{m}", RIGHT, fs=FS_TEXTE)
        cotes = VGroup(c_AD, c_DB, c_BC)

        self.play(Create(str_L), FadeIn(artA), FadeIn(appB))
        self.play(FadeIn(pts), FadeIn(labs), FadeIn(cotes))
        self.play(*[GrowArrow(c[0]) for c in charges], *[Write(c[1]) for c in charges])
        P = Panneau(0.0, 2.4, gap=0.22)
        q = P.placer(T(r"Articulation en $A$, appui simple en $B$.\\"
                       r"Déterminer les actions de liaison."))
        self.play(Write(q))
        self.etape()

        # --- 1. isoler, remplacer les liaisons par des forces inconnues
        contour = poutre(A, B, C, couleur=RED, epaisseur=16).set_stroke(opacity=0.6)
        e1 = P.placer(T(r"\textbf{1.} On \textbf{isole} la structure :\\"
                        r"les liaisons $\to$ forces inconnues."))
        self.play(Write(e1), Create(contour))
        fXA = force(A + 1.1 * LEFT, A, couleur=C_REACTION)
        fYA = force(A + 1.1 * DOWN, A, couleur=C_REACTION)
        fYB = force(B + 1.1 * DOWN, B, couleur=C_REACTION)
        lXA = MathTex("X_A", color=C_REACTION, font_size=FS_EQ).next_to(fXA.get_start(), UP, buff=0.1)
        lYA = MathTex("Y_A", color=C_REACTION, font_size=FS_EQ).next_to(fYA.get_start(), RIGHT, buff=0.1)
        lYB = MathTex("Y_B", color=C_REACTION, font_size=FS_EQ).next_to(fYB.get_start(), LEFT, buff=0.1)
        reac = VGroup(VGroup(fXA, lXA), VGroup(fYA, lYA), VGroup(fYB, lYB))
        self.play(FadeOut(artA), FadeOut(appB), FadeOut(contour), FadeOut(c_AD), FadeOut(c_DB))
        self.play(*[GrowArrow(r[0]) for r in reac], *[Write(r[1]) for r in reac])
        e2 = P.placer(T(r"3 inconnues (dessinées \textbf{positives}),\\3 équations : on peut résoudre !",
                        color=BLUE_B))
        self.play(Write(e2))
        self.etape()

        # --- 2. ΣM_A = 0
        self.play(FadeOut(q), FadeOut(e1), FadeOut(e2))
        P.reset()
        e3 = P.placer(T(r"\textbf{2.} $\sum M_{/A} = 0$ : en $A$ passent 2 inconnues."))
        self.play(Write(e3))
        eqA = MathTex(r"\sum M_{/A} =", r"0", r"+0", r"-2\times4", r"-3\times2", r"-4\times1",
                      r"+4\,Y_B", r"=0", font_size=FS_EQ - 8)
        P.placer(eqA)
        self.play(Write(eqA[0]))
        # X_A et Y_A : passent par A
        self.play(Indicate(reac[0], color=YELLOW), Indicate(reac[1], color=YELLOW))
        self.play(Write(eqA[1]), Write(eqA[2]))
        # P : d = 2
        self.terme(fP, A, -1, [cote(G.p(0, -1.6), G.p(2, -1.6), "2", DOWN, fs=FS_TEXTE)],
                   eqA[3], [ligne_action(D, UP, longueur=2)])
        # F : d = 3 (hauteur), et pas AC !
        dAC = DashedLine(A, C, color=GREY_B)
        lAC = MathTex(r"AC = 5~\mathrm{m}", color=GREY_B, font_size=FS_TEXTE - 4).rotate(np.arctan2(3, 4)).move_to(G.p(3.0, 1.75))
        self.terme(fF, A, -1, [cote(G.p(0.8, 0), G.p(0.8, 3), "3", LEFT, fs=FS_TEXTE), dAC, lAC],
                   eqA[4], [ligne_action(C, RIGHT, longueur=4.6)],
                   remarque=T(r"bras de levier = la \textbf{hauteur} 3 m, pas $AC$ !", color=C_LEVIER,
                              font_size=FS_TEXTE - 4).next_to(eqA, DOWN, buff=0.15, aligned_edge=LEFT))
        # Q : d = 4
        self.terme(fQ, A, -1, [cote(G.p(0, -1.6), G.p(4, -1.6), "4", DOWN, fs=FS_TEXTE)],
                   eqA[5], [ligne_action(C, UP, longueur=3.6)])
        # Y_B : d = 4
        self.terme(fYB, A, +1, [cote(G.p(0, -1.6), G.p(4, -1.6), "4", DOWN, fs=FS_TEXTE)],
                   eqA[6], [])
        self.play(Write(eqA[7]))
        rA = P.placer(MathTex(r"\Rightarrow\ Y_B = \frac{8+6+4}{4} = 4{,}5~\mathrm{kN}", font_size=FS_EQ))
        bA = SurroundingRectangle(rA[0][1:], color=YELLOW, buff=0.1)
        self.play(Write(rA), Create(bA))
        self.etape()

        # --- 3. ΣF_X = 0 et ΣF_Y = 0
        e4 = P.placer(T(r"\textbf{3.} Résultante statique :"))
        eX = P.placer(MathTex(r"\sum F_X = X_A + 2 = 0 \ \Rightarrow\ X_A = -2~\mathrm{kN}",
                              font_size=FS_EQ - 6))
        self.play(Write(e4))
        self.play(Indicate(reac[0], color=YELLOW), Indicate(VGroup(fF, lF), color=YELLOW))
        self.play(Write(eX))
        nX = P.placer(T(r"négatif : $\vec X_A$ est en réalité vers la \textbf{gauche}",
                        font_size=FS_TEXTE - 4, color=C_NEG), gap=0.15)
        vrai = force(A, A + 1.1 * LEFT, couleur=C_NEG).shift(0.25 * DOWN)
        self.play(Write(nX), TransformFromCopy(fXA, vrai))
        eY = P.placer(MathTex(r"\sum F_Y = Y_A - 4 - 1 + 4{,}5 = 0 \ \Rightarrow\ Y_A = 0{,}5~\mathrm{kN}",
                              font_size=FS_EQ - 6))
        self.play(FadeOut(vrai), Indicate(VGroup(reac[1], reac[2]), color=YELLOW),
                  Indicate(VGroup(fP, lP, fQ, lQ), color=YELLOW))
        self.play(Write(eY))
        self.etape()

        # --- 4. vérification : ΣM_B = 0
        self.play(*map(FadeOut, [e3, eqA, rA, bA, e4, eX, nX, eY]))
        P.reset()
        e5 = P.placer(T(r"\textbf{4.} Vérification : $\sum M_{/B} = 0$ ?"))
        self.play(Write(e5))
        e6 = P.placer(T(r"$Q$, $X_A$ et $Y_B$ ont une ligne d'action\\qui passe par $B$ : moment \textbf{nul} !",
                        color=C_LEVIER))
        lQB = DashedLine(C + 1.3 * UP, B + 1.4 * DOWN, color=C_LEVIER, stroke_width=3)
        lXB = DashedLine(A + 1.6 * LEFT, B + 1.0 * RIGHT, color=C_LEVIER, stroke_width=3)
        self.play(Create(lQB), Create(lXB), FadeIn(Dot(B, color=YELLOW)))
        self.play(Write(e6))
        eqB = P.placer(MathTex(r"\sum M_{/B} = +2\times4 - 3\times2 - 4\times0{,}5 + 0",
                               font_size=FS_EQ - 4))
        eqB2 = P.placer(MathTex(r"= 8 - 6 - 2 = 0 \quad \checkmark", font_size=FS_EQ, color=C_POS))
        eqB2.shift(1.6 * RIGHT)
        self.play(Write(eqB))
        self.play(Write(eqB2))
        self.etape(2)

    def terme(self, fl, pt, signe, cotes, terme, lignes, remarque=None):
        """Met en évidence une force, sa ligne d'action, son bras de levier et le signe."""
        fl.save_state()
        self.play(fl.animate.set_color(YELLOW), run_time=0.4)
        if lignes:
            self.play(*map(Create, lignes), run_time=0.8)
        sens = fleche_sens(pt, signe, r=0.4)
        self.play(*map(FadeIn, cotes), Create(sens), run_time=0.9)
        if remarque is not None:
            self.play(Write(remarque))
        self.play(Write(terme))
        self.next_slide()
        out = [*cotes, sens, *lignes] + ([remarque] if remarque is not None else [])
        self.play(*map(FadeOut, out), Restore(fl), run_time=0.5)
