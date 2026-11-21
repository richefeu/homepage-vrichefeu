'use strict';

// ─── État de l'application ────────────────────────────────────────────────────
// Nœuds repérés par leur indice (lettre A, B, C… dans l'ordre de la liste).
const state = {
    type: 'treillis',                    // 'treillis' (nœuds articulés) ou 'portique' (nœuds rigides)
    // Matériau de la section commune ; une section propre porte son matériau dans sec.mat
    matAll: { materialName: 'acier', E: 210e9, rho: 7850, f: 235e6 },
    section: null,
    sectionAll: { type: 'circ', d: 0.06 },
    nodes: [{ x: 0, y: 0 }, { x: 4, y: 0 }, { x: 2, y: 2 }],
    bars: [{ n1: 0, n2: 2, sec: null }, { n1: 1, n2: 2, sec: null }, { n1: 0, n2: 1, sec: null }],
    supports: [{ node: 0, type: 'XY' }, { node: 1, type: 'Y' }],
    loads: [{ node: 2, Fx: 0, Fy: -10000, Mz: 0 }],
    barLoads: [],                        // charges réparties (portique) : { bar, qx, qy } en N/m
    selfWeight: false,
    // Section éditée : -1 pour la section commune, sinon indice d'une barre à section propre
    editTarget: -1,
    get sectionParams() {
        const b = this.bars[this.editTarget];
        return b && b.sec ? b.sec : this.sectionAll;
    },
    set sectionParams(v) { this.sectionAll = v; },
    mode: 'view',                        // édition au clic : 'view', 'node' ou 'bar'
    pending: null,                       // premier nœud choisi en mode « + Barre »
    frameQty: 'M',
    showDeformed: true,
    res: null,
    view: null,
};

// ─── Persistance localStorage ────────────────────────────────────────────────
// Clés propres à cette application (même domaine que les applications poutre)
const LS_AUTOSAVE = 'msolution_treillis_autosave';
const LS_SLOTS    = 'msolution_treillis_slots';
const MAX_SLOTS   = 20;   // 14 exemples + 6 emplacements libres

const clone = o => JSON.parse(JSON.stringify(o));

function serializeState() {
    return clone({
        type: state.type, matAll: state.matAll,
        sectionParams: state.sectionAll,
        nodes: state.nodes, bars: state.bars, supports: state.supports, loads: state.loads,
        barLoads: state.barLoads, selfWeight: state.selfWeight,
    });
}

function applyStateData(data) {
    if (!data || !Array.isArray(data.nodes)) return false;
    state.type         = data.type === 'portique' ? 'portique' : 'treillis';
    state.matAll       = data.matAll ?? { materialName: data.materialName ?? 'acier', E: data.E ?? 210e9, rho: 7850, f: 235e6 };
    state.sectionAll   = data.sectionParams ?? { type: 'circ', d: 0.06 };
    state.barLoads     = data.barLoads ?? [];
    state.selfWeight   = !!data.selfWeight;
    state.nodes        = data.nodes;
    state.bars         = (data.bars ?? []).map(b => ({ sec: null, ...b }));
    state.supports     = data.supports ?? [];
    state.loads        = data.loads    ?? [];
    state.editTarget   = -1;
    state.pending      = null;
    return true;
}

// ─── Exemples (complexité croissante) ─────────────────────────────────────────
// Treillis : tube plein Ø60 mm en acier sauf mention contraire. Forces en N.
// Les exemples « exo » / « test » reprennent MSolution/exos/treillis et tests/treillis.
const TUBE = { type: 'circ', d: 0.06 };
const barList = list => list.map(([n1, n2]) => ({ n1, n2, sec: null }));

// Presse de flexion IUT (presseIUT/presse.tex, config. « poutre béton », F = 50 kN).
// Nœuds A…P = nœuds 1…16 du document. Liens rigides articulés côté liaison :
// rotule = articulé d'un côté, appui glissant = bi-articulé.
const PRESSE_BATI = (() => {
    const yb = 0.9, yp = 1.2;   // arrondis : sans effet sous charges verticales
    const sec = (A, I, h, mat) => ({ type: 'custom', A: A * 1e-4, Iz: I * 1e-8, Iy: I * 1e-8, h, ...(mat ? { mat: { materialName: mat } } : {}) });
    const col = sec(10.7, 30.6, 0.05), top = sec(78.1, 5696, 0.2), bot = sec(156.2, 11392, 0.2),
          spe = sec(300, 10000, 0.15, 'beton'), lnk = sec(100, 1000, 0.1);
    const B = (a, b, sc, o = {}) => ({ n1: a - 1, n2: b - 1, sec: sc ? clone(sc) : null, ...o });
    return { title: 'Presse IUT : bâti et poutre béton, F + poids propre', type: 'portique', selfWeight: true,
        sectionParams: { type: 'custom', A: 0.00107, Iz: 3.06e-7, Iy: 3.06e-7, h: 0.05 },
        nodes: [{x:-0.5,y:0}, {x:0.5,y:0}, {x:-0.5,y:0.8}, {x:0.5,y:0.8}, {x:-0.5,y:1.8}, {x:0.5,y:1.8}, {x:0,y:1.8},
                {x:-1,y:yb}, {x:-0.8,y:yb}, {x:-0.5,y:yb}, {x:0.5,y:yb}, {x:0.8,y:yb}, {x:1,y:yb},
                {x:-0.8,y:yp}, {x:0,y:yp}, {x:0.8,y:yp}],
        bars: [B(1,3), B(3,5), B(2,4), B(4,6), B(5,7,top), B(7,6,top),
               B(8,9,bot), B(9,10,bot), B(10,11,bot), B(11,12,bot), B(12,13,bot), B(14,15,spe), B(15,16,spe),
               B(3,10,lnk,{h1:true}), B(4,11,lnk,{h1:true,h2:true}), B(9,14,lnk,{h2:true}), B(12,16,lnk,{h1:true,h2:true})],
        supports: [{node:0,type:'Y'}, {node:1,type:'Y'}, {node:6,type:'X'}],
        loads: [{node:6,Fx:0,Fy:50000,Mz:0}, {node:14,Fx:0,Fy:-50000,Mz:0}] };
})();

