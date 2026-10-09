/**
 * Motor Health Monitoring System
 * Interactive Logic, Fuzzy Inference Engine & Canvas Visualizations
 */

// 1. Fuzzy Logic Primitives matching Milestone-3 Notebook
function trap(x, a, b, c, d) {
  if (x <= a || x >= d) return 0.0;
  if (b <= x && x <= c) return 1.0;
  if (a < x && x < b) return b !== a ? (x - a) / (b - a) : 1.0;
  return d !== c ? (d - x) / (d - c) : 1.0;
}

function trimf(x, a, b, c) {
  if (x <= a || x >= c) return 0.0;
  if (x === b) return 1.0;
  return x < b ? (x - a) / (b - a) : (c - x) / (c - b);
}

function currentMemberships(x) {
  return {
    Low: trap(x, 0, 0, 5, 10),
    Medium: trimf(x, 5, 10, 15),
    High: trap(x, 10, 15, 20, 20)
  };
}

function tempMemberships(x) {
  return {
    Low: trap(x, 25, 25, 35, 50),
    Medium: trimf(x, 40, 62.5, 85),
    High: trap(x, 75, 90, 100, 100)
  };
}

function vibMemberships(x) {
  return {
    Low: trap(x, 0, 0, 2, 4),
    Medium: trimf(x, 2.5, 5, 7.5),
    High: trap(x, 6, 8, 10, 10)
  };
}

const levels = ['Low', 'Medium', 'High'];

function ruleOutput(c, t, v) {
  const sevMap = { Low: 0, Medium: 1, High: 2 };
  const sev = sevMap[c] + sevMap[t] + sevMap[v];
  if (sev <= 1) return { label: 'Normal', score: 20 };
  if (sev <= 3) return { label: 'Warning', score: 50 };
  return { label: 'Critical', score: 80 };
}

function fuzzyPredict(current, temp, vib, inclusiveWarning = true) {
  const cm = currentMemberships(current);
  const tm = tempMemberships(temp);
  const vm = vibMemberships(vib);

  let num = 0;
  let den = 0;
  const fired = [];

  for (const c of levels) {
    for (const t of levels) {
      for (const v of levels) {
        const w = Math.min(cm[c], tm[t], vm[v]);
        if (w > 0) {
          const rule = ruleOutput(c, t, v);
          num += w * rule.score;
          den += w;
          fired.push({
            current: c,
            temp: t,
            vib: v,
            weight: Number(w.toFixed(3)),
            label: rule.label,
            score: rule.score
          });
        }
      }
    }
  }

  const score = den > 0 ? num / den : 20.0;
  let condition = 'Normal';
  if (score < 35) {
    condition = 'Normal';
  } else if (inclusiveWarning) {
    condition = score <= 65 ? 'Warning' : 'Critical';
  } else {
    condition = score < 65 ? 'Warning' : 'Critical';
  }

  return { condition, score, fired, cm, tm, vm };
}

function getMaintenanceText(condition) {
  switch (condition) {
    case 'Normal':
      return 'Motor operating within normal parameters. Continue standard routine inspection schedule.';
    case 'Warning':
      return 'Check the motor and schedule maintenance. Abnormal thermal/mechanical load detected.';
    case 'Critical':
      return 'Stop motor and inspect immediately! High danger of stator winding burn-out or bearing seizure.';
    default:
      return 'Diagnostic state pending.';
  }
}

// 12 Test Cases from Milestone 3 Phase 4
const TEST_CASES = [
  { id: 1, current: 3.0, temp: 30, vib: 1.0 },
  { id: 2, current: 5.5, temp: 42, vib: 2.0 },
  { id: 3, current: 7.5, temp: 50, vib: 3.0 },
  { id: 4, current: 10.0, temp: 60, vib: 4.0 },
  { id: 5, current: 12.5, temp: 68, vib: 4.2 },
  { id: 6, current: 14.0, temp: 72, vib: 5.5 },
  { id: 7, current: 15.5, temp: 80, vib: 6.5 },
  { id: 8, current: 17.0, temp: 88, vib: 7.8 },
  { id: 9, current: 18.5, temp: 95, vib: 9.0 },
  { id: 10, current: 19.5, temp: 98, vib: 9.8 },
  { id: 11, current: 8.0, temp: 90, vib: 8.0 },
  { id: 12, current: 4.0, temp: 85, vib: 7.0 }
];

