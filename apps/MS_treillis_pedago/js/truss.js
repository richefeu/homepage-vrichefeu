'use strict';

// ═════════════════════════════════════════════════════════════════════════════
// Structures planes de barres : treillis articulés et portiques à nœuds rigides.
// Repère global : x vers la droite, y vers le haut, Mz anti-horaire.
// N > 0 en traction. Repère local d'une barre : x de n1 vers n2, y à gauche.
// ═════════════════════════════════════════════════════════════════════════════

const nodeName = i => i < 26 ? String.fromCharCode(65 + i) : `N${i + 1}`;
const barName  = b => nodeName(b.n1) + nodeName(b.n2);

// Degrés de liberté bloqués par type de liaison (0 : x, 1 : y, 2 : θ)
const SUPPORT_DOFS = { XY: [0, 1], Y: [1], X: [0], XYtheta: [0, 1, 2] };
const SUPPORT_LABELS = {
    XY: 'Articulation', Y: 'Appui simple (roule ↔)', X: 'Appui simple (roule ↕)', XYtheta: 'Encastrement',
};

// Composantes de liaison effectives (en treillis, l'encastrement agit comme une articulation)
const supportDofs = (type, sp) => SUPPORT_DOFS[sp.type].filter(d => type === 'portique' || d < 2);

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

// ─── Vérifications de saisie ──────────────────────────────────────────────────
// Retourne un message d'erreur, ou '' si la structure est bien décrite.
function checkStructure(nodes, bars, supports, loads) {
    if (nodes.length < 2) return 'il faut au moins deux nœuds.';
    if (!bars.length) return 'il faut au moins une barre.';
    const seen = new Set();
    for (const b of bars) {
        if (b.n1 === b.n2 || !nodes[b.n1] || !nodes[b.n2]) return `la barre ${barName(b)} doit relier deux nœuds différents.`;
        const p = nodes[b.n1], q = nodes[b.n2];
        if (Math.hypot(q.x - p.x, q.y - p.y) < 1e-9) return `la barre ${barName(b)} a une longueur nulle.`;
        const key = Math.min(b.n1, b.n2) + '-' + Math.max(b.n1, b.n2);
        if (seen.has(key)) return `la barre ${barName(b)} est définie deux fois.`;
        seen.add(key);
    }
    for (let i = 0; i < nodes.length; i++) {
        for (let j = 0; j < i; j++)
            if (Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y) < 1e-9)
                return `les nœuds ${nodeName(j)} et ${nodeName(i)} sont au même endroit.`;
        if (!bars.some(b => b.n1 === i || b.n2 === i)) return `le nœud ${nodeName(i)} n'est relié à aucune barre.`;
    }
    const sup = new Set();
    for (const s of supports) {
        if (!nodes[s.node]) return 'une liaison porte sur un nœud inexistant.';
        if (sup.has(s.node)) return `le nœud ${nodeName(s.node)} a deux liaisons : gardez-en une seule.`;
        sup.add(s.node);
    }
    for (const l of loads) if (!nodes[l.node]) return 'une charge porte sur un nœud inexistant.';
    return '';
}

// ─── Rotules en extrémité de barre (portique) ─────────────────────────────────
// b.h1 / b.h2 : rotule au début / à la fin de la barre (moment nul à cette extrémité).
const releasedEnds = (type, b) => type === 'portique' ? [b.h1 ? 2 : -1, b.h2 ? 5 : -1].filter(i => i >= 0) : [];

// Nœuds dont toutes les barres sont articulées (et sans blocage de rotation) :
// leur rotation n'a plus de sens, l'équation d'équilibre en moment disparaît.
function freeRotationNodes(type, nodes, bars, supports) {
    if (type !== 'portique') return [];
    return nodes.map((_, i) => i).filter(i => {
        const ends = bars.flatMap(b => [b.n1 === i ? !!b.h1 : null, b.n2 === i ? !!b.h2 : null]).filter(e => e !== null);
        const sp = supports.find(s => s.node === i);
        return ends.length > 0 && ends.every(Boolean) && !(sp && sp.type === 'XYtheta');
    });
}

