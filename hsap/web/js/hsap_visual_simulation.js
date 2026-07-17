/* ── HSAP Visual Simulation JS ──
   v2 — State-map, multi-line timeline, event strip, comparison mode
*/

const STATE = {
  traces: {},
  worldNames: [],
  currentWorld: 0,
  frames: [],
  frameIndex: 0,
  playing: true,
  speed: 2,
  intervalId: null,
  comparisonMode: false,
  baselineStats: null,       // from A_normal_baseline steady-state
  metricRefresh: false,
};

const WORLDS = ['A_normal_baseline', 'B_hsap_abundance', 'C_crowded_abundance', 'D_high_predation_survival', 'E_behavioral_sink_recovery', 'F_behavioral_sink_extinction'];

// ── Data Loading ──
function loadTraces() {
  if (typeof HSAP_DATA === 'undefined') {
    throw new Error('HSAP_DATA missing. Check that hsap_data.js loads before visualization.');
  }
  STATE.traces = HSAP_DATA;
  STATE.worldNames = Object.keys(HSAP_DATA);
  return HSAP_DATA;
}

function switchWorld(index) {
  const name = STATE.worldNames[index];
  if (!name || !STATE.traces[name]) return;
  STATE.currentWorld = index;
  STATE.frames = STATE.traces[name].frames;
  STATE.frameIndex = 0;
  STATE.baselineStats = computeBaseline();
  // Force rebuild of metric inset for clean state
  for (const key of Object.keys(METRIC_NODES)) delete METRIC_NODES[key];
  document.getElementById('world-select').value = name;
  updateAll();
}

function computeBaseline() {
  const ref = STATE.traces['A_normal_baseline'];
  if (!ref || !ref.frames || ref.frames.length < 20) return null;
  const frames = ref.frames;
  const lo = Math.floor(frames.length * 0.2);
  const hi = Math.floor(frames.length * 0.8);
  const stable = frames.slice(lo, hi);
  if (stable.length === 0) return null;
  const baseline = {};
  for (const key of ['male_aggression','female_aggression','fertility','mean_T','mean_C','mean_E',
                     'male_T','female_T','female_E','male_C','female_C',
                     'male_fertility','female_fertility','hsap_index','population']) {
    const vals = stable.map(f => f[key]).filter(v => v !== undefined && v !== null && !Number.isNaN(v));
    baseline[key] = vals.length ? vals.reduce((a,b)=>a+b,0) / vals.length : 0;
  }
  return baseline;
}

// ── Phase Map (unchanged, uses density × threat) ──
function drawPhaseMap() {
  const canvas = document.getElementById('phase-map-canvas');
  if (!canvas) return;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width - 16;
  canvas.height = rect.height - 18;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  const pad = 40;
  const pw = W - pad*2, ph = H - pad*2;
  function x(d) { return pad + d * pw; }
  function y(t) { return pad + (1 - t) * ph; }

  // Region shading
  const regions = [
    { x1:0, y1:0.5, x2:0.5, y2:1, label:'Predator/Disease\nDominated', color:'rgba(239,83,80,0.06)' },
    { x1:0.5, y1:0.5, x2:1, y2:1, label:'Crowding\nSink', color:'rgba(255,183,77,0.06)' },
    { x1:0, y1:0, x2:0.5, y2:0.5, label:'Low Density\nAbundance', color:'rgba(102,187,106,0.06)' },
    { x1:0.5, y1:0, x2:1, y2:0.5, label:'HSAP\nCandidate', color:'rgba(79,195,247,0.06)' },
  ];
  ctx.font = '11px sans-serif';
  ctx.textAlign = 'center';
  for (const r of regions) {
    ctx.fillStyle = r.color;
    ctx.fillRect(x(r.x1), y(r.y1), x(r.x2)-x(r.x1), y(r.y2)-y(r.y1));
    ctx.fillStyle = '#8fa3bf';
    ctx.fillText(r.label, x((r.x1+r.x2)/2), y((r.y1+r.y2)/2)+12);
  }

  // Grid
  ctx.strokeStyle = '#1a2040';
  ctx.lineWidth = 1;
  for (let i = 1; i <= 4; i++) {
    ctx.beginPath(); ctx.moveTo(x(i/4), pad); ctx.lineTo(x(i/4), pad+ph); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(pad, y(i/4)); ctx.lineTo(pad+pw, y(i/4)); ctx.stroke();
  }

  // Axes
  ctx.fillStyle = '#8fa3bf'; ctx.font = '12px sans-serif'; ctx.textAlign = 'center';
  ctx.fillText('Density →', x(0.5), H-4);
  ctx.save(); ctx.translate(8, y(0.5)); ctx.rotate(-Math.PI/2); ctx.fillText('External Threat →', 0, 0); ctx.restore();

  // Trail (last 50 frames)
  const trailLen = Math.min(50, STATE.frameIndex);
  const start = Math.max(0, STATE.frameIndex - trailLen);
  for (let i = start; i <= STATE.frameIndex; i++) {
    if (i >= STATE.frames.length) break;
    const f = STATE.frames[i];
    const px = x(Math.min(1, f.density));
    const py = y(Math.min(1, f.external_threat_index));
    const alpha = 0.15 + 0.85 * ((i - start) / Math.max(1, trailLen));
    const radius = 2 + 6 * Math.sqrt(f.population / 400);
    ctx.beginPath(); ctx.arc(px, py, radius, 0, Math.PI*2);
    ctx.fillStyle = `rgba(255,255,255,${alpha*0.25})`; ctx.fill();
  }

  // Current point
  if (STATE.frameIndex < STATE.frames.length) {
    const f = STATE.frames[STATE.frameIndex];
    const px = x(Math.min(1, f.density));
    const py = y(Math.min(1, f.external_threat_index));
    const radius = 3 + 8 * Math.sqrt(f.population / 400);
    ctx.beginPath(); ctx.arc(px, py, radius, 0, Math.PI*2);
    ctx.fillStyle = hsapIndexColor(f.hsap_index); ctx.globalAlpha = 0.6; ctx.fill(); ctx.globalAlpha = 1;
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke();
  }
}

