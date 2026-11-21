'use strict';

// ═════════════════════════════════════════════════════════════════════════════
// Poutres continues : travées, solveur de rigidité, règle des trois moments.
// Conventions identiques à physics.js : Fy vers le haut, Mz anti-horaire,
// M(x) positif quand la fibre inférieure est tendue.
// ═════════════════════════════════════════════════════════════════════════════

// ─── Section à partir de ses paramètres (sans lire le DOM) ────────────────────
function buildSectionFromParams(p) {
    const type = p.type;
    if (type === 'rect') return makeSectionRect(p.b || 0.1, p.h || 0.2);
    if (type === 'circ') return makeSectionCirc(p.d || 0.15);
    if (type.startsWith('ipe')) return makeSectionProfile('IPE', p.num || IPE_DB[0].n, type.slice(4));
    if (type.startsWith('upe')) return makeSectionProfile('UPE', p.num || UPE_DB[0].n, type.slice(4));
    if (type === 'composite') {
        const comp = makeSectionComposite();
        for (const pc of (p.pieces || [])) {
            if (pc.shape === 'rect') comp.addRect(pc.add, pc.y1, pc.z1, pc.y2, pc.z2);
            else comp.addCirc(pc.add, pc.y1, pc.z1, pc.y2);
        }
        comp.finalise();
        return comp;
    }
    return makeSectionCustom(p.A || 0.01, p.Iz || 1e-5, p.Iy || 1e-5, p.h || 0.2);
}

// ─── Lettre d'une liaison (ordre de la liste, comme sur le schéma) ────────────
const supportLetter = i => String.fromCharCode(65 + i);

// ─── Découpage en travées ─────────────────────────────────────────────────────
// Les bornes sont les extrémités de la poutre et les liaisons. Une portion
// entre une extrémité libre et une liaison est un porte-à-faux (console).
function computeSegments(L, supports) {
    const pts = supports
        .map((s, i) => ({ x: s.x, letter: supportLetter(i) }))
        .filter(p => p.x > 1e-9 && p.x < L - 1e-9);
    const atX = x => {
        const i = supports.findIndex(s => Math.abs(s.x - x) < 1e-9);
        return i >= 0 ? supportLetter(i) : null;
    };
    const xs = [0, ...pts.map(p => p.x), L]
        .sort((a, b) => a - b)
        .filter((x, k, arr) => k === 0 || x - arr[k - 1] > 1e-9);
    const segs = [];
    for (let k = 0; k + 1 < xs.length; k++) {
        const a = atX(xs[k]), b = atX(xs[k + 1]);
        const label = a && b ? `${a}–${b}`
                    : a ? `${a} → extrémité` : b ? `extrémité → ${b}` : 'poutre';
        segs.push({ x1: xs[k], x2: xs[k + 1], label, overhang: !(a && b) });
    }
    return segs;
}

function segmentIndexAt(segs, x) {
    for (let k = 0; k < segs.length; k++) if (x <= segs[k].x2 + 1e-12) return k;
    return segs.length - 1;
}

// ─── Stabilité et degré d'hyperstaticité ──────────────────────────────────────
// Retourne { unknowns, degree, ok, reason }
function staticAnalysis(L, supports) {
    const unknowns = supports.reduce((s, sp) =>
        s + (sp.type === 'fixed' ? 3 : sp.type === 'pin' ? 2 : 1), 0);
    const degree = unknowns - 3;
    const xs = supports.map(s => s.x);
    if (xs.some((x, i) => xs.findIndex(y => Math.abs(y - x) < 1e-9) !== i))
        return { unknowns, degree, ok: false, reason: 'deux liaisons sont au même point : regroupez-les en une seule.' };
    if (supports.some(s => s.x < -1e-9 || s.x > L + 1e-9))
        return { unknowns, degree, ok: false, reason: 'une liaison est en dehors de la poutre.' };
    if (unknowns < 3)
        return { unknowns, degree, ok: false, reason: 'ajoutez ou bloquez une liaison.' };
    if (!supports.some(s => s.type !== 'roller'))
        return { unknowns, degree, ok: false,
                 reason: 'aucune liaison ne bloque le déplacement horizontal : remplacez un appui simple par une articulation.' };
    if (!supports.some(s => s.type === 'fixed') && supports.length < 2)
        return { unknowns, degree, ok: false, reason: 'la poutre peut tourner autour de son unique appui.' };
    return { unknowns, degree, ok: true, reason: '' };
}

