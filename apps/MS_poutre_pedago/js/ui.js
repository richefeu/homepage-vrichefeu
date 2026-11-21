'use strict';

// ─── État de l'application ────────────────────────────────────────────────────
const state = {
    L: 4.0,
    E: 210e9,
    materialName: 'acier',
    section: null,
    sectionParams: { type: 'rect', b: 0.1, h: 0.2 },
    supports: [
        { type: 'pin',    x: 0.0 },
        { type: 'roller', x: 4.0 },
    ],
    loads: [
        { type: 'force', x: 2.0, Fy: -10000, Fx: 0 },
    ],
    reactions: null,
    diagram: null,
    defl: null,
    stresses: null,
    naviX: 2.0,
};

// ─── Persistance localStorage ────────────────────────────────────────────────
const LS_AUTOSAVE = 'msolution_autosave';
const LS_SLOTS    = 'msolution_slots';
const MAX_SLOTS   = 15;   // 10 exemples + 5 emplacements libres

function serializeState() {
    return {
        L:            state.L,
        E:            state.E,
        materialName: state.materialName,
        sectionParams: JSON.parse(JSON.stringify(state.sectionParams)),
        supports:      JSON.parse(JSON.stringify(state.supports)),
        loads:         JSON.parse(JSON.stringify(state.loads)),
        naviX:         state.naviX,
    };
}

function applyStateData(data) {
    if (!data) return false;
    state.L             = data.L             ?? 4.0;
    state.E             = data.E             ?? 210e9;
    state.materialName  = data.materialName  ?? 'acier';
    state.sectionParams = data.sectionParams ?? { type: 'rect', b: 0.1, h: 0.2 };
    state.supports      = data.supports      ?? [];
    state.loads         = data.loads         ?? [];
    state.naviX         = data.naviX         ?? 2.0;
    return true;
}

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

// ─── Exemples (complexité croissante) ─────────────────────────────────────────
// Rectangle 100×200 mm en acier sauf mention contraire ; forces en N, longueurs en m.
const RECT = { type: 'rect', b: 0.1, h: 0.2 };
const EXAMPLES = [
    { title: 'Deux appuis, force au milieu',
      L: 4, supports: [{type:'pin', x:0}, {type:'roller', x:4}],
      loads: [{type:'force', x:2, Fy:-10000, Fx:0}], naviX: 2 },
    { title: 'Deux appuis, force excentrée',
      L: 4, supports: [{type:'pin', x:0}, {type:'roller', x:4}],
      loads: [{type:'force', x:1, Fy:-10000, Fx:0}], naviX: 1 },
    { title: 'Deux appuis, charge répartie (bois)',
      L: 5, supports: [{type:'pin', x:0}, {type:'roller', x:5}],
      loads: [{type:'distributed', x1:0, x2:5, qy:-5000, qx:0}], naviX: 2.5,
      materialName: 'bois', sectionParams: { type: 'rect', b: 0.1, h: 0.25 } },
    { title: 'Console, force en bout',
      L: 3, supports: [{type:'fixed', x:0}],
      loads: [{type:'force', x:3, Fy:-10000, Fx:0}], naviX: 0 },
    { title: 'Console, charge répartie',
      L: 3, supports: [{type:'fixed', x:0}],
      loads: [{type:'distributed', x1:0, x2:3, qy:-4000, qx:0}], naviX: 0 },
    { title: 'Deux appuis, couple appliqué',
      L: 4, supports: [{type:'pin', x:0}, {type:'roller', x:4}],
      loads: [{type:'moment', x:2, Mz:10000}], naviX: 2 },
    { title: 'Force inclinée (effort normal)',
      L: 4, supports: [{type:'pin', x:0}, {type:'roller', x:4}],
      loads: [{type:'force', x:2, Fy:-8660, Fx:5000}], naviX: 2 },
    { title: 'Plusieurs charges',
      L: 6, supports: [{type:'pin', x:0}, {type:'roller', x:6}],
      loads: [{type:'force', x:1.5, Fy:-12000, Fx:0},
              {type:'distributed', x1:3, x2:6, qy:-4000, qx:0}], naviX: 1.5 },
    { title: 'Poutre avec porte-à-faux',
      L: 6, supports: [{type:'pin', x:0}, {type:'roller', x:4}],
      loads: [{type:'distributed', x1:0, x2:6, qy:-5000, qx:0},
              {type:'force', x:6, Fy:-8000, Fx:0}], naviX: 4 },
    { title: 'Profilé IPE 200, cas complet',
      L: 6, supports: [{type:'pin', x:0}, {type:'roller', x:5}],
      loads: [{type:'distributed', x1:0, x2:5, qy:-6000, qx:0},
              {type:'force', x:2, Fy:-15000, Fx:0},
              {type:'force', x:6, Fy:-10000, Fx:0}], naviX: 5,
      sectionParams: { type: 'ipe-I', num: 200 } },
];

