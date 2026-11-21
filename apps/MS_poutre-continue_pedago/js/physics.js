'use strict';

const PI = Math.PI;

// ─── Bases de données profilés ────────────────────────────────────────────────
// n, A[cm²], h[mm], b[mm], Iz[cm⁴], Iy[cm⁴], tf[mm], tw[mm]
const IPE_DB = [
    {n:  80, A:  7.64, h:  80, b:  46, Iz:    80.1, Iy:    8.49, tf:  5.2, tw:  3.8},
    {n: 100, A: 10.30, h: 100, b:  55, Iz:   171.0, Iy:   15.90, tf:  5.7, tw:  4.1},
    {n: 120, A: 13.20, h: 120, b:  64, Iz:   318.0, Iy:   27.70, tf:  6.3, tw:  4.4},
    {n: 140, A: 16.40, h: 140, b:  73, Iz:   541.0, Iy:   44.90, tf:  6.9, tw:  4.7},
    {n: 160, A: 20.10, h: 160, b:  82, Iz:   869.0, Iy:   68.30, tf:  7.4, tw:  5.0},
    {n: 180, A: 23.90, h: 180, b:  91, Iz:  1317.0, Iy:  100.90, tf:  8.0, tw:  5.3},
    {n: 200, A: 28.50, h: 200, b: 100, Iz:  1943.0, Iy:  142.40, tf:  8.5, tw:  5.6},
    {n: 220, A: 33.40, h: 220, b: 110, Iz:  2772.0, Iy:  204.90, tf:  9.2, tw:  5.9},
    {n: 240, A: 39.10, h: 240, b: 120, Iz:  3892.0, Iy:  283.60, tf:  9.8, tw:  6.2},
    {n: 270, A: 45.90, h: 270, b: 135, Iz:  5790.0, Iy:  419.90, tf: 10.2, tw:  6.6},
    {n: 300, A: 53.80, h: 300, b: 150, Iz:  8356.0, Iy:  603.80, tf: 10.7, tw:  7.1},
    {n: 330, A: 62.60, h: 330, b: 160, Iz: 11770.0, Iy:  788.10, tf: 11.5, tw:  7.5},
    {n: 360, A: 72.70, h: 360, b: 170, Iz: 16270.0, Iy: 1043.00, tf: 12.7, tw:  8.0},
    {n: 400, A: 84.50, h: 400, b: 180, Iz: 23130.0, Iy: 1318.00, tf: 13.5, tw:  8.6},
    {n: 450, A: 98.80, h: 450, b: 190, Iz: 33740.0, Iy: 1676.00, tf: 14.6, tw:  9.4},
    {n: 500, A:115.50, h: 500, b: 200, Iz: 48200.0, Iy: 2142.00, tf: 16.0, tw: 10.2},
    {n: 550, A:134.40, h: 550, b: 210, Iz: 67120.0, Iy: 2668.00, tf: 17.2, tw: 11.1},
    {n: 600, A:156.00, h: 600, b: 220, Iz: 92080.0, Iy: 3387.00, tf: 19.0, tw: 12.0},
];

