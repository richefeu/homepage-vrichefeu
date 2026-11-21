// ─── Formulation d'un béton par la méthode de Dreux-Gorisse ─────────────────
// Calcul pur (aucun accès au DOM) : dreuxCompute(p, refus) → résultats.
// Les tables sont celles utilisées à l'IUT GCCD.

// Tamis : module AFNOR 20 à 50 et ouverture (mm)
const MODULES   = Array.from({ length: 31 }, (_, i) => 20 + i);
const DIAMETRES = [0.08, 0.1, 0.125, 0.16, 0.2, 0.25, 0.315, 0.4, 0.5, 0.63, 0.8, 1, 1.25, 1.6,
                   2, 2.5, 3.15, 4, 5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80];

const DTab = [5, 8, 12.5, 20, 31.5, 50, 80];

// Abaque de Copt (Figure 2) : C/E en fonction de Aff (1 à 12), pour C = 200 à 450 kg/m³
const Tab = [
    [1.1843, 1.1333, 1.0902, 1.0510, 1.0196, 0.9960, 0.9764, 0.9607, 0.9490, 0.9372, 0.9254, 0.9254],
    [1.4588, 1.4039, 1.3569, 1.3137, 1.2784, 1.2471, 1.2235, 1.2039, 1.1843, 1.1647, 1.1529, 1.1373],
    [1.7843, 1.7216, 1.6588, 1.6118, 1.5686, 1.5294, 1.4941, 1.4706, 1.4471, 1.4196, 1.4000, 1.3843],
    [2.0549, 1.9961, 1.9294, 1.8784, 1.8353, 1.7922, 1.7608, 1.7216, 1.6941, 1.6667, 1.6392, 1.6157],
    [2.3569, 2.2863, 2.2157, 2.1529, 2.0902, 2.0431, 2.0000, 1.9608, 1.9216, 1.8863, 1.8510, 1.8235],
    [2.6000, 2.5216, 2.4510, 2.3961, 2.3412, 2.2863, 2.2471, 2.2000, 2.1647, 2.1294, 2.0902, 2.0588],
];
const level = [200.0, 250.0, 300.0, 350.0, 400.0, 450.0];

// Tableau 7 : compacité c0 [consistance][serrage][Dmax]
const c0Tab = [
    [
        [0.750, 0.780, 0.795, 0.805, 0.810, 0.815, 0.820],
        [0.755, 0.785, 0.800, 0.810, 0.815, 0.820, 0.825],
        [0.760, 0.790, 0.805, 0.815, 0.820, 0.825, 0.830],
        [0, 0, 0, 0, 0, 0, 0],
    ],
    [
        [0.760, 0.790, 0.805, 0.815, 0.820, 0.825, 0.830],
        [0.765, 0.795, 0.810, 0.820, 0.825, 0.830, 0.835],
        [0.770, 0.800, 0.815, 0.825, 0.830, 0.835, 0.840],
        [0.775, 0.805, 0.820, 0.830, 0.835, 0.840, 0.845],
    ],
    [
        [0, 0, 0, 0, 0, 0, 0],
        [0.775, 0.805, 0.820, 0.830, 0.835, 0.840, 0.845],
        [0.780, 0.810, 0.825, 0.835, 0.840, 0.845, 0.850],
        [0.785, 0.815, 0.830, 0.840, 0.845, 0.850, 0.855],
    ],
];

function roundNumber(num, scale) {
    if (!('' + num).includes('e')) {
        return +(Math.round(num + 'e+' + scale) + 'e-' + scale);
    }
    const arr = ('' + num).split('e');
    const sig = (+arr[1] + scale > 0) ? '+' : '';
    return +(Math.round(+arr[0] + 'e' + sig + (+arr[1] + scale)) + 'e-' + scale);
}

// ─── Courbes granulométriques ────────────────────────────────────────────────
// Échantillonnage commun à toutes les courbes (le mélange se calcule point à point)
const CURVE_STEP = 0.05;
const CURVE_X = Array.from({ length: Math.round(30 / CURVE_STEP) + 1 }, (_, k) => 20 + k * CURVE_STEP);

// Fonction d'erreur (Abramowitz et Stegun 7.1.26, erreur < 1,5e-7)
function erf(x) {
    const sg = x < 0 ? -1 : 1;
    x = Math.abs(x);
    const t = 1 / (1 + 0.3275911 * x);
    const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return sg * y;
}
const lognormPassant = (m, mu, sig) => 50 * (1 + erf((m - mu) / (sig * Math.SQRT2)));

