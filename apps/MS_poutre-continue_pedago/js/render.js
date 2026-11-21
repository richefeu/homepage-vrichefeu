'use strict';

// ─── Utilitaires SVG ─────────────────────────────────────────────────────────

function svgEl(tag, attrs = {}) {
    const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
}

function svgRoot(w, h) {
    return svgEl('svg', { width: w, height: h,
        viewBox: `0 0 ${w} ${h}`, xmlns: 'http://www.w3.org/2000/svg' });
}

function line(parent, x1, y1, x2, y2, stroke = '#333', sw = 1, extra = {}) {
    parent.appendChild(svgEl('line', {x1, y1, x2, y2, stroke, 'stroke-width': sw, ...extra}));
}

// Indices : « Y_{A} » s'affiche Y avec A en indice
function text(parent, x, y, s, anchor = 'middle', fs = 10, fill = '#222', extra = {}) {
    const el = svgEl('text', {x, y, 'text-anchor': anchor,
        'font-size': fs, fill, 'font-family': FONT, ...extra});
    const parts = String(s).split(/_\{([^}]*)\}/);   // pairs : texte, impairs : indices
    if (parts.length === 1) {
        el.textContent = s;
    } else {
        const shift = fs * 0.3;
        parts.forEach((p, k) => {
            if (!p) return;
            const sub = k % 2 === 1;
            const after = k > 0 && !sub;    // texte qui suit un indice : on remonte
            const ts = svgEl('tspan', sub ? { dy: shift, 'font-size': fs * 0.75 }
                                          : after ? { dy: -shift } : {});
            ts.textContent = p;
            el.appendChild(ts);
        });
    }
    parent.appendChild(el);
}

function poly(parent, pts, fill, stroke = 'none', sw = 0) {
    const d = pts.map(([x,y]) => `${x},${y}`).join(' ');
    parent.appendChild(svgEl('polygon', {points: d, fill, stroke, 'stroke-width': sw}));
}

function path(parent, d, fill, stroke = 'none', sw = 0) {
    parent.appendChild(svgEl('path', {d, fill, stroke, 'stroke-width': sw}));
}

function arrowMarker(defs, id, color) {
    const marker = svgEl('marker', {id, markerWidth: 10, markerHeight: 7,
        refX: 9, refY: 3.5, orient: 'auto'});
    marker.appendChild(svgEl('polygon', {points: '0,0 10,3.5 0,7', fill: color}));
    defs.appendChild(marker);
}

function arrowLine(parent, x1, y1, x2, y2, color, markerId, sw = 1.5) {
    parent.appendChild(svgEl('line', {x1, y1, x2, y2, stroke: color,
        'stroke-width': sw, 'marker-end': `url(#${markerId})`}));
}

// ─── Helpers visuels ──────────────────────────────────────────────────────────
/* Text with a translucent white backing for readability over complex backgrounds */
function txtBG(parent, x, y, s, anchor, fs, fill, bold = false) {
    const w = s.replace(/_\{|\}/g, '').length * fs * 0.56 + 6;
    const ox = anchor === 'middle' ? -w / 2 : anchor === 'end' ? -w : 0;
    parent.appendChild(svgEl('rect', {
        x: x + ox, y: y - fs + 1, width: w, height: fs + 3,
        fill: 'rgba(255,255,255,0.82)', rx: 2,
    }));
    text(parent, x, y, s, anchor, fs, fill, bold ? { 'font-weight': '600' } : {});
}

// ─── Couleurs et typographie ──────────────────────────────────────────────────
// Palette courte, un rôle par couleur :
//   bleu = valeur positive / traction, rouge = valeur négative / compression,
//   vert = actions extérieures appliquées, orange = déformée, gris = structure.
const FONT     = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
const C_INK    = '#1f2937';   // texte, courbes
const C_MUTED  = '#6b7280';   // graduations, unités
const C_AXIS   = '#9ca3af';   // axes
const C_GRID   = '#d1d5db';   // ligne de zéro
const C_STRUCT = '#475569';   // poutre, appuis, contour de section
const C_STRUCT_FILL = '#e2e8f0';
const C_SEC_FILL    = '#dbe7f5';
const C_POS    = '#3b82f6';
const C_NEG    = '#ef4444';
const C_LOAD   = '#15803d';   // forces, charges réparties, moments appliqués
const C_DEFL   = '#ea580c';
const C_TAU    = C_POS;
const FILL_ALPHA = '59';      // ≈ 35 % d'opacité pour les zones colorées

// Nombre court pour les étiquettes : 2 décimales au plus, sans zéros inutiles
function fmtLbl(v) {
    const r = (Math.abs(v) < 5e-3 ? 0 : v).toFixed(2);
    return r.replace(/\.?0+$/, '');
}

// Indice du milieu du palier où vals atteint sa valeur extrême (max si sign > 0,
// min sinon) : sur un palier de V(x), l'étiquette se place au centre du palier.
function extremeIndex(vals, sign) {
    const target = sign > 0 ? Math.max(...vals) : Math.min(...vals);
    const tol = 1e-9 * Math.max(...vals.map(Math.abs));
    const idx = vals.map((v, i) => Math.abs(v - target) <= tol ? i : -1).filter(i => i >= 0);
    return idx[Math.floor(idx.length / 2)];
}