// Éprouvette en treillis de Howe (config. « treillis bois » : n = 6, L = 3 m, z = 0,415 m, F = 100 kN)
const PRESSE_TREILLIS = (() => {
    const n = 6, L = 3, z = 0.415, dx = L / n, nodes = [], pairs = [];
    for (let i = 0; i <= n; i++) nodes.push({ x: +(-L / 2 + i * dx).toFixed(3), y: 0 });
    for (let i = 0; i <= n; i++) nodes.push({ x: +(-L / 2 + i * dx).toFixed(3), y: z });
    const T = i => n + 1 + i;
    for (let i = 0; i < n; i++) pairs.push([i, i + 1], [T(i), T(i + 1)]);
    for (let i = 0; i <= n; i++) pairs.push([i, T(i)]);
    for (let i = 0; i < n / 2; i++) pairs.push([i, T(i + 1)]);
    for (let i = n / 2; i < n; i++) pairs.push([T(i), i + 1]);
    return { title: 'Presse IUT : éprouvette en treillis de Howe (bois)', type: 'treillis', materialName: 'bois',
        sectionParams: { type: 'rect', b: 0.045, h: 0.095 },
        nodes, bars: barList(pairs),
        supports: [{node:0,type:'XY'}, {node:n,type:'Y'}],
        loads: [{node:T(n / 2),Fx:0,Fy:-100000,Mz:0}] };
})();
const EXAMPLES = [
    { title: 'Treillis triangulaire, charge au sommet', type: 'treillis',
      nodes: [{x:0,y:0}, {x:4,y:0}, {x:2,y:2}],
      bars: barList([[0,2],[1,2],[0,1]]),
      supports: [{node:0,type:'XY'}, {node:1,type:'Y'}],
      loads: [{node:2,Fx:0,Fy:-10000,Mz:0}] },
    { title: 'Potence murale', type: 'treillis',
      nodes: [{x:0,y:0}, {x:0,y:2}, {x:3,y:0}],
      bars: barList([[0,2],[1,2]]),
      supports: [{node:0,type:'XY'}, {node:1,type:'XY'}],
      loads: [{node:2,Fx:0,Fy:-10000,Mz:0}] },
    { title: 'Poutre de Warren', type: 'treillis',
      nodes: [{x:0,y:0}, {x:1,y:2}, {x:2,y:0}, {x:3,y:2}, {x:4,y:0}, {x:5,y:2}, {x:6,y:0}],
      bars: barList([[0,2],[2,4],[4,6],[1,3],[3,5],[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]]),
      supports: [{node:0,type:'XY'}, {node:6,type:'Y'}],
      loads: [{node:2,Fx:0,Fy:-20000,Mz:0}, {node:4,Fx:0,Fy:-20000,Mz:0}] },
    { title: 'Exo 25 : ferme en bois', type: 'treillis', materialName: 'bois',
      nodes: [{x:0,y:0}, {x:1.5,y:0.866}, {x:3,y:1.732}, {x:4.5,y:0.866}, {x:6,y:0}, {x:3,y:0}],
      bars: barList([[0,5],[0,1],[1,5],[5,4],[5,3],[3,4],[2,1],[2,5],[2,3]]),
      supports: [{node:0,type:'XY'}, {node:4,type:'Y'}],
      loads: [{node:0,Fx:0,Fy:-450,Mz:0}, {node:1,Fx:0,Fy:-900,Mz:0}, {node:2,Fx:0,Fy:-900,Mz:0},
              {node:3,Fx:0,Fy:-900,Mz:0}, {node:4,Fx:0,Fy:-450,Mz:0}] },
    { title: 'Poutre de Pratt : barres à effort nul', type: 'treillis',
      nodes: [{x:0,y:0}, {x:2,y:0}, {x:4,y:0}, {x:6,y:0}, {x:8,y:0}, {x:2,y:2}, {x:4,y:2}, {x:6,y:2}],
      bars: barList([[0,1],[1,2],[2,3],[3,4],[5,6],[6,7],[1,5],[2,6],[3,7],[0,5],[5,2],[7,2],[7,4]]),
      supports: [{node:0,type:'XY'}, {node:4,type:'Y'}],
      loads: [{node:1,Fx:0,Fy:-10000,Mz:0}, {node:2,Fx:0,Fy:-10000,Mz:0}, {node:3,Fx:0,Fy:-10000,Mz:0}] },
    { title: 'Treillis hyperstatique (deux diagonales)', type: 'treillis',
      nodes: [{x:0,y:0}, {x:3,y:0}, {x:3,y:3}, {x:0,y:3}],
      bars: barList([[0,1],[1,2],[2,3],[3,0],[0,2],[1,3]]),
      supports: [{node:0,type:'XY'}, {node:1,type:'Y'}],
      loads: [{node:3,Fx:10000,Fy:0,Mz:0}, {node:2,Fx:0,Fy:-10000,Mz:0}] },
    { title: 'Portique : console IPE 300', type: 'portique',
      sectionParams: { type: 'ipe-I', num: 300 },
      nodes: [{x:0,y:0}, {x:3,y:0}],
      bars: barList([[0,1]]),
      supports: [{node:0,type:'XYtheta'}],
      loads: [{node:1,Fx:0,Fy:-50000,Mz:0}] },
    { title: 'Portique : poutre sur deux appuis', type: 'portique',
      sectionParams: { type: 'rect', b: 0.1, h: 0.3 },
      nodes: [{x:0,y:0}, {x:2,y:0}, {x:4,y:0}],
      bars: barList([[0,1],[1,2]]),
      supports: [{node:0,type:'XY'}, {node:2,type:'Y'}],
      loads: [{node:1,Fx:0,Fy:-12000,Mz:0}] },
    { title: 'Portique encastré, charge verticale', type: 'portique',
      sectionParams: { type: 'ipe-I', num: 200 },
      nodes: [{x:0,y:0}, {x:0,y:3}, {x:2,y:3}, {x:4,y:3}, {x:4,y:0}],
      bars: barList([[0,1],[1,2],[2,3],[3,4]]),
      supports: [{node:0,type:'XYtheta'}, {node:4,type:'XYtheta'}],
      loads: [{node:2,Fx:0,Fy:-20000,Mz:0}] },
    { title: 'Portique encastré, charge horizontale (vent)', type: 'portique',
      sectionParams: { type: 'ipe-I', num: 200 },
      nodes: [{x:0,y:0}, {x:0,y:4}, {x:3,y:4}, {x:3,y:0}],
      bars: barList([[0,1],[1,2],[2,3]]),
      supports: [{node:0,type:'XYtheta'}, {node:3,type:'XYtheta'}],
      loads: [{node:1,Fx:5000,Fy:0,Mz:0}] },
    { title: 'Portique encastré, charge répartie sur la traverse', type: 'portique',
      sectionParams: { type: 'ipe-I', num: 200 },
      nodes: [{x:0,y:0}, {x:0,y:3}, {x:4,y:3}, {x:4,y:0}],
      bars: barList([[0,1],[1,2],[2,3]]),
      supports: [{node:0,type:'XYtheta'}, {node:3,type:'XYtheta'}],
      loads: [], barLoads: [{bar:1,qx:0,qy:-10000}] },
    { title: 'Portique à traverse articulée (rotules), charge répartie', type: 'portique',
      sectionParams: { type: 'ipe-I', num: 200 },
      nodes: [{x:0,y:0}, {x:0,y:3}, {x:4,y:3}, {x:4,y:0}],
      bars: [{n1:0,n2:1,sec:null}, {n1:1,n2:2,sec:null,h1:true,h2:true}, {n1:2,n2:3,sec:null}],
      supports: [{node:0,type:'XYtheta'}, {node:3,type:'XYtheta'}],
      loads: [], barLoads: [{bar:1,qx:0,qy:-10000}] },
    PRESSE_BATI,
    PRESSE_TREILLIS,
];

// Exemple i → contenu d'un emplacement de sauvegarde
function exampleSlot(i) {
    const ex = EXAMPLES[i];
    const mat = ex.materialName || 'acier';
    return {
        name: `${i + 1}. ${ex.title}`,
        timestamp: 'exemple fourni',
        data: clone({
            type: ex.type, matAll: { materialName: mat, ...matProps({ materialName: mat }) },
            sectionParams: ex.sectionParams || TUBE,
            nodes: ex.nodes, bars: ex.bars, supports: ex.supports, loads: ex.loads,
            barLoads: ex.barLoads || [], selfWeight: !!ex.selfWeight,
        }),
    };
}

// ─── Initialisation ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    buildSectionUI();
    buildMaterialUI();
    installExamplesIfFirstVisit();
    bindEvents();
    tryLoadAutosave();
    syncUIFromState();
    renderSlots();
    compute();

    // Autosave + recalcul sur tout changement hors zone slots
    const onParamChange = e => {
        if (e.target.closest('.slot-row')) return;
        scheduleAutosave();
        tryBuildSection();
        scheduleRender();
    };
    document.addEventListener('input',  onParamChange);
    document.addEventListener('change', onParamChange);

    // Les dessins sont tracés à la largeur de leur conteneur
    let t = null;
    window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(renderAll, 150); });
});