// Loi log-normale (en ouverture de tamis, donc normale en module) ajustée aux passants
// mesurés par moindres carrés (Levenberg-Marquardt) → { mu, sig, rms }
function fitLognormal(passants) {
    const xs = MODULES;
    const at = y => {               // module où les mesures franchissent y % (estimation initiale)
        for (let i = 1; i < xs.length; i++) {
            const a = passants[i - 1], b = passants[i];
            if (a < y && b >= y) return xs[i - 1] + (y - a) / (b - a);
        }
        return null;
    };
    let mu = at(50) ?? 35;
    let sig = Math.max(0.3, ((at(84) ?? mu + 1) - (at(16) ?? mu - 1)) / 2);
    const sse = (m, s) => xs.reduce((acc, x, i) => acc + (lognormPassant(x, m, s) - passants[i]) ** 2, 0);
    let e = sse(mu, sig), lambda = 1e-2;
    for (let it = 0; it < 200; it++) {
        // jacobien numérique
        let JtJ = [0, 0, 0], Jtr = [0, 0];
        const h = 1e-6;
        xs.forEach((x, i) => {
            const f = lognormPassant(x, mu, sig);
            const dm = (lognormPassant(x, mu + h, sig) - f) / h;
            const ds = (lognormPassant(x, mu, sig + h) - f) / h;
            const r = passants[i] - f;
            JtJ[0] += dm * dm; JtJ[1] += dm * ds; JtJ[2] += ds * ds;
            Jtr[0] += dm * r;  Jtr[1] += ds * r;
        });
        const a = JtJ[0] * (1 + lambda), b = JtJ[1], c = JtJ[2] * (1 + lambda);
        const det = a * c - b * b;
        if (!(Math.abs(det) > 1e-30)) break;
        const dmu = (c * Jtr[0] - b * Jtr[1]) / det;
        const dsig = (a * Jtr[1] - b * Jtr[0]) / det;
        const mu2 = mu + dmu, sig2 = Math.max(0.05, sig + dsig);
        const e2 = sse(mu2, sig2);
        if (e2 < e) {
            const done = e - e2 < 1e-10 * (1 + e);
            mu = mu2; sig = sig2; e = e2; lambda /= 3;
            if (done) break;
        } else {
            lambda *= 4;
            if (lambda > 1e8) break;
        }
    }
    return { mu, sig, rms: Math.sqrt(e / xs.length) };
}

// Interpolation monotone (Fritsch-Carlson) : passe par les points sans oscillation
function pchip(xs, ys) {
    const n = xs.length, h = [], d = [], m = new Array(n);
    for (let i = 0; i < n - 1; i++) { h[i] = xs[i + 1] - xs[i]; d[i] = (ys[i + 1] - ys[i]) / h[i]; }
    m[0] = d[0]; m[n - 1] = d[n - 2];
    for (let i = 1; i < n - 1; i++) {
        if (d[i - 1] * d[i] <= 0) m[i] = 0;
        else {
            const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1];
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
        }
    }
    if (d[0] * m[0] <= 0) m[0] = 0;
    if (d[n - 2] * m[n - 1] <= 0) m[n - 1] = 0;
    return x => {
        let i = Math.min(n - 2, Math.max(0, Math.floor(x - xs[0])));   // modules entiers consécutifs
        const t = (x - xs[i]) / h[i], t2 = t * t, t3 = t2 * t;
        return (2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] +
               (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1];
    };
}

// Courbe d'un granulat → { pts: [[module, refus, passant], …], fit }
// mode 1 : loi log-normale ajustée ; mode 0 : interpolation monotone par les points
function granuCurve(refus, mode) {
    const passants = refus.map(r => 100 - r);
    let f, fit = null;
    if (mode == 1) {
        fit = fitLognormal(passants);
        f = x => lognormPassant(x, fit.mu, fit.sig);
    } else {
        f = pchip(MODULES, passants);
    }
    const pts = CURVE_X.map(x => {
        const pas = Math.min(100, Math.max(0, f(x)));
        return [x, 100 - pas, pas];
    });
    return { pts, fit };
}

// Module où la courbe atteint le passant y (interpolation linéaire)
function moduleAtPassant(curve, y, inclusive = false) {
    let r1 = 1;
    while (r1 < curve.length && (inclusive ? curve[r1][2] <= y : curve[r1][2] < y)) r1++;
    if (r1 >= curve.length) throw new Error(`la courbe n'atteint pas ${y} % de passant`);
    const r0 = r1 - 1;
    return curve[r0][0] + (curve[r1][0] - curve[r0][0]) * (y - curve[r0][2]) / (curve[r1][2] - curve[r0][2]);
}

