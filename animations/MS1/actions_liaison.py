"""
MS1 - Animations pédagogiques : calcul des actions de liaison (poutres isostatiques horizontales)

Scènes (une difficulté par scène) :
    ReactionsMethode               la méthode complète sur un cas simple (articulation + appui, 1 force)
    Isostatisme                    compter les inconnues : isostatique / hyperstatique / mécanisme
    ReactionsChargeRepartie        charge répartie partielle -> force équivalente q × longueur chargée
    ReactionsForceInclineeCouple   force inclinée (décomposition) + couple appliqué
    ReactionsConsole               encastrement : 3 inconnues dont un couple ; encastrement à droite (signe)
    ReactionsPorteAFaux            plongeoir du poly : réaction négative, effet de levier
    ReactionsAppuiIncline          appui incliné : 1 inconnue de direction connue, X_A ≠ 0
    ReactionsPieges                bilan : la check-list des pièges

Vidéo  : manim -qh actions_liaison.py ReactionsMethode Isostatisme ReactionsChargeRepartie \
             ReactionsForceInclineeCouple ReactionsConsole ReactionsPorteAFaux ReactionsAppuiIncline ReactionsPieges
Slides : manim-slides render -qh actions_liaison.py <scènes>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from outils_ms1 import *  # noqa: E402,F403


# ---------------------------------------------------------------------------
# 1. La méthode
# ---------------------------------------------------------------------------
class ReactionsMethode(PoutreScene):
    def construct(self):
        titre = self.titre(r"Actions de liaison : la méthode")
        self.play(Write(titre))

        plan = VGroup(*[T(t) for t in [
            r"\textbf{1.} \textbf{Isoler} la poutre : chaque liaison $\to$ ses inconnues (dessinées \textbf{positives})",
            r"\textbf{2.} Vérifier : 3 inconnues pour 3 équations (\textbf{isostatique})",
            r"\textbf{3.} $\sum M = 0$ au point où passent \textbf{le plus d'inconnues}",
            r"\textbf{4.} $\sum F_X = 0$ \ et \ $\sum F_Y = 0$",
            r"\textbf{5.} \textbf{Vérifier} avec $\sum M = 0$ en un autre point",
        ]]).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(0.3 * DOWN)
        for l in plan:
            self.play(FadeIn(l, shift=0.2 * RIGHT), run_time=0.7)
        self.etape()
        self.play(FadeOut(plan))

        self.repere(6)
        barre = poutre(self.X(0), self.X(6))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 6)
        pts = VGroup(self.point(0, "A", UL), self.point(2, "C", UR), self.point(6, "B", UR))
        P = self.charge(2, r"P = 12~\mathrm{kN}")
        cotes = VGroup(self.cote_x(0, 2, r"2~\mathrm{m}", dy=-0.95), self.cote_x(2, 6, r"4~\mathrm{m}", dy=-0.95))
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts))
        self.play(GrowArrow(P[0]), Write(P[1]), FadeIn(cotes))
        self.etape()

        # 1-2
        self.ecrire(T(r"\textbf{1.} On isole : articulation $\to X_A, Y_A$ \quad appui $\to Y_B$"))
        XA, YA = self.reaction("X", 0, "X_A"), self.reaction("Y", 0, "Y_A")
        YB = self.reaction("Y", 6, "Y_B")
        self.play(FadeOut(cotes))
        self.remplacer_liaisons([lA, lB], [XA, YA, YB])
        self.ecrire(T(r"\textbf{2.} 3 inconnues, 3 équations : isostatique \checkmark", color=C_POS))
        self.etape()

        # 3
        self.effacer_calculs()
        self.ecrire(T(r"\textbf{3.} $\sum M_{/A} = 0$ : $X_A$ et $Y_A$ passent par $A$ (moments nuls)"))
        eq = self.equation(r"\sum M_{/A} =", r"0", r"+0", r"-2\times12", r"+6\,Y_B", r"=0")
        self.terme(XA, 0, 0, 0, eq[1], nul=True, dir_la=RIGHT)
        self.terme(YA, 0, 0, 0, eq[2], nul=True, dir_la=UP)
        self.terme(P, 0, 2, -1, eq[3], d="2")
        self.terme(YB, 0, 6, +1, eq[4], d="6")
        self.play(Write(eq[5]))
        self.resultat(r"Y_B = \frac{24}{6} = 4~\mathrm{kN}")
        self.etape()

        # 4
        self.effacer_calculs()
        self.ecrire(T(r"\textbf{4.} Résultante statique :"))
        self.play(Indicate(XA, color=YELLOW))
        self.ecrire(MathTex(r"\sum F_X = X_A = 0 \ \Rightarrow\ X_A = 0", font_size=self.FS_CALC))
        self.play(Indicate(VGroup(YA, P, YB), color=YELLOW))
        self.ecrire(MathTex(r"\sum F_Y = Y_A - 12 + 4 = 0 \ \Rightarrow\ Y_A = 8~\mathrm{kN}", font_size=self.FS_CALC))
        self.etape()

        # 5
        self.effacer_calculs()
        self.ecrire(T(r"\textbf{5.} Vérification en $B$ :"))
        self.ecrire(MathTex(r"\sum M_{/B} = -6\times 8 + 4\times 12 + 0 + 0 = -48 + 48 = 0 \quad \checkmark",
                            font_size=self.FS_CALC, color=C_POS))
        self.etape()

        self.play(*self.valeur(XA, r"X_A = 0"), *self.valeur(YA, r"Y_A = 8~\mathrm{kN}"),
                  *self.valeur(YB, r"Y_B = 4~\mathrm{kN}"))
        self.ecrire(T(r"Bon sens : la charge est plus près de $A$ $\Rightarrow$ $Y_A > Y_B$ \checkmark",
                      color=YELLOW))
        self.etape(2)


# ---------------------------------------------------------------------------
# 2. Isostatique ?
# ---------------------------------------------------------------------------
class Isostatisme(Base):
    def construct(self):
        titre = self.titre(r"Avant de calculer : compter les inconnues")
        self.play(Write(titre))
        sous = T(r"En 2D, le PFS donne \textbf{3 équations} : il faut \textbf{3 inconnues} de liaison.",
                 color=BLUE_B).next_to(titre, DOWN, buff=0.3)
        self.play(Write(sous))

        xa, xb = -6.3, -2.9
        cas = [
            (["articulation", "appui"], r"$2 + 1 = 3$ inconnues : \textbf{isostatique} \checkmark", C_POS),
            (["encastrement", None], r"$3$ inconnues : \textbf{isostatique} \checkmark", C_POS),
            (["articulation", "articulation"], r"$2 + 2 = 4$ inconnues : \textbf{hyperstatique}\\"
                                               r"(le PFS ne suffit pas, hors MS1)", C_NEG),
            (["appui", "appui"], r"$1 + 1 = 2$ inconnues : \textbf{mécanisme}\\(la poutre peut bouger !)", RED),
        ]
        ys = [1.45, 0.05, -1.35, -2.75]
        dernier = None
        for (liaisons, texte, c), y in zip(cas, ys):
            A, B = np.array([xa, y, 0]), np.array([xb, y, 0])
            barre = poutre(A, B, epaisseur=8)
            symb = VGroup()
            for l, p in zip(liaisons, (A, B)):
                if l == "articulation":
                    symb.add(symbole_articulation(p, s=0.4))
                elif l == "appui":
                    symb.add(symbole_appui(p, s=0.4))
                elif l == "encastrement":
                    symb.add(symbole_encastrement(p, angle=-90, s=0.9))
            txt = T(texte, color=c).move_to([0, y - 0.1, 0], aligned_edge=LEFT).shift(1.6 * LEFT)
            self.play(Create(barre), FadeIn(symb))
            self.play(Write(txt))
            self.etape(0.5)
            dernier = (barre, symb, A, B)

        # le mécanisme : une force horizontale fait partir la poutre
        barre, symb, A, B = dernier
        F = force(A + 1.2 * LEFT + 0.0 * UP, A, couleur=C_FORCE)
        self.play(GrowArrow(F))
        mobile = VGroup(barre, F, symb[0][0], symb[1][0])
        self.play(mobile.animate.shift(1.0 * RIGHT), rate_func=rate_functions.ease_in_quad, run_time=1.6)
        self.etape(2)


# ---------------------------------------------------------------------------
# 3. Charge répartie
# ---------------------------------------------------------------------------
class ReactionsChargeRepartie(PoutreScene):
    def construct(self):
        titre = self.titre(r"Actions de liaison : charge répartie")
        self.play(Write(titre))
        self.repere(8)
        barre = poutre(self.X(0), self.X(8))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 8)
        pts = VGroup(self.point(0, "A", UL), self.point(2, "C", DOWN), self.point(8, "B", UR))
        q = self.repartie(2, 8, r"q = 2~\mathrm{kN/m}")
        cotes = VGroup(self.cote_x(0, 2, r"2~\mathrm{m}", dy=-0.95), self.cote_x(2, 8, r"6~\mathrm{m}", dy=-0.95))
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts))
        self.play(LaggedStart(*[GrowArrow(a) for a in q[0]], lag_ratio=0.05), Create(q[1]), Write(q[2]))
        self.play(FadeIn(cotes))
        self.ecrire(T(r"$q$ en kN/m : une force \textbf{par mètre} de poutre, sur la zone $CB$."))
        self.etape()

        # force équivalente
        self.ecrire(T(r"\textbf{Force équivalente} : intensité = $q\ \times$ \textbf{longueur chargée},"
                      r" placée au \textbf{milieu} de la zone chargée."))
        self.ecrire(MathTex(r"F_{eq} = q \times 6 = 2 \times 6 = 12~\mathrm{kN} \qquad x_{eq} = 2 + \frac{6}{2} = 5~\mathrm{m}",
                            font_size=self.FS_CALC))
        Feq = self.charge(5, r"F_{eq} = 12~\mathrm{kN}", h=1.3, couleur=YELLOW, cote_lab=RIGHT)
        self.play(q.animate.set_opacity(0.25), q[2].animate.set_opacity(0))
        self.play(TransformFromCopy(q[0], Feq[0]), Write(Feq[1]))
        ceq = self.cote_x(0, 5, r"5~\mathrm{m}", dy=-1.65)
        self.play(FadeIn(ceq))
        self.ecrire(T(r"\textbf{Piège :} la zone chargée fait 6 m (pas 8 m), son milieu est à 5 m de $A$ (pas 4 m).",
                      color=C_NEG))
        self.etape()

        # PFS
        self.effacer_calculs()
        self.play(FadeOut(cotes), FadeOut(ceq))
        XA, YA = self.reaction("X", 0, "X_A"), self.reaction("Y", 0, "Y_A")
        YB = self.reaction("Y", 8, "Y_B")
        self.remplacer_liaisons([lA, lB], [XA, YA, YB])
        self.ecrire(T(r"$\sum M_{/A} = 0$ avec la force équivalente :"))
        eq = self.equation(r"\sum M_{/A} =", r"0 + 0", r"-5\times12", r"+8\,Y_B", r"=0")
        self.play(Write(eq[1]))
        self.terme(Feq, 0, 5, -1, eq[2], d="5")
        self.terme(YB, 0, 8, +1, eq[3], d="8")
        self.play(Write(eq[4]))
        self.resultat(r"Y_B = \frac{60}{8} = 7{,}5~\mathrm{kN}")
        self.etape()
        self.effacer_calculs()
        self.ecrire(MathTex(r"\sum F_X = X_A = 0", font_size=self.FS_CALC))
        self.ecrire(MathTex(r"\sum F_Y = Y_A - 12 + 7{,}5 = 0 \ \Rightarrow\ Y_A = 4{,}5~\mathrm{kN}",
                            font_size=self.FS_CALC))
        self.ecrire(MathTex(r"\text{Vérif. : }\sum M_{/B} = -8\times4{,}5 + 3\times12 = -36 + 36 = 0 \quad\checkmark",
                            font_size=self.FS_CALC, color=C_POS))
        self.play(*self.valeur(XA, r"X_A = 0"), *self.valeur(YA, r"Y_A = 4{,}5~\mathrm{kN}"),
                  *self.valeur(YB, r"Y_B = 7{,}5~\mathrm{kN}"))
        self.ecrire(T(r"La force équivalente sert à écrire le PFS de la poutre entière (actions de liaison).",
                      color=GREY_B, font_size=FS_TEXTE - 4))
        self.etape(2)


# ---------------------------------------------------------------------------
# 4. Force inclinée et couple
# ---------------------------------------------------------------------------
class ReactionsForceInclineeCouple(PoutreScene):
    def construct(self):
        titre = self.titre(r"Actions de liaison : force inclinée et couple")
        self.play(Write(titre))
        self.repere(6)
        barre = poutre(self.X(0), self.X(6))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 6)
        pts = VGroup(self.point(0, "A", UL), self.point(2, "C", DL), self.point(4, "D", DOWN),
                     self.point(6, "B", UR))
        v = 1.7 * np.array([0.6, -0.8, 0])
        F = self.charge_vec(2, v, r"F = 10~\mathrm{kN}", cote_lab=LEFT)
        C = self.couple(4, -1, r"C = 8~\mathrm{kN\cdot m}")
        cotes = VGroup(self.cote_x(0, 2, r"2~\mathrm{m}", dy=-0.95), self.cote_x(2, 4, r"2~\mathrm{m}", dy=-0.95),
                       self.cote_x(4, 6, r"2~\mathrm{m}", dy=-0.95))
        # pente 3/4 dessinée à côté de la force
        o = F[0].get_start() + 0.25 * RIGHT + 0.05 * UP
        tri = VGroup(Line(o, o + 0.6 * RIGHT), Line(o + 0.6 * RIGHT, o + 0.6 * RIGHT + 0.8 * DOWN)).set_stroke(C_LEVIER, 3)
        l3 = MathTex("3", color=C_LEVIER, font_size=26).next_to(tri[0], UP, buff=0.05)
        l4 = MathTex("4", color=C_LEVIER, font_size=26).next_to(tri[1], RIGHT, buff=0.05)
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts), FadeIn(cotes))
        self.play(GrowArrow(F[0]), Write(F[1]), Create(tri), Write(l3), Write(l4))
        self.play(Create(C[0]), Write(C[1]))
        self.etape()

        # décomposition
        self.ecrire(T(r"\textbf{Force inclinée :} on la \textbf{décompose} (pente 3/4/5) :"))
        self.ecrire(MathTex(r"F_X = 10\times\frac{3}{5} = 6~\mathrm{kN}\ (\rightarrow) \qquad "
                            r"F_Y = 10\times\frac{4}{5} = 8~\mathrm{kN}\ (\downarrow)", font_size=self.FS_CALC))
        FX = self.charge_vec(2, 1.0 * RIGHT, r"F_X = 6~\mathrm{kN}", couleur=C_FX, cote_lab=UP)
        FX.shift(1.0 * RIGHT)  # flèche partant de C vers la droite
        FX[1].next_to(FX[0], DOWN, buff=0.1).shift(0.3 * RIGHT)
        FY = self.charge(2, r"F_Y = 8~\mathrm{kN}", h=1.3, couleur=C_FY)
        FY[1].next_to(FY[0], UP, buff=0.1).shift(0.5 * LEFT)
        self.play(FadeOut(tri), FadeOut(l3), FadeOut(l4), F.animate.set_opacity(0.2))
        self.play(GrowArrow(FX[0]), Write(FX[1]), GrowArrow(FY[0]), Write(FY[1]))
        self.play(FadeOut(F))
        self.etape()

        # PFS
        self.effacer_calculs()
        self.play(FadeOut(cotes))
        XA, YA = self.reaction("X", 0, "X_A"), self.reaction("Y", 0, "Y_A")
        YB = self.reaction("Y", 6, "Y_B")
        self.remplacer_liaisons([lA, lB], [XA, YA, YB])
        eq = self.equation(r"\sum M_{/A} =", r"0 + 0", r"+0", r"-2\times8", r"-8", r"+6\,Y_B", r"=0")
        self.play(Write(eq[1]))
        self.terme(FX, 0, 2, 0, eq[2], nul=True, dir_la=RIGHT,
                   rq=T(r"$F_X$ est sur l'axe de la poutre :\\sa ligne d'action passe par $A$ !",
                        color=C_LEVIER, font_size=FS_TEXTE - 2))
        self.terme(FY, 0, 2, -1, eq[3], d="2")
        self.terme(C, 0, 4, 0, eq[4],
                   rq=T(r"Un \textbf{couple} s'ajoute \textbf{tel quel}\\(avec son signe), quel que soit\\"
                        r"le point : pas de bras de levier.", color=C_LEVIER, font_size=FS_TEXTE - 2))
        self.terme(YB, 0, 6, +1, eq[5], d="6")
        self.play(Write(eq[6]))
        self.resultat(r"Y_B = \frac{16 + 8}{6} = 4~\mathrm{kN}")
        self.etape()

        self.effacer_calculs()
        self.ecrire(MathTex(r"\sum F_X = X_A + 6 = 0 \ \Rightarrow\ X_A = -6~\mathrm{kN}", font_size=self.FS_CALC))
        self.ecrire(MathTex(r"\sum F_Y = Y_A - 8 + 4 = 0 \ \Rightarrow\ Y_A = 4~\mathrm{kN}", font_size=self.FS_CALC))
        self.ecrire(T(r"Le couple \textbf{n'apparaît pas} dans $\sum F_X$ et $\sum F_Y$ (ce n'est pas une force).",
                      color=C_LEVIER))
        self.ecrire(MathTex(r"\text{Vérif. : }\sum M_{/B} = -6\times4 + 4\times8 - 8 = 0 \quad\checkmark",
                            font_size=self.FS_CALC, color=C_POS))
        self.play(*self.valeur(XA, r"X_A = -6~\mathrm{kN}", inverser=True),
                  *self.valeur(YA, r"Y_A = 4~\mathrm{kN}"), *self.valeur(YB, r"Y_B = 4~\mathrm{kN}"))
        self.ecrire(T(r"$X_A < 0$ : la réaction horizontale est en réalité vers la \textbf{gauche}.",
                      color=C_NEG))
        self.etape(2)


# ---------------------------------------------------------------------------
# 5. Console encastrée
# ---------------------------------------------------------------------------
class ReactionsConsole(PoutreScene):
    def construct(self):
        titre = self.titre(r"Actions de liaison : poutre encastrée (console)")
        self.play(Write(titre))
        self.repere(4, largeur=7.0, xc=-1.0)
        barre = poutre(self.X(0), self.X(4))
        enc = self.liaison("encastrement", 0)
        pts = VGroup(self.point(0, "A", UR), self.point(4, "B", UR))
        q = self.repartie(0, 4, r"q = 2~\mathrm{kN/m}")
        P = self.charge(4, r"P = 5~\mathrm{kN}", h=1.5)
        P[1].next_to(P[0], RIGHT, buff=0.1).shift(0.4 * UP)
        c = self.cote_x(0, 4, r"4~\mathrm{m}", dy=-0.95)
        self.play(FadeIn(enc), Create(barre), FadeIn(pts), FadeIn(c))
        self.play(LaggedStart(*[GrowArrow(a) for a in q[0]], lag_ratio=0.05), Create(q[1]), Write(q[2]),
                  GrowArrow(P[0]), Write(P[1]))
        self.etape()

        self.ecrire(T(r"Encastrement $\to$ \textbf{3 inconnues} : $X_A$, $Y_A$ et le \textbf{couple} $C_A$"
                      r" (dessiné $\curvearrowleft$, positif)."))
        self.ecrire(MathTex(r"F_{eq} = 2\times4 = 8~\mathrm{kN} \text{ à } 2~\mathrm{m} \text{ de } A",
                            font_size=self.FS_CALC))
        Feq = self.charge(2, r"F_{eq} = 8~\mathrm{kN}", h=1.3, couleur=YELLOW, cote_lab=RIGHT)
        q[2].set_opacity(0)
        self.play(q.animate.set_opacity(0.25), TransformFromCopy(q[0], Feq[0]), Write(Feq[1]))
        XA, YA = self.reaction("X", 0, "X_A"), self.reaction("Y", 0, "Y_A")
        CA = self.reaction("C", 0, "C_A", +1)
        self.play(FadeOut(c))
        self.remplacer_liaisons([enc], [XA, YA, CA])
        self.etape()

        self.effacer_calculs()
        eq = self.equation(r"\sum M_{/A} =", r"C_A", r"+0+0", r"-2\times8", r"-4\times5", r"=0")
        self.terme(CA, 0, 0, 0, eq[1], rq=T(r"Le couple d'encastrement\\s'écrit \textbf{tel quel}.",
                                             color=C_LEVIER, font_size=FS_TEXTE - 2))
        self.play(Write(eq[2]))
        self.terme(Feq, 0, 2, -1, eq[3], d="2")
        self.terme(P, 0, 4, -1, eq[4], d="4")
        self.play(Write(eq[5]))
        self.resultat(r"C_A = 16 + 20 = 36~\mathrm{kN\cdot m}")
        self.ecrire(MathTex(r"\sum F_X = X_A = 0 \qquad \sum F_Y = Y_A - 8 - 5 = 0 \ \Rightarrow\ Y_A = 13~\mathrm{kN}",
                            font_size=self.FS_CALC))
        self.play(*self.valeur(XA, r"X_A = 0"), *self.valeur(YA, r"Y_A = 13~\mathrm{kN}"),
                  *self.valeur(CA, r"C_A = 36~\mathrm{kN\cdot m}"))
        self.etape()

        # --- encastrement à droite : le signe change
        self.effacer_calculs()
        self.play(*map(FadeOut, [barre, pts, q, P, Feq, XA, YA, CA]))
        sous = T(r"Et si l'encastrement est \textbf{à droite} ?", color=C_NEG).next_to(titre, DOWN, buff=0.25)
        self.play(Write(sous))
        barre = poutre(self.X(0), self.X(4))
        enc = self.liaison("encastrement", 4)
        pts = VGroup(self.point(0, "A", UL), self.point(4, "B", UL))
        q = self.repartie(0, 4, r"q = 2~\mathrm{kN/m}").set_opacity(0.25)
        q[2].set_opacity(0)
        P = self.charge(0, r"P = 5~\mathrm{kN}", h=1.5)
        P[1].next_to(P[0], LEFT, buff=0.1).shift(0.4 * UP)
        Feq = self.charge(2, r"F_{eq} = 8~\mathrm{kN}", h=1.3, couleur=YELLOW, cote_lab=RIGHT)
        self.play(FadeIn(enc), Create(barre), FadeIn(pts), FadeIn(q), GrowArrow(P[0]), Write(P[1]),
                  GrowArrow(Feq[0]), Write(Feq[1]))
        XB, YB = self.reaction("X", 4, "X_B"), self.reaction("Y", 4, "Y_B")
        CB = self.reaction("C", 4, "C_B", +1)
        CB[1].shift(0.5 * RIGHT)
        self.remplacer_liaisons([enc], [XB, YB, CB])
        eq = self.equation(r"\sum M_{/B} =", r"C_B", r"+2\times8", r"+4\times5", r"=0")
        self.play(Write(eq[1]))
        self.terme(Feq, 4, 2, +1, eq[2], d="2")
        self.terme(P, 4, 0, +1, eq[3], d="4")
        self.play(Write(eq[4]))
        self.resultat(r"C_B = -36~\mathrm{kN\cdot m}")
        CB[0].set_color(C_NEG)
        self.play(*self.valeur(CB, r"C_B = -36~\mathrm{kN\cdot m}"),
                  Rotate(CB[0], PI, axis=UP, about_point=self.X(4)))
        self.ecrire(T(r"Négatif : le couple d'encastrement est en réalité \textbf{horaire} $\curvearrowright$."
                      r" On ne devine pas le signe : on le \textbf{calcule}.", color=C_NEG))
        self.etape(2)


# ---------------------------------------------------------------------------
# 6. Porte-à-faux : le plongeoir du poly
# ---------------------------------------------------------------------------
class ReactionsPorteAFaux(PoutreScene):
    def construct(self):
        titre = self.titre(r"Actions de liaison : porte-à-faux (plongeoir)")
        self.play(Write(titre))
        self.repere(3)
        barre = poutre(self.X(0), self.X(3))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 0.8)
        pts = VGroup(self.point(0, "A", UL), self.point(0.8, "B", UR), self.point(3, "C", UL))
        P = self.charge(3, r"P = 800~\mathrm{N}")
        cotes = VGroup(self.cote_x(0, 0.8, r"a = 0{,}8~\mathrm{m}", dy=-0.95),
                       self.cote_x(0.8, 3, r"b = 2{,}2~\mathrm{m}", dy=-0.95))
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts), FadeIn(cotes))
        self.play(GrowArrow(P[0]), Write(P[1]))
        self.ecrire(T(r"La charge est \textbf{en dehors} des deux liaisons (porte-à-faux)."))
        self.etape()

        self.effacer_calculs()
        self.play(FadeOut(cotes))
        XA, YA = self.reaction("X", 0, "X_A"), self.reaction("Y", 0, "Y_A")
        YB = self.reaction("Y", 0.8, "Y_B")
        self.remplacer_liaisons([lA, lB], [XA, YA, YB])
        eq = self.equation(r"\sum M_{/A} =", r"0 + 0", r"+0{,}8\,Y_B", r"-3\times800", r"=0")
        self.play(Write(eq[1]))
        self.terme(YB, 0, 0.8, +1, eq[2], d="0{,}8")
        self.terme(P, 0, 3, -1, eq[3], d="3")
        self.play(Write(eq[4]))
        self.resultat(r"Y_B = \frac{2400}{0{,}8} = 3000~\mathrm{N} = 3~\mathrm{kN}")
        self.ecrire(T(r"$Y_B = 3$ kN $>$ $P$ : effet de \textbf{levier} !", color=C_LEVIER))
        self.etape()

        self.effacer_calculs()
        self.ecrire(MathTex(r"\sum F_X = X_A = 0", font_size=self.FS_CALC))
        self.ecrire(MathTex(r"\sum F_Y = Y_A + 3000 - 800 = 0 \ \Rightarrow\ Y_A = -2200~\mathrm{N} = -2{,}2~\mathrm{kN}",
                            font_size=self.FS_CALC))
        self.play(*self.valeur(YA, r"Y_A = -2{,}2~\mathrm{kN}", inverser=True),
                  *self.valeur(YB, r"Y_B = 3~\mathrm{kN}"), *self.valeur(XA, r"X_A = 0"))
        self.ecrire(T(r"\textbf{Négatif} : l'articulation \textbf{retient} le plongeoir vers le bas.", color=C_NEG))
        self.etape()

        # sans ancrage en A : il bascule autour de B
        self.ecrire(T(r"Sans cette liaison en $A$, le plongeoir basculerait autour de $B$ :"))
        grp = VGroup(barre, P, pts[0], pts[2])
        self.play(FadeOut(YA), FadeOut(XA))
        self.play(Rotate(grp, -12 * DEGREES, about_point=self.X(0.8)), rate_func=there_and_back, run_time=2.2)
        self.play(FadeIn(YA), FadeIn(XA))
        self.etape(2)


# ---------------------------------------------------------------------------
# 7. Appui incliné
# ---------------------------------------------------------------------------
class ReactionsAppuiIncline(PoutreScene):
    def construct(self):
        titre = self.titre(r"Actions de liaison : appui incliné")
        self.play(Write(titre))
        self.repere(4, largeur=8.0)
        barre = poutre(self.X(0), self.X(4))
        lA, lB = self.liaison("articulation", 0), self.liaison("appui", 4, angle=45)
        pts = VGroup(self.point(0, "A", UL), self.point(2, "C", DOWN), self.point(4, "B", UL))
        P = self.charge(2, r"P = 10~\mathrm{kN}")
        cotes = VGroup(self.cote_x(0, 2, r"2~\mathrm{m}", dy=-1.15), self.cote_x(2, 4, r"2~\mathrm{m}", dy=-1.15))
        lab45 = MathTex(r"45^\circ", color=C_LEVIER, font_size=FS_TEXTE).move_to(self.X(4, -0.35) + 0.9 * RIGHT)
        self.play(Create(barre), FadeIn(lA), FadeIn(lB), FadeIn(pts), FadeIn(cotes), Write(lab45))
        self.play(GrowArrow(P[0]), Write(P[1]))
        self.etape()

        n = np.array([-1, 1, 0]) / np.sqrt(2)
        RB = VGroup(force(self.X(4) - 1.3 * n, self.X(4), couleur=C_REACTION))
        RB.add(MathTex(r"R_B", color=C_REACTION, font_size=FS_EQ).next_to(RB[0].get_start(), RIGHT, buff=0.1))
        XA, YA = self.reaction("X", 0, "X_A"), self.reaction("Y", 0, "Y_A")
        self.play(FadeOut(cotes))
        self.remplacer_liaisons([lA, lB], [XA, YA, RB])
        self.ecrire(T(r"Réaction \textbf{perpendiculaire} au plan de roulement : direction connue,"
                      r" \textbf{1 seule inconnue} $R_B$."))
        self.ecrire(MathTex(r"\vec R_B = \begin{pmatrix} -R_B\cos45^\circ \\ +R_B\sin45^\circ \end{pmatrix}"
                            r"\qquad \text{inconnues : } X_A,\ Y_A,\ R_B", font_size=self.FS_CALC))
        RBx = force(self.X(4) + 0.92 * RIGHT, self.X(4), couleur=C_FX)
        RBy = force(self.X(4) + 0.92 * DOWN, self.X(4), couleur=C_FY)
        self.play(RB.animate.set_opacity(0.3), TransformFromCopy(RB[0], RBx), TransformFromCopy(RB[0], RBy))
        self.etape()

        self.effacer_calculs()
        eq = self.equation(r"\sum M_{/A} =", r"0 + 0", r"-2\times10", r"+0", r"+4\,R_B\sin45^\circ", r"=0")
        self.play(Write(eq[1]))
        self.terme(P, 0, 2, -1, eq[2], d="2")
        self.terme(RBx, 0, 4, 0, eq[3], nul=True, dir_la=RIGHT,
                   rq=T(r"La composante horizontale\\est sur l'axe : moment nul.", color=C_LEVIER,
                        font_size=FS_TEXTE - 2))
        self.terme(RBy, 0, 4, +1, eq[4], d="4")
        self.play(Write(eq[5]))
        self.resultat(r"R_B = \frac{20}{4\sin45^\circ} = 5\sqrt2 \approx 7{,}07~\mathrm{kN}")
        self.etape()

        self.effacer_calculs()
        self.ecrire(MathTex(r"\sum F_X = X_A - R_B\cos45^\circ = 0 \ \Rightarrow\ X_A = 5~\mathrm{kN}",
                            font_size=self.FS_CALC))
        self.ecrire(MathTex(r"\sum F_Y = Y_A - 10 + R_B\sin45^\circ = 0 \ \Rightarrow\ Y_A = 5~\mathrm{kN}",
                            font_size=self.FS_CALC))
        self.play(*self.valeur(XA, r"X_A = 5~\mathrm{kN}"), *self.valeur(YA, r"Y_A = 5~\mathrm{kN}"))
        self.ecrire(T(r"Toutes les charges sont verticales... et pourtant $X_A \neq 0$ :"
                      r" c'est l'appui incliné qui « pousse » la poutre.", color=C_LEVIER))
        self.etape(2)


# ---------------------------------------------------------------------------
# 8. Bilan des pièges
# ---------------------------------------------------------------------------
class ReactionsPieges(Base):
    def construct(self):
        titre = self.titre(r"Actions de liaison : les pièges à éviter")
        self.play(Write(titre))
        items = [
            r"Compter les inconnues : \textbf{3} (isostatique) avant de calculer.",
            r"Inconnues dessinées \textbf{positives} ; résultat négatif $\Rightarrow$ sens inverse.",
            r"$\sum M$ au point où passent \textbf{le plus d'inconnues}.",
            r"Bras de levier = distance à la \textbf{ligne d'action} (force sur l'axe $\Rightarrow$ moment nul).",
            r"Charge répartie : $q\times$ \textbf{longueur chargée}, au \textbf{milieu de la zone chargée}.",
            r"Force inclinée : la \textbf{décomposer} en $F_X$ et $F_Y$.",
            r"Couple : \textbf{tel quel} dans $\sum M$ (avec son signe), \textbf{absent} de $\sum F$.",
            r"Encastrement : 3 inconnues dont un \textbf{couple} ; son signe se calcule.",
            r"Appui incliné : 1 inconnue, réaction \textbf{perpendiculaire} au support.",
            r"Unités : kN, m, kN$\cdot$m \ (et kN/m pour $q$).",
            r"Toujours \textbf{vérifier} avec $\sum M = 0$ en un autre point.",
        ]
        lignes = VGroup(*[
            VGroup(MathTex(r"\checkmark", color=C_POS, font_size=FS_TEXTE), T(t, font_size=FS_TEXTE - 1))
            .arrange(RIGHT, buff=0.2) for t in items
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(titre, DOWN, buff=0.35)
        if lignes.height > 6.5:
            lignes.scale_to_fit_height(6.5).next_to(titre, DOWN, buff=0.3)
        lignes.set_x(0)
        for l in lignes:
            self.play(FadeIn(l, shift=0.2 * RIGHT), run_time=0.6)
            self.wait(0.4)
        self.etape(2)
