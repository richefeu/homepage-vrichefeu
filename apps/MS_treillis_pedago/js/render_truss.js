'use strict';

// ═════════════════════════════════════════════════════════════════════════════
// Dessin des structures planes (s'appuie sur les utilitaires de render.js)
// ═════════════════════════════════════════════════════════════════════════════

// Pas de grille « rond » adapté à l'étendue de la structure
function niceStep(v) {
    for (const s of [0.1, 0.2, 0.25, 0.5, 1, 2, 2.5, 5, 10, 20]) if (s >= v) return s;
    return 50;
}

// Transformation monde (m, y vers le haut) → écran (px, y vers le bas)
// extra : marge supplémentaire (px) autour du dessin, pour les diagrammes tracés hors des barres
function makeView(el, nodes, editing, extra = 0) {
    const W = el.clientWidth || 820;
    let xs = nodes.map(n => n.x), ys = nodes.map(n => n.y);
    if (!xs.length) { xs = [0, 4]; ys = [0, 2]; }
    let x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const span = Math.max(x1 - x0, y1 - y0, 1);
    // en édition, de la place autour de la structure pour ajouter des nœuds
    const pad = editing ? 0.3 * span : 0.06 * span;
    x0 -= pad; x1 += pad; y0 -= pad; y1 += pad;
    const ML = 64 + extra, MR = 64 + extra, MT = 48 + extra, MB = (editing ? 48 : 84) + extra;
    const sc = Math.min((W - ML - MR) / (x1 - x0), 440 / (y1 - y0));
    const H = Math.max(240, (y1 - y0) * sc + MT + MB);
    const ox = ML + ((W - ML - MR) - (x1 - x0) * sc) / 2 - x0 * sc;
    const oy = MT + ((H - MT - MB) - (y1 - y0) * sc) / 2 + y1 * sc;
    return { W, H, sc, span, x0, x1, y0, y1,
             X: x => ox + x * sc, Y: y => oy - y * sc,
             toWorld: (px, py) => [(px - ox) / sc, (oy - py) / sc] };
}

// Symbole de liaison au nœud (cx, cy)
function drawSupportSymbol(svg, type, kind, cx, cy) {
    if (kind === 'XYtheta' && type === 'portique') {
        line(svg, cx - 16, cy, cx + 16, cy, C_STRUCT, 2.5);
        drawHatch(svg, cx - 15, cy, cx + 15, cy + 10);
    } else if (kind === 'Y') {
        drawRoller(svg, cx, cy);
    } else if (kind === 'X') {
        const g = svgEl('g', { transform: `rotate(90 ${cx} ${cy})` });
        drawRoller(g, cx, cy);
        svg.appendChild(g);
    } else {
        drawPin(svg, cx, cy);
    }
}