// n, A[cm²], h[mm], b[mm], Iz[cm⁴], Iy[cm⁴], e[mm], tf[mm], tw[mm]
const UPE_DB = [
    {n:  80, A:  8.80, h:  80, b:  50, Iz:  106.0, Iy:  19.4, e: 15.7, tf:  7.5, tw:  5.0},
    {n: 100, A: 11.50, h: 100, b:  55, Iz:  207.0, Iy:  29.3, e: 16.6, tf:  8.5, tw:  5.5},
    {n: 120, A: 14.20, h: 120, b:  60, Iz:  364.0, Iy:  43.2, e: 17.5, tf:  9.5, tw:  6.0},
    {n: 140, A: 17.20, h: 140, b:  65, Iz:  592.0, Iy:  62.2, e: 18.4, tf: 10.5, tw:  6.5},
    {n: 160, A: 20.30, h: 160, b:  74, Iz:  926.0, Iy:  96.5, e: 21.3, tf: 11.5, tw:  7.0},
    {n: 180, A: 23.90, h: 180, b:  80, Iz: 1380.0, Iy: 128.0, e: 22.6, tf: 12.0, tw:  7.5},
    {n: 200, A: 28.40, h: 200, b:  80, Iz: 1950.0, Iy: 137.0, e: 20.4, tf: 13.0, tw:  8.0},
    {n: 220, A: 34.40, h: 220, b:  85, Iz: 2830.0, Iy: 163.0, e: 20.9, tf: 14.0, tw:  8.5},
    {n: 240, A: 39.70, h: 240, b:  85, Iz: 3920.0, Iy: 177.0, e: 20.3, tf: 15.0, tw:  9.0},
    {n: 270, A: 46.20, h: 270, b:  95, Iz: 5890.0, Iy: 254.0, e: 22.5, tf: 16.0, tw: 10.0},
    {n: 300, A: 54.50, h: 300, b: 100, Iz: 8550.0, Iy: 325.0, e: 23.2, tf: 17.5, tw: 11.0},
    {n: 330, A: 62.60, h: 330, b: 105, Iz:11690.0, Iy: 407.0, e: 24.0, tf: 18.5, tw: 11.5},
    {n: 360, A: 72.70, h: 360, b: 110, Iz:16110.0, Iy: 510.0, e: 24.7, tf: 20.0, tw: 12.0},
    {n: 400, A: 84.50, h: 400, b: 115, Iz:23440.0, Iy: 651.0, e: 25.4, tf: 21.0, tw: 13.5},
];

// ─── Factories de section ─────────────────────────────────────────────────────

function makeSectionRect(b, h) {
    return {
        type: 'rect', b, h,
        area: b * h,
        Iz: b * h * h * h / 12,
        Iy: h * b * b * b / 12,
        height: h,
        zc: h / 2,
        name: `Rectangle ${fmt(b*1000,0)}×${fmt(h*1000,0)} mm`,
        widthAt(z) { return (z >= 0 && z <= h) ? b : 0; },
        keyZValues() { return [0, h]; }
    };
}

function makeSectionCirc(d) {
    const r = d / 2;
    return {
        type: 'circ', d,
        area: PI * r * r,
        Iz: PI * r * r * r * r / 4,
        Iy: PI * r * r * r * r / 4,
        height: d,
        zc: r,
        name: `Circulaire ⌀${fmt(d*1000,0)} mm`,
        widthAt(z) {
            const dz = z - r;
            return (Math.abs(dz) < r) ? 2 * Math.sqrt(r*r - dz*dz) : 0;
        },
        keyZValues() { return [0, d]; }
    };
}

