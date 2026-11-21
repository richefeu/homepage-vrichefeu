// ─── Graphique granulométrique (SVG) ─────────────────────────────────────────
// Abscisse : module AFNOR 20 à 50 (échelle log des tamis) ; ordonnée : passants
// cumulés (%) à gauche, refus à droite.

const CHART_COLORS = {
    axis:  '#9ca3af',
    grid:  '#eef0f3',
    ink:   '#1f2937',
    muted: '#6b7280',
    granu: { S: '#a16207', g: '#6b7280', G: '#374151' },   // granulats
    ref:   '#2563eb',   // courbe de référence de Dreux
    mix:   '#ee7d1f',   // courbe du mélange
    cut:   '#b91c1c',   // lignes de partage
};

const GRANU_NAMES = { S: 'Sable', g: 'Gravette', G: 'Gravier' };

function svgEl(tag, attrs = {}, text) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (text !== undefined) e.textContent = text;
    return e;
}

function fmtChart(v, d = 1) {
    return (Math.round(v * 10 ** d) / 10 ** d).toString();
}

// refus : { S, g, G } ; res : résultat de dreuxCompute (ou null) ; p : paramètres
function renderChart(el, refus, res, p, legendEl) {
    const nbGranu = p.nbGranu;
    const W = Math.max(320, el.clientWidth || 760);
    const narrow = W < 560;
    const H = Math.round(Math.min(560, Math.max(300, W * 0.62)));
    const m = { l: narrow ? 34 : 46, r: narrow ? 34 : 46, t: 26, b: narrow ? 46 : 52 };
    const pw = W - m.l - m.r, ph = H - m.t - m.b;
    const X = mod => m.l + (mod - 20) / 30 * pw;
    const Y = pas => m.t + (1 - pas / 100) * ph;

    const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, 'font-family': 'system-ui, sans-serif', 'font-size': 12 });
    // halo blanc sous les étiquettes posées sur les courbes
    const halo = { stroke: '#fff', 'stroke-width': 3, 'paint-order': 'stroke', 'stroke-linejoin': 'round' };
    const g = (attrs) => svg.appendChild(svgEl('g', attrs));
    const line = (p, x1, y1, x2, y2, attrs) => p.appendChild(svgEl('line', { x1, y1, x2, y2, ...attrs }));
    const text = (p, x, y, s, attrs) => p.appendChild(svgEl('text', { x, y, ...attrs }, s));
    const path = (p, pts, attrs) => p.appendChild(svgEl('path', {
        d: pts.map((q, i) => (i ? 'L' : 'M') + q[0].toFixed(1) + ' ' + q[1].toFixed(1)).join(''),
        fill: 'none', ...attrs }));

    // Quadrillage et axes
    const grid = g({ stroke: CHART_COLORS.grid });
    for (let mod = 21; mod < 50; mod++) line(grid, X(mod), m.t, X(mod), m.t + ph);
    for (let p = 10; p < 100; p += 10) line(grid, m.l, Y(p), m.l + pw, Y(p));
    svg.appendChild(svgEl('rect', { x: m.l, y: m.t, width: pw, height: ph, fill: 'none', stroke: CHART_COLORS.axis }));

    const lab = g({ fill: CHART_COLORS.muted, 'text-anchor': 'middle' });
    const stepMod = narrow ? 3 : 1;
    for (let i = 0; i < MODULES.length; i += stepMod) {
        text(lab, X(MODULES[i]), m.t + ph + 15, MODULES[i], { fill: CHART_COLORS.ink });
    }
    const stepD = narrow ? 3 : 2;
    for (let i = 0; i < DIAMETRES.length; i += stepD) {
        text(lab, X(MODULES[i]), m.t + ph + 29, DIAMETRES[i], { 'font-size': 10 });
    }
    text(lab, m.l + pw / 2, H - 6, 'Module (en haut) et ouverture des tamis en mm (en bas)', { 'font-size': 11 });
    for (let p = 0; p <= 100; p += 10) {
        text(lab, m.l - 6, Y(p) + 4, p, { 'text-anchor': 'end' });
        text(lab, m.l + pw + 6, Y(p) + 4, 100 - p, { 'text-anchor': 'start' });
    }
    text(lab, m.l - 6, m.t - 9, 'Passants (%)', { 'text-anchor': 'start', fill: CHART_COLORS.ink });
    text(lab, m.l + pw + 6, m.t - 9, 'Refus (%)', { 'text-anchor': 'end', fill: CHART_COLORS.ink });

    // Courbes des granulats : points de mesure + courbe lissée
    const keys = nbGranu == 2 ? ['S', 'g'] : ['S', 'g', 'G'];
    const curves = res ? res.curves : Object.fromEntries(keys.map(k => [k, granuCurve(refus[k], p.courbe).pts]));
    for (const k of keys) {
        const col = CHART_COLORS.granu[k];
        const gr = g({ stroke: col, fill: col });
        path(gr, curves[k].map(q => [X(q[0]), Y(q[2])]), { 'stroke-width': 1.5, fill: 'none' });
        refus[k].forEach((r, i) => gr.appendChild(svgEl('circle', { cx: X(MODULES[i]), cy: Y(100 - r), r: 2.5 })));
    }

    if (res) {
        // Lignes de partage
        const cut = g({ stroke: CHART_COLORS.cut, 'stroke-dasharray': '5 3', 'stroke-width': 1.2 });
        for (const [x0, y0, x1, y1] of res.lignesConstr) line(cut, X(x0), Y(y0), X(x1), Y(y1));

        // Proportions lues sur l'axe de droite
        const levels = nbGranu == 2
            ? [['S', 0, res.YS, res.Srate], ['g', res.YS, 100, res.grate]]
            : [['S', 0, res.YS, res.Srate], ['g', res.YS, res.YG, res.grate], ['G', res.YG, 100, res.Grate]];
        const pct = g({ fill: CHART_COLORS.cut, 'text-anchor': 'end', 'font-weight': 600 });
        for (const [k, lo, hi, v] of levels) {
            if (hi - lo < 4) continue;
            text(pct, m.l + pw - 6, Y((lo + hi) / 2) + 4, `${k} : ${fmtChart(v)} %`, halo);
        }

        // Courbe de référence O-A-B
        const ref = g({ stroke: CHART_COLORS.ref, fill: CHART_COLORS.ref });
        const [[ox, oy, ax, ay], [, , bx, by]] = res.briseeConstr;
        path(ref, [[X(ox), Y(oy)], [X(ax), Y(ay)], [X(bx), Y(by)]], { 'stroke-width': 2, fill: 'none' });
        for (const [x, y] of [[ox, oy], [ax, ay], [bx, by]]) ref.appendChild(svgEl('circle', { cx: X(x), cy: Y(y), r: 3.5 }));
        // projections de A sur les axes : X (mm) en bas, Y (%) à gauche
        const proj = g({ stroke: CHART_COLORS.ref, 'stroke-dasharray': '2 3' });
        line(proj, X(ax), Y(ay), X(ax), m.t + ph);
        line(proj, m.l, Y(ay), X(ax), Y(ay));
        const lbl = { ...halo, 'font-weight': 600 };
        text(ref, X(ox) + 6, Y(oy) - 6, 'O', lbl);
        text(ref, X(ax) - 6, Y(ay) - 8, 'A', { ...lbl, 'text-anchor': 'end' });
        text(ref, X(bx) - 8, Y(by) + 16, 'B', { ...lbl, 'text-anchor': 'end' });
        text(ref, m.l + 6, Y(ay) - 6, `Y = ${fmtChart(res.Y)} %`, lbl);
        text(ref, X(ax) + 5, m.t + ph - 6, `X = ${fmtChart(res.X)} mm`, lbl);

        // Courbe du mélange
        path(svg, res.Mrefus.map(q => [X(q[0]), Y(100 - q[1])]), { stroke: CHART_COLORS.mix, 'stroke-width': 2.5 });
    }

    el.innerHTML = '';
    el.appendChild(svg);
    if (legendEl) renderLegend(legendEl, keys, !!res, res && p.courbe == 1 ? res.fits : null);
}

// fits : écarts de l'ajustement, affichés à côté du nom de chaque granulat
function renderLegend(el, keys, withResult, fits) {
    const items = keys.map(k => [GRANU_NAMES[k] + (fits && fits[k] ? ` (écart ${fmtChart(fits[k].rms)} %)` : ''),
        CHART_COLORS.granu[k], false]);
    if (withResult) items.push(['Référence de Dreux O-A-B', CHART_COLORS.ref, false],
        ['Mélange', CHART_COLORS.mix, false], ['Lignes de partage', CHART_COLORS.cut, true]);
    el.innerHTML = items.map(([n, c, d]) =>
        `<span><i class="${d ? 'dash' : ''}" style="border-color:${c}"></i>${n}</span>`).join('');
}