// Point + étiquette sur une valeur extrême. L'étiquette se place côté ligne de
// zéro (à l'intérieur de la zone colorée) pour ne pas déborder sur les axes.
// placed : boîtes des étiquettes déjà posées ; en cas de chevauchement,
// l'étiquette est décalée verticalement (vers la ligne de zéro).
function markExtreme(parent, px, py, baseline, label, xLeft, xRight, anchorForced = null, placed = []) {
    parent.appendChild(svgEl('circle', { cx: px, cy: py, r: 3.5, fill: C_INK }));
    const step = py < baseline ? 15 : -15;
    let ly = py < baseline ? py + 17 : py - 8;
    const anchor = anchorForced
        || (px < xLeft + 70 ? 'start' : px > xRight - 70 ? 'end' : 'middle');
    const lx = anchor === 'start' ? px + 6 : anchor === 'end' ? px - 6 : px;
    const w = label.replace(/_\{|\}/g, '').length * 11 * 0.56 + 6;
    const x0 = anchor === 'middle' ? lx - w / 2 : anchor === 'end' ? lx - w : lx;
    const hits = y => placed.some(b => x0 < b.x1 && x0 + w > b.x0 && y - 11 < b.y1 && y + 3 > b.y0);
    for (let k = 0; k < 6 && hits(ly); k++) ly += step;
    placed.push({ x0, x1: x0 + w, y0: ly - 11, y1: ly + 3 });
    txtBG(parent, lx, ly, label, anchor, 11, C_INK, true);
}

// ─── Zone colorée avec changements de signe ───────────────────────────────────
function filledArea(parent, pts, baseline, cPos, cNeg) {
    if (pts.length < 2) return;
    let current = [];
    let lastY = pts[0][1];
    let lastSign = lastY < baseline ? 1 : (lastY > baseline ? -1 : 0);

    const flush = (sign) => {
        if (current.length < 2) { current = []; return; }
        const first = current[0], last = current[current.length - 1];
        const closed = [[first[0], baseline], ...current, [last[0], baseline]];
        poly(parent, closed, sign >= 0 ? cPos : cNeg, 'none', 0);
        current = [];
    };

    for (let i = 0; i < pts.length; i++) {
        const [x, y] = pts[i];
        const curSign = y < baseline ? 1 : (y > baseline ? -1 : 0);

        if (i > 0 && curSign !== 0 && lastSign !== 0 && curSign !== lastSign) {
            // zero crossing - interpolate
            const [px, py] = pts[i-1];
            const t = (baseline - py) / (y - py);
            const mx = px + t * (x - px);
            current.push([mx, baseline]);
            flush(lastSign);
            current = [[mx, baseline]];
        }
        current.push([x, y]);
        lastSign = curSign || lastSign;
        lastY = y;
    }
    flush(lastSign);
}