// Figure 2 : abaque permettant de déterminer Copt
// → { Copt, out } avec out = 'low' (C < 200) ou 'high' (C > 450) hors abaque
function getCopt(C_E, Aff) {
    const aff0 = Math.min(Math.floor(Aff), 11), aff1 = aff0 + 1;   // abaque lu de 1 à 12 cm
    const iaff0 = aff0 - 1, iaff1 = iaff0 + 1;
    const val = [];
    for (let i = 0; i < 6; i++) {
        const val0 = Tab[i][iaff0], val1 = Tab[i][iaff1];
        val[i] = val0 + (Aff - aff0) * (val1 - val0) / (aff1 - aff0);
    }
    let i1 = 0;
    while (i1 < 6 && val[i1] <= C_E) i1++;
    if (i1 == 0) return { Copt: 0, out: 'low' };
    if (i1 == 6) return { Copt: 0, out: 'high' };
    const i0 = i1 - 1;
    const frac = (C_E - val[i0]) / (val[i1] - val[i0]);
    return { Copt: level[i0] + frac * (level[i1] - level[i0]), out: null };
}

// Tableau 7 : compacité du béton en fonction de Dmax, de la consistance et du serrage
function getC0(D, aff, serrage) {
    let i1 = 1;
    while (i1 < 7 && D >= DTab[i1]) i1++;
    const i0 = i1 - 1;
    let iaff;
    if (aff >= 10) { iaff = 0; if (serrage == 3) serrage = 2; }
    else if (aff <= 4) { iaff = 2; if (serrage == 0) serrage = 1; }
    else iaff = 1;
    const v0 = c0Tab[iaff][serrage][i0], v1 = c0Tab[iaff][serrage][i1];
    return v0 + (v1 - v0) * (D - DTab[i0]) / (DTab[i1] - DTab[i0]);
}