function bindEvents() {
    document.querySelectorAll('input[name="struct-type"]').forEach(r =>
        r.addEventListener('change', e => setStructureType(e.target.value)));
    id('btn-add-node').addEventListener('click', addNode);
    id('btn-add-bar').addEventListener('click', addBar);
    id('btn-add-support').addEventListener('click', addSupport);
    id('btn-add-load').addEventListener('click', addLoad);
    id('btn-reset-examples').addEventListener('click', resetExamples);
    id('btn-clear-slots').addEventListener('click', clearAllSlots);
    id('btn-export').addEventListener('click', exportSlotsToFile);
    id('btn-import').addEventListener('click', importSlotsFromFile);
    id('section-target').addEventListener('change', e => {
        state.editTarget = +e.target.value;
        refreshSectionEditor();
    });
    id('section-type').addEventListener('change', () => {
        updateSectionParams();
        state.section = null;
    });
    id('material-select').addEventListener('change', e => {
        const m = matTarget();
        if (e.target.value === 'custom' && m.materialName !== 'custom') Object.assign(m, matProps(m));
        m.materialName = e.target.value;
        syncMaterialUI();
    });
    const custom = (elId, key, k) => id(elId).addEventListener('input', e => {
        matTarget()[key] = (parseFloat(e.target.value) || 0) * k;
        syncMaterialUI();
    });
    custom('material-custom-E', 'E', 1e9);
    custom('material-custom-rho', 'rho', 1);
    custom('material-custom-f', 'f', 1e6);
    id('self-weight').addEventListener('change', e => { state.selfWeight = e.target.checked; });
    id('btn-add-bar-load').addEventListener('click', addBarLoad);

    // Édition au clic sur le schéma
    document.querySelectorAll('.tool[data-mode]').forEach(btn =>
        btn.addEventListener('click', () => setMode(btn.dataset.mode)));
    id('schema-svg').addEventListener('click', onSchemaClick);
    id('show-deformed').addEventListener('change', e => { state.showDeformed = e.target.checked; renderSchema(); });

    // Effort affiché sur les diagrammes du portique
    document.querySelectorAll('.tool.qty').forEach(btn => btn.addEventListener('click', () => {
        state.frameQty = btn.dataset.qty;
        document.querySelectorAll('.tool.qty').forEach(b => b.classList.toggle('active', b === btn));
        renderFrame();
    }));
}

// ─── Type de structure ────────────────────────────────────────────────────────
const TYPE_HINTS = {
    treillis: 'Nœuds articulés : chaque barre ne porte qu\'un effort normal N. Charges appliquées aux nœuds.',
    portique: 'Nœuds rigides : les barres portent N, V et M. Une rotule en bout de barre y annule le moment.',
};

function setStructureType(type) {
    state.type = type;
    // En treillis, un encastrement se comporte comme une articulation
    if (type === 'treillis') state.supports.forEach(s => { if (s.type === 'XYtheta') s.type = 'XY'; });
    syncTypeUI();
    renderLists();
}

function syncTypeUI() {
    document.querySelectorAll('input[name="struct-type"]').forEach(r => { r.checked = r.value === state.type; });
    id('type-hint').textContent = TYPE_HINTS[state.type];
    id('bar-loads-block').style.display = state.type === 'portique' ? '' : 'none';
    id('self-weight').checked = state.selfWeight;
    id('self-weight-hint').textContent = state.type === 'portique'
        ? 'Charge répartie ρ·g·A sur chaque barre.'
        : 'En treillis, le poids de chaque barre est réparti pour moitié sur ses deux nœuds.';
}

// ─── Listes de saisie ─────────────────────────────────────────────────────────
function renderLists() {
    renderNodesList();
    renderBarsList();
    renderSupportsList();
    renderLoadsList();
    renderBarLoadsList();
    renderSectionTarget();
}

function nodeSelect(value, onChange) {
    const sel = document.createElement('select');
    sel.className = 'inp-node';
    state.nodes.forEach((_, i) => {
        const o = document.createElement('option');
        o.value = i; o.textContent = nodeName(i);
        sel.appendChild(o);
    });
    sel.value = value;
    sel.addEventListener('change', e => { onChange(+e.target.value); renderLists(); });
    return sel;
}

function deleteButton(onClick) {
    const btn = document.createElement('button');
    btn.textContent = '✕'; btn.className = 'btn-icon';
    btn.addEventListener('click', () => { onClick(); renderLists(); scheduleAutosave(); scheduleRender(); });
    return btn;
}

function renderNodesList() {
    const ul = id('nodes-list');
    ul.innerHTML = '';
    state.nodes.forEach((n, i) => {
        const li = document.createElement('li');
        li.className = 'item-row';
        const lbl = document.createElement('span');
        lbl.className = 'item-label'; lbl.textContent = nodeName(i);
        li.appendChild(lbl);
        li.appendChild(labelText('x (m) :')); li.appendChild(numInput(n.x, 0.1, v => { n.x = v; }, 'x'));
        li.appendChild(labelText('y (m) :')); li.appendChild(numInput(n.y, 0.1, v => { n.y = v; }, 'y'));
        li.appendChild(deleteButton(() => deleteNode(i)));
        ul.appendChild(li);
    });
}

function addNode() {
    if (state.nodes.length >= 26) { showError('26 nœuds au maximum.'); return; }
    const last = state.nodes[state.nodes.length - 1];
    state.nodes.push(last ? { x: last.x + 1, y: last.y } : { x: 0, y: 0 });
    renderLists(); scheduleAutosave(); scheduleRender();
}

// Supprime un nœud et tout ce qui s'y rattache, puis renumérote
// Retire les barres pour lesquelles drop(b, k) est vrai, en gardant les charges réparties cohérentes
function removeBars(drop) {
    const keep = [], map = new Map();
    state.bars.forEach((b, k) => { if (!drop(b, k)) { map.set(k, keep.length); keep.push(b); } });
    state.bars = keep;
    state.barLoads = state.barLoads.filter(l => map.has(l.bar)).map(l => ({ ...l, bar: map.get(l.bar) }));
    state.editTarget = -1;
}

function deleteNode(i) {
    const re = k => (k > i ? k - 1 : k);
    removeBars(b => b.n1 === i || b.n2 === i);
    state.bars = state.bars.map(b => ({ ...b, n1: re(b.n1), n2: re(b.n2) }));
    state.supports = state.supports.filter(s => s.node !== i).map(s => ({ ...s, node: re(s.node) }));
    state.loads = state.loads.filter(l => l.node !== i).map(l => ({ ...l, node: re(l.node) }));
    state.nodes.splice(i, 1);
    state.editTarget = -1;
    state.pending = null;
}

function renderBarsList() {
    const ul = id('bars-list');
    ul.innerHTML = '';
    state.bars.forEach((b, i) => {
        const li = document.createElement('li');
        li.className = 'item-row';
        const lbl = document.createElement('span');
        lbl.className = 'item-label bar-label'; lbl.textContent = barName(b);
        li.appendChild(lbl);
        li.appendChild(nodeSelect(b.n1, v => { b.n1 = v; }));
        li.appendChild(labelText('–'));
        li.appendChild(nodeSelect(b.n2, v => { b.n2 = v; }));

        const secSel = document.createElement('select');
        secSel.className = 'inp-sec';
        secSel.title = 'Section de la barre';
        [['common', 'commune'], ['own', 'propre']].forEach(([v, t]) => {
            const o = document.createElement('option'); o.value = v; o.textContent = t; secSel.appendChild(o);
        });
        secSel.value = b.sec ? 'own' : 'common';
        secSel.addEventListener('change', e => {
            if (e.target.value === 'own') { b.sec = { ...clone(state.sectionAll), mat: clone(state.matAll) }; state.editTarget = i; }
            else { b.sec = null; if (state.editTarget === i) state.editTarget = -1; }
            refreshSectionEditor();
        });
        li.appendChild(secSel);
        if (state.type === 'portique') {
            const hs = document.createElement('select');
            hs.className = 'inp-hinge';
            hs.title = 'Rotule en bout de barre : le moment y est nul';
            const a = nodeName(b.n1), c = nodeName(b.n2);
            [['', 'sans rotule'], ['1', `rotule en ${a}`], ['2', `rotule en ${c}`], ['12', `rotules en ${a} et ${c}`]]
                .forEach(([v, t]) => { const o = document.createElement('option'); o.value = v; o.textContent = t; hs.appendChild(o); });
            hs.value = (b.h1 ? '1' : '') + (b.h2 ? '2' : '');
            hs.addEventListener('change', e => { b.h1 = e.target.value.includes('1'); b.h2 = e.target.value.includes('2'); });
            li.appendChild(hs);
        }
        li.appendChild(deleteButton(() => removeBars((_, k) => k === i)));
        ul.appendChild(li);
    });
}