// Exemple i → contenu d'un emplacement de sauvegarde
function exampleSlot(i) {
    const ex = EXAMPLES[i];
    const mat = ex.materialName || 'acier';
    return {
        name: `${i + 1}. ${ex.title}`,
        timestamp: 'exemple fourni',
        data: JSON.parse(JSON.stringify({
            L: ex.L, E: MATERIALS[mat].E, materialName: mat,
            sectionParams: ex.sectionParams || RECT,
            supports: ex.supports, loads: ex.loads, naviX: ex.naviX,
        })),
    };
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
const MATERIALS = {
    acier:     { E: 210e9, label: 'Acier (210 GPa)' },
    aluminium: { E:  70e9, label: 'Aluminium (70 GPa)' },
    beton:     { E:  30e9, label: 'Béton (30 GPa)' },
    bois:      { E:  11e9, label: 'Bois (11 GPa)' },
    custom:    { E:  0,    label: 'Custom…' },
};

// ─── Initialisation ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    buildSectionUI();
    buildMaterialUI();
    installExamplesIfFirstVisit();
    bindEvents();

    if (tryLoadAutosave()) {
        syncUIFromState();
    } else {
        updateSectionParams();
        renderSupportsList();
        renderLoadsList();
    }

    renderSlots();
    tryBuildSection();
    compute();

    // Autosave + rendu réactif sur tout changement hors zone slots
    const onParamChange = e => {
        if (e.target.closest('.slot-row')) return;
        scheduleAutosave();
        tryBuildSection();
        scheduleRender();
    };
    document.addEventListener('input',  onParamChange);
    document.addEventListener('change', onParamChange);
});