// ─── Schéma de la structure ───────────────────────────────────────────────────
// d = { type, nodes, bars, supports, loads, res, mode, pending, showDeformed }
// Retourne la vue (pour convertir un clic en coordonnées).
function renderStructure(el, d) {
    const editing = d.mode === 'node' || d.mode === 'bar';
    const v = makeView(el, d.nodes, editing);
    const svg = svgRoot(v.W, v.H);
    svg.classList.add(editing ? 'editing' : 'viewing');
    const defs = svgEl('defs');
    arrowMarker(defs, 'arr-load', C_LOAD);
    arrowMarker(defs, 'arr-moment-ccw', C_LOAD);
    arrowMarker(defs, 'arr-moment-cw', C_LOAD);
    svg.appendChild(defs);
    svg.appendChild(svgEl('rect', { x: 0, y: 0, width: v.W, height: v.H, fill: 'transparent' }));

    // Grille d'édition (pas d'accrochage)
    if (editing) {
        const st = niceStep(v.span / 12);
        for (let x = Math.ceil(v.x0 / st) * st; x <= v.x1; x += st)
            line(svg, v.X(x), v.Y(v.y0), v.X(x), v.Y(v.y1), Math.abs(x) < 1e-9 ? '#d7dbe2' : '#eef0f3', 1);
        for (let y = Math.ceil(v.y0 / st) * st; y <= v.y1; y += st)
            line(svg, v.X(v.x0), v.Y(y), v.X(v.x1), v.Y(y), Math.abs(y) < 1e-9 ? '#d7dbe2' : '#eef0f3', 1);
        text(svg, v.W - 8, v.H - 8, `grille : ${fmtLbl(st)} m`, 'end', 11, C_MUTED);
    }

    const res = d.res, truss = d.type === 'treillis';
    const Nmax = res ? Math.max(...res.barRes.map(b => Math.abs(b.N)), 1e-9) : 1;

    // Barres
    d.bars.forEach((b, k) => {
        const p = d.nodes[b.n1], q = d.nodes[b.n2];
        if (!p || !q) return;
        let col = C_STRUCT, w = 4, extra = {};
        if (res && truss) {
            const N = res.barRes[k].N;
            if (Math.abs(N) < 1e-6 * Nmax) { col = C_AXIS; extra = { 'stroke-dasharray': '7,5' }; }
            else col = N > 0 ? C_POS : C_NEG;
        }
        line(svg, v.X(p.x), v.Y(p.y), v.X(q.x), v.Y(q.y), col, w, { 'stroke-linecap': 'round', ...extra });
    });

    // Déformée amplifiée
    if (res && d.showDeformed) {
        const nd = res.nd;
        // déplacement maximal, y compris entre les nœuds (flexion sous charge répartie)
        let umax = 0;
        d.bars.forEach((b, k) => {
            const p = d.nodes[b.n1], q = d.nodes[b.n2];
            const pts = deformedBar(d.type, d.nodes, b, res.barRes[k], res.U, nd, 1);
            pts.forEach(([x, y], j) => {
                const t = j / (pts.length - 1);
                umax = Math.max(umax, Math.hypot(x - (p.x + (q.x - p.x) * t), y - (p.y + (q.y - p.y) * t)));
            });
        });
        if (umax > 0) {
            const raw = 0.08 * v.span / umax;
            const amp = raw > 1 ? Math.round(raw / 10 ** Math.floor(Math.log10(raw))) * 10 ** Math.floor(Math.log10(raw)) : raw;
            d.bars.forEach((b, k) => {
                const pts = deformedBar(d.type, d.nodes, b, res.barRes[k], res.U, nd, amp);
                svg.appendChild(svgEl('polyline', {
                    points: pts.map(([x, y]) => `${v.X(x)},${v.Y(y)}`).join(' '),
                    fill: 'none', stroke: C_DEFL, 'stroke-width': 2, 'stroke-dasharray': '6,4' }));
            });
            text(svg, v.W - 8, 20, `déformée amplifiée × ${amp >= 1 ? Math.round(amp) : fmtVal(amp)}`, 'end', 11, C_DEFL);
        }
    }

    // Étiquettes des barres : nom, ou effort normal après calcul (treillis)
    d.bars.forEach((b, k) => {
        const p = d.nodes[b.n1], q = d.nodes[b.n2];
        if (!p || !q) return;
        const mx = (v.X(p.x) + v.X(q.x)) / 2, my = (v.Y(p.y) + v.Y(q.y)) / 2;
        const dx = v.X(q.x) - v.X(p.x), dy = v.Y(q.y) - v.Y(p.y), l = Math.hypot(dx, dy) || 1;
        const ox = -dy / l * 13, oy = dx / l * 13;
        if (res && truss) {
            const N = res.barRes[k].N;
            const col = Math.abs(N) < 1e-6 * Nmax ? C_MUTED : N > 0 ? C_POS : C_NEG;
            txtBG(svg, mx + ox, my + oy + 4, `${fmtLbl(N / 1e3)} kN`, 'middle', 11, col, true);
        } else {
            txtBG(svg, mx + ox, my + oy + 4, barName(b), 'middle', 11, C_MUTED);
        }
    });

    // Rotules en bout de barre (portique) : petit cercle près de l'extrémité
    if (d.type === 'portique') drawHinges(svg, v, d.nodes, d.bars);

    // Charges réparties (portique) : flèches le long de la barre
    for (const bl of (d.barLoads || [])) {
        const b = d.bars[bl.bar];
        if (!b) continue;
        const qx = bl.qx || 0, qy = bl.qy || 0, qn = Math.hypot(qx, qy);
        if (qn < 1e-9) continue;
        const p = d.nodes[b.n1], q = d.nodes[b.n2];
        const P1 = [v.X(p.x), v.Y(p.y)], P2 = [v.X(q.x), v.Y(q.y)];
        const ux = qx / qn, uy = -qy / qn, len = 26;
        const nA = Math.max(3, Math.round(Math.hypot(P2[0] - P1[0], P2[1] - P1[1]) / 22));
        const tail = t => [P1[0] + (P2[0] - P1[0]) * t - ux * len, P1[1] + (P2[1] - P1[1]) * t - uy * len];
        line(svg, ...tail(0), ...tail(1), C_LOAD, 1.2);
        for (let i = 0; i <= nA; i++) {
            const t = i / nA, [tx, ty] = tail(t);
            arrowLine(svg, tx, ty, tx + ux * (len - 4), ty + uy * (len - 4), C_LOAD, 'arr-load', 1.2);
        }
        const [mx, my] = tail(0.5);
        txtBG(svg, mx - ux * 10, my - uy * 10 + 4, `${fmtLbl(qn / 1e3)} kN/m`, 'middle', 11, C_LOAD, true);
    }
    if (d.selfWeight) text(svg, 10, v.H - 8, '+ poids propre des barres', 'start', 11, C_LOAD);

    // Liaisons
    for (const sp of d.supports) {
        const n = d.nodes[sp.node];
        if (n) drawSupportSymbol(svg, d.type, sp.type, v.X(n.x), v.Y(n.y));
    }

    // Charges nodales
    for (const l of d.loads) {
        const n = d.nodes[l.node];
        if (!n) continue;
        const cx = v.X(n.x), cy = v.Y(n.y);
        const F = Math.hypot(l.Fx || 0, l.Fy || 0);
        if (F > 1e-9) {
            const ux = (l.Fx || 0) / F, uy = -(l.Fy || 0) / F;    // direction écran
            // Flèche « entrante » (pointe sur le nœud), sauf si une barre arrive
            // de ce côté : la flèche part alors du nœud pour ne pas la masquer.
            const blocked = d.bars.some(b => {
                if (b.n1 !== l.node && b.n2 !== l.node) return false;
                const o = d.nodes[b.n1 === l.node ? b.n2 : b.n1];
                const bx = v.X(o.x) - cx, by = v.Y(o.y) - cy, bl = Math.hypot(bx, by) || 1;
                return (-ux * bx - uy * by) / bl > Math.cos(25 * Math.PI / 180);
            });
            const [tx, ty, hx, hy] = blocked
                ? [cx + ux * 8, cy + uy * 8, cx + ux * 56, cy + uy * 56]
                : [cx - ux * 52, cy - uy * 52, cx - ux * 8, cy - uy * 8];
            arrowLine(svg, tx, ty, hx, hy, C_LOAD, 'arr-load', 2.5);
            const [lx, ly] = blocked ? [hx + ux * 12, hy + uy * 12] : [tx - ux * 10, ty - uy * 10];
            txtBG(svg, lx, ly + 4, `${fmtLbl(F / 1e3)} kN`, 'middle', 12, C_LOAD, true);
        }
        if (d.type === 'portique' && Math.abs(l.Mz || 0) > 1e-9) {
            drawMomentSymbol(svg, cx, cy, 16, l.Mz >= 0, C_LOAD);
            txtBG(svg, cx, cy - 24, `${fmtLbl(Math.abs(l.Mz) / 1e3)} kN·m`, 'middle', 12, C_LOAD, true);
        }
    }

    // Réactions (sous chaque liaison)
    if (res) {
        for (const r of res.reactions) {
            const n = d.nodes[r.node], nm = nodeName(r.node);
            const cx = v.X(n.x), cy = v.Y(n.y);
            const lines = [];
            if (Math.abs(r.Rx) > 1e-6) lines.push(`X_{${nm}} = ${fmtLbl(r.Rx / 1e3)} kN`);
            if (Math.abs(r.Ry) > 1e-6) lines.push(`Y_{${nm}} = ${fmtLbl(r.Ry / 1e3)} kN`);
            if (Math.abs(r.Mz) > 1e-6) lines.push(`M_{${nm}} = ${fmtLbl(r.Mz / 1e3)} kN·m`);
            const anc = cx < 90 ? 'start' : cx > v.W - 90 ? 'end' : 'middle';
            const lx = anc === 'start' ? cx - 20 : anc === 'end' ? cx + 20 : cx;
            lines.forEach((s, k) => txtBG(svg, lx, cy + 44 + 15 * k, s, anc, 11, C_INK));
        }
    }

    // Nœuds
    d.nodes.forEach((n, i) => {
        const cx = v.X(n.x), cy = v.Y(n.y);
        if (d.pending === i)
            svg.appendChild(svgEl('circle', { cx, cy, r: 10, fill: 'none', stroke: C_POS, 'stroke-width': 2.5 }));
        svg.appendChild(svgEl('circle', { cx, cy, r: 4.5, fill: '#fff', stroke: C_INK, 'stroke-width': 1.5 }));
        txtBG(svg, cx - 9, cy - 9, nodeName(i), 'end', 13, C_INK, true);
    });

    // Légende des couleurs (treillis calculé)
    if (res && truss) {
        const items = [['traction', C_POS, null], ['compression', C_NEG, null], ['effort nul', C_AXIS, '7,5']];
        let x = 10;
        for (const [lbl, col, dash] of items) {
            line(svg, x, 16, x + 22, 16, col, 4, dash ? { 'stroke-dasharray': dash } : {});
            text(svg, x + 28, 20, lbl, 'start', 11, C_MUTED);
            x += 40 + lbl.length * 6.5;
        }
    }

    el.innerHTML = '';
    el.appendChild(svg);
    return v;
}