// Genetic Programming Convergence Data (Reproduction of Seed 42 run)
const GP_HISTORY = [
  0.7833, 0.8000, 0.8556, 0.8556, 0.8556, 0.8556, 0.8667, 0.8667, 0.8667, 0.8667,
  0.8667, 0.8667, 0.8778, 0.8778, 0.8778, 0.8778, 0.8778, 0.8778, 0.8778, 0.8944,
  0.8944, 0.8944, 0.8944, 0.8944, 0.8944
];
const GP_INITIAL_FITNESS = 0.7222;

// DOM Elements
const currentSlider = document.getElementById('currentSlider');
const tempSlider = document.getElementById('tempSlider');
const vibSlider = document.getElementById('vibSlider');

const currentValDisplay = document.getElementById('currentValDisplay');
const tempValDisplay = document.getElementById('tempValDisplay');
const vibValDisplay = document.getElementById('vibValDisplay');

const inclusiveWarningToggle = document.getElementById('inclusiveWarningToggle');
const healthScoreDisplay = document.getElementById('healthScoreDisplay');
const gaugeArc = document.getElementById('gaugeArc');
const conditionBanner = document.getElementById('conditionBanner');
const prescriptionText = document.getElementById('prescriptionText');
const firedRuleCount = document.getElementById('firedRuleCount');
const firedRulesBody = document.getElementById('firedRulesBody');
const testSuiteTableBody = document.getElementById('testSuiteTableBody');
const btnResetInputs = document.getElementById('btnResetInputs');
const btnExportCsv = document.getElementById('btnExportCsv');
const btnRunBatchTests = document.getElementById('btnRunBatchTests');

// Canvases
const motorCanvas = document.getElementById('motorCanvas');
const motorCtx = motorCanvas.getContext('2d');
const curveCurrentCanvas = document.getElementById('curveCurrentCanvas');
const curveTempCanvas = document.getElementById('curveTempCanvas');
const curveVibCanvas = document.getElementById('curveVibCanvas');
const gpCanvas = document.getElementById('gpCanvas');

// Animation variables
let animationId = null;
let motorAngle = 0;
let lastTimestamp = 0;

// State
let currentState = {
  current: 12.5,
  temp: 68.0,
  vib: 4.2,
  inclusiveWarning: true
};

// Initialize App
function initApp() {
  setupEventListeners();
  populateTestSuiteTable();
  updateSimulation();
  drawGpChart();
  startMotorAnimation();
}

function setupEventListeners() {
  currentSlider.addEventListener('input', (e) => {
    currentState.current = parseFloat(e.target.value);
    updateSimulation();
  });

  tempSlider.addEventListener('input', (e) => {
    currentState.temp = parseFloat(e.target.value);
    updateSimulation();
  });

  vibSlider.addEventListener('input', (e) => {
    currentState.vib = parseFloat(e.target.value);
    updateSimulation();
  });

  inclusiveWarningToggle.addEventListener('change', (e) => {
    currentState.inclusiveWarning = e.target.checked;
    updateSimulation();
    populateTestSuiteTable();
  });

  btnResetInputs.addEventListener('click', () => {
    setInputs(12.5, 68.0, 4.2);
  });

  btnExportCsv.addEventListener('click', exportResultsCsv);

  btnRunBatchTests.addEventListener('click', () => {
    let idx = 0;
    const interval = setInterval(() => {
      if (idx < TEST_CASES.length) {
        const t = TEST_CASES[idx];
        setInputs(t.current, t.temp, t.vib);
        highlightTableRow(t.id);
        idx++;
      } else {
        clearInterval(interval);
      }
    }, 600);
  });
}