function addBar() {
    // première paire de nœuds pas encore reliée
    const n = state.nodes.length;
    for (let a = 0; a < n; a++) for (let b = a + 1; b < n; b++) {
        if (!state.bars.some(r => (r.n1 === a && r.n2 === b) || (r.n1 === b && r.n2 === a))) {
            state.bars.push({ n1: a, n2: b, sec: null });
            renderLists(); scheduleAutosave(); scheduleRender();
            return;
        }
    }
    showError('Tous les nœuds sont déjà reliés : ajoutez d\'abord un nœud.');
}

function renderSupportsList() {
    const ul = id('supports-list');
    ul.innerHTML = '';
    const types = state.type === 'portique' ? ['XY', 'Y', 'X', 'XYtheta'] : ['XY', 'Y', 'X'];
    state.supports.forEach((s, i) => {
        const li = document.createElement('li');
        li.className = 'item-row';
        li.appendChild(labelText('Nœud'));
        li.appendChild(nodeSelect(s.node, v => { s.node = v; }));
        const sel = document.createElement('select');
        sel.className = 'inp-support';
        types.forEach(t => {
            const o = document.createElement('option'); o.value = t; o.textContent = SUPPORT_LABELS[t]; sel.appendChild(o);
        });
        sel.value = s.type;
        sel.addEventListener('change', e => { s.type = e.target.value; });
        li.appendChild(sel);
        li.appendChild(deleteButton(() => state.supports.splice(i, 1)));
        ul.appendChild(li);
    });
}

function addSupport() {
    const free = state.nodes.findIndex((_, i) => !state.supports.some(s => s.node === i));
    if (free < 0) { showError('Chaque nœud a déjà une liaison.'); return; }
    state.supports.push({ node: free, type: 'XY' });
    renderLists(); scheduleAutosave(); scheduleRender();
}

function renderLoadsList() {
    const ul = id('loads-list');
    ul.innerHTML = '';
    state.loads.forEach((l, i) => {
        const li = document.createElement('li');
        li.className = 'item-row';
        li.appendChild(labelText('Nœud'));
        li.appendChild(nodeSelect(l.node, v => { l.node = v; }));
        li.appendChild(labelText('Fx (kN) :')); li.appendChild(numInput((l.Fx || 0) / 1e3, 0.1, v => { l.Fx = v * 1e3; }, 'Fx'));
        li.appendChild(labelText('Fy (kN) :')); li.appendChild(numInput((l.Fy || 0) / 1e3, 0.1, v => { l.Fy = v * 1e3; }, 'Fy'));
        if (state.type === 'portique') {
            li.appendChild(labelText('Mz (kN·m) :'));
            li.appendChild(numInput((l.Mz || 0) / 1e3, 0.1, v => { l.Mz = v * 1e3; }, 'Mz'));
        }
        li.appendChild(deleteButton(() => state.loads.splice(i, 1)));
        ul.appendChild(li);
    });
}

function renderBarLoadsList() {
    const ul = id('bar-loads-list');
    ul.innerHTML = '';
    state.barLoads.forEach((l, i) => {
        const li = document.createElement('li');
        li.className = 'item-row';
        li.appendChild(labelText('Barre'));
        const sel = document.createElement('select');
        sel.className = 'inp-node';
        state.bars.forEach((b, k) => { const o = document.createElement('option'); o.value = k; o.textContent = barName(b); sel.appendChild(o); });
        sel.value = l.bar;
        sel.addEventListener('change', e => { l.bar = +e.target.value; });
        li.appendChild(sel);
        li.appendChild(labelText('qx (kN/m) :')); li.appendChild(numInput((l.qx || 0) / 1e3, 0.1, v => { l.qx = v * 1e3; }, 'qx'));
        li.appendChild(labelText('qy (kN/m) :')); li.appendChild(numInput((l.qy || 0) / 1e3, 0.1, v => { l.qy = v * 1e3; }, 'qy'));
        li.appendChild(deleteButton(() => state.barLoads.splice(i, 1)));
        ul.appendChild(li);
    });
}

function addBarLoad() {
    if (!state.bars.length) return;
    state.barLoads.push({ bar: 0, qx: 0, qy: -5000 });
    renderLists(); scheduleAutosave(); scheduleRender();
}

function addLoad() {
    if (!state.nodes.length) return;
    state.loads.push({ node: state.nodes.length - 1, Fx: 0, Fy: -10000, Mz: 0 });
    renderLists(); scheduleAutosave(); scheduleRender();
}

// ─── Section : commune ou propre à une barre ──────────────────────────────────
function renderSectionTarget() {
    const sel = id('section-target');
    sel.innerHTML = '';
    const add = (v, t) => { const o = document.createElement('option'); o.value = v; o.textContent = t; sel.appendChild(o); };
    add(-1, 'toutes les barres (commune)');
    state.bars.forEach((b, i) => { if (b.sec) add(i, `barre ${barName(b)} (propre)`); });
    if (!(state.bars[state.editTarget] && state.bars[state.editTarget].sec)) state.editTarget = -1;
    sel.value = state.editTarget;
}

function refreshSectionEditor() {
    renderSectionTarget();
    id('section-type').value = state.sectionParams.type;
    updateSectionParams();
    syncMaterialUI();
    tryBuildSection();
}

function tryBuildSection() {
    try {
        state.section = buildSection();
        const s = state.section;
        id('section-info').textContent =
            `${s.name}\nA = ${fmt(s.area*1e4,2)} cm²\n` +
            `Iz = ${fmt(s.Iz*1e8,2)} cm⁴\nIy = ${fmt(s.Iy*1e8,2)} cm⁴`;
        const b = state.bars[state.editTarget];
        id('section-card-title').textContent = b && b.sec ? `Section — barre ${barName(b)}` : 'Section commune';
    } catch {
        state.section = null;
        id('section-info').textContent = '';
    }
}

function syncUIFromState() {
    syncTypeUI();
    renderLists();
    refreshSectionEditor();
}

// ─── Édition au clic ──────────────────────────────────────────────────────────
const TOOL_HINTS = {
    view: '',
    node: 'Cliquez sur la grille pour placer un nœud (il s\'accroche aux points de la grille).',
    bar:  'Cliquez sur un nœud de départ puis sur un nœud d\'arrivée. L\'arrivée devient le départ suivant ; cliquez dans le vide pour arrêter.',
};

function setMode(mode) {
    state.mode = mode;
    state.pending = null;
    document.querySelectorAll('.tool[data-mode]').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
    id('tool-hint').textContent = TOOL_HINTS[mode];
    id('tool-hint').style.display = TOOL_HINTS[mode] ? '' : 'none';
    renderSchema();
}