// ─── Solveur de rigidité (éléments de poutre d'Euler-Bernoulli + barre) ────────
// segSections[k] : section de la travée k (computeSegments). Retourne
// { ok, reactions, deflectionAt(x) } ou { ok:false, error }.
function solveContinuous(L, supports, loads, E, segs, segSections) {
    // Nœuds : extrémités, liaisons, points d'application, puis maillage fin
    const keys = new Set([0, L]);
    for (const s of supports) keys.add(s.x);
    for (const l of loads) {
        if (l.type === 'distributed') { keys.add(l.x1); keys.add(l.x2); }
        else keys.add(l.x);
    }
    const base = [...keys].filter(x => x >= 0 && x <= L).sort((a, b) => a - b)
        .filter((x, k, arr) => k === 0 || x - arr[k - 1] > 1e-9);
    const hMax = L / 120;
    const X = [base[0]];
    for (let k = 1; k < base.length; k++) {
        const n = Math.max(1, Math.ceil((base[k] - base[k - 1]) / hMax));
        for (let j = 1; j <= n; j++) X.push(base[k - 1] + (base[k] - base[k - 1]) * j / n);
    }
    const nN = X.length, nD = 3 * nN, BW = 6;   // demi-largeur de bande
    const nodeAt = x => {
        let best = 0;
        for (let i = 1; i < nN; i++) if (Math.abs(X[i] - x) < Math.abs(X[best] - x)) best = i;
        return best;
    };

    // Matrice bande : K[i][j - i + BW], j ∈ [i-BW, i+BW]
    const K = Array.from({ length: nD }, () => new Float64Array(2 * BW + 1));
    const addK = (i, j, v) => { K[i][j - i + BW] += v; };
    const F = new Float64Array(nD);

    for (let e = 0; e + 1 < nN; e++) {
        const le = X[e + 1] - X[e];
        const sec = segSections[segmentIndexAt(segs, (X[e] + X[e + 1]) / 2)];
        const EI = E * sec.Iz, EA = E * (sec.area > 0 ? sec.area : sec.Iz * 1e4);
        const a = EA / le, b = 12 * EI / le ** 3, c = 6 * EI / le ** 2,
              d = 4 * EI / le, f = 2 * EI / le;
        const ke = [
            [ a, 0,  0, -a, 0,  0],
            [ 0, b,  c,  0, -b, c],
            [ 0, c,  d,  0, -c, f],
            [-a, 0,  0,  a, 0,  0],
            [ 0, -b, -c, 0, b, -c],
            [ 0, c,  f,  0, -c, d],
        ];
        const dofs = [3 * e, 3 * e + 1, 3 * e + 2, 3 * e + 3, 3 * e + 4, 3 * e + 5];
        for (let r = 0; r < 6; r++) for (let s = 0; s < 6; s++) addK(dofs[r], dofs[s], ke[r][s]);

        // Charges réparties : forces nodales équivalentes
        for (const l of loads) {
            if (l.type !== 'distributed') continue;
            const xm = (X[e] + X[e + 1]) / 2;
            if (xm < l.x1 || xm > l.x2) continue;
            const q = l.qy, qx = l.qx || 0;
            F[3 * e]     += qx * le / 2;     F[3 * e + 3] += qx * le / 2;
            F[3 * e + 1] += q * le / 2;      F[3 * e + 4] += q * le / 2;
            F[3 * e + 2] += q * le * le / 12; F[3 * e + 5] -= q * le * le / 12;
        }
    }
    for (const l of loads) {
        if (l.type === 'force') {
            const n = nodeAt(l.x);
            F[3 * n] += l.Fx || 0; F[3 * n + 1] += l.Fy;
        } else if (l.type === 'moment') {
            F[3 * nodeAt(l.x) + 2] += l.Mz;
        }
    }

    // Degrés de liberté bloqués par les liaisons
    const fixedDofs = [];
    supports.forEach((s, i) => {
        const n = nodeAt(s.x);
        const comps = s.type === 'roller' ? [1] : s.type === 'pin' ? [0, 1] : [0, 1, 2];
        for (const c of comps) fixedDofs.push({ dof: 3 * n + c, si: i, comp: c });
    });
    const isFixed = new Uint8Array(nD);
    for (const f of fixedDofs) isFixed[f.dof] = 1;
    const Korig = fixedDofs.map(f => Float64Array.from(K[f.dof]));

    // Conditions aux limites : ligne et colonne remplacées par l'identité
    for (let i = 0; i < nD; i++) {
        if (!isFixed[i]) continue;
        for (let j = Math.max(0, i - BW); j <= Math.min(nD - 1, i + BW); j++) {
            K[i][j - i + BW] = 0; K[j][i - j + BW] = 0;
        }
        K[i][BW] = 1;
    }
    const rhs = Float64Array.from(F, (v, i) => isFixed[i] ? 0 : v);

    // Élimination de Gauss en bande (matrice symétrique définie positive)
    const scale = Math.max(...K.map(r => Math.abs(r[BW])));
    for (let i = 0; i < nD; i++) {
        const piv = K[i][BW];
        if (!isFixed[i] && !(piv > 1e-12 * scale))   // lignes bloquées : pivot 1
            return { ok: false, error: 'Système singulier : la poutre est un mécanisme (liaisons insuffisantes).' };
        for (let r = i + 1; r <= Math.min(nD - 1, i + BW); r++) {
            const m = K[r][i - r + BW] / piv;
            if (m === 0) continue;
            for (let j = i; j <= Math.min(nD - 1, i + BW); j++) K[r][j - r + BW] -= m * K[i][j - i + BW];
            rhs[r] -= m * rhs[i];
        }
    }
    const U = new Float64Array(nD);
    for (let i = nD - 1; i >= 0; i--) {
        let s = rhs[i];
        for (let j = i + 1; j <= Math.min(nD - 1, i + BW); j++) s -= K[i][j - i + BW] * U[j];
        U[i] = s / K[i][BW];
    }

    // Réactions : R = K·U − F aux degrés de liberté bloqués
    const reactions = supports.map(s => ({ x: s.x, Rx: 0, Ry: 0, Mz: 0 }));
    fixedDofs.forEach((f, k) => {
        let r = -F[f.dof];
        for (let j = Math.max(0, f.dof - BW); j <= Math.min(nD - 1, f.dof + BW); j++)
            r += Korig[k][j - f.dof + BW] * U[j];
        const key = f.comp === 0 ? 'Rx' : f.comp === 1 ? 'Ry' : 'Mz';
        reactions[f.si][key] = r;
    });

    // Flèche par interpolation d'Hermite dans chaque élément
    const deflectionAt = x => {
        let e = 0;
        while (e < nN - 2 && X[e + 1] < x) e++;
        const le = X[e + 1] - X[e], t = Math.min(1, Math.max(0, (x - X[e]) / le));
        const h1 = 1 - 3 * t * t + 2 * t ** 3, h2 = le * (t - 2 * t * t + t ** 3),
              h3 = 3 * t * t - 2 * t ** 3,     h4 = le * (t ** 3 - t * t);
        return h1 * U[3 * e + 1] + h2 * U[3 * e + 2] + h3 * U[3 * e + 4] + h4 * U[3 * e + 5];
    };
    return { ok: true, reactions, deflectionAt };
}