// Rotules : cercle blanc à 9 px de l'extrémité concernée, sur l'axe de la barre
function drawHinges(svg, v, nodes, bars) {
    for (const b of bars) {
        const p = nodes[b.n1], q = nodes[b.n2];
        if (!p || !q) continue;
        const P1 = [v.X(p.x), v.Y(p.y)], P2 = [v.X(q.x), v.Y(q.y)];
        const l = Math.hypot(P2[0] - P1[0], P2[1] - P1[1]) || 1;
        const ex = (P2[0] - P1[0]) / l, ey = (P2[1] - P1[1]) / l;
        for (const [on, P, sgn] of [[b.h1, P1, 1], [b.h2, P2, -1]])
            if (on) svg.appendChild(svgEl('circle', { cx: P[0] + sgn * ex * 11, cy: P[1] + sgn * ey * 11, r: 4,
                fill: '#fff', stroke: C_INK, 'stroke-width': 1.5 }));
    }
}

// ─── Diagrammes N, V, M d'un portique, dessinés le long des barres ────────────
// N et V : valeurs positives à gauche du sens de parcours de la barre (n1 → n2).
// M : tracé du côté des fibres tendues.
function renderFrameDiagram(el, d, qty) {
    const v = makeView(el, d.nodes, false, 36);
    const svg = svgRoot(v.W, v.H);
    const res = d.res;
    // valeurs échantillonnées le long de chaque barre (paraboles sous charge répartie)
    const NS = 24;
    const fn = b => qty === 'N' ? b.Nat : qty === 'V' ? b.Vat : b.Mat;
    const vals = res.barRes.map(b => Array.from({ length: NS + 1 }, (_, i) => fn(b)(b.L * i / NS)));
    const vmax = Math.max(...vals.flat().map(Math.abs), 1e-9);
    const k = 0.12 * Math.min(v.W, v.H) / vmax;          // px par N (ou N·m)
    const unit = qty === 'M' ? 'kN·m' : 'kN';
    const side = qty === 'M' ? -1 : 1;                    // M côté fibres tendues (droite de n1→n2)

    for (const b of d.bars) {
        const p = d.nodes[b.n1], q = d.nodes[b.n2];
        line(svg, v.X(p.x), v.Y(p.y), v.X(q.x), v.Y(q.y), C_STRUCT, 3, { 'stroke-linecap': 'round' });
    }
    drawHinges(svg, v, d.nodes, d.bars);
    for (const sp of d.supports) {
        const n = d.nodes[sp.node];
        drawSupportSymbol(svg, d.type, sp.type, v.X(n.x), v.Y(n.y));
    }

    const isZero = vals.flat().every(x => Math.abs(x) < 1e-6 * Math.max(vmax, 1));
    d.bars.forEach((b, i) => {
        const p = d.nodes[b.n1], q = d.nodes[b.n2];
        const P1 = [v.X(p.x), v.Y(p.y)], P2 = [v.X(q.x), v.Y(q.y)];
        const dx = P2[0] - P1[0], dy = P2[1] - P1[1], l = Math.hypot(dx, dy);
        // normale « à gauche » en coordonnées écran (y vers le bas)
        const nx = dy / l * side, ny = -dx / l * side;
        const vs = vals[i];
        const at = t => [P1[0] + dx * t, P1[1] + dy * t];
        const off = (P, val) => [P[0] + nx * val * k, P[1] + ny * val * k];
        const fillPart = (A, B, va, vb) => {
            const col = (va + vb) / 2 >= 0 ? C_POS : C_NEG;
            poly(svg, [A, B, off(B, vb), off(A, va)], col + FILL_ALPHA, 'none', 0);
            line(svg, ...off(A, va), ...off(B, vb), C_INK, 1.3);
        };
        for (let j = 0; j < NS; j++) {
            const a = vs[j], c = vs[j + 1], A = at(j / NS), B = at((j + 1) / NS);
            if (a * c < 0) {   // changement de signe dans l'intervalle
                const t = a / (a - c), Pm = [A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t];
                fillPart(A, Pm, a, 0); fillPart(Pm, B, 0, c);
            } else fillPart(A, B, a, c);
        }
        // Valeurs : une seule si constante, sinon aux extrémités et à l'extremum intérieur
        const lab = (P, val) => {
            if (Math.abs(val) < 1e-3 * vmax) return;
            const [ox, oy] = off(P, val);
            const s = Math.sign(val) || 1;
            txtBG(svg, ox + nx * 12 * s, oy + ny * 12 * s + 4, `${fmtLbl(val / 1e3)}`, 'middle', 11, C_INK, true);
        };
        const vmin = Math.min(...vs), vmx = Math.max(...vs);
        if (vmx - vmin < 1e-6 * vmax) lab(at(0.5), vs[0]);
        else {
            lab(P1, vs[0]); lab(P2, vs[NS]);
            const j = vs.reduce((bj, x, jj) => Math.abs(x) > Math.abs(vs[bj]) ? jj : bj, 0);
            if (j > 1 && j < NS - 1 && Math.abs(vs[j]) > 1.05 * Math.max(Math.abs(vs[0]), Math.abs(vs[NS])))
                lab(at(j / NS), vs[j]);
        }
    });

    d.nodes.forEach((n, i) => {
        svg.appendChild(svgEl('circle', { cx: v.X(n.x), cy: v.Y(n.y), r: 3.5, fill: '#fff', stroke: C_INK, 'stroke-width': 1.3 }));
        txtBG(svg, v.X(n.x) - 9, v.Y(n.y) - 9, nodeName(i), 'end', 12, C_INK, true);
    });

    const legend = {
        N: 'N (kN) : traction > 0, tracé à gauche du sens de parcours de la barre',
        V: 'V (kN) : tracé à gauche du sens de parcours de la barre',
        M: 'M (kN·m) : tracé du côté des fibres tendues',
    }[qty];
    text(svg, 10, 20, legend, 'start', 12, C_MUTED);
    if (isZero) text(svg, v.W / 2, 40, `${qty} est nul dans toutes les barres`, 'middle', 12, C_MUTED, { 'font-style': 'italic' });
    el.innerHTML = '';
    el.appendChild(svg);
    return unit;
}