function onSchemaClick(e) {
    const v = state.view, svg = id('schema-svg').querySelector('svg');
    if (state.mode === 'view' || !v || !svg) return;
    const rect = svg.getBoundingClientRect();
    const px = (e.clientX - rect.left) * v.W / rect.width;
    const py = (e.clientY - rect.top) * v.H / rect.height;
    const hit = state.nodes.findIndex(n => Math.hypot(v.X(n.x) - px, v.Y(n.y) - py) < 12);

    if (state.mode === 'node') {
        if (hit >= 0) return;
        if (state.nodes.length >= 26) { showError('26 nœuds au maximum.'); return; }
        const st = niceStep(v.span / 12);
        let [x, y] = v.toWorld(px, py);
        x = +(Math.round(x / st) * st).toFixed(6);
        y = +(Math.round(y / st) * st).toFixed(6);
        if (state.nodes.some(n => Math.hypot(n.x - x, n.y - y) < 1e-9)) return;
        state.nodes.push({ x, y });
    } else {
        if (hit < 0) { state.pending = null; renderSchema(); return; }
        if (state.pending === null || state.pending === hit) { state.pending = hit; renderSchema(); return; }
        const a = state.pending;
        if (!state.bars.some(b => (b.n1 === a && b.n2 === hit) || (b.n1 === hit && b.n2 === a)))
            state.bars.push({ n1: a, n2: hit, sec: null });
        state.pending = hit;
    }
    renderLists();
    scheduleAutosave();
    compute();
}

// ─── Calcul principal ─────────────────────────────────────────────────────────
function compute() {
    clearError();
    state.res = null;
    const { type, nodes, bars, supports, loads } = state;
    let err = checkStructure(nodes, bars, supports, loads);
    const dg = structureDegree(type, nodes, bars, supports);

    if (!err) {
        try {
            state.barSections = bars.map(b => buildSectionFromParams(b.sec || state.sectionAll));
        } catch (e) { err = 'section : ' + e.message; }
    }
    state.barMats = bars.map((_, k) => barMat(k));
    if (!err && state.barMats.some(m => !(m.E > 0))) err = 'le module d\'Young E doit être strictement positif.';
    if (!err && state.barSections.some(s => !(s.area > 0) || (type === 'portique' && !(s.Iz > 0))))
        err = 'chaque section doit avoir une aire (et, pour un portique, un moment quadratique) strictement positive.';
    if (!err && type === 'portique' && state.barLoads.some(l => !bars[l.bar]))
        err = 'une charge répartie porte sur une barre inexistante.';

    let mechanism = false;
    if (!err && dg.degree >= 0) {
        const r = solveStructure({ type, nodes, bars, supports, loads, barLoads: state.barLoads,
            selfWeight: state.selfWeight, sections: state.barSections,
            E: state.barMats.map(m => m.E), rho: state.barMats.map(m => m.rho) });
        if (r.ok) state.res = r;
        else if (r.mechanism) mechanism = true;
        else err = r.error;
    }
    updateStatus(err, dg, mechanism);
    renderAll();
    id('results').style.display = state.res ? 'flex' : 'none';
}

let _renderTimer = null;
function scheduleRender() {
    clearTimeout(_renderTimer);
    _renderTimer = setTimeout(compute, 80);   // recalcul automatique
}

// ─── Message d'état (degré d'hyperstaticité) ─────────────────────────────────
function updateStatus(err, dg, mechanism) {
    const el = id('static-status');
    const name = state.type === 'treillis' ? 'Treillis' : 'Portique';
    const legend = ` (b barres, r inconnues de liaison, n nœuds${dg.c ? ', c rotules en bout de barre' : ''}${dg.f ? ', f nœuds entièrement articulés' : ''})`;
    let ok = false, txt;
    if (err) txt = `Structure incomplète : ${err}`;
    else if (dg.degree < 0) txt = `${name} hypostatique — ${dg.formula}${legend} : ajoutez une barre ou une liaison.`;
    else if (mechanism) txt = `Mécanisme — ${dg.formula}, mais la structure peut bouger sans déformer ses barres : revoyez la disposition des barres ou des liaisons.`;
    else {
        ok = true;
        txt = dg.degree === 0 ? `✓ ${name} isostatique — ${dg.formula}${legend}`
                              : `✓ ${name} hyperstatique de degré ${dg.degree} — ${dg.formula}${legend}`;
    }
    el.textContent = txt;
    el.className = 'status ' + (ok ? 'status-ok' : 'status-bad');
}

// ─── Rendu ────────────────────────────────────────────────────────────────────
function renderSchema() {
    state.view = renderStructure(id('schema-svg'), {
        type: state.type, nodes: state.nodes, bars: state.bars, supports: state.supports,
        loads: state.loads, barLoads: state.type === 'portique' ? state.barLoads : [],
        selfWeight: state.selfWeight, res: state.res, mode: state.mode, pending: state.pending,
        showDeformed: state.showDeformed,
    });
}

function renderFrame() {
    const show = state.res && state.type === 'portique';
    id('frame-card').style.display = show ? '' : 'none';
    if (show) renderFrameDiagram(id('frame-svg'), {
        type: state.type, nodes: state.nodes, bars: state.bars, supports: state.supports, res: state.res,
    }, state.frameQty);
}

function renderAll() {
    renderSchema();
    renderSection(id('section-svg'), state.section);
    if (!state.res) return;
    renderFrame();
    renderReactionsTable();
    renderBarsTable();
    renderEquilibrium();
    renderDispTable();
}