// ─── Schéma de la poutre ──────────────────────────────────────────────────────
function renderBeamSchema(el, L, supports, loads, reactions) {
    const ML = 64, MR = 38, MT = 60, MB = 60;
    const W = el.clientWidth || 820;
    const BW = W - ML - MR;
    const BY = MT + 30;   // y de la ligne de la poutre

    // Réactions empilées sous chaque appui : la hauteur dépend du nombre de lignes
    const rxnLines = (reactions || []).map((rxn, i) => {
        const lbl = String.fromCharCode(65 + i), out = [];
        if (Math.abs(rxn.Ry) > 1e-6) out.push(`Y_{${lbl}} = ${fmtLbl(rxn.Ry/1e3)} kN`);
        if (Math.abs(rxn.Rx) > 1e-6) out.push(`X_{${lbl}} = ${fmtLbl(rxn.Rx/1e3)} kN`);
        if (Math.abs(rxn.Mz) > 1e-6) out.push(`M_{${lbl}} = ${fmtLbl(rxn.Mz/1e3)} kN·m`);
        return out;
    });
    const nLines = Math.max(1, ...rxnLines.map(l => l.length));
    const axY = BY + 68 + 15 * (nLines - 1) + 18;
    const H = axY + 34;

    // Ancrage d'une étiquette selon sa position : vers l'intérieur près des bords
    const anchorAt = x => x < ML + 60 ? 'start' : x > ML + BW - 60 ? 'end' : 'middle';

    const svg = svgRoot(W, H);
    const defs = svgEl('defs');
    arrowMarker(defs, 'arr-fy-dn',   C_LOAD);          // force vers le bas
    arrowMarker(defs, 'arr-fy-up',   C_LOAD);          // force vers le haut
    arrowMarker(defs, 'arr-dist-dn', C_LOAD);          // charge répartie vers le bas
    arrowMarker(defs, 'arr-dist-up', C_LOAD);          // charge répartie vers le haut
    arrowMarker(defs, 'arr-fx',      C_LOAD);
    arrowMarker(defs, 'arr-moment-ccw', C_LOAD);
    arrowMarker(defs, 'arr-moment-cw',  C_LOAD);
    svg.appendChild(defs);

    const sx = x => ML + (x / L) * BW;
    const LH = 44, LH2 = 34;

    let maxFy = 0, maxDist = 0;
    for (const l of loads) {
        if (l.type === 'force')       maxFy   = Math.max(maxFy,   Math.abs(l.Fy));
        else if (l.type === 'distributed') maxDist = Math.max(maxDist, Math.abs(l.qy));
    }
    const fScF = maxFy   > 0 ? LH  / maxFy   : 1;
    const fScU = maxDist > 0 ? LH2 / maxDist : 1;

    // ── Charges réparties (derrière la poutre) ────────────────────────────────
    for (const l of loads) {
        if (l.type !== 'distributed') continue;
        const x1s = sx(l.x1), x2s = sx(l.x2);
        //const h2  = Math.abs(l.qy) * fScU;
        const h2  = 40;
        const nArr = Math.max(2, Math.round((x2s - x1s) / 20));

        if (l.qy < 0) {
            // ↓ Charge vers le bas : zone AU-DESSUS, flèches pointant vers la poutre
            const col = C_LOAD;
            svg.appendChild(svgEl('rect', {
                x: x1s, y: BY - h2, width: x2s - x1s, height: h2,
                fill: 'rgba(21,128,61,0.10)', stroke: col, 'stroke-width': 0.9,
            }));
            line(svg, x1s, BY - h2, x2s, BY - h2, col, 1.2);
            for (let i = 0; i <= nArr; i++) {
                const xa = x1s + (x2s - x1s) * i / nArr;
                arrowLine(svg, xa, BY - h2, xa, BY - 3, col, 'arr-dist-dn', 1.3);
            }
            txtBG(svg, (x1s+x2s)/2, BY - h2 - 6,
                `${fmtLbl(Math.abs(l.qy)/1e3)} kN/m`, 'middle', 12, col, true);
        } else {
            // ↑ Charge vers le haut : zone EN-DESSOUS, flèches pointant vers la poutre
            const col = C_LOAD;
            svg.appendChild(svgEl('rect', {
                x: x1s, y: BY + 3, width: x2s - x1s, height: h2,
                fill: 'rgba(21,128,61,0.10)', stroke: col, 'stroke-width': 0.9,
            }));
            line(svg, x1s, BY + 3 + h2, x2s, BY + 3 + h2, col, 1.2);
            for (let i = 0; i <= nArr; i++) {
                const xa = x1s + (x2s - x1s) * i / nArr;
                arrowLine(svg, xa, BY + 3 + h2, xa, BY + 3, col, 'arr-dist-up', 1.3);
            }
            txtBG(svg, (x1s+x2s)/2, BY + 3 + h2 + 14,
                `${fmtLbl(Math.abs(l.qy)/1e3)} kN/m`, 'middle', 12, col, true);
        }
    }

    // ── Poutre : ligne épaisse noire ──────────────────────────────────────────
    line(svg, ML, BY, ML + BW, BY, C_INK, 5, { 'stroke-linecap': 'square' });

    // ── Appuis ────────────────────────────────────────────────────────────────
    for (let i = 0; i < supports.length; i++) {
        const s = supports[i], cx = sx(s.x);
        if      (s.type === 'roller') drawRoller(svg, cx, BY);
        else if (s.type === 'pin')    drawPin(svg, cx, BY);
        else                          drawFixed(svg, cx, BY);
        // Étiquette sous le symbole
        text(svg, cx, BY + 50, String.fromCharCode(65 + i),
            'middle', 14, C_INK, { 'font-weight': '700' });
    }

    // ── Forces ponctuelles ────────────────────────────────────────────────────
    for (const l of loads) {
        if (l.type !== 'force') continue;
        const xf = sx(l.x);

        if (Math.abs(l.Fy) > 1e-9) {
            //const h2 = Math.abs(l.Fy) * fScF;
            const h2 = 60;
            if (l.Fy < 0) {
                // ↓ Force vers le bas : au-dessus, flèche vers la poutre
                // Étiquette au-dessus de la flèche : ne croise pas celle d'une charge répartie
                arrowLine(svg, xf, BY - h2, xf, BY - 3, C_LOAD, 'arr-fy-dn', 2.5);
                const anc = anchorAt(xf);
                txtBG(svg, anc === 'start' ? xf - 6 : anc === 'end' ? xf + 6 : xf, BY - h2 - 6,
                    `${fmtLbl(Math.abs(l.Fy)/1e3)} kN`, anc, 12, C_LOAD, true);
            } else {
                // ↑ Force vers le haut : en-dessous, flèche vers la poutre
                const right = xf > ML + BW - 60;
                arrowLine(svg, xf, BY + h2, xf, BY + 3, C_LOAD, 'arr-fy-up', 2.5);
                txtBG(svg, right ? xf - 8 : xf + 8, BY + h2 - 2,
                    `${fmtLbl(Math.abs(l.Fy)/1e3)} kN`, right ? 'end' : 'start', 12, C_LOAD, true);
            }
        }

        if (l.Fx) {
            // Force horizontale : flèche dans le plan de la poutre
            const dir = l.Fx > 0 ? 1 : -1;
            arrowLine(svg, xf - dir * 32, BY, xf - dir * 5, BY, C_LOAD, 'arr-fx', 2);
            txtBG(svg, xf - dir * 18, BY - 8,
                `${fmtLbl(Math.abs(l.Fx)/1e3)} kN`, 'middle', 11, C_LOAD);
        }
    }

    // ── Moments ───────────────────────────────────────────────────────────────
    for (const l of loads) {
        if (l.type !== 'moment') continue;
        const xm = sx(l.x);
        drawMomentSymbol(svg, xm, BY, 15, l.Mz >= 0, C_LOAD);
        const anc = anchorAt(xm);
        txtBG(svg, anc === 'start' ? xm - 15 : anc === 'end' ? xm + 15 : xm, BY - 24,
            `${fmtLbl(Math.abs(l.Mz)/1e3)} kN·m`, anc, 12, C_LOAD, true);
    }

    // ── Réactions ────────────────────────────────────────────────────────────
    if (reactions) {
        for (let i = 0; i < reactions.length; i++) {
            const cx = sx(reactions[i].x), anc = anchorAt(cx);
            const lx = anc === 'start' ? cx - 12 : anc === 'end' ? cx + 12 : cx;
            rxnLines[i].forEach((s, k) => txtBG(svg, lx, BY + 68 + 15 * k, s, anc, 11, C_INK));
        }
    }

    // ── Axe x ─────────────────────────────────────────────────────────────────
    line(svg, ML, axY, ML + BW, axY, C_GRID, 1);
    for (let i = 0; i <= 5; i++) {
        const xv = L * i / 5, xs2 = sx(xv);
        line(svg, xs2, axY - 3, xs2, axY + 3, C_AXIS, 1);
        text(svg, xs2, axY + 16, fmtLbl(xv), 'middle', 11, C_MUTED);
    }
    text(svg, ML + BW + 12, axY + 4, 'x [m]', 'start', 11, C_MUTED, { 'font-style': 'italic' });

    el.innerHTML = '';
    el.appendChild(svg);
}