// ─── Contraintes avec section variable ────────────────────────────────────────
function computeStressesVar(diagram, sectionAt) {
    return diagram.map(pt => {
        const s = computeStresses([pt], sectionAt(pt.x));
        return s ? s[0] : null;
    });
}

// ─── Règle des trois moments (Clapeyron) ──────────────────────────────────────
// Ω^L = (1/L)∫ M₀(ξ)(L−ξ) dξ et Ω^R = (1/L)∫ M₀(ξ) ξ dξ, M₀ étant le moment de la
// travée isolée sur deux appuis simples (charges de la travée seules).
function spanOmegas(xL, xR, loads) {
    const Ls = xR - xL;
    const inside = [];
    for (const l of loads) {
        if (l.type === 'distributed') {
            const a = Math.max(l.x1, xL), b = Math.min(l.x2, xR);
            if (b - a > 1e-12) inside.push({ ...l, x1: a, x2: b });
        } else if (l.x > xL + 1e-9 && l.x < xR - 1e-9) {
            inside.push(l);
        }
    }
    if (!inside.length) return { OL: 0, OR: 0 };
    const sup = [{ type: 'pin', x: xL }, { type: 'roller', x: xR }];
    const res = solveReactions(sup, inside);
    if (!res.ok) return { OL: 0, OR: 0 };

    // Simpson sur chaque morceau régulier (M₀·ξ est au plus cubique : exact)
    const brk = new Set([xL, xR]);
    for (const l of inside) {
        if (l.type === 'distributed') { brk.add(l.x1); brk.add(l.x2); } else brk.add(l.x);
    }
    const pts = [...brk].sort((a, b) => a - b);
    const M0 = x => computeAtX(sup, inside, res.reactions, x).M;
    let OL = 0, OR = 0;
    for (let k = 0; k + 1 < pts.length; k++) {
        const a = pts[k], b = pts[k + 1], h = b - a;
        if (h < 1e-12) continue;
        // valeurs prises juste à l'intérieur du morceau (sauts aux forces ponctuelles)
        const xa = a + 1e-9 * h, xb = b - 1e-9 * h, xm = (a + b) / 2;
        const fR = x => M0(x) * (x - xL), fL = x => M0(x) * (xR - x);
        OR += h / 6 * (fR(xa) + 4 * fR(xm) + fR(xb));
        OL += h / 6 * (fL(xa) + 4 * fL(xm) + fL(xb));
    }
    return { OL: OL / Ls, OR: OR / Ls };
}