// Remplit une table : en-têtes (HTML) et lignes (tableaux de cellules HTML)
function fillTable(tableId, heads, rows) {
    const t = id(tableId);
    t.querySelector('thead').innerHTML = `<tr>${heads.map(h => `<th>${h}</th>`).join('')}</tr>`;
    t.querySelector('tbody').innerHTML = rows.map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`).join('');
}

const kN = v => fmt(v / 1e3, 2);

function renderReactionsTable() {
    const port = state.type === 'portique';
    fillTable('reactions-table',
        ['Nœud', 'R<sub>x</sub> (kN)', 'R<sub>y</sub> (kN)', ...(port ? ['M<sub>z</sub> (kN·m)'] : [])],
        state.res.reactions.map(r => [nodeName(r.node), kN(r.Rx), kN(r.Ry), ...(port ? [kN(r.Mz)] : [])]));
}

function renderBarsTable() {
    const port = state.type === 'portique';
    const res = state.res;
    const Nmax = Math.max(...res.barRes.map(b => Math.max(Math.abs(b.N1), Math.abs(b.N2))), 1e-9);
    const two = (a, b) => Math.abs(a - b) > 1e-6 * Nmax ? `${kN(a)} → ${kN(b)}` : kN(a);
    const rows = state.bars.map((b, k) => {
        const br = res.barRes[k], mat = state.barMats[k];
        const Nc = Math.min(br.N1, br.N2), Nt = Math.max(br.N1, br.N2);
        const zero = Math.max(Math.abs(Nc), Math.abs(Nt)) < 1e-6 * Nmax;
        const nature = zero ? '<span class="tag zero">nul</span>'
                     : Nc < 0 ? '<span class="tag neg">compression</span>' : '<span class="tag pos">traction</span>';
        const bk = bucklingCheck(mat.E, br.sec, br.L, zero ? 0 : Nc);
        const safety = bk.safety === null ? '—'
                     : bk.safety < 1 ? `<span class="danger">⚠ ${fmt(bk.safety, 2)}</span>` : fmt(bk.safety, 2);
        const smax = maxStress(br), ratio = mat.f > 0 ? smax / mat.f : null;
        const rt = ratio === null ? '—' : ratio > 1 ? `<span class="danger">⚠ ${fmt(ratio, 2)}</span>` : fmt(ratio, 2);
        return [port ? hingeMark(b) : barName(b), fmt(br.L, 2), two(br.N1, br.N2), nature,
                ...(port ? [two(br.V, br.Vat(br.L)), kN(br.M1), kN(br.M2), kN(br.Mabs)] : []),
                fmt(smax / 1e6, 1), rt, Nc < 0 && !zero ? kN(bk.Ncr) : '—', safety];
    });
    fillTable('bars-table',
        ['Barre', 'L (m)', 'N (kN)', 'Nature',
         ...(port ? ['V (kN)', 'M<sub>début</sub> (kN·m)', 'M<sub>fin</sub> (kN·m)', '|M|<sub>max</sub> (kN·m)'] : []),
         'σ<sub>max</sub> (MPa)', 'σ<sub>max</sub>/f', 'N<sub>cr</sub> (kN)', 'N<sub>cr</sub>/|N|'],
        rows);
    id('bars-note').innerHTML =
        (port ? `σ<sub>max</sub> = |N|/A + |M|<sub>max</sub>·v/I, v étant la distance du centre de gravité à la fibre la plus éloignée.
                 Valeurs « a → b » : début → fin de barre (charge répartie ou poids propre).
                 M &gt; 0 tend les fibres situées à droite du sens de parcours ; ◦ signale une rotule. `
              : `σ<sub>max</sub> = |N|/A. `) +
        `f : contrainte limite du matériau (valeur indicative). Flambement des barres comprimées :
         N<sub>cr</sub> = π²·E·I<sub>min</sub>/L², barre supposée bi-articulée (longueur de flambement = L).
         Si N<sub>cr</sub>/|N| &lt; 1, la barre flambe.`;
}

// Nom de barre avec ses rotules : ◦AB, AB◦, ◦AB◦
const hingeMark = b => `${b.h1 ? '◦' : ''}${barName(b)}${b.h2 ? '◦' : ''}`;

function renderEquilibrium() {
    const card = id('equilibrium-card');
    if (state.type !== 'treillis') { card.style.display = 'none'; return; }
    card.style.display = '';
    const eq = nodeEquilibrium(state.nodes, state.bars, state.supports, state.res.loadsEff, state.res);
    const num = v => fmt(v, 2).replace('-', '−');
    const c3 = v => (Math.abs(v) < 5e-4 ? 0 : v).toFixed(3).replace('-', '−');
    const deg = v => `${+(Math.abs(v) < 1e-9 ? 0 : v).toFixed(1)}°`;
    let h = `<p>Méthode des nœuds : en chaque nœud, la somme des forces est nulle. Une barre tendue (N &gt; 0) tire sur le nœud
             dans la direction de son autre extrémité ; α est l'angle de cette direction avec l'axe x. Forces en kN.
             ${state.selfWeight ? 'F<sub>y</sub> comprend le poids propre réparti aux nœuds.' : ''}</p><ul class="eq-list">`;
    for (const e of eq) {
        const nm = nodeName(e.node);
        const sup = state.supports.find(s => s.node === e.node);
        const dofs = sup ? supportDofs(state.type, sup) : [];
        const eqLine = axis => {
            const sym = [], val = [];
            for (const t of e.terms) {
                const f = axis === 'x' ? t.cx : t.cy;
                sym.push(`N<sub>${t.name}</sub>·${axis === 'x' ? 'cos' : 'sin'}(${deg(t.deg)})`);
                val.push(`(${num(t.N / 1e3)})×(${c3(f)})`);
            }
            const F = axis === 'x' ? e.ext.Fx : e.ext.Fy;
            if (Math.abs(F) > 1e-9) { sym.push(`F<sub>${axis}</sub>`); val.push(`(${num(F / 1e3)})`); }
            if (e.reaction && dofs.includes(axis === 'x' ? 0 : 1)) {
                sym.push(`${axis === 'x' ? 'X' : 'Y'}<sub>${nm}</sub>`);
                val.push(`(${num((axis === 'x' ? e.reaction.Rx : e.reaction.Ry) / 1e3)})`);
            }
            const sum = axis === 'x' ? e.sx : e.sy;
            return `<span class="eq">ΣF<sub>${axis}</sub> : ${sym.join(' + ')} = ${val.join(' + ')} = <strong>${num(sum / 1e3)}</strong></span>`;
        };
        h += `<li><span class="eq-node">Nœud ${nm}</span>${eqLine("x")}${eqLine("y")}</li>`;
    }
    card.querySelector('#equilibrium').innerHTML = h + '</ul>';
}

function renderDispTable() {
    const port = state.type === 'portique';
    const { U, nd, dropped } = state.res;
    fillTable('disp-table',
        ['Nœud', 'u<sub>x</sub> (mm)', 'u<sub>y</sub> (mm)', ...(port ? ['θ (mrad)'] : [])],
        state.nodes.map((_, i) => [nodeName(i), fmt(U[nd * i] * 1e3, 3), fmt(U[nd * i + 1] * 1e3, 3),
                                   ...(port ? [dropped[nd * i + 2] ? '—' : fmt(U[nd * i + 2] * 1e3, 3)] : [])]));
}

// ═══ Blocs communs avec les applications poutre ═══════════════════════════════

function tryLoadAutosave() {
    try {
        const raw = localStorage.getItem(LS_AUTOSAVE);
        return raw ? applyStateData(JSON.parse(raw)) : false;
    } catch { return false; }
}

let _autosaveTimer = null;
function scheduleAutosave() {
    clearTimeout(_autosaveTimer);
    _autosaveTimer = setTimeout(() => {
        try { localStorage.setItem(LS_AUTOSAVE, JSON.stringify(serializeState())); } catch {}
    }, 500);
}

function getSlots() {
    try {
        const arr = JSON.parse(localStorage.getItem(LS_SLOTS) || '[]');
        while (arr.length < MAX_SLOTS) arr.push(null);
        return arr.slice(0, MAX_SLOTS);
    } catch { return Array(MAX_SLOTS).fill(null); }
}

function persistSlots(slots) {
    try { localStorage.setItem(LS_SLOTS, JSON.stringify(slots)); } catch {}
}

function saveToSlot(i) {
    const slots  = getSlots();
    const nameEl = id(`slot-name-${i}`);
    const name   = nameEl?.value.trim() || `Sauvegarde ${i + 1}`;
    if (nameEl) nameEl.value = name;
    slots[i] = {
        name,
        timestamp: new Date().toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' }),
        data: serializeState(),
    };
    persistSlots(slots);
    renderSlots();
}

function loadFromSlot(i) {
    const slot = getSlots()[i];
    if (!slot?.data) return;
    applyStateData(slot.data);
    syncUIFromState();
    compute();
}

function deleteSlot(i) {
    const slots = getSlots();
    slots[i] = null;
    persistSlots(slots);
    renderSlots();
}

function renderSlots() {
    const ul = id('slots-list');
    if (!ul) return;
    const slots = getSlots();
    ul.innerHTML = '';
    slots.forEach((slot, i) => {
        const li = document.createElement('li');
        li.className = 'slot-row';

        const nameInp = document.createElement('input');
        nameInp.type        = 'text';
        nameInp.id          = `slot-name-${i}`;
        nameInp.className   = 'slot-name';
        nameInp.placeholder = `Sauvegarde ${i + 1} (vide)`;
        if (slot) {
            nameInp.value = slot.name;
            nameInp.title = slot.timestamp === 'exemple fourni'
                ? `${slot.name} (exemple fourni)` : `${slot.name} — enregistré le ${slot.timestamp}`;
        }
        li.appendChild(nameInp);

        const btnSave = document.createElement('button');
        btnSave.textContent = '💾';
        btnSave.className = 'btn-slot';
        btnSave.title = 'Enregistrer la poutre actuelle ici';
        btnSave.addEventListener('click', () => saveToSlot(i));
        li.appendChild(btnSave);

        const btnLoad = document.createElement('button');
        btnLoad.textContent = '📂';
        btnLoad.className = 'btn-slot';
        btnLoad.title = 'Ouvrir cette sauvegarde';
        btnLoad.disabled = !slot;
        btnLoad.addEventListener('click', () => loadFromSlot(i));
        li.appendChild(btnLoad);

        const btnDel = document.createElement('button');
        btnDel.textContent = '✕';
        btnDel.className = 'btn-slot btn-slot-del';
        btnDel.title = 'Effacer cette sauvegarde';
        btnDel.disabled = !slot;
        btnDel.addEventListener('click', () => deleteSlot(i));
        li.appendChild(btnDel);

        ul.appendChild(li);
    });
}

// Premier lancement (aucune sauvegarde jamais enregistrée) : on installe les exemples
function installExamplesIfFirstVisit() {
    try { if (localStorage.getItem(LS_SLOTS) !== null) return; } catch { return; }
    const slots = getSlots();
    EXAMPLES.forEach((_, i) => { slots[i] = exampleSlot(i); });
    persistSlots(slots);
}

function resetExamples() {
    const n = EXAMPLES.length;
    if (!confirm(`Réécrire les ${n} exemples dans les emplacements 1 à ${n} ?\n\n` +
        `Ce que vous avez enregistré dans ces emplacements sera perdu ` +
        `(les emplacements ${n + 1} à ${MAX_SLOTS} ne sont pas modifiés).`)) return;
    const slots = getSlots();
    EXAMPLES.forEach((_, i) => { slots[i] = exampleSlot(i); });
    persistSlots(slots);
    renderSlots();
}

function clearAllSlots() {
    if (!confirm(`Effacer les ${MAX_SLOTS} emplacements (exemples compris) ?\n\n` +
        `Les exemples pourront être remis avec « Recharger les exemples ».`)) return;
    persistSlots(Array(MAX_SLOTS).fill(null));
    renderSlots();
}

// ─── Matériaux ────────────────────────────────────────────────────────────────
// E (Pa), masse volumique ρ (kg/m³), contrainte limite f (Pa) : valeurs indicatives
// (acier S235, béton C25 en compression, bois C24 en flexion)
const MATERIALS = {
    acier:     { E: 210e9, rho: 7850, f: 235e6, label: 'Acier (210 GPa)' },
    aluminium: { E:  70e9, rho: 2700, f: 160e6, label: 'Aluminium (70 GPa)' },
    beton:     { E:  30e9, rho: 2500, f:  25e6, label: 'Béton (30 GPa)' },
    bois:      { E:  11e9, rho:  420, f:  24e6, label: 'Bois (11 GPa)' },
    custom:    { E:  0,    rho: 7850, f: 235e6, label: 'Custom…' },
};

// Propriétés d'un matériau { materialName, E, rho, f } (valeurs saisies si « custom »)
function matProps(m) {
    if (m.materialName !== 'custom') {
        const d = MATERIALS[m.materialName] || MATERIALS.acier;
        return { E: d.E, rho: d.rho, f: d.f };
    }
    return { E: m.E || 0, rho: m.rho || 0, f: m.f || 0 };
}
const barMat = k => { const b = state.bars[k]; return matProps((b && b.sec && b.sec.mat) || state.matAll); };

// Matériau en cours d'édition : celui de la section commune ou de la barre choisie
function matTarget() {
    const b = state.bars[state.editTarget];
    if (b && b.sec) return b.sec.mat || (b.sec.mat = clone(state.matAll));
    return state.matAll;
}

function syncMaterialUI() {
    const m = matTarget(), pr = matProps(m);
    id('material-select').value = m.materialName;
    const custom = m.materialName === 'custom';
    id('material-custom-row').style.display = custom ? '' : 'none';
    if (custom) {
        id('material-custom-E').value = +(pr.E / 1e9).toFixed(3);
        id('material-custom-rho').value = pr.rho;
        id('material-custom-f').value = +(pr.f / 1e6).toFixed(3);
    }
    id('material-props').textContent =
        `E = ${fmtLbl(pr.E / 1e9)} GPa · ρ = ${fmtLbl(pr.rho)} kg/m³ · f = ${fmtLbl(pr.f / 1e6)} MPa`;
}

// ─── Section UI ───────────────────────────────────────────────────────────────
function buildSectionUI() {
    const sel = id('section-type');
    sel.innerHTML = '';
    [
        ['rect',        'Rectangle'],
        ['circ',        'Circulaire'],
        ['ipe-I',       'IPE (I — debout)'],
        ['ipe-H',       'IPE (H — couché)'],
        ['upe-C',       'UPE (C)'],
        ['upe-U',       'UPE (U — âme en bas)'],
        ['upe-Ui',      'UPE (Ui — âme en haut)'],
        ['composite',   'Composée'],
        ['custom',      'Custom (A, Iz, Iy, h)'],
    ].forEach(([v, t]) => {
        const opt = document.createElement('option');
        opt.value = v; opt.textContent = t;
        sel.appendChild(opt);
    });
}

function buildMaterialUI() {
    const sel = id('material-select');
    for (const [k, v] of Object.entries(MATERIALS)) {
        const opt = document.createElement('option');
        opt.value = k; opt.textContent = v.label;
        if (k === 'acier') opt.selected = true;
        sel.appendChild(opt);
    }
}

function updateSectionParams() {
    const type = id('section-type').value;
    const box = id('section-params');
    box.innerHTML = '';
    const p = state.sectionParams;
    p.type = type;

    if (type === 'rect') {
        box.appendChild(labeledInput('b (m)', 'sec-b', p.b || 0.1));
        box.appendChild(labeledInput('h (m)', 'sec-h', p.h || 0.2));
    } else if (type === 'circ') {
        box.appendChild(labeledInput('d (m)', 'sec-d', p.d || 0.15));
    } else if (type.startsWith('ipe') || type.startsWith('upe')) {
        const db = type.startsWith('ipe') ? IPE_DB : UPE_DB;
        const nums = db.map(e => e.n);
        box.appendChild(labeledSelect('Numéro', 'sec-num', nums, p.num || nums[0]));
    } else if (type === 'composite') {
        const wrap = document.createElement('div');
        wrap.id = 'composite-pieces';
        wrap.className = 'composite-pieces';
        if (!p.pieces) p.pieces = [];
        box.appendChild(wrap);
        const btnAdd = document.createElement('button');
        btnAdd.textContent = '+ Pièce'; btnAdd.className = 'btn-small';
        btnAdd.addEventListener('click', () => {
            addCompositePiece(); renderComposite();
            tryBuildSection(); scheduleRender(); scheduleAutosave();
        });
        box.appendChild(btnAdd);
        renderComposite();
    } else { // custom
        box.appendChild(labeledInput('A (m²)', 'sec-A', p.A || 0.01));
        box.appendChild(labeledInput('Iz (m⁴)', 'sec-Iz', p.Iz || 1e-5));
        box.appendChild(labeledInput('Iy (m⁴)', 'sec-Iy', p.Iy || 1e-5));
        box.appendChild(labeledInput('h (m)', 'sec-h', p.h || 0.2));
    }
}

function addCompositePiece() {
    if (!state.sectionParams.pieces) state.sectionParams.pieces = [];
    state.sectionParams.pieces.push({ add: true, shape: 'rect', y1:-0.1, z1:0, y2:0.1, z2:0.2 });
}

function renderComposite() {
    const wrap = id('composite-pieces');
    if (!wrap) return;
    wrap.innerHTML = '';
    const pieces = state.sectionParams.pieces || [];
    pieces.forEach((p, i) => {
        const row = document.createElement('div');
        row.className = 'piece-row';

        const signSel = document.createElement('select');
        signSel.className = 'piece-sign';
        ['+','-'].forEach(s => {
            const o = document.createElement('option');
            o.value = s; o.textContent = s;
            if ((p.add && s==='+') || (!p.add && s==='-')) o.selected = true;
            signSel.appendChild(o);
        });
        signSel.addEventListener('change', e => { p.add = (e.target.value==='+'); });
        row.appendChild(signSel);

        const shapeSel = document.createElement('select');
        shapeSel.className = 'piece-shape';
        ['rect','circ'].forEach(s => {
            const o = document.createElement('option');
            o.value = s; o.textContent = s;
            if (p.shape===s) o.selected = true;
            shapeSel.appendChild(o);
        });
        shapeSel.addEventListener('change', e => {
            p.shape = e.target.value; renderComposite();
            tryBuildSection(); scheduleRender();
        });
        row.appendChild(shapeSel);

        if (p.shape === 'rect') {
            ['y1','z1','y2','z2'].forEach(k => {
                const inp = document.createElement('input');
                inp.type = 'number'; inp.step = 'any';
                inp.value = p[k] || 0; inp.title = k;
                inp.placeholder = k;
                inp.className = 'piece-coord';
                inp.addEventListener('input', e => { p[k] = parseFloat(e.target.value)||0; });
                row.appendChild(inp);
            });
        } else {
            ['cy','cz','r'].forEach((k, ki) => {
                const keys = ['y1','z1','y2'];
                const inp = document.createElement('input');
                inp.type = 'number'; inp.step = 'any';
                inp.value = p[keys[ki]] || 0; inp.title = k;
                inp.placeholder = k;
                inp.className = 'piece-coord';
                inp.addEventListener('input', e => { p[keys[ki]] = parseFloat(e.target.value)||0; });
                row.appendChild(inp);
            });
        }

        const btnDel = document.createElement('button');
        btnDel.textContent = '✕'; btnDel.className = 'btn-icon';
        btnDel.addEventListener('click', () => {
            state.sectionParams.pieces.splice(i, 1);
            renderComposite();
            tryBuildSection(); scheduleRender(); scheduleAutosave();
        });
        row.appendChild(btnDel);
        wrap.appendChild(row);
    });
}

function buildSection() {
    const p = state.sectionParams;
    const type = p.type;
    if (type === 'rect') {
        const b = readNum('sec-b', p.b);
        const h = readNum('sec-h', p.h);
        return makeSectionRect(b, h);
    } else if (type === 'circ') {
        const d = readNum('sec-d', p.d);
        return makeSectionCirc(d);
    } else if (type.startsWith('ipe')) {
        const orient = type.slice(4); // 'I' or 'H'
        const num = parseInt(id('sec-num')?.value || p.num);
        return makeSectionProfile('IPE', num, orient);
    } else if (type.startsWith('upe')) {
        const orient = type.slice(4); // 'C', 'U', or 'Ui'
        const num = parseInt(id('sec-num')?.value || p.num);
        return makeSectionProfile('UPE', num, orient);
    } else if (type === 'composite') {
        const comp = makeSectionComposite();
        for (const piece of (p.pieces || [])) {
            if (piece.shape === 'rect') comp.addRect(piece.add, piece.y1, piece.z1, piece.y2, piece.z2);
            else comp.addCirc(piece.add, piece.y1, piece.z1, piece.y2);
        }
        comp.finalise();
        return comp;
    } else { // custom
        const A  = readNum('sec-A', p.A);
        const Iz = readNum('sec-Iz', p.Iz);
        const Iy = readNum('sec-Iy', p.Iy);
        const h  = readNum('sec-h',  p.h);
        return makeSectionCustom(A, Iz, Iy, h);
    }
}

// ─── Export / Import fichier ──────────────────────────────────────────────────
async function exportSlotsToFile() {
    const payload = JSON.stringify({ version: 1, slots: getSlots() }, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });

    if (window.showSaveFilePicker) {
        try {
            const fh = await window.showSaveFilePicker({
                suggestedName: 'msolution_treillis.json',
                types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }],
            });
            const writable = await fh.createWritable();
            await writable.write(blob);
            await writable.close();
        } catch (e) {
            if (e.name !== 'AbortError') showError('Export : ' + e.message);
        }
    } else {
        // Fallback universel : téléchargement
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'msolution_treillis.json';
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
}

async function importSlotsFromFile() {
    let text;
    if (window.showOpenFilePicker) {
        try {
            const [fh] = await window.showOpenFilePicker({
                types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }],
            });
            text = await (await fh.getFile()).text();
        } catch (e) {
            if (e.name !== 'AbortError') showError('Import : ' + e.message);
            return;
        }
    } else {
        // Fallback universel : <input type="file">
        text = await pickFileText('.json');
        if (!text) return;
    }
    try {
        const data = JSON.parse(text);
        // Accepte { version, slots:[...] } ou un tableau brut
        const raw = Array.isArray(data) ? data : data.slots;
        if (!Array.isArray(raw)) throw new Error('Format invalide');

        // Confirmation : l'import écrase les sauvegardes en mémoire
        const nOld = getSlots().filter(Boolean).length;
        const nNew = raw.slice(0, MAX_SLOTS).filter(Boolean).length;
        const plural = n => `${n} sauvegarde${n > 1 ? 's' : ''}`;
        if (nOld > 0 && !confirm(
            `Le fichier contient ${plural(nNew)}.\n` +
            `Elles vont remplacer vos ${plural(nOld)} actuelles, qui seront perdues.\n\n` +
            `Conseil : exportez d'abord vos sauvegardes actuelles si vous voulez les garder.\n\n` +
            `Continuer l'import ?`)) return;

        while (raw.length < MAX_SLOTS) raw.push(null);
        persistSlots(raw.slice(0, MAX_SLOTS));
        renderSlots();
    } catch (e) {
        showError('Import : ' + e.message);
    }
}