// p : paramètres (nombres), refus : { S:[31], g:[31], G:[31] } refus cumulés (%)
function dreuxCompute(p, refus) {
    const r = { warnings: [] };
    const data = MODULES.map((m, i) => ({
        module: m, diametre: DIAMETRES[i], refus_S: refus.S[i], refus_g: refus.g[i], refus_G: refus.G[i],
    }));
    const cS = granuCurve(refus.S, p.courbe), cg = granuCurve(refus.g, p.courbe), cG = granuCurve(refus.G, p.courbe);
    const curveS = cS.pts, curveg = cg.pts, curveG = cG.pts;
    r.curves = { S: curveS, g: curveg, G: curveG };
    r.fits = { S: cS.fit, g: cg.fit, G: cG.fit };

    // ===== Dmax : premier tamis sans refus du plus gros granulat
    const key = p.nbGranu == 2 ? 'refus_g' : 'refus_G';
    let i = 0;
    while (i < data.length && data[i][key] > 0) i++;
    r.DmaxCalc = i < data.length ? data[i].diametre : null;
    r.DmaxImpose = p.Dmax > 0;
    if (r.DmaxImpose) i = DIAMETRES.indexOf(+p.Dmax);
    if (i < 0 || i >= data.length) throw new Error(`le ${p.nbGranu == 2 ? 'gravette' : 'gravier'} a du refus sur tous les tamis`);
    const Dmax = data[i].diametre;
    const ModDmax = data[i].module;
    r.Dmax = Dmax;
    r.ModDmax = ModDmax;

    // ===== Module de finesse du sable (0 : calculé sur les tamis 0,16 à 80 mm)
    let Mfs = p.Mfs;
    r.MfsCalc = Mfs === 0;
    if (Mfs === 0) {
        for (let k = 23 - 20; k <= 50 - 20; k += 3) Mfs += data[k].refus_S;
        Mfs = roundNumber(Mfs / 100.0, 4);
    }
    r.Mfs = Mfs;

    // ===== G' (Tableau 4)
    const Gq = [[0.35, 0.4, 0.45], [0.45, 0.5, 0.55], [0.55, 0.6, 0.65]][p.qualite];
    const [Gfin, Gmoyen, Ggros] = Gq;
    let Gprime;
    if (Dmax <= 12.5) Gprime = Gfin;
    else if (Dmax < 20.0) Gprime = Gfin + (Dmax - 12.5) / (20.0 - 12.5) * (Gmoyen - Gfin);
    else if (Dmax <= 31.5) Gprime = Gmoyen;
    else if (Dmax < 50.0) Gprime = Gmoyen + (Dmax - 31.5) / (50.0 - 31.5) * (Ggros - Gmoyen);
    else Gprime = Ggros;
    r.Gprime = Gprime;

    // ===== C/E (formule de Bolomey)
    const C_E = roundNumber(p.sig28 / (Gprime * p.classVraie) + 0.5, 4);
    r.C_E = C_E;

    // ===== Copt (abaque)
    const ab = getCopt(C_E, p.aff);
    const Copt = roundNumber(ab.Copt, 4);
    r.Copt = Copt;
    r.CoptOut = ab.out;
    if (ab.out === 'high') r.warnings.push(`C/E = ${C_E} demande plus de 450 kg/m³ de ciment (hors abaque) : ` +
        `seul Cmin est retenu, résultat à revoir (résistance trop élevée ou ciment de classe trop faible)`);

    // ===== Cmin
    const Cmin1 = (250.0 + 10 * p.sig28) / Math.pow(1.25 * Dmax, 0.2);
    let Cmin = Cmin1;
    if (p.agressivite == 1) Cmin = Math.max(Cmin1, 700.0 / Math.pow(1.25 * Dmax, 0.2));
    else if (p.expose == 1) Cmin = Math.max(Cmin1, 550.0 / Math.pow(1.25 * Dmax, 0.2));
    Cmin = roundNumber(Cmin, 4);
    r.Cmin = Cmin;

    const Cav = roundNumber(Math.max(Copt, Cmin), 4);
    r.Cav = Cav;
    const Eav = roundNumber(Cav / C_E, 4);
    r.Eav = Eav;

    // ===== Correction des dosages en pâte selon Dmax
    let corr;
    if (Dmax <= 5) corr = 15;
    else if (Dmax <= 8) corr = 15 + (Dmax - 5) / (8 - 5) * (9 - 15);
    else if (Dmax <= 12.5) corr = 9 + (Dmax - 8) / (12.5 - 8) * (4 - 9);
    else if (Dmax <= 20) corr = 4 + (Dmax - 12.5) / (20 - 12.5) * (0 - 4);
    else if (Dmax <= 31.5) corr = 0 + (Dmax - 20) / (31.5 - 20) * (-4 - 0);
    else if (Dmax <= 50) corr = -4 + (Dmax - 31.5) / (50 - 31.5) * (-8 - (-4));
    else if (Dmax <= 80) corr = -8 + (Dmax - 50) / (80 - 50) * (-12 - (-8));
    else corr = -12;
    corr = roundNumber(corr, 1);
    r.corr = corr;

    const C = roundNumber(Cav * (100.0 + corr) / 100.0, 4);
    const E = roundNumber(Eav * (100.0 + corr) / 100.0, 4);
    r.C = C;
    r.E = E;

    // ******* Courbe de référence de Dreux : O (module 20, 0 %), A (X, Y), B (Dmax, 100 %)

    // ===== X
    let X, ModX;
    if (Dmax <= 20.0) {
        X = Dmax / 2.0;
        let k = 0;
        while (k < data.length && data[k].diametre < X) k++;
        ModX = (k + 1 < data.length)
            ? data[k].module + (X - data[k].diametre) * (data[k + 1].module - data[k].module) /
              (data[k + 1].diametre - data[k].diametre)
            : data[k].module;
    } else {
        ModX = (ModDmax + 38) / 2.0;
        let k = 0;
        while (k < data.length && data[k].module < ModX) k++;
        X = (k + 1 < data.length)
            ? data[k].diametre + (ModX - data[k].module) * (data[k + 1].diametre - data[k].diametre) /
              (data[k + 1].module - data[k].module)
            : data[k].diametre;
    }
    r.X = roundNumber(X, 1);
    r.ModX = ModX;

    // ===== Y (Tableau 6)
    const C0 = 200.0, C1 = 450.0;
    // vibration : celle du serrage choisi (le piquage est traité comme une vibration faible)
    let K0, K1;
    if (p.serrage <= 1) {
        if (p.S_roule == 1) { K0 = 8.0; K1 = -2.0; } else { K0 = 10.0; K1 = 0.0; }
    } else if (p.serrage == 2) {
        if (p.S_roule == 1) { K0 = 6.0; K1 = -4.0; } else { K0 = 8.0; K1 = -2.0; }
    } else {
        if (p.S_roule == 1) { K0 = 4.0; K1 = -6.0; } else { K0 = 6.0; K1 = -4.0; }
    }
    const K = roundNumber(K0 + (K1 - K0) * (C - C0) / (C1 - C0), 4);
    const Ks = roundNumber(6.0 * Mfs - 15.0, 4);
    const Kprime = roundNumber(K + Ks + p.Kp, 4);
    const Y = roundNumber(50.0 - Math.sqrt(1.25 * Dmax) + Kprime, 1);
    Object.assign(r, { K, Ks, Kp: p.Kp, Kprime, Y });

    // ===== Pourcentages en volumes absolus (lignes de partage)
    const a1 = (Y - 0.0) / (ModX - 20.0);
    const b1 = Y - a1 * ModX;
    const a2 = (100.0 - Y) / (ModDmax - ModX);
    const b2 = Y - a2 * ModX;

    // droite joignant 95 % de passant du sable à 5 % du gravillon
    const ys = 95, yg1 = 5.0;
    const xs  = moduleAtPassant(curveS, ys);
    const xg1 = moduleAtPassant(curveg, yg1);
    const A = (yg1 - ys) / (xg1 - xs);
    const B = ys - A * xs;
    let ModDi = (B - b1) / (a1 - A);
    if (ModX < ModDi) ModDi = (B - b2) / (a2 - A);
    let YS = A * ModDi + B;
    const Srate = roundNumber(YS, 1);

    let grate = 0.0, Grate = 0.0;
    let xG, xg2, YG, ModDi2;
    const yG = 5, yg2 = 95;
    if (p.nbGranu == 2) {
        grate = roundNumber(100.0 - Srate, 1);
    } else {
        // droite joignant 95 % de passant du gravillon à 5 % du gravier
        xG  = moduleAtPassant(curveG, yG, true);
        xg2 = moduleAtPassant(curveg, yg2);
        if (Math.abs(xG - xg2) > 0.01) {
            const A2 = (yG - yg2) / (xG - xg2);
            const B2 = yG - A2 * xG;
            ModDi2 = (B2 - b1) / (a1 - A2);
            if (ModX < ModDi2) ModDi2 = (B2 - b2) / (a2 - A2);
            YG = A2 * ModDi2 + B2;
        } else {
            ModDi2 = xG;
            YG = (ModX > ModDi2) ? a1 * ModDi2 + b1 : a2 * ModDi2 + b2;
        }
        YG = roundNumber(YG, 1);
        YS = roundNumber(YS, 1);
        grate = roundNumber(YG - YS, 1);
        Grate = roundNumber(100.0 - YG, 1);
    }
    Object.assign(r, { Srate, grate, Grate, YS, YG });

    // ==== Traits de construction [x0, passant0, x1, passant1]
    r.lignesConstr = [[xs, ys, xg1, yg1], [50, YS, ModDi, YS]];
    if (p.nbGranu != 2) r.lignesConstr.push([xg2, yg2, xG, yG], [50, YG, ModDi2, YG]);
    r.briseeConstr = [[20, 0, ModX, Y], [ModX, Y, ModDmax, 100]];

    // ==== Courbe du mélange (refus)
    r.Mrefus = curveS.map((pt, k) => [pt[0],
        0.01 * Srate * pt[1] + 0.01 * grate * curveg[k][1] + (p.nbGranu == 2 ? 0 : 0.01 * Grate * curveG[k][1])]);

    // ===== Compacité du béton
    const c0 = roundNumber(getC0(Dmax, p.aff, p.serrage), 4);
    // forme : sable concassé → −0,03 ; sable roulé et gros granulats concassés → −0,01
    const grosConcasses = p.g_roule == 0 || (p.nbGranu != 2 && p.G_roule == 0);
    let c1 = p.S_roule == 0 ? -0.03 : grosConcasses ? -0.01 : 0.0;
    c1 = roundNumber(c1, 4);
    const c2 = p.granuLeger == 1 ? -0.03 : 0.0;
    const c3 = roundNumber((C - 350.0) / 5000.0, 4);
    const c  = roundNumber(c0 + c1 + c2 + c3, 4);
    const Vc = roundNumber(C / (p.rhos_C * 1000.0), 4);
    const V  = roundNumber(c - Vc, 4);
    Object.assign(r, { c0, c1, c2, c3, c, Vc, V });

    // ===== Masses de granulats
    const Vs = roundNumber(0.01 * Srate * V, 4);
    const Vg = roundNumber(0.01 * grate * V, 4);
    const VG = roundNumber(0.01 * Grate * V, 4);
    const S = roundNumber(Vs * p.rhos_S * 1000.0, 4);
    const g = roundNumber(Vg * p.rhos_g * 1000.0, 4);
    const G = roundNumber(VG * p.rhos_G * 1000.0, 4);
    Object.assign(r, { Vs, Vg, VG, S, g, G });

    return r;
}