function makeSectionProfile(type, number, orient) {
    const db = (type === 'IPE') ? IPE_DB : UPE_DB;
    const d = db.find(e => e.n === number);
    if (!d) throw new Error(`${type} ${number} inconnu`);

    const A_m2  = d.A  * 1e-4;
    const h_m   = d.h  * 1e-3;
    const b_m   = d.b  * 1e-3;
    const Iz_m4 = d.Iz * 1e-8;
    const Iy_m4 = d.Iy * 1e-8;
    const tf_m  = d.tf * 1e-3;
    const tw_m  = d.tw * 1e-3;
    const e_m   = d.e  ? d.e * 1e-3 : h_m / 2;

    let sec = { type: 'profile', profType: type, number, orient,
                area: A_m2, h_: h_m, b_: b_m, tf_: tf_m, tw_: tw_m, e_: e_m };

    if (type === 'IPE') {
        if (orient === 'I') {
            Object.assign(sec, { Iz: Iz_m4, Iy: Iy_m4, height: h_m, zc: h_m / 2,
                name: `IPE ${number} (I)` });
            sec.widthAt = function(z) {
                if (z < 0 || z > h_m) return 0;
                if (z <= tf_m || z >= h_m - tf_m) return b_m;
                return tw_m;
            };
            sec.keyZValues = () => [0, tf_m, h_m - tf_m, h_m];
        } else { // 'H' - couché
            Object.assign(sec, { Iz: Iy_m4, Iy: Iz_m4, height: b_m, zc: b_m / 2,
                name: `IPE ${number} (H)` });
            sec.widthAt = function(z) {
                if (z < 0 || z > b_m) return 0;
                const center = b_m / 2;
                return (Math.abs(z - center) <= tw_m / 2) ? h_m : 2 * tf_m;
            };
            sec.keyZValues = () => [0, b_m/2 - tw_m/2, b_m/2 + tw_m/2, b_m];
        }
    } else { // UPE
        if (orient === 'C') {
            Object.assign(sec, { Iz: Iz_m4, Iy: Iy_m4, height: h_m, zc: h_m / 2,
                name: `UPE ${number} (C)` });
            sec.widthAt = function(z) {
                if (z < 0 || z > h_m) return 0;
                if (z <= tf_m || z >= h_m - tf_m) return tw_m + b_m;
                return tw_m;
            };
            sec.keyZValues = () => [0, tf_m, h_m - tf_m, h_m];
        } else if (orient === 'U') {
            // âme en bas, semelles pointant vers le haut
            Object.assign(sec, { Iz: Iy_m4, Iy: Iz_m4, height: b_m, zc: e_m,
                name: `UPE ${number} (U)` });
            sec.widthAt = function(z) {
                if (z < 0 || z > b_m) return 0;
                return (z <= tw_m) ? h_m : 2 * tf_m;
            };
            sec.keyZValues = () => [0, tw_m, b_m];
        } else { // 'Ui' - âme en haut, semelles pointant vers le bas
            Object.assign(sec, { Iz: Iy_m4, Iy: Iz_m4, height: b_m, zc: b_m - e_m,
                name: `UPE ${number} (Ui)` });
            sec.widthAt = function(z) {
                if (z < 0 || z > b_m) return 0;
                return (z >= b_m - tw_m) ? h_m : 2 * tf_m;
            };
            sec.keyZValues = () => [0, b_m - tw_m, b_m];
        }
    }
    return sec;
}