function setInputs(c, t, v) {
  currentState.current = c;
  currentState.temp = t;
  currentState.vib = v;
  currentSlider.value = c;
  tempSlider.value = t;
  vibSlider.value = v;
  updateSimulation();
}

function updateSimulation() {
  const { current, temp, vib, inclusiveWarning } = currentState;

  // Update text values
  currentValDisplay.textContent = current.toFixed(1);
  tempValDisplay.textContent = temp.toFixed(1);
  vibValDisplay.textContent = vib.toFixed(1);

  // Compute fuzzy output
  const res = fuzzyPredict(current, temp, vib, inclusiveWarning);

  // Update membership chips
  updateMembershipChips('current', res.cm);
  updateMembershipChips('temp', res.tm);
  updateMembershipChips('vib', res.vm);

  // Update health score display & radial gauge
  healthScoreDisplay.textContent = res.score.toFixed(2);
  updateRadialGauge(res.score, res.condition);

  // Update condition banner & maintenance prescription
  updateConditionBanner(res.condition, res.score);
  prescriptionText.textContent = getMaintenanceText(res.condition);

  // Update fired rules table
  updateFiredRules(res.fired);

  // Update status pill
  updateStatusPill(res.condition);

  // Redraw membership curves with cursor
  drawMembershipCurves(current, temp, vib, res.cm, res.tm, res.vm);
}

function updateMembershipChips(type, mems) {
  for (const lvl of ['low', 'med', 'high']) {
    const valKey = lvl === 'low' ? 'Low' : (lvl === 'med' ? 'Medium' : 'High');
    const val = mems[valKey];
    const chip = document.getElementById(`chip_${type}_${lvl}`);
    const chipVal = document.getElementById(`val_${type}_${lvl}`);
    if (chipVal) chipVal.textContent = val.toFixed(2);
    if (chip) {
      if (val > 0.05) {
        chip.classList.add('active');
      } else {
        chip.classList.remove('active');
      }
    }
  }
}

function updateRadialGauge(score, condition) {
  const circumference = 2 * Math.PI * 42; // ~263.89
  const offset = circumference - (score / 100) * circumference;
  gaugeArc.style.strokeDashoffset = offset;

  if (score < 35) {
    gaugeArc.style.stroke = 'var(--status-normal)';
    healthScoreDisplay.style.color = 'var(--status-normal)';
  } else if (condition === 'Warning') {
    gaugeArc.style.stroke = 'var(--status-warning)';
    healthScoreDisplay.style.color = 'var(--status-warning)';
  } else {
    gaugeArc.style.stroke = 'var(--status-critical)';
    healthScoreDisplay.style.color = 'var(--status-critical)';
  }
}

function updateConditionBanner(condition, score) {
  conditionBanner.className = 'condition-badge-banner';
  if (condition === 'Normal') {
    conditionBanner.classList.add('condition-normal');
    conditionBanner.textContent = 'NORMAL OPERATING CONDITION';
  } else if (condition === 'Warning') {
    conditionBanner.classList.add('condition-warning');
    conditionBanner.textContent = score === 65.0 ? 'WARNING (PPT TEST CASE)' : 'WARNING - MAINTENANCE REQUIRED';
  } else {
    conditionBanner.classList.add('condition-critical');
    conditionBanner.textContent = 'CRITICAL FAULT - STOP MOTOR';
  }
}

function updateStatusPill(condition) {
  const pill = document.getElementById('systemHealthPill');
  const txt = document.getElementById('systemStatusText');
  if (condition === 'Normal') {
    pill.style.borderColor = 'rgba(16, 185, 129, 0.4)';
    pill.style.color = 'var(--status-normal)';
    txt.textContent = 'System Healthy';
  } else if (condition === 'Warning') {
    pill.style.borderColor = 'rgba(245, 158, 11, 0.4)';
    pill.style.color = 'var(--status-warning)';
    txt.textContent = 'Advisory Warning';
  } else {
    pill.style.borderColor = 'rgba(239, 68, 68, 0.4)';
    pill.style.color = 'var(--status-critical)';
    txt.textContent = 'Critical Alarm Active';
  }
}