// ─── Degré d'hyperstaticité ───────────────────────────────────────────────────
// Treillis : h = b + r − 2n ; portique : h = 3b + r − 3n − c (+ f), avec c le nombre
// de rotules en bout de barre et f le nombre de nœuds entièrement articulés.
function structureDegree(type, nodes, bars, supports) {
    const b = bars.length, n = nodes.length;
    const r = supports.reduce((s, sp) => s + supportDofs(type, sp).length, 0);
    if (type === 'treillis') {
        const degree = b + r - 2 * n;
        return { b, r, n, c: 0, f: 0, degree, formula: `b + r − 2n = ${b} + ${r} − ${2 * n} = ${degree}` };
    }
    const c = bars.reduce((s, br) => s + releasedEnds(type, br).length, 0);
    const f = freeRotationNodes(type, nodes, bars, supports).length;
    const degree = 3 * b + r - 3 * n - c + f;
    const formula = c === 0 ? `3b + r − 3n = ${3 * b} + ${r} − ${3 * n} = ${degree}`
        : f === 0 ? `3b + r − 3n − c = ${3 * b} + ${r} − ${3 * n} − ${c} = ${degree}`
        : `3b + r − 3n − c + f = ${3 * b} + ${r} − ${3 * n} − ${c} + ${f} = ${degree}`;
    return { b, r, n, c, f, degree, formula };
}

// ─── Géométrie d'une barre ────────────────────────────────────────────────────
function barGeom(nodes, b) {
    const p = nodes[b.n1], q = nodes[b.n2];
    const L = Math.hypot(q.x - p.x, q.y - p.y);
    return { L, c: (q.x - p.x) / L, s: (q.y - p.y) / L };
}

// Matrice de rigidité locale d'un élément poutre-colonne (u1 v1 θ1 u2 v2 θ2)
function frameLocalK(E, sec, L) {
    const EA = E * sec.area, EI = E * sec.Iz;
    const a = EA / L, b = 12 * EI / L ** 3, c = 6 * EI / L ** 2, d = 4 * EI / L, f = 2 * EI / L;
    return [
        [ a, 0,  0, -a, 0,  0],
        [ 0, b,  c,  0, -b, c],
        [ 0, c,  d,  0, -c, f],
        [-a, 0,  0,  a, 0,  0],
        [ 0, -b, -c, 0, b, -c],
        [ 0, c,  f,  0, -c, d],
    ];
}

// u_local = T · u_global (par nœud : [c s 0 ; −s c 0 ; 0 0 1]) ; fromLocal = Tᵀ
function toLocal(c, s, u) {
    return [c * u[0] + s * u[1], -s * u[0] + c * u[1], u[2],
            c * u[3] + s * u[4], -s * u[3] + c * u[4], u[5]];
}
function fromLocal(c, s, f) {
    return [c * f[0] - s * f[1], s * f[0] + c * f[1], f[2],
            c * f[3] - s * f[4], s * f[3] + c * f[4], f[5]];
}

// Charge répartie uniforme (locale qa axiale, qt transversale) : forces nodales
// équivalentes d'une barre bi-encastrée
const fixedEndLoads = (qa, qt, L) => [qa * L / 2, qt * L / 2, qt * L * L / 12, qa * L / 2, qt * L / 2, -qt * L * L / 12];

// Condensation statique des rotations libérées R : k' = k_ff − k_fR k_RR⁻¹ k_Rf,
// p' = p_f − k_fR k_RR⁻¹ p_R. Lignes et colonnes libérées mises à zéro.
function condense(k, p, R) {
    if (!R.length) return { k, p, inv: null };
    const kRR = R.map(i => R.map(j => k[i][j]));
    const inv = R.length === 1 ? [[1 / kRR[0][0]]] : (() => {
        const det = kRR[0][0] * kRR[1][1] - kRR[0][1] * kRR[1][0];
        return [[kRR[1][1] / det, -kRR[0][1] / det], [-kRR[1][0] / det, kRR[0][0] / det]];
    })();
    const k2 = k.map(r => r.slice()), p2 = p.slice();
    for (let i = 0; i < 6; i++) {
        if (R.includes(i)) continue;
        for (let j = 0; j < 6; j++) {
            if (R.includes(j)) continue;
            let v = 0;
            for (let a = 0; a < R.length; a++) for (let b = 0; b < R.length; b++) v += k[i][R[a]] * inv[a][b] * k[R[b]][j];
            k2[i][j] -= v;
        }
        let w = 0;
        for (let a = 0; a < R.length; a++) for (let b = 0; b < R.length; b++) w += k[i][R[a]] * inv[a][b] * p[R[b]];
        p2[i] -= w;
    }
    for (const r of R) { for (let j = 0; j < 6; j++) { k2[r][j] = 0; k2[j][r] = 0; } p2[r] = 0; }
    return { k: k2, p: p2, inv };
}