// ── State Map (replaces fake habitat: rank × energy scatter) ──
function drawStateMap() {
  const canvas = document.getElementById('state-map-canvas');
  if (!canvas) return;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width - 16;
  canvas.height = rect.height - 18;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];
  const sample = f.agent_sample || [];
  if (sample.length === 0) {
    ctx.fillStyle = '#b8c7dd'; ctx.font = '16px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('No agents', W/2, H/2); return;
  }

  const pad = { top: 20, bottom: 28, left: 36, right: 16 };
  const pw = W - pad.left - pad.right, ph = H - pad.top - pad.bottom;
  const maxEnergy = Math.max(0.01, ...sample.map(a => a.energy));
  const maxRank = Math.max(0.01, ...sample.map(a => a.rank));

  // Grid
  ctx.strokeStyle = '#1a2040'; ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const x = pad.left + (i/4)*pw, y = pad.top + (i/4)*ph;
    ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, pad.top+ph); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left+pw, y); ctx.stroke();
  }

  // Axes labels
  ctx.fillStyle = '#8fa3bf'; ctx.font = '12px sans-serif'; ctx.textAlign = 'center';
  ctx.fillText('Rank →', pad.left + pw/2, H-4);
  ctx.save(); ctx.translate(10, pad.top + ph/2); ctx.rotate(-Math.PI/2); ctx.fillText('Energy →', 0, 0); ctx.restore();
  ctx.textAlign = 'right'; ctx.fillText('1.0', pad.left-4, pad.top+10);
  ctx.fillText('0', pad.left-4, pad.top+ph+4);
  ctx.textAlign = 'center'; ctx.fillText('0', pad.left, H-6); ctx.fillText(maxRank.toFixed(1), pad.left+pw, H-6);

  // Extinction warning
  if (sample.length === 0) {
    ctx.fillStyle = '#ef5350'; ctx.font = 'bold 28px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('POPULATION ZERO', W/2, H/2); return;
  }

  // Draw points
  for (const a of sample) {
    const px = pad.left + (a.rank / maxRank) * pw;
    const py = pad.top + ph - (a.energy / maxEnergy) * ph;
    const radius = Math.max(2, Math.min(6, 3 + 0.1 * (a.age || 0)));

    // Cortisol glow
    if (a.C > 0.6) {
      ctx.beginPath(); ctx.arc(px, py, radius+4, 0, Math.PI*2);
      ctx.fillStyle = `rgba(206,147,216,${(a.C-0.6)*0.35})`; ctx.fill();
    }

    const color = a.sex === 'male' ? '#42a5f5' : (a.pregnant ? '#ec407a' : '#ffa726');
    ctx.beginPath(); ctx.arc(px, py, radius, 0, Math.PI*2);
    ctx.fillStyle = color;
    ctx.globalAlpha = a.health < 0.3 ? 0.4 : 1;
    ctx.fill(); ctx.globalAlpha = 1;

    // Injury ring
    if (a.injury) {
      ctx.beginPath(); ctx.arc(px, py, radius+2, 0, Math.PI*2);
      ctx.strokeStyle = '#ef5350'; ctx.lineWidth = 1.5; ctx.setLineDash([2,2]); ctx.stroke(); ctx.setLineDash([]);
    }
    // Pregnant ring
    if (a.pregnant) {
      ctx.beginPath(); ctx.arc(px, py, radius+1, 0, Math.PI*2);
      ctx.strokeStyle = '#ec407a'; ctx.lineWidth = 2; ctx.stroke();
    }
  }

  // Density hint
  if (f.density > 0) {
    ctx.fillStyle = `rgba(255,100,100,${Math.min(0.12, f.density*0.1)})`;
    ctx.fillRect(pad.left, pad.top, pw, ph);
  }
}

// ── Age/Sex Mini Bars ──
function drawAgeSexBars() {
  const canvas = document.getElementById('agesex-canvas');
  if (!canvas) return;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width - 16;
  canvas.height = rect.height - 18;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];
  const sample = f.agent_sample || [];
  if (sample.length === 0) { ctx.fillStyle='#b8c7dd'; ctx.font='13px sans-serif'; ctx.textAlign='center'; ctx.fillText('No agents', W/2, H/2); return; }

  const barW = Math.max(6, (W-20) / 3 - 4);
  const barH = H - 10;
  const maxCount = Math.max(1, sample.length);

  const groups = { 'male_juvenile':[], 'male_adult':[], 'male_senior':[], 'female_juvenile':[], 'female_adult':[], 'female_senior':[] };
  for (const a of sample) {
    const ageGroup = a.age < 10 ? 'juvenile' : a.age < 50 ? 'adult' : 'senior';
    const key = `${a.sex}_${ageGroup}`;
    if (groups[key]) groups[key].push(a);
  }

  const colors = { 'male_juvenile':'#42a5f5', 'male_adult':'#1e88e5', 'male_senior':'#0d47a1',
                   'female_juvenile':'#ffa726', 'female_adult':'#fb8c00', 'female_senior':'#e65100' };

  let x = 6;
  for (const [key, agents] of Object.entries(groups)) {
    const h = (agents.length / maxCount) * barH;
    ctx.fillStyle = colors[key] || '#6a7090';
    ctx.fillRect(x, barH - h, barW, h);
    x += barW + 4;
  }

  // Labels
  ctx.fillStyle = '#c8d4e8'; ctx.font = '12px sans-serif'; ctx.textAlign = 'center';
  x = 6;
  for (const key of Object.keys(groups)) {
    const parts = key.split('_');
    ctx.fillText(parts[0][0]+parts[1][0], x + barW/2, H-1);
    x += barW + 4;
  }
}