function makeSectionComposite() {
    const sec = {
        type: 'composite',
        pieces: [],
        area: 0, Iz: 0, Iy: 0, height: 0, zc: 0,
        _zmin: 0, _zmax: 0, _ymin: 0, _ymax: 0,
        name: 'Section composée',

        addRect(add, y1, z1, y2, z2) {
            if (y1 > y2) [y1, y2] = [y2, y1];
            if (z1 > z2) [z1, z2] = [z2, z1];
            this.pieces.push({ add, shape: 'rect', y1, z1, y2, z2 });
        },

        addCirc(add, cy, cz, r) {
            this.pieces.push({ add, shape: 'circ', y1: cy, z1: cz, y2: Math.abs(r), z2: 0 });
        },

        finalise() {
            let zmin = Infinity, zmax = -Infinity, ymin = Infinity, ymax = -Infinity;
            for (const p of this.pieces) {
                if (!p.add) continue;
                let pz1, pz2, py1, py2;
                if (p.shape === 'rect') {
                    py1 = p.y1; py2 = p.y2; pz1 = p.z1; pz2 = p.z2;
                } else {
                    const r = p.y2;
                    py1 = p.y1 - r; py2 = p.y1 + r;
                    pz1 = p.z1 - r; pz2 = p.z1 + r;
                }
                zmin = Math.min(zmin, pz1); zmax = Math.max(zmax, pz2);
                ymin = Math.min(ymin, py1); ymax = Math.max(ymax, py2);
            }
            if (!isFinite(zmin)) zmin = zmax = ymin = ymax = 0;
            this._zmin = zmin; this._zmax = zmax;
            this._ymin = ymin; this._ymax = ymax;
            this.height = zmax - zmin;

            let sumA = 0, sumAz = 0, sumAy = 0;
            for (const p of this.pieces) {
                const sign = p.add ? 1 : -1;
                let a, yc, zc;
                if (p.shape === 'rect') {
                    a = (p.y2 - p.y1) * (p.z2 - p.z1);
                    yc = (p.y1 + p.y2) / 2; zc = (p.z1 + p.z2) / 2;
                } else {
                    const r = p.y2;
                    a = PI * r * r; yc = p.y1; zc = p.z1;
                }
                sumA += sign * a; sumAz += sign * a * zc; sumAy += sign * a * yc;
            }
            this.area = sumA;
            const zG = Math.abs(sumA) > 1e-20 ? sumAz / sumA : 0;
            const yG = Math.abs(sumA) > 1e-20 ? sumAy / sumA : 0;

            let iz = 0, iy = 0;
            for (const p of this.pieces) {
                const sign = p.add ? 1 : -1;
                let a, yc, zc, iz_own, iy_own;
                if (p.shape === 'rect') {
                    const bw = p.y2 - p.y1, bh = p.z2 - p.z1;
                    a = bw * bh; yc = (p.y1+p.y2)/2; zc = (p.z1+p.z2)/2;
                    iz_own = bw * bh*bh*bh / 12; iy_own = bh * bw*bw*bw / 12;
                } else {
                    const r = p.y2;
                    a = PI*r*r; yc = p.y1; zc = p.z1;
                    iz_own = PI*r*r*r*r/4; iy_own = iz_own;
                }
                const dz = zc - zG, dy = yc - yG;
                iz += sign * (iz_own + a * dz*dz);
                iy += sign * (iy_own + a * dy*dy);
            }
            this.Iz = iz; this.Iy = iy;
            this.zc = zG - zmin;
            this.name = `Section composée (${this.pieces.length} pièces)`;
        },

        widthAt(z) {
            const z_abs = z + this._zmin;
            let w = 0;
            for (const p of this.pieces) {
                let c = 0;
                if (p.shape === 'rect') {
                    if (z_abs >= p.z1 && z_abs <= p.z2) c = p.y2 - p.y1;
                } else {
                    const r = p.y2, dz = z_abs - p.z1;
                    if (Math.abs(dz) < r) c = 2 * Math.sqrt(r*r - dz*dz);
                }
                w += p.add ? c : -c;
            }
            return Math.max(0, w);
        },

        keyZValues() {
            const keys = new Set([0, this.height]);
            for (const p of this.pieces)
                if (p.shape === 'rect') {
                    keys.add(p.z1 - this._zmin);
                    keys.add(p.z2 - this._zmin);
                }
            return [...keys].sort((a, b) => a - b);
        }
    };
    return sec;
}

function makeSectionCustom(A, Iz, Iy, h) {
    const avgWidth = h > 0 ? A / h : 0;
    return {
        type: 'custom',
        area: A, Iz, Iy,
        height: h, zc: h / 2,
        name: 'Section custom',
        widthAt(z) { return (z >= 0 && z <= h) ? avgWidth : 0; },
        keyZValues() { return [0, h]; }
    };
}