function updateFiredRules(fired) {
  firedRuleCount.textContent = fired.length;
  firedRulesBody.innerHTML = '';

  fired.forEach(r => {
    const tr = document.createElement('tr');
    const badgeClass = r.label === 'Normal' ? 'badge-normal' : (r.label === 'Warning' ? 'badge-warning' : 'badge-critical');
    tr.innerHTML = `
      <td><strong>I:</strong>${r.current} &bull; <strong>T:</strong>${r.temp} &bull; <strong>V:</strong>${r.vib}</td>
      <td><span class="rule-weight-badge">${r.weight.toFixed(3)}</span></td>
      <td><span class="test-badge ${badgeClass}">${r.label} (${r.score})</span></td>
    `;
    firedRulesBody.appendChild(tr);
  });
}

function populateTestSuiteTable() {
  testSuiteTableBody.innerHTML = '';
  TEST_CASES.forEach(tc => {
    // Note: Test 5 in strict mode gives Critical, in PPT mode gives Warning
    const res = fuzzyPredict(tc.current, tc.temp, tc.vib, currentState.inclusiveWarning);
    const tr = document.createElement('tr');
    tr.id = `testRow_${tc.id}`;
    if (tc.id === 5) tr.classList.add('highlight-row');

    const badgeClass = res.condition === 'Normal' ? 'badge-normal' : (res.condition === 'Warning' ? 'badge-warning' : 'badge-critical');
    const pptNote = tc.id === 5 ? ' (PPT)' : '';

    tr.innerHTML = `
      <td><strong>#${tc.id.toString().padStart(2, '0')}</strong></td>
      <td>${tc.current.toFixed(1)}</td>
      <td>${tc.temp.toFixed(1)}</td>
      <td>${tc.vib.toFixed(1)}</td>
      <td><strong>${res.score.toFixed(2)}</strong></td>
      <td><span class="test-badge ${badgeClass}">${res.condition}${pptNote}</span></td>
      <td><button class="btn" style="padding: 0.15rem 0.5rem; font-size: 0.7rem;" onclick="loadTestCase(${tc.id})">Load</button></td>
    `;

    tr.addEventListener('click', (e) => {
      if (e.target.tagName !== 'BUTTON') {
        loadTestCase(tc.id);
      }
    });

    testSuiteTableBody.appendChild(tr);
  });
}

window.loadTestCase = function(id) {
  const tc = TEST_CASES.find(t => t.id === id);
  if (tc) {
    setInputs(tc.current, tc.temp, tc.vib);
    highlightTableRow(id);
  }
};

function highlightTableRow(id) {
  document.querySelectorAll('#testSuiteTableBody tr').forEach(r => r.classList.remove('highlight-row'));
  const row = document.getElementById(`testRow_${id}`);
  if (row) row.classList.add('highlight-row');
}

// 2. Membership Curves Canvas Plotting
function drawMembershipCurves(curVal, tempVal, vibVal, cm, tm, vm) {
  drawSingleCurve(curveCurrentCanvas, [0, 20], [
    { name: 'Low', pts: [[0, 1], [5, 1], [10, 0]], color: '#38bdf8' },
    { name: 'Med', pts: [[5, 0], [10, 1], [15, 0]], color: '#f59e0b' },
    { name: 'High', pts: [[10, 0], [15, 1], [20, 1]], color: '#ef4444' }
  ], curVal, 'A');

  drawSingleCurve(curveTempCanvas, [25, 100], [
    { name: 'Low', pts: [[25, 1], [35, 1], [50, 0]], color: '#38bdf8' },
    { name: 'Med', pts: [[40, 0], [62.5, 1], [85, 0]], color: '#f59e0b' },
    { name: 'High', pts: [[75, 0], [90, 1], [100, 1]], color: '#ef4444' }
  ], tempVal, '°C');

  drawSingleCurve(curveVibCanvas, [0, 10], [
    { name: 'Low', pts: [[0, 1], [2, 1], [4, 0]], color: '#38bdf8' },
    { name: 'Med', pts: [[2.5, 0], [5, 1], [7.5, 0]], color: '#f59e0b' },
    { name: 'High', pts: [[6, 0], [8, 1], [10, 1]], color: '#ef4444' }
  ], vibVal, 'mm/s');
}