// ── Appui à rouleaux ─────────────────────────────────────────────────────────
function drawRoller(parent, cx, by) {
    const s = 11;
    // Triangle (apex sur la poutre, base en bas)
    poly(parent, [[cx, by], [cx - s, by + s * 1.7], [cx + s, by + s * 1.7]],
        C_STRUCT_FILL, C_STRUCT, 1.5);
    // Cercle au nœud (point d'articulation)
    parent.appendChild(svgEl('circle', {
        cx, cy: by, r: 4.5, fill: '#fff', stroke: C_STRUCT, 'stroke-width': 1.5,
    }));
    // Galets
    const wy = by + s * 1.7 + 6;
    for (const dx of [-(s - 3), 0, s - 3])
        parent.appendChild(svgEl('circle', {
            cx: cx + dx, cy: wy, r: 3.5, fill: '#fff', stroke: C_STRUCT, 'stroke-width': 1.2,
        }));
    // Ligne de sol + hachures
    line(parent, cx - s - 5, wy + 5, cx + s + 5, wy + 5, C_STRUCT, 1.5);
    drawHatch(parent, cx - s - 4, wy + 5, cx + s + 4, wy + 12);
}

// ── Articulation (rotule) ────────────────────────────────────────────────────
function drawPin(parent, cx, by) {
    const s = 11;
    poly(parent, [[cx, by], [cx - s, by + s * 1.7], [cx + s, by + s * 1.7]],
        C_STRUCT_FILL, C_STRUCT, 1.5);
    parent.appendChild(svgEl('circle', {
        cx, cy: by, r: 4.5, fill: '#fff', stroke: C_STRUCT, 'stroke-width': 1.5,
    }));
    line(parent, cx - s - 3, by + s * 1.7 + 3, cx + s + 3, by + s * 1.7 + 3, C_STRUCT, 1.5);
    drawHatch(parent, cx - s - 3, by + s * 1.7 + 3, cx + s + 3, by + s * 1.7 + 11);
}

// ── Encastrement ─────────────────────────────────────────────────────────────
function drawFixed(parent, cx, by) {
    const hw = 10, hh = 22;
    // Bloc hachuré centré sur la poutre
    drawHatch(parent, cx - hw, by - hh / 2, cx + hw, by + hh / 2);
    // Bordure
    parent.appendChild(svgEl('rect', {
        x: cx - hw, y: by - hh / 2, width: 2 * hw, height: hh,
        fill: 'none', stroke: C_STRUCT, 'stroke-width': 1.8,
    }));
}

// ── Hachures diagonales correctement clippées ─────────────────────────────────
function drawHatch(parent, x1, y1, x2, y2) {
    parent.appendChild(svgEl('rect', {
        x: x1, y: y1, width: x2 - x1, height: y2 - y1, fill: C_STRUCT_FILL,
    }));
    const step = 5;
    const range = (x2 - x1) + (y2 - y1);
    for (let d = step; d < range; d += step) {
        // Segment de la diagonale coupé au rectangle
        let ax = x1 + Math.min(d, x2 - x1);
        let ay = y1 + Math.max(0, d - (x2 - x1));
        let bx = x1 + Math.max(0, d - (y2 - y1));
        let by2 = y1 + Math.min(d, y2 - y1);
        if (ax < bx || ay > y2 || bx > x2) continue;
        line(parent, ax, ay, bx, by2, C_STRUCT, 0.8);
    }
}

function drawMomentSymbol(parent, cx, cy, r, ccw, color) {
    const start = ccw ? 30 : 150;
    const end   = ccw ? 330 : -30;
    const sa = start * PI/180, ea = end * PI/180;
    const x1 = cx + r * Math.cos(sa), y1 = cy + r * Math.sin(sa);
    const x2 = cx + r * Math.cos(ea), y2 = cy + r * Math.sin(ea);
    const sweep = ccw ? 0 : 1;
    parent.appendChild(svgEl('path', {
        d: `M ${x1} ${y1} A ${r} ${r} 0 1 ${sweep} ${x2} ${y2}`,
        fill: 'none', stroke: color, 'stroke-width': 1.5,
        'marker-end': `url(#arr-moment-${ccw?'ccw':'cw'})`
    }));
}