// ── Action Composition Bar ──
function drawActionBar() {
  const canvas = document.getElementById('action-bar-canvas');
  if (!canvas) return;
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width - 16;
  canvas.height = rect.height - 18;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];
  const actions = f.actions || {};
  const total = Object.values(actions).reduce((a,b)=>a+b, 0);
  if (total === 0) { ctx.fillStyle='#b8c7dd'; ctx.font='12px sans-serif'; ctx.textAlign='center'; ctx.fillText('No actions', W/2, H/2); return; }

  const barW = W - 12;
  const barH = Math.max(8, H - 20);
  const actionColors = { 'forage':'#4dd0e1', 'mate':'#ab47bc', 'fight':'#ef5350', 'guard':'#ffb74d', 'rest':'#6a7090', 'move':'#42a5f5' };
  const actionOrder = ['forage','mate','fight','guard','move','rest'];

  let x = 6;
  for (const act of actionOrder) {
    const count = actions[act] || 0;
    if (count === 0) continue;
    const w = (count / total) * barW;
    ctx.fillStyle = actionColors[act] || '#6a7090';
    ctx.fillRect(x, (H - barH)/2, Math.max(2, w), barH);
    x += w;
  }

  // Legend
  let lx = 6;
  ctx.font = '12px sans-serif'; ctx.textAlign = 'left';
  for (const act of actionOrder) {
    const count = actions[act] || 0;
    if (count === 0) continue;
    ctx.fillStyle = actionColors[act]; ctx.fillRect(lx, H-9, 6, 6);
    ctx.fillStyle = '#c8d4e8'; ctx.fillText(`${act}(${count})`, lx+8, H-4);
    lx += ctx.measureText(`${act}(${count})`).width + 12;
    if (lx > W) break;
  }
}

// ── Metric Inset — stable DOM, no reflow ──
function fmtCount(v) {
  const n = Number.isFinite(+v) ? +v : 0;
  return String(n).padStart(2, '0');
}

const METRIC_ROWS = [
  ['world', 'World'],
  ['step', 'Step'],
  ['population', 'Population'],
  ['growth', 'Growth'],
  ['birthsDeaths', 'Births/Deaths'],
  ['matingsFights', 'Matings/Fights'],
  ['density', 'Density'],
  ['resources', 'Resources'],
  ['sexRatio', 'Sex Ratio (M/F)'],
  ['rankInequality', 'Rank Inequality'],
  ['predator', 'Predator'],
  ['disease', 'Disease'],
  ['threatIndex', 'Threat Index'],
  ['maleAgg', 'Male Agg'],
  ['femaleAgg', 'Female Agg'],
  ['fertility', 'Fertility'],
  ['fertSex', 'Fert ♂/♀'],
  ['tSex', 'T ♂/♀'],
  ['eSex', 'E ♂/♀'],
  ['cSex', 'C ♂/♀'],
  ['infanticide', 'Infanticide'],
  ['neglect', 'Neglect'],
];

const METRIC_NODES = {};

function buildMetricInset() {
  const container = document.getElementById('metric-values');
  if (!container) return;

  const grid = document.createElement('div');
  grid.className = 'metrics-grid';

  for (const [key, label] of METRIC_ROWS) {
    const row = document.createElement('div');
    row.className = 'metric-item';
    row.dataset.metric = key;
    const lab = document.createElement('span');
    lab.className = 'metric-label';
    lab.textContent = label;
    const val = document.createElement('span');
    val.className = 'metric-value';
    val.textContent = '00';
    row.appendChild(lab);
    row.appendChild(val);
    grid.appendChild(row);
    METRIC_NODES[key] = val;
  }

  const hsapBlock = document.createElement('div');
  hsapBlock.className = 'metric-block hsap-block';
  hsapBlock.innerHTML =
    '<span style="color:#b8c7dd;font-size:12px;">HSAP Index: </span>' +
    '<span id="metric-hsap-index" style="font-size:18px;font-weight:700;">0.000</span>' +
    '<span id="metric-hsap-phase" style="font-size:12px;color:#b8c7dd;margin-left:6px;"></span>';
  grid.appendChild(hsapBlock);

  const scenarioBlock = document.createElement('div');
  scenarioBlock.className = 'metric-block scenario-block';
  scenarioBlock.id = 'metric-scenario-label';
  scenarioBlock.textContent = 'Transition';
  grid.appendChild(scenarioBlock);

  container.replaceChildren(grid);
  METRIC_NODES.hsapIndex = document.getElementById('metric-hsap-index');
  METRIC_NODES.hsapPhase = document.getElementById('metric-hsap-phase');
  METRIC_NODES.scenario = document.getElementById('metric-scenario-label');
}

function setMetric(key, text, mode) {
  const node = METRIC_NODES[key];
  if (!node) return;
  node.textContent = text;
  node.className = 'metric-value';
  if (key === 'population') node.classList.add('pop');
  if (mode === 'danger') node.classList.add('hot-danger');
  if (mode === 'warn') node.classList.add('hot-neglect');
  if (mode === 'quiet') node.classList.add('quiet-value');
  if (mode === 'good') node.classList.add('good-value');
}