// ─── Premier moment statique S(z) pour Jourawski ──────────────────────────────
// S(z) = ∫_z^h (ξ - zc) * b(ξ) dξ  (aire au-dessus de z)
//
// Stratégie : on utilise les keyZValues comme bornes de segments afin qu'aucun
// sous-intervalle ne straddl une discontinuité de largeur.  Dans chaque segment
// on applique la règle du point-milieu avec SUB sous-intervalles :
//   • SUB points sur un segment à b constant → résultat exact (tous les zm
//     donnent la même largeur, la somme se réduit à b·Δz·(zm_seg − zc)).
//   • SUB points sur un segment à b variable (partie circulaire) → précis.
function computeSz(sec, z) {
    const h = sec.height;
    if (z >= h) return 0;
    if (z < 0) z = 0;
    const zc = sec.zc;

    const keys = (sec.keyZValues ? sec.keyZValues() : [0, h])
        .map(Number)
        .filter(k => k > z && k < h)
        .sort((a, b) => a - b);
    const bounds = [z, ...keys, h];

    const SUB = 8;
    let S = 0;
    for (let i = 0; i + 1 < bounds.length; i++) {
        const z1 = bounds[i], z2 = bounds[i + 1];
        if (z2 - z1 < 1e-15) continue;
        const dz = (z2 - z1) / SUB;
        for (let j = 0; j < SUB; j++) {
            const zm = z1 + (j + 0.5) * dz;
            S += sec.widthAt(zm) * dz * (zm - zc);
        }
    }
    return S;
}

// ─── Solveur statique isostatique ─────────────────────────────────────────────
// supports: [{type: 'roller'|'pin'|'fixed', x}]
// loads: [{type:'force', x, Fy, Fx}]
//         [{type:'moment', x, Mz}]
//         [{type:'distributed', x1, x2, qy, qx}]

function gauss3(A, b) {
    const M = A.map((row, i) => [...row, b[i]]);
    for (let col = 0; col < 3; col++) {
        let pivot = col;
        for (let row = col+1; row < 3; row++)
            if (Math.abs(M[row][col]) > Math.abs(M[pivot][col])) pivot = row;
        [M[col], M[pivot]] = [M[pivot], M[col]];
        if (Math.abs(M[col][col]) < 1e-14) return null;
        for (let row = col+1; row < 3; row++) {
            const f = M[row][col] / M[col][col];
            for (let k = col; k <= 3; k++) M[row][k] -= f * M[col][k];
        }
    }
    const x = [0, 0, 0];
    for (let i = 2; i >= 0; i--) {
        x[i] = M[i][3];
        for (let j = i+1; j < 3; j++) x[i] -= M[i][j] * x[j];
        x[i] /= M[i][i];
    }
    return x;
}

function solveReactions(supports, loads) {
    const unknowns = [];
    for (let i = 0; i < supports.length; i++) {
        const s = supports[i];
        if (s.type === 'roller') {
            unknowns.push({si: i, comp: 1});
        } else if (s.type === 'pin') {
            unknowns.push({si: i, comp: 0});
            unknowns.push({si: i, comp: 1});
        } else { // fixed
            unknowns.push({si: i, comp: 0});
            unknowns.push({si: i, comp: 1});
            unknowns.push({si: i, comp: 2});
        }
    }
    if (unknowns.length !== 3)
        return { ok: false, error: `Nombre d'inconnues = ${unknowns.length} (attendu 3 pour une poutre isostatique)` };

    const A = [[0,0,0],[0,0,0],[0,0,0]];
    for (let j = 0; j < 3; j++) {
        const {si, comp} = unknowns[j];
        const xs = supports[si].x;
        if (comp === 0) { A[0][j] = 1; }
        else if (comp === 1) { A[1][j] = 1; A[2][j] = xs; }
        else { A[2][j] = 1; }
    }

    let sumFx = 0, sumFy = 0, sumMz = 0;
    for (const l of loads) {
        if (l.type === 'force') {
            sumFx += (l.Fx || 0);
            sumFy += l.Fy;
            sumMz += l.Fy * l.x;
        } else if (l.type === 'moment') {
            sumMz += l.Mz;
        } else { // distributed
            const len = l.x2 - l.x1;
            const xmid = (l.x1 + l.x2) / 2;
            sumFx += (l.qx || 0) * len;
            sumFy += l.qy * len;
            sumMz += l.qy * len * xmid;
        }
    }

    const sol = gauss3(A, [-sumFx, -sumFy, -sumMz]);
    if (!sol) return { ok: false, error: 'Système singulier (structure géométriquement variable ?)' };

    const reactions = supports.map(s => ({x: s.x, Rx: 0, Ry: 0, Mz: 0}));
    for (let j = 0; j < 3; j++) {
        const {si, comp} = unknowns[j];
        if (comp === 0) reactions[si].Rx = sol[j];
        else if (comp === 1) reactions[si].Ry = sol[j];
        else reactions[si].Mz = sol[j];
    }
    return { ok: true, reactions };
}