function bindEvents() {
    id('beam-length').addEventListener('input', e => {
        state.L = parseFloat(e.target.value) || 4;
        scheduleRender();
    });
    id('btn-add-support').addEventListener('click', addSupport);
    id('btn-add-load').addEventListener('click', addLoad);
    id('btn-navier').addEventListener('click', handleNavierClick);
    id('navier-x').addEventListener('input', e => {
        state.naviX = parseFloat(e.target.value) || 0;
        scheduleAutosave();
    });
    id('btn-reset-examples').addEventListener('click', resetExamples);
    id('btn-clear-slots').addEventListener('click', clearAllSlots);
    id('btn-export').addEventListener('click', exportSlotsToFile);
    id('btn-import').addEventListener('click', importSlotsFromFile);
    id('section-type').addEventListener('change', () => {
        updateSectionParams();
        state.section = null;
    });
    id('material-select').addEventListener('change', e => {
        const mat = e.target.value;
        state.materialName = mat;
        if (mat === 'custom') {
            id('material-custom-row').style.display = '';
        } else {
            id('material-custom-row').style.display = 'none';
            state.E = MATERIALS[mat].E;
        }
    });
    id('material-custom-E').addEventListener('input', e => {
        state.E = (parseFloat(e.target.value) || 0) * 1e9;
    });
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

// ─── Supports ─────────────────────────────────────────────────────────────────
function addSupport() {
    state.supports.push({ type: 'pin', x: 0 });
    renderSupportsList();
    scheduleAutosave(); scheduleRender();
}

function renderSupportsList() {
    const ul = id('supports-list');
    ul.innerHTML = '';
    state.supports.forEach((s, i) => {
        const li = document.createElement('li');
        li.className = 'item-row';

        const labelEl = document.createElement('span');
        labelEl.className = 'item-label';
        labelEl.textContent = String.fromCharCode(65+i) + ' ';
        li.appendChild(labelEl);

        const typeSel = document.createElement('select');
        typeSel.className = 'inp-small';
        [['roller','Appui simple'],['pin','Articulation'],['fixed','Encastrement']].forEach(([v,t]) => {
            const o = document.createElement('option');
            o.value=v; o.textContent=t;
            if (s.type===v) o.selected=true;
            typeSel.appendChild(o);
        });
        typeSel.addEventListener('change', e => { s.type = e.target.value; });
        li.appendChild(typeSel);

        const xInp = numInput(s.x, 0.001, v => { s.x = v; });
        xInp.title = 'x (m)'; xInp.placeholder = 'x (m)';
        li.appendChild(xInp);

        const btn = document.createElement('button');
        btn.textContent = '✕'; btn.className = 'btn-icon';
        btn.addEventListener('click', () => {
            state.supports.splice(i, 1); renderSupportsList();
            scheduleAutosave(); scheduleRender();
        });
        li.appendChild(btn);
        ul.appendChild(li);
    });
}

// ─── Chargements ──────────────────────────────────────────────────────────────
function addLoad() {
    state.loads.push({ type: 'force', x: state.L/2, Fy: -10000, Fx: 0 });
    renderLoadsList();
    scheduleAutosave(); scheduleRender();
}

function renderLoadsList() {
    const ul = id('loads-list');
    ul.innerHTML = '';
    state.loads.forEach((l, i) => {
        const li = document.createElement('li');
        li.className = 'item-row item-load';

        const typeSel = document.createElement('select');
        typeSel.className = 'inp-small';
        [['force','Force'],['moment','Moment'],['distributed','Charge répartie']].forEach(([v,t]) => {
            const o = document.createElement('option');
            o.value=v; o.textContent=t;
            if (l.type===v) o.selected=true;
            typeSel.appendChild(o);
        });
        typeSel.addEventListener('change', e => {
            const nt = e.target.value;
            if (nt === 'force')       Object.assign(l, {type:'force', x:l.x||0, Fy:l.Fy||-10000, Fx:0});
            else if (nt==='moment')   Object.assign(l, {type:'moment', x:l.x||0, Mz:l.Mz||10000});
            else                      Object.assign(l, {type:'distributed', x1:0, x2:state.L, qy:-5000, qx:0});
            renderLoadsList();
        });
        li.appendChild(typeSel);

        if (l.type === 'force') {
            li.appendChild(labelText('x:')); li.appendChild(numInput(l.x, 0.01, v=>l.x=v, 'x (m)'));
            li.appendChild(labelText('Fy(kN):')); li.appendChild(numInput(l.Fy/1e3, 0.1, v=>l.Fy=v*1e3, 'Fy'));
            li.appendChild(labelText('Fx(kN):')); li.appendChild(numInput((l.Fx||0)/1e3, 0.1, v=>l.Fx=v*1e3, 'Fx'));
        } else if (l.type === 'moment') {
            li.appendChild(labelText('x:')); li.appendChild(numInput(l.x, 0.01, v=>l.x=v, 'x (m)'));
            li.appendChild(labelText('Mz(kN·m):')); li.appendChild(numInput(l.Mz/1e3, 0.1, v=>l.Mz=v*1e3, 'Mz'));
        } else {
            li.appendChild(labelText('x1:')); li.appendChild(numInput(l.x1, 0.01, v=>l.x1=v, 'x1 (m)'));
            li.appendChild(labelText('x2:')); li.appendChild(numInput(l.x2, 0.01, v=>l.x2=v, 'x2 (m)'));
            li.appendChild(labelText('qy(kN/m):')); li.appendChild(numInput(l.qy/1e3, 0.1, v=>l.qy=v*1e3, 'qy'));
        }

        const btn = document.createElement('button');
        btn.textContent = '✕'; btn.className = 'btn-icon';
        btn.addEventListener('click', () => {
            state.loads.splice(i, 1); renderLoadsList();
            scheduleAutosave(); scheduleRender();
        });
        li.appendChild(btn);
        ul.appendChild(li);
    });
}

// ─── Calcul principal ─────────────────────────────────────────────────────────
function compute() {
    clearError();
    updateStatus();

    // Les résultats ne s'affichent que pour une poutre isostatique
    if (staticUnknowns() !== 3) {
        state.reactions = state.diagram = state.defl = state.stresses = null;
        id('results').style.display = 'none';
        renderAll();
        return;
    }

    // Build section
    try {
        state.section = buildSection();
    } catch(e) {
        showError('Section : ' + e.message);
        return;
    }

    // Solve
    const result = solveReactions(state.supports, state.loads);
    if (!result.ok) { showError(result.error); id('results').style.display = 'none'; return; }
    state.reactions = result.reactions;

    // Diagram
    state.diagram = computeDiagram(state.L, state.supports, state.loads, state.reactions, 300);

    // Deflection
    state.defl = computeDeflection(state.diagram, state.section, state.E, state.supports);

    // Stresses
    state.stresses = state.section ? computeStresses(state.diagram, state.section) : null;

    renderAll();
    id('results').style.display = 'flex';

    // Re-lancer Navier si le panneau était déjà visible
    if (id('navier-result').style.display !== 'none') {
        handleNavierClick();
    }
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
                suggestedName: 'msolution_slots.json',
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
        a.href = url; a.download = 'msolution_slots.json';
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

// ─── Section preview silencieuse ─────────────────────────────────────────────
function tryBuildSection() {
    try {
        state.section = buildSection();
        const s = state.section;
        id('section-info').textContent =
            `${s.name}\nA = ${fmt(s.area*1e4,2)} cm²\n` +
            `Iz = ${fmt(s.Iz*1e8,2)} cm⁴\nYG = ${fmt(s.zc*1000,1)} mm`;
    } catch {
        state.section = null;
        id('section-info').textContent = '';
    }
}

// ─── Synchronisation DOM → state (après chargement) ──────────────────────────
function syncUIFromState() {
    id('beam-length').value = state.L;

    id('section-type').value = state.sectionParams.type;
    updateSectionParams();

    id('material-select').value = state.materialName;
    if (state.materialName === 'custom') {
        id('material-custom-row').style.display = '';
        id('material-custom-E').value = (state.E / 1e9).toFixed(0);
    } else {
        id('material-custom-row').style.display = 'none';
    }

    renderSupportsList();
    renderLoadsList();
    id('navier-x').value = state.naviX;
}

// ─── Navier en un point x ─────────────────────────────────────────────────────
function handleNavierClick() {
    if (!state.section || !state.diagram) {
        showError('Lancez d\'abord le calcul principal.'); return;
    }
    clearError();
    const xNav = parseFloat(id('navier-x').value);
    if (isNaN(xNav)) { showError('x Navier invalide'); return; }

    // Interpolate N, V, M at x
    const diag = state.diagram;
    let N=0, V=0, M=0;
    const last = diag[diag.length-1];
    for (let i=1; i<diag.length; i++) {
        if (diag[i].x >= xNav || i === diag.length-1) {
            const dx = diag[i].x - diag[i-1].x;
            const t = dx > 1e-15 ? (xNav - diag[i-1].x) / dx : 0;
            const tc = Math.max(0, Math.min(1, t));
            N = diag[i-1].N + tc*(diag[i].N-diag[i-1].N);
            V = diag[i-1].V + tc*(diag[i].V-diag[i-1].V);
            M = diag[i-1].M + tc*(diag[i].M-diag[i-1].M);
            break;
        }
    }

    const nd = computeNavier(state.section, N, V, M, 100);
    renderNavier(id('navier-svg'), state.section, nd);
    id('navier-result').style.display = 'block';
    id('navier-x-display').textContent = xNav.toFixed(2) + ' m';
    id('navier-N').textContent = fmt(-N/1e3, 2) + ' kN';
    id('navier-V').textContent = fmt(-V/1e3, 2) + ' kN';
    id('navier-M').textContent = fmt(M/1e3, 2) + ' kN·m';
}

// ─── État statique (nombre d'inconnues de liaison) ───────────────────────────
function staticUnknowns() {
    return state.supports.reduce((s, sp) =>
        s + (sp.type === 'fixed' ? 3 : sp.type === 'pin' ? 2 : 1), 0);
}

function updateStatus() {
    const el = id('static-status');
    const n = staticUnknowns();
    const inc = `${n} inconnue${n > 1 ? 's' : ''} de liaison pour 3 équations d'équilibre`;
    if (n === 3) {
        el.textContent = `✓ Poutre isostatique — ${inc}`;
    } else if (n < 3) {
        el.textContent = `Poutre hypostatique — ${inc} : ajoutez ou bloquez une liaison.`;
    } else {
        el.textContent = `Poutre hyperstatique — ${inc} : hors du champ de cette application.`;
    }
    el.className = 'status ' + (n === 3 ? 'status-ok' : 'status-bad');
}

// ─── Rendu global ─────────────────────────────────────────────────────────────
function renderAll() {
    updateStatus();
    renderBeamSchema(id('schema-svg'), state.L, state.supports, state.loads, state.reactions);
    renderSection(id('section-svg'), state.section);

    if (state.reactions) renderReactionsTable();
    if (state.diagram) {
        const xs = state.diagram.map(p => p.x);
        const L2 = xs[xs.length-1];
        renderScalarPanel(id('N-svg'), xs, state.diagram.map(p=>-p.N),
            'N(x) — Effort normal', {name:'kN', scale:1e3}, C_POS, C_NEG);
        renderScalarPanel(id('V-svg'), xs, state.diagram.map(p=>-p.V),
            'V(x) — Effort tranchant', {name:'kN', scale:1e3}, C_POS, C_NEG);
        renderScalarPanel(id('M-svg'), xs, state.diagram.map(p=>p.M),
            'M(x) — Moment fléchissant', {name:'kN·m', scale:1e3}, C_POS, C_NEG);
    }
    if (state.defl) renderDeflPanel(id('defl-svg'), state.defl);
    if (state.stresses) renderStressTable();
}

let _renderTimer = null;
function scheduleRender() {
    clearTimeout(_renderTimer);
    _renderTimer = setTimeout(compute, 80);   // recalcul automatique
}

function renderReactionsTable() {
    const tb = id('reactions-table').querySelector('tbody');
    tb.innerHTML = '';
    state.reactions.forEach((rxn, i) => {
        const tr = document.createElement('tr');
        const id2 = String.fromCharCode(65+i);
        [id2, fmt(rxn.x,2), fmt(rxn.Rx/1e3,2), fmt(rxn.Ry/1e3,2), fmt(rxn.Mz/1e3,2)]
            .forEach(v => { const td = document.createElement('td'); td.textContent=v; tr.appendChild(td); });
        tb.appendChild(tr);
    });
}

function renderStressTable() {
    const tb = id('stress-table').querySelector('tbody');
    tb.innerHTML = '';
    // Show only key points (supports + loads + extrema)
    const keyXs = new Set();
    for (const s of state.supports) keyXs.add(s.x);
    for (const l of state.loads) {
        if (l.type==='force' || l.type==='moment') keyXs.add(l.x);
        else { keyXs.add(l.x1); keyXs.add(l.x2); }
    }
    // Also add max/min M points
    const Ms = state.diagram.map(p=>p.M);
    const iMaxM = Ms.indexOf(Math.max(...Ms));
    const iMinM = Ms.indexOf(Math.min(...Ms));
    keyXs.add(state.diagram[iMaxM].x);
    keyXs.add(state.diagram[iMinM].x);

    const sortedX = [...keyXs].sort((a,b)=>a-b);
    for (const x of sortedX) {
        const near = state.stresses.reduce((best, p) =>
            Math.abs(p.x-x) < Math.abs(best.x-x) ? p : best, state.stresses[0]);
        const tr = document.createElement('tr');
        [fmt(near.x,2), fmt(near.sig_inf/1e6,2), fmt(near.sig_sup/1e6,2), fmt(near.tau/1e6,2)]
            .forEach(v => { const td = document.createElement('td'); td.textContent=v; tr.appendChild(td); });
        tb.appendChild(tr);
    }
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