// ─── Résolution (méthode des déplacements) ────────────────────────────────────
// m = { type, nodes, bars, supports, loads, barLoads, selfWeight,
//       sections[k], E[k], rho[k] }   (unités SI ; g = 9,81 m/s²)
// Retourne { ok, U, nd, reactions, barRes, loadsEff } ou { ok:false, error }.
function solveStructure(m) {
    const { type, nodes, bars, supports } = m;
    const nd = type === 'treillis' ? 2 : 3;
    const nD = nd * nodes.length;
    const K = Array.from({ length: nD }, () => new Float64Array(nD));
    const F = new Float64Array(nD);
    const G = 9.81;

    // Charges nodales effectives (en treillis, le poids propre est réparti aux nœuds)
    const loadsEff = m.loads.map(l => ({ ...l }));
    // Charges réparties par barre (globales, N/m) : saisies + poids propre en portique
    const q = bars.map(() => ({ qx: 0, qy: 0 }));
    if (type === 'portique') for (const bl of (m.barLoads || [])) {
        if (!q[bl.bar]) continue;
        q[bl.bar].qx += bl.qx || 0; q[bl.bar].qy += bl.qy || 0;
    }
    if (m.selfWeight) bars.forEach((b, k) => {
        const w = m.rho[k] * m.sections[k].area * G;          // N/m
        if (type === 'portique') q[k].qy -= w;
        else {
            const L = barGeom(nodes, b).L;
            loadsEff.push({ node: b.n1, Fx: 0, Fy: -w * L / 2, Mz: 0, weight: true },
                          { node: b.n2, Fx: 0, Fy: -w * L / 2, Mz: 0, weight: true });
        }
    });

    // Éléments
    const elems = bars.map((b, k) => {
        const { L, c, s } = barGeom(nodes, b);
        const E = m.E[k], sec = m.sections[k];
        if (type === 'treillis') {
            const kk = E * sec.area / L;
            const r1 = [c * c, c * s, -c * c, -c * s], r2 = [c * s, s * s, -c * s, -s * s];
            const Kg = [r1, r2, r1.map(v => -v), r2.map(v => -v)].map(r => r.map(v => kk * v));
            const dofs = [2 * b.n1, 2 * b.n1 + 1, 2 * b.n2, 2 * b.n2 + 1];
            for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) K[dofs[i]][dofs[j]] += Kg[i][j];
            return { L, c, s, E, sec, dofs };
        }
        const qa = q[k].qx * c + q[k].qy * s, qt = -q[k].qx * s + q[k].qy * c;
        const kl = frameLocalK(E, sec, L), pl = fixedEndLoads(qa, qt, L);
        const R = releasedEnds(type, b);
        const cd = condense(kl, pl, R);
        const T = [[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
                   [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]];
        const Kg = Array.from({ length: 6 }, (_, i) => Array.from({ length: 6 }, (_, j) => {
            let v = 0;
            for (let a = 0; a < 6; a++) for (let bb = 0; bb < 6; bb++) v += T[a][i] * cd.k[a][bb] * T[bb][j];
            return v;
        }));
        const pg = fromLocal(c, s, cd.p);
        const dofs = [3 * b.n1, 3 * b.n1 + 1, 3 * b.n1 + 2, 3 * b.n2, 3 * b.n2 + 1, 3 * b.n2 + 2];
        for (let i = 0; i < 6; i++) {
            F[dofs[i]] += pg[i];
            for (let j = 0; j < 6; j++) K[dofs[i]][dofs[j]] += Kg[i][j];
        }
        return { L, c, s, E, sec, dofs, qa, qt, kl, pl, R, inv: cd.inv };
    });

    for (const l of loadsEff) {
        F[nd * l.node] += l.Fx || 0;
        F[nd * l.node + 1] += l.Fy || 0;
        if (nd === 3) F[3 * l.node + 2] += l.Mz || 0;
    }

    // Degrés de liberté bloqués, et rotations sans rigidité (nœud entièrement articulé)
    const blocked = new Uint8Array(nD);
    for (const sp of supports) for (const d of supportDofs(type, sp)) blocked[nd * sp.node + d] = 1;
    const scale = Math.max(...[...Array(nD).keys()].map(i => Math.abs(K[i][i])), 1e-30);
    const dropped = new Uint8Array(nD);
    if (nd === 3) for (let i = 0; i < nodes.length; i++) {
        const r = 3 * i + 2;
        if (!blocked[r] && Math.abs(K[r][r]) < 1e-12 * scale) {
            if (Math.abs(F[r]) > 1e-9)
                return { ok: false, error: `un couple est appliqué au nœud ${nodeName(i)}, où toutes les barres sont articulées.` };
            dropped[r] = 1;
        }
    }
    const free = [...Array(nD).keys()].filter(i => !blocked[i] && !dropped[i]);
    const nf = free.length;

    // Système réduit, élimination de Gauss avec pivot partiel
    const A = free.map(i => free.map(j => K[i][j]));
    const rhs = free.map(i => F[i]);
    for (let col = 0; col < nf; col++) {
        let piv = col;
        for (let r = col + 1; r < nf; r++) if (Math.abs(A[r][col]) > Math.abs(A[piv][col])) piv = r;
        if (Math.abs(A[piv][col]) < 1e-9 * scale)
            return { ok: false, mechanism: true,
                     error: 'la structure est un mécanisme : elle peut bouger sans déformer ses barres.' };
        [A[col], A[piv]] = [A[piv], A[col]]; [rhs[col], rhs[piv]] = [rhs[piv], rhs[col]];
        for (let r = col + 1; r < nf; r++) {
            const f = A[r][col] / A[col][col];
            if (f === 0) continue;
            for (let j = col; j < nf; j++) A[r][j] -= f * A[col][j];
            rhs[r] -= f * rhs[col];
        }
    }
    const x = new Float64Array(nf);
    for (let i = nf - 1; i >= 0; i--) {
        let v = rhs[i];
        for (let j = i + 1; j < nf; j++) v -= A[i][j] * x[j];
        x[i] = v / A[i][i];
    }
    const U = new Float64Array(nD);
    free.forEach((i, k) => { U[i] = x[k]; });

    // Réactions : R = K·U − F aux degrés de liberté bloqués
    const reactions = supports.map(sp => {
        const r = { node: sp.node, Rx: 0, Ry: 0, Mz: 0 };
        for (const d of supportDofs(type, sp)) {
            const i = nd * sp.node + d;
            let v = -F[i];
            for (let j = 0; j < nD; j++) v += K[i][j] * U[j];
            r[['Rx', 'Ry', 'Mz'][d]] = v;
        }
        return r;
    });

    // Efforts dans les barres : fonctions N(s), V(s), M(s) le long de la barre
    const barRes = bars.map((b, k) => {
        const el = elems[k];
        const { L, c, s, E, sec } = el;
        if (type === 'treillis') {
            const du = (U[el.dofs[2]] - U[el.dofs[0]]) * c + (U[el.dofs[3]] - U[el.dofs[1]]) * s;
            const N = E * sec.area / L * du;
            return { L, c, s, E, sec, N, N1: N, N2: N, V: 0, M1: 0, M2: 0, Mabs: 0,
                     Nat: () => N, Vat: () => 0, Mat: () => 0 };
        }
        const ul = toLocal(c, s, el.dofs.map(i => U[i]));
        // rotations d'extrémité libérées (rotule) : u_R = k_RR⁻¹ (p_R − k_Rf u_f)
        if (el.R.length) {
            const rhsR = el.R.map(r => el.pl[r] - [0, 1, 2, 3, 4, 5].filter(j => !el.R.includes(j))
                .reduce((acc, j) => acc + el.kl[r][j] * ul[j], 0));
            el.R.forEach((r, a) => { ul[r] = el.R.reduce((acc, _, bb) => acc + el.inv[a][bb] * rhsR[bb], 0); });
        }
        // efforts exercés par les nœuds sur la barre : f = k·u − p
        const f = el.kl.map((row, i) => row.reduce((acc, v, j) => acc + v * ul[j], 0) - el.pl[i]);
        const { qa, qt } = el;
        const Nat = t => -f[0] - qa * t;
        const Vat = t => -f[1] - qt * t;
        const Mat = t => -f[2] + f[1] * t + qt * t * t / 2;
        // |M| maximal : extrémités et point où V s'annule
        const cand = [0, L];
        if (Math.abs(qt) > 1e-12) { const t0 = -f[1] / qt; if (t0 > 0 && t0 < L) cand.push(t0); }
        const Mabs = Math.max(...cand.map(t => Math.abs(Mat(t))));
        return { L, c, s, E, sec, ul, qa, qt, f,
                 N: Nat(0), N1: Nat(0), N2: Nat(L), V: Vat(0), M1: Mat(0), M2: Mat(L), Mabs, Nat, Vat, Mat };
    });

    return { ok: true, U, nd, reactions, barRes, loadsEff, q, dropped };
}