// ─── N, V, M en un point x ───────────────────────────────────────────────────
function computeAtX(supports, loads, reactions, x) {
    let N = 0, V = 0, M = 0;
    for (const rxn of reactions) {
        if (rxn.x <= x) {
            N += rxn.Rx;
            V += rxn.Ry;
            M += rxn.Ry * (x - rxn.x) - rxn.Mz;
        }
    }
    for (const l of loads) {
        if (l.type === 'force') {
            if (l.x <= x) {
                N += (l.Fx || 0);
                V += l.Fy;
                M += l.Fy * (x - l.x);
            }
        } else if (l.type === 'moment') {
            if (l.x <= x) M -= l.Mz;
        } else { // distributed
            if (l.x1 >= x) continue;
            const xEnd = Math.min(x, l.x2);
            const len = xEnd - l.x1;
            const xc = (l.x1 + xEnd) / 2;
            N += (l.qx || 0) * len;
            V += l.qy * len;
            M += l.qy * len * (x - xc);
        }
    }
    return { N, V, M };
}

// ─── Diagramme N/V/M ─────────────────────────────────────────────────────────
function computeDiagram(L, supports, loads, reactions, nPts = 200) {
    const eps = 1e-9;
    const xSet = new Set();
    for (let i = 0; i <= nPts; i++) xSet.add(L * i / nPts);
    for (const s of supports) { xSet.add(Math.max(0, s.x-eps)); xSet.add(s.x); xSet.add(Math.min(L, s.x+eps)); }
    for (const l of loads) {
        const pts = l.type === 'distributed' ? [l.x1, l.x2] : [l.x];
        for (const p of pts) { xSet.add(Math.max(0,p-eps)); xSet.add(p); xSet.add(Math.min(L,p+eps)); }
    }
    const xs = [...xSet].filter(x => x >= 0 && x <= L).sort((a,b) => a-b);
    return xs.map(x => {
        const {N, V, M} = computeAtX(supports, loads, reactions, x);
        return {x, N, V, M};
    });
}

// ─── Déformée ─────────────────────────────────────────────────────────────────
function computeDeflection(diagram, section, E, supports) {
    if (!section || !E || E === 0) return null;
    const EI = E * section.Iz;
    if (EI === 0) return null;
    const n = diagram.length;

    // Intégration θ_raw par trapèzes : M/(EI)
    const theta_raw = new Float64Array(n);
    for (let i = 1; i < n; i++) {
        const dx = diagram[i].x - diagram[i-1].x;
        theta_raw[i] = theta_raw[i-1] + 0.5*(diagram[i-1].M + diagram[i].M)/EI*dx;
    }
    // Intégration v_raw par trapèzes
    const v_raw = new Float64Array(n);
    for (let i = 1; i < n; i++) {
        const dx = diagram[i].x - diagram[i-1].x;
        v_raw[i] = v_raw[i-1] + 0.5*(theta_raw[i-1]+theta_raw[i])*dx;
    }

    const nearestIdx = xs => {
        let best = 0;
        for (let i = 1; i < n; i++)
            if (Math.abs(diagram[i].x - xs) < Math.abs(diagram[best].x - xs)) best = i;
        return best;
    };

    let C1 = 0, C2 = 0, found = false;
    const fixed = supports ? supports.find(s => s.type === 'fixed') : null;
    if (fixed) {
        const idx = nearestIdx(fixed.x);
        C1 = -theta_raw[idx];
        C2 = -(v_raw[idx] + C1 * diagram[idx].x);
        found = true;
    }
    if (!found && supports && supports.length >= 2) {
        const bcs = supports.map(s => ({idx: nearestIdx(s.x), x: s.x}));
        const i0 = bcs[0].idx, i1 = bcs[1].idx;
        const x0 = bcs[0].x, x1 = bcs[1].x;
        if (Math.abs(x1 - x0) > 1e-12)
            C1 = -(v_raw[i1] - v_raw[i0]) / (x1 - x0);
        C2 = -(v_raw[i0] + C1 * x0);
    } else if (!found && supports && supports.length === 1) {
        const idx = nearestIdx(supports[0].x);
        C2 = -(v_raw[idx] + C1 * diagram[idx].x);
    }

    return diagram.map((pt, i) => ({
        x: pt.x,
        v: v_raw[i] + C1 * pt.x + C2,
        theta: theta_raw[i] + C1
    }));
}