function drawSingleCurve(canvas, xRange, sets, currentVal, unit) {
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const padL = 20;
  const padR = 10;
  const padT = 10;
  const padB = 20;

  ctx.clearRect(0, 0, w, h);

  // Background grid
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padL, h - padB);
  ctx.lineTo(w - padR, h - padB);
  ctx.moveTo(padL, padT);
  ctx.lineTo(padL, h - padB);
  ctx.stroke();

  const mapX = (x) => padL + ((x - xRange[0]) / (xRange[1] - xRange[0])) * (w - padL - padR);
  const mapY = (y) => (h - padB) - y * (h - padT - padB);

  // Draw curves
  sets.forEach(s => {
    ctx.strokeStyle = s.color;
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    s.pts.forEach((pt, idx) => {
      const px = mapX(pt[0]);
      const py = mapY(pt[1]);
      if (idx === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.stroke();
  });

  // Draw current value cursor
  const curX = mapX(currentVal);
  ctx.strokeStyle = '#f8fafc';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([3, 3]);
  ctx.beginPath();
  ctx.moveTo(curX, padT);
  ctx.lineTo(curX, h - padB);
  ctx.stroke();
  ctx.setLineDash([]);

  // Marker dot
  ctx.fillStyle = '#38bdf8';
  ctx.beginPath();
  ctx.arc(curX, h - padB, 3.5, 0, Math.PI * 2);
  ctx.fill();

  // Labels
  ctx.fillStyle = '#64748b';
  ctx.font = '9px monospace';
  ctx.fillText(xRange[0] + unit, padL, h - 5);
  ctx.fillText(xRange[1] + unit, w - padR - 25, h - 5);
}

// 3. Cyber-Physical Animated Motor Canvas
function startMotorAnimation() {
  function render(timestamp) {
    if (!lastTimestamp) lastTimestamp = timestamp;
    const dt = (timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;

    drawMotor(dt);
    animationId = requestAnimationFrame(render);
  }
  animationId = requestAnimationFrame(render);
}

function drawMotor(dt) {
  const w = motorCanvas.width;
  const h = motorCanvas.height;
  const ctx = motorCtx;
  const { current, temp, vib } = currentState;

  // RPM estimation based on current
  const baseRpm = Math.max(300, Math.min(2850, 1500 - (current - 10) * 45));
  document.getElementById('rpmValue').textContent = Math.round(baseRpm);
  document.getElementById('vibAmpValue').textContent = vib.toFixed(2);

  // Angle step
  motorAngle += (baseRpm / 60) * Math.PI * 2 * dt;

  // Vibration jitter
  const vibAmplitude = (vib / 10) * 4.5;
  const shakeX = (Math.random() - 0.5) * vibAmplitude;
  const shakeY = (Math.random() - 0.5) * vibAmplitude;

  ctx.clearRect(0, 0, w, h);
  ctx.save();
  ctx.translate(w / 2 + shakeX, h / 2 + shakeY);

  // Thermal glow effect behind motor
  const tempRatio = Math.max(0, Math.min(1, (temp - 25) / 75));
  let glowColor = 'rgba(56, 189, 248, 0.05)';
  if (temp > 65) {
    glowColor = `rgba(239, 68, 68, ${0.15 + tempRatio * 0.35})`;
  } else if (temp > 45) {
    glowColor = `rgba(245, 158, 11, ${0.1 + tempRatio * 0.2})`;
  }

  const grad = ctx.createRadialGradient(0, 0, 40, 0, 0, 140);
  grad.addColorStop(0, glowColor);
  grad.addColorStop(1, 'transparent');
  ctx.fillStyle = grad;
  ctx.fillRect(-w / 2, -h / 2, w, h);

  // 1. Motor Mount Base
  ctx.fillStyle = '#1e293b';
  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(-150, 60, 300, 25, 4);
  ctx.fill();
  ctx.stroke();

  // Mounting bolts
  ctx.fillStyle = '#64748b';
  [-125, -75, 75, 125].forEach(bx => {
    ctx.fillRect(bx - 5, 70, 10, 8);
  });

  // 2. Stator Main Housing Frame
  const statorGrad = ctx.createLinearGradient(0, -65, 0, 65);
  statorGrad.addColorStop(0, '#334155');
  statorGrad.addColorStop(0.5, '#1e293b');
  statorGrad.addColorStop(1, '#0f172a');
  ctx.fillStyle = statorGrad;
  ctx.beginPath();
  ctx.roundRect(-120, -55, 200, 115, 8);
  ctx.fill();
  ctx.stroke();

  // Cooling Fins on Stator Frame
  ctx.strokeStyle = '#475569';
  ctx.lineWidth = 3;
  for (let fx = -110; fx <= 70; fx += 16) {
    ctx.beginPath();
    ctx.moveTo(fx, -54);
    ctx.lineTo(fx, 58);
    ctx.stroke();
  }

  // 3. Terminal Box on top
  ctx.fillStyle = '#0f172a';
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.roundRect(-40, -82, 50, 27, 4);
  ctx.fill();
  ctx.stroke();

  // Cable gland
  ctx.fillStyle = '#475569';
  ctx.fillRect(-22, -90, 14, 8);

  // 4. Front Bearing Housing & Drive End
  ctx.fillStyle = '#1e293b';
  ctx.strokeStyle = '#475569';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(80, 2, 42, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // 5. Rotating Drive Shaft extending from bearing
  ctx.fillStyle = '#94a3b8';
  ctx.strokeStyle = '#cbd5e1';
  ctx.lineWidth = 1.5;
  ctx.fillRect(80, -9, 85, 18);
  ctx.strokeRect(80, -9, 85, 18);

  // Keyway notch rotating on shaft
  const keyX = 110 + Math.cos(motorAngle) * 20;
  ctx.fillStyle = '#334155';
  ctx.fillRect(keyX, -7, 6, 14);

  // 6. Non-Drive End Cooling Fan Cowl
  ctx.fillStyle = '#0f172a';
  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(-155, -45, 35, 95, 6);
  ctx.fill();
  ctx.stroke();

  // Fan grille slots
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 2;
  [-30, -15, 0, 15, 30].forEach(gy => {
    ctx.beginPath();
    ctx.moveTo(-150, gy);
    ctx.lineTo(-125, gy);
    ctx.stroke();
  });

  // 7. Status Warning Strobe Light
  let strobeCol = '#10b981';
  if (temp > 65 || vib > 6 || current > 14) strobeCol = '#ef4444';
  else if (temp > 50 || vib > 3.5 || current > 11) strobeCol = '#f59e0b';

  ctx.fillStyle = strobeCol;
  ctx.shadowColor = strobeCol;
  ctx.shadowBlur = 15;
  ctx.beginPath();
  ctx.arc(105, -35, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowBlur = 0;

  ctx.restore();
}

// 4. Genetic Programming Optimization Chart
function drawGpChart() {
  const ctx = gpCanvas.getContext('2d');
  const w = gpCanvas.width;
  const h = gpCanvas.height;
  const padL = 45;
  const padR = 25;
  const padT = 25;
  const padB = 30;

  ctx.clearRect(0, 0, w, h);

  // Y range: 0.65 to 0.95
  const minY = 0.65;
  const maxY = 0.95;

  const mapX = (g) => padL + ((g - 1) / 24) * (w - padL - padR);
  const mapY = (val) => (h - padB) - ((val - minY) / (maxY - minY)) * (h - padT - padB);

  // Grid lines
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  for (let yv = 0.70; yv <= 0.95; yv += 0.05) {
    const ypos = mapY(yv);
    ctx.beginPath();
    ctx.moveTo(padL, ypos);
    ctx.lineTo(w - padR, ypos);
    ctx.stroke();

    ctx.fillStyle = '#64748b';
    ctx.font = '10px monospace';
    ctx.fillText(`${(yv * 100).toFixed(0)}%`, 10, ypos + 4);
  }

  // Generation X-axis marks
  [1, 5, 10, 15, 20, 25].forEach(gen => {
    const xpos = mapX(gen);
    ctx.fillStyle = '#64748b';
    ctx.font = '10px monospace';
    ctx.fillText(`G${gen}`, xpos - 10, h - 10);
  });

  // Initial baseline line
  const initY = mapY(GP_INITIAL_FITNESS);
  ctx.strokeStyle = '#f43f5e';
  ctx.lineWidth = 1.5;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(padL, initY);
  ctx.lineTo(w - padR, initY);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.fillStyle = '#f43f5e';
  ctx.font = '10px sans-serif';
  ctx.fillText('Initial Baseline (72.2%)', padL + 10, initY - 6);

  // GP Convergence Area Fill
  const areaGrad = ctx.createLinearGradient(0, padT, 0, h - padB);
  areaGrad.addColorStop(0, 'rgba(56, 189, 248, 0.25)');
  areaGrad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');
  ctx.fillStyle = areaGrad;

  ctx.beginPath();
  ctx.moveTo(mapX(1), mapY(GP_HISTORY[0]));
  for (let i = 1; i < GP_HISTORY.length; i++) {
    ctx.lineTo(mapX(i + 1), mapY(GP_HISTORY[i]));
  }
  ctx.lineTo(mapX(25), h - padB);
  ctx.lineTo(mapX(1), h - padB);
  ctx.closePath();
  ctx.fill();

  // GP Convergence Curve
  ctx.strokeStyle = '#38bdf8';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  for (let i = 0; i < GP_HISTORY.length; i++) {
    const gx = mapX(i + 1);
    const gy = mapY(GP_HISTORY[i]);
    if (i === 0) ctx.moveTo(gx, gy);
    else ctx.lineTo(gx, gy);
  }
  ctx.stroke();

  // Point dots
  for (let i = 0; i < GP_HISTORY.length; i++) {
    const gx = mapX(i + 1);
    const gy = mapY(GP_HISTORY[i]);
    ctx.fillStyle = i === 19 ? '#22c55e' : '#38bdf8';
    ctx.beginPath();
    ctx.arc(gx, gy, i === 19 ? 5.5 : 3, 0, Math.PI * 2);
    ctx.fill();
  }

  // Peak Annotation
  const peakX = mapX(20);
  const peakY = mapY(GP_HISTORY[19]);
  ctx.fillStyle = '#22c55e';
  ctx.font = 'bold 11px sans-serif';
  ctx.fillText('Peak 89.4% (Gen 20)', peakX - 55, peakY - 10);
}

// 5. CSV Exporter
function exportResultsCsv() {
  let csv = 'Test,Current (A),Temperature (°C),Vibration (mm/s),Health Score,Condition\n';
  TEST_CASES.forEach(tc => {
    const res = fuzzyPredict(tc.current, tc.temp, tc.vib, currentState.inclusiveWarning);
    csv += `${tc.id},${tc.current.toFixed(1)},${tc.temp.toFixed(0)},${tc.vib.toFixed(1)},${res.score.toFixed(2)},${res.condition}\n`;
  });

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', 'phase4_test_results.csv');
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Run initialization on load
window.addEventListener('DOMContentLoaded', initApp);