// ─── Contrainte maximale : |N|/A + |M|·v/I, v = distance de G à la fibre extrême ─
function maxStress(br) {
    const sec = br.sec, v = Math.max(sec.zc, sec.height - sec.zc);
    const Nmax = Math.max(Math.abs(br.N1), Math.abs(br.N2));
    return Nmax / sec.area + (sec.Iz > 0 ? br.Mabs * v / sec.Iz : 0);
}

// ─── Flambement d'Euler (barre bi-articulée, longueur de flambement = L) ──────
// N : effort normal le plus comprimé de la barre
function bucklingCheck(E, sec, L, N) {
    const Imin = Math.min(sec.Iz, sec.Iy > 0 ? sec.Iy : sec.Iz);
    const Ncr = Math.PI ** 2 * E * Imin / (L * L);
    return { Ncr, safety: N < 0 && Ncr > 0 ? Ncr / -N : null };
}

// ─── Équilibre des nœuds (treillis) ───────────────────────────────────────────
// Pour chaque nœud : termes de ΣFx et ΣFy. Une barre tendue tire sur le nœud,
// dans la direction de son autre extrémité. loads : charges nodales effectives.
function nodeEquilibrium(nodes, bars, supports, loads, res) {
    return nodes.map((nd, i) => {
        const terms = [];
        bars.forEach((b, k) => {
            if (b.n1 !== i && b.n2 !== i) return;
            const o = nodes[b.n1 === i ? b.n2 : b.n1];
            const ang = Math.atan2(o.y - nd.y, o.x - nd.x);
            terms.push({ kind: 'bar', name: barName(b), N: res.barRes[k].N,
                         deg: ang * 180 / Math.PI, cx: Math.cos(ang), cy: Math.sin(ang) });
        });
        const ext = loads.filter(l => l.node === i)
            .reduce((a, l) => ({ Fx: a.Fx + (l.Fx || 0), Fy: a.Fy + (l.Fy || 0) }), { Fx: 0, Fy: 0 });
        const r = res.reactions.find(q => q.node === i);
        const sx = terms.reduce((a, t) => a + t.N * t.cx, 0) + ext.Fx + (r ? r.Rx : 0);
        const sy = terms.reduce((a, t) => a + t.N * t.cy, 0) + ext.Fy + (r ? r.Ry : 0);
        return { node: i, terms, ext, reaction: r || null, sx, sy };
    });
}

