// ─── Interface : saisies, résultats, sauvegardes ────────────────────────────

const id = s => document.getElementById(s);
const clone = o => JSON.parse(JSON.stringify(o));

// ─── Persistance localStorage ────────────────────────────────────────────────
const LS_AUTOSAVE = 'formulation_beton_autosave';
const LS_SLOTS    = 'formulation_beton_slots';
const MAX_SLOTS   = 10;   // 5 exemples + 5 emplacements libres

// ─── Valeurs par défaut ───────────────────────────────────────────────────────
const DEFAULT_PARAMS = {
    qualite: 2, expose: 0, agressivite: 0, nbGranu: 3,
    sig28: 35, classVraie: 54, aff: 6, serrage: 3, Kp: 0,
    Mfs: 0, Dmax: 0, courbe: 1, S_roule: 1, g_roule: 1, G_roule: 1, granuLeger: 0,
    rhos_S: 2.58, rhos_g: 2.58, rhos_G: 2.58, rhos_C: 3.1,
    teneurEauSable: 2.5, volumeGacher: 100,
};

// Analyses granulométriques de référence (refus cumulés %, tamis 0,08 à 80 mm)
const DEFAULT_REFUS = {
    S: [100, 98.418, 97.233, 95.256, 92.49, 88.932, 83.794, 79.446, 73.517, 67.984, 61.66, 53.754,
        44.664, 31.62, 21.343, 14.624, 8.6956, 3.9525, 0.3952, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    g: [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        65.22, 10.28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    G: [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
        100, 100, 100, 100, 98.42, 71.15, 16.21, 0, 0, 0, 0, 0],
};

// Bornes appliquées à la saisie
const LIMITS = { sig28: [10, 60], aff: [2, 12], Mfs: [0, 5], classVraie: [20, 80],
    rhos_C: [1, 5], rhos_S: [1, 5], rhos_g: [1, 5], rhos_G: [1, 5],
    teneurEauSable: [0, 30], volumeGacher: [0, 1e6] };

let state = { params: clone(DEFAULT_PARAMS), refus: clone(DEFAULT_REFUS) };
let lastResult = null;

// ─── Exemples (de complexité croissante) ────────────────────────────────────
const EXAMPLES = [
    { title: 'Béton binaire (sable + gravette), 25 MPa',
      params: { nbGranu: 2, qualite: 1, sig28: 25, aff: 7, serrage: 2 } },
    { title: 'Béton ternaire courant, 25 MPa',
      params: { nbGranu: 3, qualite: 1, sig28: 25, aff: 7, serrage: 2 } },
    { title: 'Béton ternaire 35 MPa, très bonne qualité',
      params: {} },
    { title: 'Béton exposé, granulats concassés, pompable',
      params: { qualite: 2, sig28: 30, aff: 9, serrage: 2, expose: 1, Kp: 6,
                S_roule: 0, g_roule: 0, G_roule: 0 } },
    { title: 'Béton ferme en milieu agressif, 40 MPa',
      params: { qualite: 2, sig28: 40, aff: 3, serrage: 3, agressivite: 1, g_roule: 0, G_roule: 0 } },
];

function exampleSlot(i) {
    const ex = EXAMPLES[i];
    return {
        name: `${i + 1}. ${ex.title}`,
        timestamp: 'exemple fourni',
        data: { params: { ...clone(DEFAULT_PARAMS), ...ex.params }, refus: clone(DEFAULT_REFUS) },
    };
}

// ─── Initialisation ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    buildGranuTable();
    installExamplesIfFirstVisit();
    tryLoadAutosave();
    syncUIFromState();
    renderSlots();
    compute();

    document.addEventListener('input', e => {
        if (e.target.closest('.slot-row')) return;
        readInput(e.target, false);
        scheduleAutosave();
        compute();
    });
    document.addEventListener('change', e => {
        if (e.target.closest('.slot-row')) return;
        readInput(e.target, true);
        scheduleAutosave();
        compute();
    });

    id('btn-reset-examples').addEventListener('click', resetExamples);
    id('btn-clear-slots').addEventListener('click', clearAllSlots);
    id('btn-export').addEventListener('click', exportSlotsToFile);
    id('btn-import').addEventListener('click', importSlotsFromFile);

    let t = null;
    window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(renderChartNow, 150); });
});