function updateMetricInset() {
  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];
  if (!METRIC_NODES.world) buildMetricInset();

  setMetric('world', STATE.worldNames[STATE.currentWorld] || 'Unknown');
  setMetric('step', `${f.step} / ${STATE.frames.length - 1}`);
  setMetric('population', String(f.population));
  setMetric('growth', `${(f.growth_rate * 100).toFixed(1)}%`,
    f.growth_rate >= 0 ? 'good' : 'danger');
  setMetric('birthsDeaths', `${fmtCount(f.births)}/${fmtCount(f.deaths)}`);
  setMetric('matingsFights', `${fmtCount(f.matings)}/${fmtCount(f.actions?.fight || 0)}`);
  setMetric('density', f.density.toFixed(3));
  setMetric('resources', f.resource_abundance.toFixed(2));
  setMetric('sexRatio',
    `${(f.sex_ratio * 100).toFixed(0)}/${((1 - f.sex_ratio) * 100).toFixed(0)}`);
  setMetric('rankInequality', f.rank_inequality.toFixed(2));
  setMetric('predator', f.predator_pressure.toFixed(2));
  setMetric('disease', f.disease_pressure.toFixed(2));
  setMetric('threatIndex', f.external_threat_index.toFixed(3),
    f.external_threat_index > 0.5 ? 'danger' : 'good');
  setMetric('maleAgg', f.male_aggression.toFixed(3),
    f.male_aggression > 0.7 ? 'danger' : '');
  setMetric('femaleAgg', f.female_aggression.toFixed(3),
    f.female_aggression > 0.7 ? 'warn' : '');
  setMetric('fertility', f.fertility.toFixed(3),
    f.fertility > 0.5 ? 'good' : 'warn');
  setMetric('fertSex',
    `${(f.male_fertility || 0).toFixed(2)} / ${(f.female_fertility || 0).toFixed(2)}`);
  setMetric('tSex',
    `${(f.male_T || 0).toFixed(2)} / ${(f.female_T || 0).toFixed(2)}`);
  setMetric('eSex',
    `${(f.male_E || 0).toFixed(2)} / ${(f.female_E || 0).toFixed(2)}`);
  setMetric('cSex',
    `${(f.male_C || 0).toFixed(2)} / ${(f.female_C || 0).toFixed(2)}`);
  setMetric('infanticide', fmtCount(f.infanticide),
    f.infanticide > 0 ? 'danger' : 'quiet');
  setMetric('neglect', fmtCount(f.neglect),
    f.neglect > 0 ? 'warn' : 'quiet');

  METRIC_NODES.hsapIndex.textContent = f.hsap_index.toFixed(3);
  METRIC_NODES.hsapIndex.style.color = hsapIndexColor(f.hsap_index);
  const phase = (f.hsap_phase || 'unknown')
    .replace(/-/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
  METRIC_NODES.hsapPhase.textContent = ` ${phase}`;
  METRIC_NODES.scenario.textContent = f.scenario_label || '';
  METRIC_NODES.scenario.style.color = scenarioLabelColor(f.scenario_label);
}

// ── Warning Ribbon ──
function updateWarningRibbon() {
  const el = document.getElementById('warning-ribbon');
  if (!el) return;
  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];
  const warnings = [];

  if (f.population === 0) warnings.push('Population at zero');
  else if (f.population < 10) warnings.push('Very low population');
  if (f.external_threat_index > 0.7) warnings.push('High external threat');
  if (f.density > 0.8) warnings.push('Overcrowded');
  if (f.resource_abundance < 0.2) warnings.push('Resource scarcity');
  if (f.male_aggression > 0.9) warnings.push('High male aggression');
  if (f.female_aggression > 0.95) warnings.push('High female aggression');
  if (f.growth_rate < -0.3 && f.population > 0) warnings.push('Rapid decline');
  if (f.infanticide > 3) warnings.push('Elevated infanticide');
  if (f.neglect > 5) warnings.push('Elevated neglect');

  if (warnings.length === 0) {
    el.className = 'quiet';
    el.innerHTML = '✓ Normal conditions';
    return;
  }
  el.className = '';
  el.innerHTML = `<span style="font-weight:600;margin-right:8px;">⚠</span>${warnings.join(' · ')}`;
}

// ── Badge (extinction/stability) ──
function updateBadge() {
  const el = document.getElementById('badge');
  if (!el) return;
  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];

  if (f.population === 0) {
    el.style.display = 'inline-block'; el.className = 'badge badge-extinct'; el.textContent = 'ZERO POP';
    return;
  }
  if (f.sink_active) {
    el.style.display = 'inline-block'; el.className = 'badge badge-sink'; el.textContent = 'SINK';
    return;
  }
  if (f.post_sink_recovery) {
    el.style.display = 'inline-block'; el.className = 'badge badge-recovery'; el.textContent = 'RECOVERY';
    return;
  }
  if (f.population > 50 && Math.abs(f.growth_rate) < 0.01) {
    el.style.display = 'inline-block'; el.className = 'badge badge-stable'; el.textContent = 'STABLE';
  } else {
    el.style.display = 'none';
  }
}