// ─── Panneau N, V ou M ────────────────────────────────────────────────────────
// marks : valeurs remarquables imposées [{x, value, label}] (ex. moments sur appuis)
function renderScalarPanel(el, xs, ys, title, unitLabel, cPos, cNeg, marks = []) {
    const W = el.clientWidth || 820, H = 150;
    const ML = 60, MR = 20, MT = 26, MB = 26;
    const PW = W - ML - MR, PH = H - MT - MB;

    const absMax = Math.max(...ys.map(Math.abs));
    // Diagramme identiquement nul : échelle de ±1 unité au lieu de ±0
    const isZero = absMax < 1e-6 * unitLabel.scale;
    const niceM = isZero ? unitLabel.scale : niceMax(absMax);
    const scX = x => ML + (x / xs[xs.length-1]) * PW;
    const baseline = MT + PH / 2;
    const scY = (v) => baseline - (v / niceM) * (PH / 2);

    const svg = svgRoot(W, H);

    // Zero line
    line(svg, ML, baseline, ML+PW, baseline, C_GRID, 1);
    // Filled area
    const svgPts = xs.map((x,i) => [scX(x), scY(ys[i])]);
    filledArea(svg, svgPts, baseline, cPos + FILL_ALPHA, cNeg + FILL_ALPHA);
    // Curve
    const d = svgPts.map(([x,y],i) => `${i===0?'M':'L'}${x},${y}`).join(' ');
    svg.appendChild(svgEl('path', {d, fill:'none', stroke: C_INK, 'stroke-width':1.5}));
    if (isZero)
        text(svg, ML + PW/2, baseline - 8, 'nul sur toute la poutre', 'middle', 12, C_MUTED,
             { 'font-style': 'italic' });

    // Valeurs extrêmes (max positif, min négatif) avec leur abscisse
    if (!isZero) {
        const sym = title.split('(')[0];
        const Lx = xs[xs.length - 1];
        const placed = [];
        for (const m of marks)
            markExtreme(svg, scX(m.x), scY(m.value), baseline, m.label, ML, ML + PW, null, placed);
        // Max et min au même x (saut d'effort tranchant sur un appui) :
        // étiquettes de part et d'autre du point pour qu'elles ne se chevauchent pas
        const iMax = extremeIndex(ys, 1), iMin = extremeIndex(ys, -1);
        const sameX = Math.abs(xs[iMax] - xs[iMin]) < 1e-3 * xs[xs.length - 1];
        for (const sign of [1, -1]) {
            const i = sign > 0 ? iMax : iMin;
            if (ys[i] * sign < 1e-3 * absMax) continue;
            // déjà annoncé par une marque au même endroit
            if (marks.some(m => Math.abs(m.x - xs[i]) < 1e-3 * Lx)) continue;
            const v = ys[i] / unitLabel.scale;
            markExtreme(svg, svgPts[i][0], svgPts[i][1], baseline,
                `${sym}_{${sign > 0 ? 'max' : 'min'}} = ${fmtLbl(v)} ${unitLabel.name}  (x = ${fmtLbl(xs[i])} m)`,
                ML, ML + PW, sameX ? (sign > 0 ? 'end' : 'start') : null, placed);
        }
    }

    // Y axis + labels
    line(svg, ML, MT, ML, MT+PH, C_AXIS, 1);
    for (const v of [-niceM, 0, niceM]) {
        const y2 = scY(v);
        line(svg, ML-4, y2, ML, y2, C_AXIS, 1);
        text(svg, ML-7, y2+4, fmtVal(v/unitLabel.scale), 'end', 11, C_MUTED);
    }
    // X axis ticks
    const L = xs[xs.length-1];
    for (const xv of [0, L/4, L/2, 3*L/4, L]) {
        const xs2 = scX(xv);
        line(svg, xs2, MT+PH, xs2, MT+PH+4, C_AXIS, 1);
        text(svg, xs2, MT+PH+17, fmtLbl(xv), 'middle', 11, C_MUTED);
    }

    // Title + unit
    text(svg, ML - 7, MT - 10, `[${unitLabel.name}]`, 'end', 11, C_MUTED);

    el.innerHTML = '';
    el.appendChild(svg);
}

function fmtVal(v) {
    if (Math.abs(v) < 1e-12) return '0';
    if (Math.abs(v) >= 1000 || (Math.abs(v) < 0.01 && v !== 0)) return v.toExponential(1);
    const r = v.toPrecision(3);
    return r.includes('.') ? r.replace(/\.?0+$/, '') : r;
}

function niceMax(v) {
    if (v < 1e-12) return 1;
    const exp = Math.pow(10, Math.floor(Math.log10(v)));
    const frac = v / exp;
    let nice;
    if (frac <= 1) nice = 1;
    else if (frac <= 2) nice = 2;
    else if (frac <= 2.5) nice = 2.5;
    else if (frac <= 5) nice = 5;
    else nice = 10;
    return nice * exp;
}