// ─── Déformée d'une barre (points globaux, amplification amp) ─────────────────
// Portique : Hermite sur les déplacements d'extrémité de la barre (rotations libérées
// comprises) + solution particulière bi-encastrée sous la charge répartie.
function deformedBar(type, nodes, b, br, U, nd, amp, nSeg = 16) {
    const p = nodes[b.n1];
    const { L, c, s } = br;
    if (type === 'treillis') {
        const q = nodes[b.n2];
        return [[p.x + amp * U[nd * b.n1], p.y + amp * U[nd * b.n1 + 1]],
                [q.x + amp * U[nd * b.n2], q.y + amp * U[nd * b.n2 + 1]]];
    }
    const u = br.ul, EI = br.E * br.sec.Iz, EA = br.E * br.sec.area;
    const pts = [];
    for (let k = 0; k <= nSeg; k++) {
        const t = k / nSeg, xs = t * L;
        const ua = u[0] * (1 - t) + u[3] * t + br.qa * xs * (L - xs) / (2 * EA);
        const h1 = 1 - 3 * t * t + 2 * t ** 3, h2 = L * (t - 2 * t * t + t ** 3),
              h3 = 3 * t * t - 2 * t ** 3,     h4 = L * (t ** 3 - t * t);
        const v = h1 * u[1] + h2 * u[2] + h3 * u[4] + h4 * u[5] + br.qt * xs * xs * (L - xs) ** 2 / (24 * EI);
        const lx = xs + amp * ua, ly = amp * v;
        pts.push([p.x + lx * c - ly * s, p.y + lx * s + ly * c]);
    }
    return pts;
}