// ── Causal Chain (uses baseline reference) ──
function updateCausalChain() {
  const container = document.getElementById('chain-container');
  if (!container) return;
  if (STATE.frameIndex >= STATE.frames.length) return;
  const f = STATE.frames[STATE.frameIndex];
  const b = STATE.baselineStats;

  // Extinct
  if (f.population === 0) {
    container.innerHTML = `<div style="color:#ef5350;font-size:13px;text-align:center;padding:8px;">Population at zero — chain not evaluable.</div>`;
    return;
  }
  // Too few agents
  if (f.population < 20) {
    container.innerHTML = `<div style="color:#ffb74d;font-size:13px;text-align:center;padding:8px;">Too few agents (${f.population}) for reliable chain interpretation.</div>`;
    return;
  }

  // Only mark Male T ↓ and Fertility ↓ as successful if baseline values are > 0
  const maleTDown = b && b.male_T > 0.01 ? (f.male_T||0) < b.male_T * 0.95 : false;
  const fertDown = b && b.fertility > 0.01 ? f.fertility < b.fertility * 0.95 : false;

  const links = [
    { label: 'Low threat', check: f.external_threat_index < 0.25 },
    { label: '♂ T lower', check: maleTDown },
    { label: '♂ Agg lower', check: b ? f.male_aggression < b.male_aggression * 0.95 : false },
    { label: '♀ Agg higher', check: b ? f.female_aggression > b.female_aggression * 1.05 : false },
    { label: 'Fertility lower', check: fertDown },
    { label: 'Pop stable', check: Math.abs(f.growth_rate) < 0.02 && f.population > 0 },
  ];

  container.innerHTML = links.map((link,i) => `
    <div class="causal-link ${link.check?'active':'inactive'}">
      <span>${link.label}</span>
      <span class="arrow">${i < links.length-1 ? '→' : ''}</span>
      <span class="status ${link.check?'yes':'no'}">${link.check ? '✓' : '✗'}</span>
    </div>
  `).join('');
}

// ── Timeline Series Helper (Repair Batch 9) ──
function drawTimelineSeries(ctx, values, allFrameCount, pad, plotW, plotH, baseY, color, lineWidth) {
  if (values.length < 2) return;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  ctx.beginPath();
  for (let i = 0; i < values.length; i++) {
    const x = pad + (i / (allFrameCount - 1)) * plotW;
    const y = baseY - ((values[i] - min) / range) * plotH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth || 1;
  ctx.stroke();
}

// ── Timeline Legend ──
const TIMELINE_LEGEND = [
  { name: 'Population', color: '#4fc3f7' },
  { name: 'HSAP', color: '#90ee90' },
  { name: 'Birth', color: '#00ff88' },
  { name: 'Death', color: '#ff5555' },
  { name: 'Mate', color: '#ff00ff' },
  { name: 'Infant', color: '#ffaa00' },
  { name: 'Neglect', color: '#888888' },
];

function drawTimelineLegend(ctx, W) {
  ctx.font = '13px sans-serif';
  let x = 16;
  const y = 14;
  for (const item of TIMELINE_LEGEND) {
    ctx.strokeStyle = item.color;
    ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 16, y); ctx.stroke();
    ctx.fillStyle = '#c8d4e8';
    ctx.fillText(item.name, x + 20, y + 4);
    x += ctx.measureText(item.name).width + 34;
    if (x > W - 40) { x = 16; break; }
  }
}

// ── Timeline Renderer (Production) ──
function drawTimelineDebug(canvas, ctx) {
  const frameIndex = STATE.frameIndex;
  const totalFrames = STATE.frames.length;
  const W = canvas.width, H = canvas.height;

  if (STATE.frames.length < 2) return;

  // Legend at top
  drawTimelineLegend(ctx, W);

  // Plot area below legend
  const legendH = 28;
  const pad = { top: legendH + 8, bottom: 20, left: 40, right: 12 };
  const plotW = W - pad.left - pad.right;
  const plotH = H - pad.top - pad.bottom;
  const allFrames = STATE.frames;
  const visibleFrames = allFrames.slice(0, frameIndex + 1);
  const baseY = H - pad.bottom;

  // Population trace (blue, thick)
  drawTimelineSeries(ctx, visibleFrames.map(f => f.population), allFrames.length, pad.left, plotW, plotH, baseY, '#4fc3f7', 2);

  // HSAP Index trace (green, thick)
  drawTimelineSeries(ctx, visibleFrames.map(f => f.hsap_index), allFrames.length, pad.left, plotW, plotH, baseY, '#90ee90', 2);

  // Event traces (thin, independent scales)
  drawTimelineSeries(ctx, visibleFrames.map(f => f.births || 0), allFrames.length, pad.left, plotW, plotH, baseY, '#00ff88', 1);
  drawTimelineSeries(ctx, visibleFrames.map(f => f.deaths || 0), allFrames.length, pad.left, plotW, plotH, baseY, '#ff5555', 1);
  drawTimelineSeries(ctx, visibleFrames.map(f => f.matings || 0), allFrames.length, pad.left, plotW, plotH, baseY, '#ff00ff', 1);
  drawTimelineSeries(ctx, visibleFrames.map(f => f.infanticide || 0), allFrames.length, pad.left, plotW, plotH, baseY, '#ffaa00', 1);
  drawTimelineSeries(ctx, visibleFrames.map(f => f.neglect || 0), allFrames.length, pad.left, plotW, plotH, baseY, '#888888', 1);

  // Current frame marker
  const markerX = pad.left + (frameIndex / (allFrames.length - 1)) * plotW;
  ctx.beginPath();
  ctx.moveTo(markerX, pad.top);
  ctx.lineTo(markerX, baseY);
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 1;
  ctx.stroke();

  // Timestep label below marker
  ctx.font = '12px monospace';
  ctx.fillStyle = '#b8c7dd';
  ctx.textAlign = 'center';
  ctx.fillText(`t=${frameIndex}`, markerX, H - 4);
  ctx.textAlign = 'left';
}