// ─── Panneau déformée ─────────────────────────────────────────────────────────
function renderDeflPanel(el, defl) {
    const W = el.clientWidth || 820, H = 140;
    const ML = 60, MR = 20, MT = 26, MB = 26;
    const PW = W - ML - MR, PH = H - MT - MB;

    const vs = defl.map(d => d.v);
    const L = defl[defl.length-1].x;
    const absMax = Math.max(...vs.map(Math.abs), 1e-15);
    const niceM = niceMax(absMax * 1e3); // mm
    const scX = x => ML + (x / L) * PW;
    const baseline = MT + PH / 2;
    const scY = v => baseline - (v * 1e3 / niceM) * (PH / 2);

    const svg = svgRoot(W, H);
    line(svg, ML, baseline, ML+PW, baseline, C_GRID, 1);

    const pts = defl.map(d => [scX(d.x), scY(d.v)]);
    const d = pts.map(([x,y],i) => `${i===0?'M':'L'}${x},${y}`).join(' ');
    svg.appendChild(svgEl('path', {d, fill:'none', stroke: C_DEFL, 'stroke-width':2.5}));

    // Flèche maximale (plus grand déplacement en valeur absolue)
    if (absMax > 1e-12) {
        const absVs = vs.map(Math.abs);
        const i = extremeIndex(absVs, 1);
        markExtreme(svg, pts[i][0], pts[i][1], baseline,
            `u_{max} = ${fmtVal(vs[i] * 1e3)} mm  (x = ${fmtLbl(defl[i].x)} m)`,
            ML, ML + PW);
    }

    line(svg, ML, MT, ML, MT+PH, C_AXIS, 1);
    for (const v of [-niceM, 0, niceM]) {
        const y2 = scY(v * 1e-3);
        line(svg, ML-4, y2, ML, y2, C_AXIS, 1);
        text(svg, ML-7, y2+4, fmtVal(v), 'end', 11, C_MUTED);
    }
    const L2 = defl[defl.length-1].x;
    for (const xv of [0, L2/4, L2/2, 3*L2/4, L2]) {
        const xs2 = scX(xv);
        line(svg, xs2, MT+PH, xs2, MT+PH+4, C_AXIS, 1);
        text(svg, xs2, MT+PH+17, fmtLbl(xv), 'middle', 11, C_MUTED);
    }
    text(svg, ML-7, MT-10, '[mm]', 'end', 11, C_MUTED);

    el.innerHTML = '';
    el.appendChild(svg);
}