// ─── Saisies ──────────────────────────────────────────────────────────────────
function buildGranuTable() {
    const tb = id('granu-tbody');
    MODULES.forEach((mod, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${DIAMETRES[i]}</td><td>${mod}</td>` +
            ['S', 'g', 'G'].map(k => `<td${k === 'G' ? ' class="col-G"' : ''}>` +
                `<input type="number" min="0" max="100" step="any" data-r="${k}" data-i="${i}"></td>`).join('');
        tb.appendChild(tr);
    });
}

// final = true à la validation (change) : on borne la valeur et on la réaffiche
function readInput(el, final) {
    if (el.dataset.r) {
        let v = parseFloat(el.value);
        if (isNaN(v)) { if (final) el.value = state.refus[el.dataset.r][+el.dataset.i]; return; }
        v = Math.min(100, Math.max(0, v));
        state.refus[el.dataset.r][+el.dataset.i] = v;
        if (final) el.value = v;
        return;
    }
    const key = el.dataset.p;
    if (!key) return;
    if (el.type === 'checkbox') { state.params[key] = el.checked ? 1 : 0; return; }
    if (el.type === 'radio') { if (el.checked) state.params[key] = +el.value; syncGranuColumns(); return; }
    let v = parseFloat(el.value);
    if (isNaN(v)) { if (final) el.value = state.params[key]; return; }
    const lim = LIMITS[key];
    if (lim) v = Math.min(lim[1], Math.max(lim[0], v));
    if (!final && lim && v !== parseFloat(el.value)) return;   // saisie en cours hors bornes
    state.params[key] = v;
    if (final) el.value = v;

    // Le serrage doit rester compatible avec la consistance (Tableau 7)
    if (key === 'aff' && final) {
        const p = state.params;
        if (p.aff >= 10 && p.serrage == 3) p.serrage = 2;
        if (p.aff <= 4 && p.serrage == 0) p.serrage = 1;
        syncUIFromState();
    }
}

function syncUIFromState() {
    document.querySelectorAll('[data-p]').forEach(el => {
        const v = state.params[el.dataset.p];
        if (el.type === 'checkbox') el.checked = v == 1;
        else if (el.type === 'radio') el.checked = +el.value === +v;
        else el.value = v;
    });
    document.querySelectorAll('[data-r]').forEach(el => {
        el.value = state.refus[el.dataset.r][+el.dataset.i];
    });
    syncGranuColumns();
}

// Béton binaire : le gravier n'intervient pas
function syncGranuColumns() {
    const off = state.params.nbGranu == 2;
    document.querySelectorAll('.col-G').forEach(el => el.classList.toggle('col-off', off));
    document.querySelectorAll('.col-G input, .col-G select').forEach(el => { el.disabled = off; });
}

// ─── Calcul ───────────────────────────────────────────────────────────────────
function compute() {
    const p = state.params;
    const st = id('status');
    try {
        lastResult = dreuxCompute(p, state.refus);
    } catch (e) {
        lastResult = null;
        st.className = 'status status-bad';
        st.textContent = 'Calcul impossible : ' + e.message + '.';
    }
    const r = lastResult;
    if (r) {
        const ok = r.warnings.length === 0 && [r.C, r.E, r.S, r.g, r.G].every(Number.isFinite);
        st.className = 'status ' + (ok ? 'status-ok' : 'status-bad');
        st.textContent = ok
            ? `Béton ${p.nbGranu == 2 ? 'binaire' : 'ternaire'} · Dmax = ${r.Dmax} mm · ` +
              `C = ${fmt(r.C, 0)} kg/m³ · E = ${fmt(r.E, 0)} L/m³ · E/C = ${fmt(r.E / r.C, 2)}`
            : (r.warnings.join(' ; ') || 'Résultat non défini : vérifiez les données') + '.';
    }
    id('dmax-calc').textContent = r && r.DmaxCalc ? `Calculé (${r.DmaxCalc} mm)` : 'Calculé';
    id('mfs-hint').textContent = r && r.MfsCalc
        ? `0 : calculé à partir de l'analyse du sable (Mf = ${fmt(r.Mfs, 2)}).`
        : '0 : calculé à partir de l\'analyse du sable.';
    id('results').style.display = r ? 'flex' : 'none';
    if (r) { renderComposition(r); renderSteps(r); }
    renderChartNow();
}

function renderChartNow() {
    renderChart(id('chart-svg'), state.refus, lastResult, state.params, id('chart-legend'));
}

function fmt(v, d) {
    if (!Number.isFinite(v)) return '—';
    const s = v.toFixed(d);
    return s === (-0).toFixed(d) ? (0).toFixed(d) : s;
}

// ─── Tableaux de résultats ────────────────────────────────────────────────────
function renderComposition(r) {
    const p = state.params;
    const tern = p.nbGranu != 2;
    const delta = 0.01 * p.teneurEauSable * r.S;   // eau apportée par le sable humide
    const ff = p.volumeGacher / 1000;
    const rows = [
        ['Ciment', r.C, r.C],
        ['Eau', r.E, r.E - delta],
        ['Sable', r.S, r.S + delta],
        ['Gravette', r.g, r.g],
        ...(tern ? [['Gravier', r.G, r.G]] : []),
    ];
    const tot1 = rows.reduce((s, x) => s + x[1], 0);
    const tot2 = rows.reduce((s, x) => s + x[2], 0);
    id('compo-table').tHead.innerHTML =
        `<tr><th>Constituant</th><th>Pour 1 m³ (kg)</th><th>Gâchée de ${fmt(p.volumeGacher, 0)} L (kg)</th></tr>`;
    id('compo-table').tBodies[0].innerHTML = rows.map(([n, a, b]) =>
        `<tr><td>${n}</td><td>${fmt(a, 1)}</td><td>${fmt(ff * b, 2)}</td></tr>`).join('') +
        `<tr class="total"><td>Total</td><td>${fmt(tot1, 1)}</td><td>${fmt(ff * tot2, 2)}</td></tr>`;
    id('compo-note').textContent = p.teneurEauSable > 0
        ? `Gâchée : le sable humide (teneur en eau ${p.teneurEauSable} %) apporte ${fmt(ff * delta, 2)} kg d'eau, ` +
          `retirés de l'eau de gâchage et ajoutés à la masse de sable à peser.`
        : '';
}

function renderSteps(r) {
    const p = state.params;
    const tern = p.nbGranu != 2;
    const rows = [
        ['Granulats'],
        ['Dimension maximale', 'D<sub>max</sub>', fmt(r.Dmax, 2), 'mm', r.DmaxImpose
            ? `imposée (calculée : ${r.DmaxCalc ?? '—'} mm)` : `premier tamis sans refus du ${tern ? 'gravier' : 'gravette'}`],
        ['Module de finesse du sable', 'M<sub>f</sub>', fmt(r.Mfs, 2), '', r.MfsCalc ? 'Σ refus (tamis 0,16 à 80 mm) / 100' : 'valeur saisie'],
        ['Dosages en ciment et en eau'],
        ['Coefficient granulaire', 'G′', fmt(r.Gprime, 3), '', 'Tableau 4 (qualité, D<sub>max</sub>)'],
        ['Rapport ciment / eau', 'C/E', fmt(r.C_E, 3), '', 'σ′<sub>28</sub> / (G′ σ′<sub>c</sub>) + 0,5'],
        ['Dosage optimal', 'C<sub>opt</sub>', r.CoptOut ? '—' : fmt(r.Copt, 1), 'kg/m³', r.CoptOut === 'low'
            ? 'abaque : moins de 200 kg/m³, C<sub>min</sub> s\'impose' : r.CoptOut === 'high' ? 'hors abaque (plus de 450 kg/m³)' : 'abaque (C/E, affaissement)'],
        ['Dosage minimal', 'C<sub>min</sub>', fmt(r.Cmin, 1), 'kg/m³',
            p.agressivite == 1 ? 'milieu agressif' : p.expose == 1 ? 'béton exposé' : '(250 + 10 σ′<sub>28</sub>) / (1,25 D<sub>max</sub>)<sup>0,2</sup>'],
        ['Ciment avant correction', 'C', fmt(r.Cav, 1), 'kg/m³', 'max(C<sub>opt</sub>, C<sub>min</sub>)'],
        ['Eau avant correction', 'E', fmt(r.Eav, 1), 'L/m³', 'C / (C/E)'],
        ['Correction de la pâte', '', fmt(r.corr, 1), '%', 'selon D<sub>max</sub>'],
        ['Ciment', 'C', fmt(r.C, 1), 'kg/m³', ''],
        ['Eau', 'E', fmt(r.E, 1), 'L/m³', ''],
        ['Courbe de référence O-A-B'],
        ['Abscisse du point A', 'X', fmt(r.X, 1), 'mm', r.Dmax <= 20 ? 'D<sub>max</sub> / 2' : 'milieu entre le module 38 (5 mm) et D<sub>max</sub>'],
        ['Terme correcteur (dosage, vibration, forme)', 'K', fmt(r.K, 2), '', `Tableau 6 : C, vibration ${
            ['faible', 'faible', 'normale', 'puissante'][p.serrage]}${p.serrage == 0 ? ' (piquage)' : ''}, sable ${p.S_roule == 1 ? 'roulé' : 'concassé'}`],
        ['Correction de finesse du sable', 'K<sub>s</sub>', fmt(r.Ks, 2), '', '6 M<sub>f</sub> − 15'],
        ['Correction de pompabilité', 'K<sub>p</sub>', fmt(r.Kp, 0), '', ''],
        ['Terme correcteur total', 'K′', fmt(r.Kprime, 2), '', 'K + K<sub>s</sub> + K<sub>p</sub>'],
        ['Ordonnée du point A', 'Y', fmt(r.Y, 1), '%', '50 − √(1,25 D<sub>max</sub>) + K′'],
        ['Proportions en volumes absolus'],
        ['Sable', '%S', fmt(r.Srate, 1), '%', 'lignes de partage'],
        ['Gravette', '%g', fmt(r.grate, 1), '%', ''],
        ...(tern ? [['Gravier', '%G', fmt(r.Grate, 1), '%', '']] : []),
        ['Compacité et volumes absolus (pour 1 m³)'],
        ['Compacité de base', 'c<sub>0</sub>', fmt(r.c0, 3), '', 'Tableau 7 (D<sub>max</sub>, consistance, serrage)'],
        ['Correction de forme', 'c<sub>1</sub>', fmt(r.c1, 3), '', 'sable concassé : −0,03 ; gros granulats seuls concassés : −0,01'],
        ['Correction granulats légers', 'c<sub>2</sub>', fmt(r.c2, 3), '', ''],
        ['Correction de dosage', 'c<sub>3</sub>', fmt(r.c3, 3), '', '(C − 350) / 5000'],
        ['Compacité', 'γ', fmt(r.c, 3), '', 'c<sub>0</sub> + c<sub>1</sub> + c<sub>2</sub> + c<sub>3</sub>'],
        ['Volume de ciment', 'V<sub>c</sub>', fmt(r.Vc, 4), 'm³', 'C / ρ<sub>c</sub>'],
        ['Volume des granulats', 'V', fmt(r.V, 4), 'm³', 'γ − V<sub>c</sub>'],
        ['Volume de sable', 'V<sub>S</sub>', fmt(r.Vs, 4), 'm³', '%S · V'],
        ['Volume de gravette', 'V<sub>g</sub>', fmt(r.Vg, 4), 'm³', '%g · V'],
        ...(tern ? [['Volume de gravier', 'V<sub>G</sub>', fmt(r.VG, 4), 'm³', '%G · V']] : []),
    ];
    id('steps-table').tBodies[0].innerHTML = rows.map(row => row.length === 1
        ? `<tr class="group"><td colspan="5">${row[0]}</td></tr>`
        : `<tr><td>${row[0]}</td><td class="sym">${row[1]}</td><td>${row[2]}</td><td>${row[3]}</td><td class="note">${row[4]}</td></tr>`
    ).join('');
}

// ═══ Sauvegardes (mêmes blocs que les applications MS) ════════════════════════

function serializeState() { return clone(state); }

function applyStateData(d) {
    if (!d || !d.params || !d.refus) return false;
    state = {
        params: { ...clone(DEFAULT_PARAMS), ...d.params },
        refus: Object.fromEntries(['S', 'g', 'G'].map(k =>
            [k, MODULES.map((_, i) => +(d.refus[k]?.[i] ?? DEFAULT_REFUS[k][i]))])),
    };
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
    if (!slot?.data || !applyStateData(slot.data)) return;
    syncUIFromState();
    scheduleAutosave();
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
        btnSave.title = 'Enregistrer la formulation actuelle ici';
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

// ─── Export / Import fichier ──────────────────────────────────────────────────
async function exportSlotsToFile() {
    const payload = JSON.stringify({ version: 1, slots: getSlots() }, null, 2);
    const blob = new Blob([payload], { type: 'application/json' });

    if (window.showSaveFilePicker) {
        try {
            const fh = await window.showSaveFilePicker({
                suggestedName: 'formulation_beton.json',
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
        a.href = url; a.download = 'formulation_beton.json';
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
            const f = inp.files[0];
            resolve(f ? await f.text() : null);
        });
        inp.click();
    });
}

function showError(msg) {
    const el = id('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 6000);
}