// ── Timeline (multi-line + event strip) ──
function drawTimeline() {
  const canvas = document.getElementById('timeline-canvas');
  if (!canvas) return;
  const parent = canvas.parentElement;
  const rect = parent.getBoundingClientRect();
  canvas.width = rect.width - 16;
  canvas.height = Math.max(130, rect.height - 80);
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // DIAGNOSTIC: minimal debug renderer — Repair Batch 5
  drawTimelineDebug(canvas, ctx);
  return;

  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  const frames = STATE.frames;
  if (frames.length < 2) return;
  const currentFrame = STATE.frameIndex;

  // Split into main area (top 70%) and event strip (bottom 30%)
  const eventH = Math.max(20, H * 0.25);
  const mainH = H - eventH;

  const pad = { top: 16, bottom: 4, left: 44, right: 12 };
  const pw = W - pad.left - pad.right;
  const ph = mainH - pad.top - pad.bottom;
  const xScale = pw / Math.max(1, frames.length - 1);
  function chartX(i) { return pad.left + i * xScale; }
  function chartY(v, minV, maxV) { return pad.top + ph - ((v - minV) / (maxV - minV)) * ph; }

  // Sink/recovery background shading
  for (let i = 0; i < frames.length; i++) {
    if (frames[i].sink_active) {
      ctx.fillStyle = 'rgba(239,83,80,0.08)';
      ctx.fillRect(chartX(i), pad.top, Math.max(2, xScale*1.5), ph);
    } else if (frames[i].post_sink_recovery) {
      ctx.fillStyle = 'rgba(102,187,106,0.08)';
      ctx.fillRect(chartX(i), pad.top, Math.max(2, xScale*1.5), ph);
    }
  }

  // Grid
  ctx.strokeStyle = '#1a2040'; ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) {
    const yPos = pad.top + (i/4)*ph;
    ctx.beginPath(); ctx.moveTo(pad.left, yPos); ctx.lineTo(W-pad.right, yPos); ctx.stroke();
  }

  const maxPop = Math.max(1, ...frames.map(f=>f.population));

  // Permanent lines
  const lines = [
    { key:'population', data:frames.map(f=>f.population), color:'#ffd54f', label:'Population', scale:v=>v/maxPop, yMin:0, yMax:1 },
    { key:'fertility', data:frames.map(f=>f.fertility), color:'#66bb6a', label:'Fertility', scale:v=>v, yMin:0, yMax:1 },
    { key:'male_aggression', data:frames.map(f=>f.male_aggression), color:'#42a5f5', label:'♂ Agg', scale:v=>v, yMin:0, yMax:1 },
    { key:'female_aggression', data:frames.map(f=>f.female_aggression), color:'#ffa726', label:'♀ Agg', scale:v=>v, yMin:0, yMax:1 },
    { key:'hsap_index', data:frames.map(f=>f.hsap_index), color:'#ffffff', label:'HSAP', scale:v=>v, yMin:0, yMax:1, dash:[3,2] },
  ];

  // Draw areas (population fill)
  ctx.beginPath();
  ctx.moveTo(chartX(0), chartY(0, 0, 1));
  for (let i = 0; i < frames.length; i++) {
    ctx.lineTo(chartX(i), chartY(frames[i].population / maxPop, 0, 1));
  }
  ctx.lineTo(chartX(frames.length-1), chartY(0, 0, 1));
  ctx.closePath();
  ctx.fillStyle = 'rgba(255,213,79,0.08)'; ctx.fill();

  for (const line of lines) {
    ctx.beginPath();
    for (let i = 0; i < frames.length; i++) {
      const v = Math.min(line.yMax, Math.max(line.yMin, line.scale(frames[i][line.key])));
      const x = chartX(i), y = chartY(v, line.yMin, line.yMax);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.strokeStyle = line.color; ctx.lineWidth = line.key === 'population' ? 2 : 1.5;
    if (line.dash) ctx.setLineDash(line.dash);
    ctx.stroke(); ctx.setLineDash([]);
  }

  // Y-axis
  ctx.fillStyle = '#8fa3bf'; ctx.font = '11px sans-serif'; ctx.textAlign = 'right';
  ctx.fillText(maxPop, pad.left-4, pad.top+10);
  ctx.fillText(Math.round(maxPop/2), pad.left-4, chartY(0.5,0,1)+3);
  ctx.fillText(0, pad.left-4, pad.top+ph+4);

  // X-axis (event strip area - steps)
  ctx.textAlign = 'center'; ctx.font = '10px sans-serif';
  const stepInterval = Math.max(1, Math.floor(frames.length / 8));
  for (let i = 0; i < frames.length; i += stepInterval) {
    ctx.fillText(frames[i].step, chartX(i), pad.top+ph+12);
  }

  // Current position line — bold white cursor
  if (currentFrame >= 0 && currentFrame < frames.length) {
    const cx = chartX(currentFrame);
    ctx.beginPath(); ctx.moveTo(cx, pad.top); ctx.lineTo(cx, pad.top+ph);
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.stroke();
    // Small triangle marker at top
    ctx.beginPath(); ctx.moveTo(cx-4, pad.top); ctx.lineTo(cx+4, pad.top); ctx.lineTo(cx, pad.top+6); ctx.closePath();
    ctx.fillStyle = '#ffffff'; ctx.fill();
  }

  // ── Event Strip ──
  const esTop = mainH + 2;
  const esH = eventH - 4;
  const esPad = { left: pad.left, right: pad.right };

  // Background
  ctx.fillStyle = '#0a0d16'; ctx.fillRect(esPad.left, esTop, W-esPad.left-esPad.right, esH);

  // Event markers
  const eventTypes = [
    { key:'births', color:'#66bb6a', label:'Birth' },
    { key:'deaths', color:'#ef5350', label:'Death' },
    { key:'matings', color:'#ab47bc', label:'Mate' },
    { key:'infanticide', color:'#ff1744', label:'Infant' },
    { key:'neglect', color:'#ffb74d', label:'Neglect' },
  ];

  const esScaleX = esH / Math.max(1, ...frames.map(f=>f.population || 1));
  const maxEvent = Math.max(1, ...eventTypes.flatMap(et => frames.map(f => f[et.key] || 0)));

  for (const et of eventTypes) {
    for (let i = 0; i < frames.length; i++) {
      const val = frames[i][et.key] || 0;
      if (val === 0) continue;
      const x = chartX(i);
      const h = Math.max(2, (val / maxEvent) * esH * 0.8);
      ctx.fillStyle = et.color; ctx.globalAlpha = 0.5 + 0.5 * (val / maxEvent);
      ctx.fillRect(x-1, esTop + esH - h, Math.max(2, xScale-1), h);
      ctx.globalAlpha = 1;
    }
  }

  // Event axis labels
  ctx.fillStyle = '#8fa3bf'; ctx.font = '13px sans-serif'; ctx.textAlign = 'left';
  let ex = esPad.left + 4;
  for (const et of eventTypes) {
    ctx.fillStyle = et.color; ctx.fillRect(ex, esTop+2, 6, 6);
    ctx.fillStyle = '#c8d4e8'; ctx.fillText(et.label, ex+9, esTop+9);
    ex += ctx.measureText(et.label).width + 18;
    if (ex > W - esPad.right) break;
  }

  // Event y-axis
  ctx.textAlign = 'right'; ctx.font = '12px sans-serif'; ctx.fillStyle = '#b8c7dd';
  ctx.fillText(maxEvent, esPad.left-4, esTop+10);
  ctx.fillText(0, esPad.left-4, esTop+esH);

  // Position line continues into event strip — bold white cursor
  if (currentFrame >= 0 && currentFrame < frames.length) {
    const cx = chartX(currentFrame);
    ctx.beginPath(); ctx.moveTo(cx, esTop); ctx.lineTo(cx, esTop+esH);
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 2; ctx.stroke();
  }

  // ── Timeline status label ──
  ctx.fillStyle = '#b8c7dd'; ctx.font = '12px sans-serif'; ctx.textAlign = 'right';
  const currentStep = frames[currentFrame] ? frames[currentFrame].step : 0;
  ctx.fillText(`Timestep: ${currentStep} / ${frames[frames.length-1].step}`, W - pad.right, H - 2);
}