// ─── Dessin de section droite ─────────────────────────────────────────────────
function renderSection(el, sec) {
    if (!sec) { el.innerHTML = ''; return; }
    const W = Math.max(el.clientWidth || 0, 160), H = 180;
    const PAD = 16;
    const svg = svgRoot(W, H);
    const defs = svgEl('defs');
    svg.appendChild(defs);

    // Collect pieces (y1,z1,y2,z2) in section coordinates
    // z = 0 at bottom, increasing upward; y = lateral axis
    const addPieces = [], voidPieces = [];
    let ymin, ymax, zmin = 0, zmax;

    if (sec.type === 'rect') {
        const { b, h } = sec;
        addPieces.push({y1:-b/2, z1:0, y2:b/2, z2:h});
        ymin = -b/2; ymax = b/2; zmax = h;

    } else if (sec.type === 'circ') {
        // handled specially below
        ymin = -sec.d/2; ymax = sec.d/2; zmax = sec.d;

    } else if (sec.type === 'profile') {
        const { profType, orient, h_, b_, tf_, tw_ } = sec;
        if (profType === 'IPE' && orient === 'I') {
            addPieces.push({y1:-b_/2, z1:0,      y2: b_/2, z2:tf_});
            addPieces.push({y1:-tw_/2, z1:tf_,   y2: tw_/2,z2:h_-tf_});
            addPieces.push({y1:-b_/2, z1:h_-tf_, y2: b_/2, z2:h_});
            ymin = -b_/2; ymax = b_/2; zmax = h_;
        } else if (profType === 'IPE' && orient === 'H') {
            // section height = b_, width span = h_
            addPieces.push({y1:-h_/2,     z1:0, y2:-h_/2+tf_, z2:b_});  // left flange
            addPieces.push({y1: h_/2-tf_, z1:0, y2: h_/2,     z2:b_});  // right flange
            addPieces.push({y1:-h_/2+tf_, z1:b_/2-tw_/2, y2:h_/2-tf_, z2:b_/2+tw_/2}); // web
            ymin = -h_/2; ymax = h_/2; zmax = b_;
        } else if (profType === 'UPE' && orient === 'C') {
            // web at y=[0,tw_], flanges extend to y=b_ (b_ = back-of-web to free edge)
            addPieces.push({y1:0, z1:0,      y2:b_,  z2:tf_});     // bottom flange
            addPieces.push({y1:0, z1:tf_,    y2:tw_, z2:h_-tf_}); // web
            addPieces.push({y1:0, z1:h_-tf_, y2:b_,  z2:h_});     // top flange
            ymin = 0; ymax = b_; zmax = h_;
        } else if (profType === 'UPE' && orient === 'U') {
            // web horizontal at bottom, two vertical flanges
            addPieces.push({y1:-h_/2, z1:0,   y2: h_/2,    z2:tw_});  // web
            addPieces.push({y1:-h_/2, z1:tw_,  y2:-h_/2+tf_,z2:b_}); // left flange
            addPieces.push({y1: h_/2-tf_,z1:tw_,y2: h_/2,  z2:b_}); // right flange
            ymin = -h_/2; ymax = h_/2; zmax = b_;
        } else if (profType === 'UPE' && orient === 'Ui') {
            // web horizontal at top, two vertical flanges pointing down
            addPieces.push({y1:-h_/2, z1:b_-tw_, y2: h_/2,    z2:b_}); // web
            addPieces.push({y1:-h_/2, z1:0,       y2:-h_/2+tf_,z2:b_-tw_}); // left flange
            addPieces.push({y1: h_/2-tf_,z1:0,   y2: h_/2,    z2:b_-tw_}); // right flange
            ymin = -h_/2; ymax = h_/2; zmax = b_;
        }

    } else if (sec.type === 'composite') {
        for (const p of sec.pieces) {
            if (p.add) addPieces.push(p);
            else       voidPieces.push(p);
        }
        ymin = sec._ymin; ymax = sec._ymax;
        zmin = sec._zmin; zmax = sec._zmax;

    } else { // custom
        const wEst = sec.area > 0 ? Math.sqrt(sec.area * sec.height / sec.height) : 0.1;
        const w = sec.area / Math.max(sec.height, 1e-9);
        addPieces.push({y1:-w/2, z1:0, y2:w/2, z2:sec.height});
        ymin = -w/2; ymax = w/2; zmax = sec.height;
    }

    // Scale mapping
    const dy = (ymax - ymin) || 1e-3;
    const dz = (zmax - zmin) || 1e-3;
    const scY = (W - 2*PAD) / dy;
    const scZ = (H - 2*PAD) / dz;
    const sc  = Math.min(scY, scZ);
    const offX = (W - dy*sc) / 2;
    const offY = (H - dz*sc) / 2;

    const mY = y => offX + (y - ymin) * sc;
    const mZ = z => offY + (zmax - z) * sc;   // z=0 (bottom) → large SVG y

    const fillRect = (y1, z1, y2, z2, fill, strk) => {
        svg.appendChild(svgEl('rect', {
            x: mY(Math.min(y1,y2)), y: mZ(Math.max(z1,z2)),
            width:  Math.abs(y2-y1)*sc, height: Math.abs(z2-z1)*sc,
            fill, stroke: strk, 'stroke-width': 0.7
        }));
    };
    const fillCircSvg = (cy, cz, r, fill, strk) => {
        svg.appendChild(svgEl('circle', {
            cx: mY(cy), cy: mZ(cz), r: r*sc,
            fill, stroke: strk, 'stroke-width': 0.7
        }));
    };

    const SFILL = C_SEC_FILL, SSTROKE = C_STRUCT, SSW = 1.2;

    if (sec.type === 'circ') {
        const r = Math.min(W, H) / 2 - PAD;
        svg.appendChild(svgEl('circle', {cx: W/2, cy: H/2, r,
            fill: SFILL, stroke: SSTROKE, 'stroke-width': SSW}));
    } else if (sec.type === 'composite') {
        for (const p of addPieces) {
            if (p.shape === 'rect') fillRect(p.y1, p.z1, p.y2, p.z2, SFILL, SSTROKE);
            else fillCircSvg(p.y1, p.z1, p.y2, SFILL, SSTROKE);
        }
        for (const p of voidPieces) {
            if (p.shape === 'rect') fillRect(p.y1, p.z1, p.y2, p.z2, '#fff', SSTROKE);
            else fillCircSvg(p.y1, p.z1, p.y2, '#fff', SSTROKE);
        }
    } else {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        for (const p of addPieces) {
            const rx = g.appendChild(svgEl('rect', {
                x: mY(Math.min(p.y1,p.y2)), y: mZ(Math.max(p.z1,p.z2)),
                width: Math.abs(p.y2-p.y1)*sc, height: Math.abs(p.z2-p.z1)*sc,
                fill: SFILL, stroke: SSTROKE, 'stroke-width': SSW
            }));
        }
        svg.appendChild(g);
    }

    // ── Centroid line ─────────────────────────────────────────────────────────
    const zcAbs = sec.type === 'composite' ? sec.zc + sec._zmin : sec.zc;
    const zcSvg = mZ(zcAbs);
    // Dashed red line across section
    line(svg, PAD / 2, zcSvg, W - PAD - 6, zcSvg, C_INK, 1,
        { 'stroke-dasharray': '5,3' });
    // "G" label with background
    const gx = W - PAD - 4;
    svg.appendChild(svgEl('rect', {x: gx - 2, y: zcSvg - 10, width: 12, height: 13,
        fill: 'rgba(255,255,255,0.85)', rx: 1}));
    text(svg, gx + 4, zcSvg + 1, 'G', 'middle', 11, C_INK, { 'font-weight': '700' });

    el.innerHTML = '';
    el.appendChild(svg);
}

// ─── Remplissage vertical (entre une droite x=baseX et une courbe) ────────────
// Utilisé pour le diagramme de Navier σ(y) où l'axe de position est vertical.
function filledAreaVertical(parent, pts, baseX, cPos, cNeg) {
    if (pts.length < 2) return;
    let seg = [], lastSign = 0;

    const flush = sign => {
        if (seg.length < 2) { seg = []; return; }
        const closed = [[baseX, seg[0][1]], ...seg, [baseX, seg[seg.length-1][1]]];
        poly(parent, closed, sign > 0 ? cPos : cNeg, 'none', 0);
        seg = [];
    };

    for (let i = 0; i < pts.length; i++) {
        const [x, y] = pts[i];
        const sign = x > baseX + 0.5 ? 1 : (x < baseX - 0.5 ? -1 : 0);
        const eff  = sign !== 0 ? sign : lastSign;

        if (i > 0 && lastSign !== 0 && sign !== 0 && sign !== lastSign) {
            const [px, py] = pts[i-1];
            const t  = (baseX - px) / (x - px);
            const my = py + t * (y - py);
            seg.push([baseX, my]);
            flush(lastSign);
            seg = [[baseX, my]];
        }
        seg.push([x, y]);
        if (sign !== 0) lastSign = sign;
    }
    flush(lastSign || 1);
}

