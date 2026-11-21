"""
MS1 - Animations pédagogiques : les 3 liaisons planes

Scènes :
    AppuiSimple     rotation et 1 translation libres -> 1 inconnue (cas incliné à 45°)
    Articulation    rotation libre, translations bloquées -> 2 inconnues X, Y
    Encastrement    tout est bloqué -> 3 inconnues X, Y, C
    LiaisonsBilan   tableau récapitulatif

Vidéo  : manim -qh liaisons.py AppuiSimple Articulation Encastrement LiaisonsBilan
Slides : manim-slides render -qh liaisons.py AppuiSimple Articulation Encastrement LiaisonsBilan
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403

class LiaisonBase(Base):
    def mouvement(self, P, texte, libre):
        ligne = VGroup(T(texte), ok_ko(libre)).arrange(RIGHT, buff=0.3)
        P.placer(ligne)
        self.play(Write(ligne[0]))
        self.play(FadeIn(ligne[1], scale=1.6))
        return ligne

    def secousse(self, mob, direction, amplitude=0.08, fois=2):
        """Mouvement bloqué : la poutre « essaie » de bouger et revient."""
        for _ in range(fois):
            self.play(mob.animate.shift(amplitude * direction), rate_func=there_and_back, run_time=0.35)

    def essai_rotation(self, mob, centre, angle, run_time=1.8):
        self.play(Rotate(mob, angle, about_point=centre), rate_func=there_and_back, run_time=run_time)


# ---------------------------------------------------------------------------
# 1. L'appui simple
# ---------------------------------------------------------------------------
class AppuiSimple(LiaisonBase):
    def construct(self):
        titre = self.titre(r"L'appui simple")
        self.play(Write(titre))

        S = np.array([-2.0, -0.2, 0])
        barre = poutre(S + 4.3 * LEFT, S)
        app = symbole_appui(S, s=0.7)
        labB = MathTex("B", font_size=FS_EQ).next_to(S, UR, buff=0.12)
        self.play(Create(barre), FadeIn(app), Write(labB))
        P = Panneau(0.6, 2.3, gap=0.3)

        # mouvements
        self.mouvement(P, r"Translation \textbf{horizontale} : libre", True)
        mobile = VGroup(barre, app[0], labB)
        self.play(mobile.animate.shift(1.0 * LEFT), rate_func=there_and_back, run_time=2.2)
        self.mouvement(P, r"\textbf{Rotation} : libre", True)
        self.essai_rotation(VGroup(barre), S, -14 * DEGREES)
        self.etape(0.5)
        self.mouvement(P, r"Translation \textbf{verticale} : bloquée", False)
        self.secousse(mobile, DOWN)
        self.etape(0.5)

        # action de liaison
        e = P.placer(T(r"Le support s'oppose au mouvement bloqué\\par une \textbf{force verticale} :"),
                     gap=0.2)
        e.shift(0.2 * DOWN)
        self.play(Write(e))
        fY = force(S + 1.4 * DOWN, S, couleur=C_REACTION)
        lY = MathTex(r"Y_B", color=C_REACTION, font_size=FS_EQ).next_to(fY.get_start(), RIGHT, buff=0.12)
        self.play(FadeOut(app), GrowArrow(fY), Write(lY))
        inc = P.placer(T(r"\textbf{1 inconnue} : l'intensité $Y_B$", color=YELLOW))
        inc.shift(0.2 * DOWN)
        self.play(Write(inc), Circumscribe(inc, color=YELLOW))
        self.etape()

        # appui incliné
        self.tout_effacer(garder=[titre])
        A, B = np.array([-5.6, 0.0, 0]), np.array([-1.6, 0.0, 0])
        barre = poutre(A, B)
        appA = symbole_appui(A, angle=-45, s=0.6)
        appB = symbole_appui(B, s=0.6)
        lA = MathTex("A", font_size=FS_EQ).next_to(A, UL, buff=0.12)
        lB = MathTex("B", font_size=FS_EQ).next_to(B, UR, buff=0.12)
        self.play(Create(barre), FadeIn(appA), FadeIn(appB), Write(lA), Write(lB))
        P = Panneau(-0.1, 2.3, gap=0.3)
        e1 = P.placer(T(r"Un appui peut être \textbf{incliné} (ici à $45^\circ$)."))
        self.play(Write(e1))
        self.etape()
        n = np.array([1, 1, 0]) / np.sqrt(2)
        normale = DashedLine(A - 1.6 * n, A + 0.9 * n, color=C_LEVIER)
        e2 = P.placer(T(r"La force est \textbf{perpendiculaire}\\au plan de roulement :"))
        self.play(Create(normale), Write(e2))
        fA = force(A - 1.5 * n, A, couleur=C_REACTION)
        fB = force(B + 1.3 * DOWN, B, couleur=C_REACTION)
        lfA = MathTex(r"\vec R_A", color=C_REACTION, font_size=FS_EQ).next_to(fA.get_start(), DOWN, buff=0.1)
        lfB = MathTex(r"\vec R_B", color=C_REACTION, font_size=FS_EQ).next_to(fB.get_start(), RIGHT, buff=0.1)
        self.play(FadeOut(appA), FadeOut(appB), GrowArrow(fA), GrowArrow(fB), Write(lfA), Write(lfB))
        eqA = P.placer(MathTex(r"\vec R_A = \begin{pmatrix} R_A\cos 45^\circ \\ R_A \sin 45^\circ \end{pmatrix}"
                               r"\qquad \vec R_B = \begin{pmatrix} 0 \\ Y_B \end{pmatrix}", font_size=FS_EQ))
        self.play(Write(eqA))
        e3 = P.placer(T(r"Direction connue $\Rightarrow$ \textbf{1 seule inconnue}\\par appui ($R_A$, $Y_B$).",
                        color=YELLOW))
        self.play(Write(e3))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. L'articulation
# ---------------------------------------------------------------------------
class Articulation(LiaisonBase):
    def construct(self):
        titre = self.titre(r"L'articulation")
        self.play(Write(titre))

        S = np.array([-2.0, -0.2, 0])
        barre = poutre(S + 4.3 * LEFT, S)
        art = symbole_articulation(S, s=0.7)
        labA = MathTex("A", font_size=FS_EQ).next_to(S, UR, buff=0.12)
        self.play(Create(barre), FadeIn(art), Write(labA))
        P = Panneau(0.6, 2.3, gap=0.3)

        self.mouvement(P, r"\textbf{Rotation} : libre", True)
        self.essai_rotation(VGroup(barre), S, -14 * DEGREES)
        self.essai_rotation(VGroup(barre), S, 10 * DEGREES, run_time=1.4)
        self.etape(0.5)
        self.mouvement(P, r"Translation \textbf{horizontale} : bloquée", False)
        self.secousse(VGroup(barre, labA), LEFT)
        self.mouvement(P, r"Translation \textbf{verticale} : bloquée", False)
        self.secousse(VGroup(barre, labA), DOWN)
        self.etape(0.5)

        e = P.placer(T(r"Une force de direction \textbf{inconnue},\\"
                       r"décomposée en 2 composantes :"), gap=0.2)
        e.shift(0.2 * DOWN)
        self.play(Write(e))
        v = np.array([1.2, 1.0, 0])
        fR = force(S - v, S, couleur=GREY_B)
        lR = MathTex(r"\vec R_A", color=GREY_B, font_size=FS_EQ).next_to(fR.get_start(), DL, buff=0.05)
        self.play(FadeOut(art), GrowArrow(fR), Write(lR))
        fX = force(S + 1.2 * LEFT, S, couleur=C_REACTION).shift(0.0 * UP)
        fY = force(S + 1.2 * DOWN, S, couleur=C_REACTION)
        lX = MathTex("X_A", color=C_REACTION, font_size=FS_EQ).next_to(fX, UP, buff=0.1).shift(0.3 * LEFT)
        lY = MathTex("Y_A", color=C_REACTION, font_size=FS_EQ).next_to(fY.get_start(), RIGHT, buff=0.12)
        self.play(TransformFromCopy(fR, fX), TransformFromCopy(fR, fY), Write(lX), Write(lY))
        self.play(FadeOut(fR), FadeOut(lR))
        inc = P.placer(T(r"\textbf{2 inconnues} : $X_A$ et $Y_A$", color=YELLOW))
        inc.shift(0.2 * DOWN)
        self.play(Write(inc), Circumscribe(inc, color=YELLOW))
        rq = P.placer(T(r"Inconnues dessinées \textbf{positives} (sens des axes) :\\"
                        r"le signe du résultat donnera le vrai sens.", font_size=FS_TEXTE - 4,
                        color=GREY_B))
        self.play(Write(rq))
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. L'encastrement
# ---------------------------------------------------------------------------
class Encastrement(LiaisonBase):
    def construct(self):
        titre = self.titre(r"L'encastrement")
        self.play(Write(titre))

        S = np.array([-4.9, -0.2, 0])
        barre = poutre(S, S + 4.3 * RIGHT)
        mur = symbole_encastrement(S, angle=-90, s=1.4)
        labA = MathTex("A", font_size=FS_EQ).next_to(S, UR, buff=0.12)
        self.play(FadeIn(mur), Create(barre), Write(labA))
        P = Panneau(0.6, 2.3, gap=0.3)

        self.mouvement(P, r"Translation \textbf{horizontale} : bloquée", False)
        self.secousse(VGroup(barre, labA), RIGHT)
        self.mouvement(P, r"Translation \textbf{verticale} : bloquée", False)
        self.secousse(VGroup(barre, labA), DOWN)
        self.mouvement(P, r"\textbf{Rotation} : bloquée", False)
        for _ in range(2):
            self.essai_rotation(VGroup(barre, labA), S, -3 * DEGREES, run_time=0.4)
        self.etape(0.5)

        e = P.placer(T(r"Le mur s'oppose à \textbf{tout} mouvement :\\"
                       r"une force (2 composantes) \textbf{et un couple}."), gap=0.2)
        e.shift(0.2 * DOWN)
        self.play(Write(e))
        fX = force(S + 1.2 * LEFT, S, couleur=C_REACTION)
        fY = force(S + 1.2 * DOWN, S, couleur=C_REACTION)
        lX = MathTex("X_A", color=C_REACTION, font_size=FS_EQ).next_to(fX.get_start(), LEFT, buff=0.1)
        lY = MathTex("Y_A", color=C_REACTION, font_size=FS_EQ).next_to(fY.get_start(), RIGHT, buff=0.12)
        cA = moment_inconnu(S, +1, r=0.85, nom="C_A")
        self.play(FadeOut(mur), GrowArrow(fX), GrowArrow(fY), Write(lX), Write(lY))
        self.play(Create(cA[0]), Write(cA[1]))
        inc = P.placer(T(r"\textbf{3 inconnues} : $X_A$, $Y_A$ et $C_A$", color=YELLOW))
        inc.shift(0.2 * DOWN)
        self.play(Write(inc), Circumscribe(inc, color=YELLOW))
        rq = P.placer(T(r"$C_A$ est dessiné dans le sens \textbf{positif} $\curvearrowleft$.",
                        font_size=FS_TEXTE - 4, color=GREY_B))
        self.play(Write(rq))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. Bilan
# ---------------------------------------------------------------------------
class LiaisonsBilan(LiaisonBase):
    def construct(self):
        titre = self.titre(r"Les 3 liaisons planes : bilan")
        self.play(Write(titre))

        xs = [-5.4, -2.3, 1.2, 4.9]
        y_entete = 2.3
        entetes = VGroup(*[T(r"\textbf{" + t + "}", color=BLUE_B).move_to([x, y_entete, 0])
                           for t, x in zip(["Liaison", "Symbole", "Mouvements bloqués", "Inconnues"], xs)])
        trait = Line([-7, y_entete - 0.4, 0], [7, y_entete - 0.4, 0], color=GREY_C)
        self.play(FadeIn(entetes), Create(trait))

        lignes = [
            ("Appui simple", symbole_appui, r"1 translation", r"1 : \ $Y$", 1.2),
            ("Articulation", symbole_articulation, r"2 translations", r"2 : \ $X,\ Y$", -0.4),
            ("Encastrement", symbole_encastrement, r"2 translations\\+ la rotation", r"3 : \ $X,\ Y,\ C$", -2.0),
        ]
        for nom, symb, bloque, inc, y in lignes:
            p = np.array([xs[1], y + (0.0 if symb is symbole_encastrement else 0.3), 0])
            if symb is symbole_encastrement:
                dessin = VGroup(symb(p + 0.7 * LEFT, angle=-90, s=1.0), poutre(p + 0.7 * LEFT, p + 0.9 * RIGHT))
            else:
                dessin = VGroup(symb(p, s=0.6), poutre(p + 0.9 * LEFT, p + 0.9 * RIGHT))
            cel = VGroup(
                T(r"\textbf{" + nom + "}").move_to([xs[0], y, 0]),
                dessin,
                T(bloque).move_to([xs[2], y, 0]),
                T(inc, color=YELLOW).move_to([xs[3], y, 0]),
            )
            self.play(FadeIn(cel[0]), FadeIn(cel[1]))
            self.play(Write(cel[2]))
            self.play(Write(cel[3]))
            self.etape(0.5)
        note = T(r"Mouvement libre $\Rightarrow$ action nulle (connue)\\"
                 r"Mouvement bloqué $\Rightarrow$ action inconnue",
                 font_size=FS_TEXTE - 2, color=GREY_B).to_edge(DOWN, buff=0.3)
        self.play(Write(note))
        self.etape(2)