// ── Comparison Mode ──
function drawComparison() {
  const panel = document.getElementById('comparison-panel');
  if (!panel) return;
  panel.style.display = STATE.comparisonMode ? 'grid' : 'none';
  if (!STATE.comparisonMode) return;
  panel.style.gridTemplateColumns = `repeat(${WORLDS.length}, 1fr)`;

  for (const name of WORLDS) {
    const canvas = document.getElementById(`cmp-${name}`);
    const ctx = canvas?.getContext('2d');
    if (!ctx || !STATE.traces[name]) continue;
    const frames = STATE.traces[name].frames;
    if (!frames || frames.length < 2) continue;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = Math.max(100, rect.width - 12);
    canvas.height = Math.max(80, rect.height - 28);
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    const pad = { top: 12, bottom: 16, left: 4, right: 4 };
    const pw = W - pad.left - pad.right, ph = H - pad.top - pad.bottom;
    const xScale = pw / Math.max(1, frames.length - 1);
    function cx(i) { return pad.left + i * xScale; }
    function cy(v) { return pad.top + ph - v * ph; }

    const metrics = [
      { key:'population', color:'#ffd54f', scale:v=>Math.min(1, v/300) },
      { key:'male_aggression', color:'#42a5f5', scale:v=>v },
      { key:'female_aggression', color:'#ffa726', scale:v=>v },
      { key:'fertility', color:'#66bb6a', scale:v=>v },
      { key:'hsap_index', color:'#ffffff', scale:v=>v, dash:[2,2] },
    ];

    for (const m of metrics) {
      ctx.beginPath();
      for (let i = 0; i < frames.length; i++) {
        const v = Math.min(1, Math.max(0, m.scale(frames[i][m.key])));
        const x = cx(i), y = cy(v);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = m.color; ctx.lineWidth = 0.8;
      if (m.dash) ctx.setLineDash(m.dash);
      ctx.stroke(); ctx.setLineDash([]);
    }

    // Title
    ctx.fillStyle = '#b8c7dd'; ctx.font = '10px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText(name.replace(/_/g,' '), W/2, H-2);

    // Last HSAP value
    const last = frames[frames.length-1];
    ctx.fillStyle = hsapIndexColor(last.hsap_index);
    ctx.font = 'bold 10px sans-serif'; ctx.textAlign = 'right';
    ctx.fillText(`HSAP ${last.hsap_index.toFixed(2)}`, W-2, pad.top+8);
  }
}

// ── Color Helpers ──
function hsapIndexColor(hsap) {
  if (hsap < 0.35) return '#ef5350';
  if (hsap < 0.60) return '#ffb74d';
  if (hsap < 0.80) return '#66bb6a';
  return '#4fc3f7';
}
function hsapPhaseColor(phase) {
  switch (phase) {
    case 'external-control': return '#ef5350';
    case 'transition': return '#ffb74d';
    case 'hsap-active': return '#66bb6a';
    case 'strong-social-regulation': return '#4fc3f7';
    default: return '#6a7090';
  }
}
function scenarioLabelColor(label) {
  switch (label) {
    case 'Extinct': return '#ef5350';
    case 'Behavioral sink': return '#ab47bc';
    case 'Post-sink recovery': return '#66bb6a';
    case 'External-control': return '#ef5350';
    case 'HSAP-active': return '#66bb6a';
    case 'Crowded stable': return '#ffb74d';
    case 'Transition': return '#6a7090';
    default: return '#6a7090';
  }
}

// ── Animation ──
function animate() {
  if (!STATE.playing || STATE.frames.length === 0) return;
  for (let s = 0; s < STATE.speed; s++) {
    STATE.frameIndex = Math.min(STATE.frameIndex + 1, STATE.frames.length - 1);
  }
  if (STATE.frameIndex >= STATE.frames.length - 1) {
    // Restart from beginning instead of stopping
    STATE.frameIndex = 0;
  }
  updateAll();
}

function updateAll() {
  updateMetricInset();
  updateCausalChain();
  updateWarningRibbon();
  updateBadge();
  drawPhaseMap();
  drawStateMap();
  drawAgeSexBars();
  drawActionBar();
  drawTimeline();
  drawComparison();

  // Refresh indicator
  const el = document.getElementById('metric-refresh');
  if (el) {
    el.style.opacity = '1';
    clearTimeout(el._timer);
    el._timer = setTimeout(() => { el.style.opacity = '0'; }, 200);
  }
}

function startAnimation() {
  if (STATE.intervalId) clearInterval(STATE.intervalId);
  STATE.intervalId = setInterval(animate, 100);
}

// ── Controls ──
function setupControls() {
  document.getElementById('play-btn').addEventListener('click', () => {
    if (STATE.playing) {
      // Pause
      STATE.playing = false;
      document.getElementById('play-btn').textContent = '▶';
    } else {
      // Play — restart from beginning if at end
      if (STATE.frameIndex >= STATE.frames.length - 1) STATE.frameIndex = 0;
      STATE.playing = true;
      document.getElementById('play-btn').textContent = '⏸';
    }
  });
  document.getElementById('step-back').addEventListener('click', () => {
    STATE.playing = false; document.getElementById('play-btn').textContent = '▶';
    STATE.frameIndex = Math.max(0, STATE.frameIndex - 1); updateAll();
  });
  document.getElementById('step-fwd').addEventListener('click', () => {
    STATE.playing = false; document.getElementById('play-btn').textContent = '▶';
    STATE.frameIndex = Math.min(STATE.frames.length - 1, STATE.frameIndex + 1); updateAll();
  });
  document.getElementById('restart-btn').addEventListener('click', () => {
    STATE.frameIndex = 0; STATE.playing = true; document.getElementById('play-btn').textContent = '⏸'; updateAll();
  });
  document.getElementById('world-select').addEventListener('change', (e) => {
    const idx = STATE.worldNames.indexOf(e.target.value);
    if (idx >= 0) switchWorld(idx);
    document.getElementById('play-btn').textContent = '⏸'; STATE.playing = true;
  });
  document.getElementById('png-btn').addEventListener('click', savePNG);
  document.getElementById('comparison-btn').addEventListener('click', () => {
    STATE.comparisonMode = !STATE.comparisonMode;
    document.getElementById('comparison-btn').classList.toggle('active');
    drawComparison();
  });
  document.getElementById('about-btn').addEventListener('click', () => {
    const panel = document.getElementById('about-panel');
    if (panel) panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
  });

  // Timeline scrubbing — click to jump to frame
  const timelineCanvas = document.getElementById('timeline-canvas');
  if (timelineCanvas) {
    timelineCanvas.addEventListener('click', (e) => {
      const rect = timelineCanvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const ratio = Math.max(0, Math.min(1, x / rect.width));
      STATE.frameIndex = Math.round(ratio * (STATE.frames.length - 1));
      STATE.playing = false;
      document.getElementById('play-btn').textContent = '▶';
      updateAll();
    });
    timelineCanvas.style.cursor = 'pointer';
  }

  // Keyboard
  document.addEventListener('keydown', (e) => {
    switch (e.key) {
      case ' ': e.preventDefault(); document.getElementById('play-btn').click(); break;
      case 'ArrowLeft': document.getElementById('step-back').click(); break;
      case 'ArrowRight': document.getElementById('step-fwd').click(); break;
      case 'r': case 'R': document.getElementById('restart-btn').click(); break;
      case 'p': case 'P': savePNG(); break;
      case 'm': case 'M': document.getElementById('comparison-btn').click(); break;
    }
  });
}

function savePNG() {
  const canvas = document.getElementById('timeline-canvas');
  if (!canvas) return;
  const link = document.createElement('a');
  link.download = `hsap_${STATE.worldNames[STATE.currentWorld]}_step${STATE.frameIndex}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

// ── Init ──
function init() {
  document.getElementById('loading').style.display = 'flex';
  // Populate version in About panel
  const versionEl = document.getElementById('about-version');
  if (versionEl) versionEl.textContent = 'v1.0';
  try {
    loadTraces();
    if (STATE.worldNames.length > 0) {
      switchWorld(0);
      setupControls();
      startAnimation();
    }
    document.getElementById('loading').style.display = 'none';
  } catch (e) {
    document.getElementById('loading').innerHTML = `<span style="color:#ef5350">Failed to load trace data: ${e.message}</span>`;
    console.error(e);
  }
}

let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(updateAll, 150);
});

document.addEventListener('DOMContentLoaded', init);