// ─── Diagramme de Navier ──────────────────────────────────────────────────────
function renderNavier(el, sec, naverData) {
    const { zs, sigma, tau } = naverData;
    const W = el.clientWidth || 820, H = 240;
    const ML = 64, MR = 20, MT = 30, MB = 26;
    const halfW = (W - ML - MR) / 2;
    const PH = H - MT - MB;

    const sigMax = niceMax(Math.max(...sigma.map(Math.abs), 1e-12));
    const tauMax = niceMax(Math.max(...tau, 1e-12));
    const h = sec.height, zc = sec.zc;

    const svg = svgRoot(W, H);
    svg.appendChild(svgEl('defs'));

    // Axe vertical : y = z − zc  (y=0 au barycentre)
    // z=0 (bas) → SVG y = MT+PH ; z=h (haut) → SVG y = MT
    const scZ   = z  => MT + (1 - z/h) * PH;
    const ycSvg = scZ(zc);   // ordonnée SVG du barycentre

    const sigBase = ML + halfW/2;
    const tauBase = ML + halfW + halfW/2;
    // Marge de chaque côté pour que les graduations σ et τ ne se touchent pas
    const halfSpan = halfW/2 - 32;
    const sigX = v => sigBase + (v / sigMax) * halfSpan;
    const tauX = v => tauBase + (v / tauMax) * halfSpan;

    // Séparateur σ / τ
    line(svg, ML+halfW, MT - 20, ML+halfW, MT+PH+MB, C_GRID, 1);

    // ── σ(y) ─────────────────────────────────────────────────────────────────
    // Axe σ=0 (trait vertical)
    line(svg, sigBase, MT, sigBase, MT+PH, C_AXIS, 1);
    // Remplissage entre σ=0 et la courbe
    const sigPts = zs.map((z,i) => [sigX(sigma[i]), scZ(z)]);
    filledAreaVertical(svg, sigPts, sigBase, C_POS + FILL_ALPHA, C_NEG + FILL_ALPHA);
    // Courbe
    svg.appendChild(svgEl('path', {
        d: sigPts.map(([x,y],i) => `${i===0?'M':'L'}${x},${y}`).join(' '),
        fill: 'none', stroke: C_INK, 'stroke-width': 1.5,
    }));

    // ── τ(y) ─────────────────────────────────────────────────────────────────
    line(svg, tauBase, MT, tauBase, MT+PH, C_AXIS, 1);
    const tauPts  = zs.map((z,i) => [tauX(tau[i]), scZ(z)]);
    // Remplissage τ (toujours positif)
    const tauClosed = [
        [tauBase, scZ(zs[0])],
        ...tauPts,
        [tauBase, scZ(zs[zs.length-1])],
    ];
    poly(svg, tauClosed, C_TAU + FILL_ALPHA, 'none', 0);
    svg.appendChild(svgEl('path', {
        d: tauPts.map(([x,y],i) => `${i===0?'M':'L'}${x},${y}`).join(' '),
        fill: 'none', stroke: C_INK, 'stroke-width': 1.5,
    }));

    // ── Ligne barycentre y=0 ──────────────────────────────────────────────────
    line(svg, ML, ycSvg, ML+halfW*2, ycSvg, C_INK, 0.9, {'stroke-dasharray':'4,3'});

    // ── Axe y (vertical gauche) ───────────────────────────────────────────────
    line(svg, ML, MT, ML, MT+PH, C_AXIS, 1);
    for (const z of [0, zc, h]) {
        const sy = scZ(z);
        const lbl = fmt((z - zc)*1000, 0);   // y en mm
        line(svg, ML-4, sy, ML, sy, C_AXIS, 1);
        text(svg, ML-7, sy+4, lbl, 'end', 11, z===zc ? C_INK : C_MUTED,
             z===zc ? {'font-weight':'700'} : {});
    }
    text(svg, 14, MT+PH/2, 'y [mm]', 'middle', 11, C_MUTED,
         {transform: `rotate(-90 14 ${MT+PH/2})`});

    // ── Graduations σ ─────────────────────────────────────────────────────────
    for (const v of [-sigMax, 0, sigMax]) {
        const xs2 = sigX(v);
        line(svg, xs2, MT+PH, xs2, MT+PH+4, C_AXIS, 1);
        text(svg, xs2, MT+PH+17, fmtVal(v/1e6), 'middle', 11, C_MUTED);
    }
    // ── Graduations τ ─────────────────────────────────────────────────────────
    for (const v of [0, tauMax]) {
        const xs3 = tauX(v);
        line(svg, xs3, MT+PH, xs3, MT+PH+4, C_AXIS, 1);
        text(svg, xs3, MT+PH+17, fmtVal(v/1e6), 'middle', 11, C_MUTED);
    }

    // ── Titres ────────────────────────────────────────────────────────────────
    text(svg, sigBase, MT-12, 'Contrainte normale σ(y)  [MPa]', 'middle', 12, C_INK, { 'font-weight': '600' });
    text(svg, tauBase, MT-12, 'Contrainte de cisaillement τ(y)  [MPa]', 'middle', 12, C_INK, { 'font-weight': '600' });

    el.innerHTML = '';
    el.appendChild(svg);
}