// Données pour l'affichage pédagogique. Retourne null si la méthode ne
// s'applique pas (avec une raison), sinon les travées et les équations.
// Mfinal(x) : moment fléchissant calculé (pour les valeurs connues et la solution).
function clapeyronData(L, supports, loads, segSections, segs, Mfinal) {
    const order = supports.map((s, i) => ({ ...s, letter: supportLetter(i) }))
        .sort((a, b) => a.x - b.x);
    if (order.length < 2)
        return { applicable: false, reason: 'il faut au moins deux appuis pour former une travée.' };
    for (let k = 1; k < order.length - 1; k++)
        if (order[k].type === 'fixed')
            return { applicable: false, reason: `l'encastrement intérieur ${order[k].letter} n'entre pas dans la règle des trois moments.` };
    const first = order[0], last = order[order.length - 1];
    if (first.type === 'fixed' && first.x > 1e-9)
        return { applicable: false, reason: `l'encastrement ${first.letter} n'est pas en extrémité de poutre.` };
    if (last.type === 'fixed' && last.x < L - 1e-9)
        return { applicable: false, reason: `l'encastrement ${last.letter} n'est pas en extrémité de poutre.` };
    for (const l of loads)
        if (l.type === 'moment' && order.some(s => Math.abs(s.x - l.x) < 1e-9 && s !== first && s !== last))
            return { applicable: false, reason: 'un couple est appliqué sur un appui intérieur.' };

    // Travées entre appuis successifs
    const spans = [];
    for (let k = 0; k + 1 < order.length; k++) {
        const xL = order[k].x, xR = order[k + 1].x;
        const sec = segSections[segmentIndexAt(segs, (xL + xR) / 2)];
        const om = spanOmegas(xL, xR, loads);
        spans.push({ name: `${order[k].letter}${order[k + 1].letter}`, xL, xR,
                     Ls: xR - xL, I: sec.Iz, OL: om.OL, OR: om.OR });
    }
    const Iref = spans[0].I;
    const sameI = spans.every(s => Math.abs(s.I - Iref) <= 1e-9 * Iref);
    // Longueurs réduites L' = L·Iréf/I et Ω réduits (identiques si I constant)
    for (const s of spans) { s.Lr = s.Ls * Iref / s.I; s.OLr = s.OL * Iref / s.I; s.ORr = s.OR * Iref / s.I; }

    // Moments sur appuis : inconnus ou imposés
    // Moment lu du côté de la travée (le dernier appui est lu juste à sa gauche,
    // sinon sa propre réaction d'encastrement serait déjà comptée)
    const eps = 1e-9 * L;
    const Mside = k => Mfinal(k === order.length - 1 ? order[k].x - eps : order[k].x + eps);
    const nodes = order.map((s, k) => {
        const isEnd = k === 0 || k === order.length - 1;
        let known = null, why = '';
        if (isEnd && s.type !== 'fixed') {
            known = Mside(k);
            if (Math.abs(known) < 1e-2) known = 0;      // résidu du décalage eps
            const over = (k === 0 && s.x > 1e-9) || (k === order.length - 1 && s.x < L - 1e-9);
            why = over ? 'imposé par le porte-à-faux' : (known !== 0 ? 'imposé par le couple appliqué' : 'appui simple d\'extrémité');
        }
        return { letter: s.letter, x: s.x, known, why, value: Mside(k) };
    });

    // Une équation par moment inconnu : { node, terms:[{coef, k}], rhs, kind }
    const eqs = [];
    nodes.forEach((nd, k) => {
        if (nd.known !== null) return;
        const terms = [];
        let rhs;
        if (k === 0) {                         // encastrement à gauche
            const s = spans[0];
            terms.push({ coef: 2 * s.Lr, k: 0 }, { coef: s.Lr, k: 1 });
            rhs = { value: -6 * s.OLr, parts: [`Ω${sub(1)}ᴸ`] };
        } else if (k === nodes.length - 1) {    // encastrement à droite
            const s = spans[k - 1];
            terms.push({ coef: s.Lr, k: k - 1 }, { coef: 2 * s.Lr, k });
            rhs = { value: -6 * s.ORr, parts: [`Ω${sub(k)}ᴿ`] };
        } else {
            const s1 = spans[k - 1], s2 = spans[k];
            terms.push({ coef: s1.Lr, k: k - 1 }, { coef: 2 * (s1.Lr + s2.Lr), k, split: [s1.Lr, s2.Lr] },
                       { coef: s2.Lr, k: k + 1 });
            rhs = { value: -6 * (s1.ORr + s2.OLr), parts: [`Ω${sub(k)}ᴿ`, `Ω${sub(k + 1)}ᴸ`] };
        }
        // Résidu avec les moments calculés (contrôle de cohérence)
        const lhs = terms.reduce((acc, t) => acc + t.coef * nodes[t.k].value, 0);
        eqs.push({ node: k, terms, rhs, residual: lhs - rhs.value });
    });

    return { applicable: true, spans, nodes, eqs, sameI, Iref };
}

// Indice numérique Unicode (1 → ₁)
function sub(n) { return String(n).replace(/\d/g, d => '₀₁₂₃₄₅₆₇₈₉'[d]); }