// ─── Profil de Navier ─────────────────────────────────────────────────────────
// Retourne {zs, sigma, tau} avec z de 0 (bas) à height (haut)
function computeNavier(sec, N, V, M, nPts = 100) {
    const h = sec.height;
    const Iz = sec.Iz;
    const A = sec.area;
    const zc = sec.zc;
    const zs = [], sigma = [], tau = [];

    // Points clés + points uniformes
    const zSet = new Set(sec.keyZValues().map(v => +v.toFixed(12)));
    for (let i = 0; i <= nPts; i++) zSet.add(+(h * i / nPts).toFixed(12));
    const sortedZ = [...zSet].sort((a, b) => a - b);

    for (const z of sortedZ) {
        // Contrainte normale : Navier σ(z) = N/A - M*(z-zc)/Iz
        const sig = (A > 0 ? N / A : 0) - M * (z - zc) / Iz;
        // Cisaillement : Jourawski τ(z)
        const b = sec.widthAt(z);
        let t = 0;
        if (b > 1e-15 && Iz > 0) {
            const Sz = computeSz(sec, z);
            t = Math.abs(V) * Math.abs(Sz) / (Iz * b);
        }
        zs.push(z); sigma.push(sig); tau.push(t);
    }
    return { zs, sigma, tau };
}

// ─── Contraintes résumées ─────────────────────────────────────────────────────
function computeStresses(diagram, section) {
    if (!section) return null;
    const { Iz, zc, height, area } = section;
    return diagram.map(pt => {
        const sig_inf =  pt.M * zc / Iz + (area > 0 ? pt.N / area : 0);
        const sig_sup = -pt.M * (height - zc) / Iz + (area > 0 ? pt.N / area : 0);
        // Jourawski au barycentre (valeur max approchée)
        const Sz_c = computeSz(section, zc);
        const bz_c = section.widthAt(zc);
        const tau = (bz_c > 1e-15 && Iz > 0)
            ? Math.abs(pt.V) * Math.abs(Sz_c) / (Iz * bz_c) : 0;
        return { x: pt.x, sig_inf, sig_sup, tau };
    });
}

// ─── Utilitaires ──────────────────────────────────────────────────────────────
function fmt(v, dec = 3) {
    if (!isFinite(v)) return '—';
    const r = v.toFixed(dec);
    return /^-0(\.0*)?$/.test(r) ? r.slice(1) : r;   // pas de « -0.00 »
}

function fmtSci(v) {
    if (Math.abs(v) < 1e-15) return '0';
    const exp = Math.floor(Math.log10(Math.abs(v)));
    if (exp >= -3 && exp <= 4) return fmt(v, Math.max(0, 3 - exp));
    return v.toExponential(3);
}