function pickFileText(accept) {
    return new Promise(resolve => {
        const inp = document.createElement('input');
        inp.type = 'file'; inp.accept = accept;
        inp.addEventListener('change', async () => {
            resolve(inp.files[0] ? await inp.files[0].text() : null);
        });
        inp.click();
    });
}
// ─── Helpers DOM ──────────────────────────────────────────────────────────────
function id(s) { return document.getElementById(s); }

function labeledInput(label, elId, defaultVal) {
    const wrap = document.createElement('div');
    wrap.className = 'param-row';
    const lbl = document.createElement('label');
    lbl.textContent = label; lbl.htmlFor = elId;
    const inp = document.createElement('input');
    inp.type = 'number'; inp.id = elId; inp.step = 'any';
    inp.value = defaultVal;
    inp.addEventListener('input', e => {
        const key = elId.replace('sec-', '');
        state.sectionParams[key] = parseFloat(e.target.value) || 0;
        state.section = null;
    });
    wrap.appendChild(lbl); wrap.appendChild(inp);
    return wrap;
}

function labeledSelect(label, elId, options, selected) {
    const wrap = document.createElement('div');
    wrap.className = 'param-row';
    const lbl = document.createElement('label');
    lbl.textContent = label; lbl.htmlFor = elId;
    const sel = document.createElement('select');
    sel.id = elId;
    options.forEach(v => {
        const o = document.createElement('option');
        o.value = v; o.textContent = v;
        if (v === selected) o.selected = true;
        sel.appendChild(o);
    });
    sel.addEventListener('change', e => {
        state.sectionParams.num = parseInt(e.target.value);
        state.section = null;
    });
    wrap.appendChild(lbl); wrap.appendChild(sel);
    return wrap;
}

function numInput(val, step, onChange, placeholder='') {
    const inp = document.createElement('input');
    inp.type = 'number'; inp.step = step;
    inp.value = val; inp.placeholder = placeholder;
    inp.className = 'inp-num';
    inp.addEventListener('input', e => onChange(parseFloat(e.target.value)||0));
    return inp;
}

function labelText(t) {
    const s = document.createElement('span');
    s.textContent = t; s.className = 'lbl-inline';
    return s;
}

function readNum(elId, fallback) {
    const el = id(elId);
    if (!el) return fallback;
    return parseFloat(el.value) || fallback;
}

function showError(msg) {
    const el = id('error-msg');
    el.textContent = msg;
    el.style.display = '';
}

function clearError() {
    id('error-msg').style.display = 'none';
}
