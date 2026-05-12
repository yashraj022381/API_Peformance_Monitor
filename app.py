import threading
from flask import Flask
from database import init_db
from checker import background_monitor
from routes import register_routes

app = Flask(__name__)

"""HTML_PAGE = <!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>API Performance Monitor</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
/* ── Fonts & Reset ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
 
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
 
:root {
  --bg:       #0a0e1a;
  --surface:  #111827;
  --card:     #161f2e;
  --border:   #1e2d42;
  --accent:   #00d9ff;
  --green:    #00ff88;
  --red:      #ff3b5c;
  --yellow:   #ffc847;
  --text:     #e2e8f0;
  --muted:    #64748b;
  --mono:     'Space Mono', monospace;
  --sans:     'DM Sans', sans-serif;
}
 
body {
  font-family: var(--sans);
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}
 
/* Animated grid background */
body::before {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image:
    linear-gradient(rgba(0,217,255,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,217,255,.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}
 
/* ── Header ────────────────────────────────────────────────────────────── */
header {
  position: relative; z-index: 10;
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.4rem 2.5rem;
  border-bottom: 1px solid var(--border);
  background: rgba(10,14,26,.8);
  backdrop-filter: blur(12px);
}
 
.logo {
  display: flex; align-items: center; gap: .75rem;
  font-family: var(--mono); font-size: 1rem; letter-spacing: .05em;
  color: var(--accent);
}
.logo-dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%,100%{ opacity:1; transform:scale(1); }
  50%    { opacity:.5; transform:scale(1.3); }
}
 
.status-bar {
  font-family: var(--mono); font-size: .75rem; color: var(--muted);
  display: flex; align-items: center; gap: 1.5rem;
}
#clock { color: var(--accent); }
.live-dot {
  width:8px; height:8px; border-radius:50%; background:var(--green);
  box-shadow: 0 0 6px var(--green); animation: pulse 1.5s infinite;
}
 
/* ── Main Layout ───────────────────────────────────────────────────────── */
main {
  position: relative; z-index: 5;
  max-width: 1400px; margin: 0 auto;
  padding: 2rem 2rem 4rem;
}
 
h2 {
  font-family: var(--mono);
  font-size: .7rem; letter-spacing: .15em; text-transform: uppercase;
  color: var(--muted); margin-bottom: 1rem;
}
 
/* ── Stat Cards ────────────────────────────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem; margin-bottom: 2.5rem;
}
 
.stat-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.4rem 1.6rem;
  position: relative; overflow: hidden;
  animation: fadeUp .5s ease both;
}
.stat-card::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 2px; background: var(--accent);
}
.stat-card.green::after { background: var(--green); }
.stat-card.red::after   { background: var(--red); }
.stat-card.yellow::after{ background: var(--yellow); }
 
.stat-label {
  font-size: .72rem; color: var(--muted); letter-spacing: .08em;
  text-transform: uppercase; font-family: var(--mono); margin-bottom: .5rem;
}
.stat-value {
  font-family: var(--mono); font-size: 2rem; font-weight: 700;
  line-height: 1; color: var(--text);
}
.stat-value.accent { color: var(--accent); }
.stat-value.green  { color: var(--green); }
.stat-value.red    { color: var(--red); }
.stat-value.yellow { color: var(--yellow); }
 
@keyframes fadeUp {
  from { opacity:0; transform:translateY(16px); }
  to   { opacity:1; transform:translateY(0); }
}
 
/* ── Section Grid ──────────────────────────────────────────────────────── */
.section-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 1.5rem; margin-bottom: 2rem;
}
@media (max-width: 1000px) { .section-grid { grid-template-columns: 1fr; } }
 
/* ── Panel ─────────────────────────────────────────────────────────────── */
.panel {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 1.6rem;
}
 
/* ── API Table ─────────────────────────────────────────────────────────── */
.api-table { width:100%; border-collapse: collapse; }
.api-table th {
  font-family: var(--mono); font-size: .65rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--muted); text-align: left;
  padding: .5rem .75rem; border-bottom: 1px solid var(--border);
}
.api-table td {
  padding: .85rem .75rem;
  font-size: .88rem;
  border-bottom: 1px solid rgba(30,45,66,.5);
  vertical-align: middle;
}
.api-table tr:last-child td { border-bottom: none; }
.api-table tr { transition: background .2s; cursor: pointer; }
.api-table tr:hover td { background: rgba(0,217,255,.04); }
.api-table tr.selected td { background: rgba(0,217,255,.08); }
 
.api-name {
  font-weight: 500; color: var(--text); display: block;
}
.api-url {
  font-family: var(--mono); font-size: .7rem; color: var(--muted);
}
.badge {
  display: inline-flex; align-items: center; gap: .35rem;
  padding: .25rem .65rem; border-radius: 20px;
  font-family: var(--mono); font-size: .72rem; font-weight: 700;
}
.badge.up   { background: rgba(0,255,136,.12); color: var(--green); }
.badge.down { background: rgba(255,59,92,.12);  color: var(--red); }
.badge.unk  { background: rgba(100,116,139,.12); color: var(--muted); }
 
.ms-value { font-family: var(--mono); font-size: .85rem; }
.ms-fast  { color: var(--green); }
.ms-ok    { color: var(--yellow); }
.ms-slow  { color: var(--red); }
 
.btn-check {
  background: transparent; border: 1px solid var(--border);
  color: var(--accent); padding: .3rem .7rem; border-radius: 6px;
  font-family: var(--mono); font-size: .7rem; cursor: pointer;
  transition: all .2s;
}
.btn-check:hover { background: var(--accent); color: var(--bg); }
.btn-del {
  background: transparent; border: 1px solid transparent;
  color: var(--muted); padding: .3rem .6rem; border-radius: 6px;
  font-family: var(--mono); font-size: .75rem; cursor: pointer;
  transition: all .2s; margin-left: .3rem;
}
.btn-del:hover { border-color: var(--red); color: var(--red); }
 
/* ── Add API Form ──────────────────────────────────────────────────────── */
.add-form { display: flex; flex-direction: column; gap: .9rem; }
.form-group label {
  display: block; font-size: .72rem; font-family: var(--mono);
  color: var(--muted); letter-spacing: .08em; margin-bottom: .4rem;
  text-transform: uppercase;
}
.form-group input {
  width: 100%; background: var(--surface); border: 1px solid var(--border);
  color: var(--text); padding: .65rem .9rem; border-radius: 8px;
  font-family: var(--mono); font-size: .82rem;
  transition: border-color .2s;
}
.form-group input:focus {
  outline: none; border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(0,217,255,.1);
}
.btn-add {
  background: var(--accent); color: var(--bg);
  border: none; padding: .75rem; border-radius: 8px;
  font-family: var(--mono); font-weight: 700; font-size: .82rem;
  cursor: pointer; transition: opacity .2s; letter-spacing: .05em;
}
.btn-add:hover { opacity: .85; }
.form-msg { font-size: .78rem; margin-top: .4rem; min-height: 1.2em; }
.form-msg.ok  { color: var(--green); }
.form-msg.err { color: var(--red); }
 
/* ── Chart Panel ───────────────────────────────────────────────────────── */
.chart-panel {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 1.6rem; margin-bottom: 1.5rem;
}
.chart-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1.2rem;
}
.chart-title { font-family: var(--mono); font-size: .82rem; color: var(--accent); }
.chart-subtitle { font-size: .72rem; color: var(--muted); margin-top: .2rem; }
 
#responseChart { max-height: 220px; }
 
/* ── Loading ───────────────────────────────────────────────────────────── */
.spinner {
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid var(--border); border-top-color: var(--accent);
  border-radius: 50%; animation: spin .6s linear infinite;
}
@keyframes spin { to { transform:rotate(360deg); } }
 
.empty { text-align:center; padding: 3rem 1rem; color: var(--muted);
  font-size: .85rem; }
 
/* ── Toast ─────────────────────────────────────────────────────────────── */
#toast {
  position: fixed; bottom: 2rem; right: 2rem; z-index: 9999;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 10px; padding: .9rem 1.4rem;
  font-family: var(--mono); font-size: .8rem;
  transform: translateY(120%); transition: transform .3s ease;
  box-shadow: 0 8px 32px rgba(0,0,0,.4);
}
#toast.show { transform: translateY(0); }
</style>
</head>
<body>
 
<header>
  <div class="logo">
    <div class="logo-dot"></div>
    API PERFORMANCE MONITOR
  </div>
  <div class="status-bar">
    <span id="clock">--:--:--</span>
    <div class="live-dot"></div>
    <span>LIVE</span>
  </div>
</header>
 
<main>
 
  <!-- ── Global Stats ── -->
  <h2>// Overview</h2>
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">APIs Monitored</div>
      <div class="stat-value accent" id="stat-apis">–</div>
    </div>
    <div class="stat-card green">
      <div class="stat-label">Success Rate (1h)</div>
      <div class="stat-value green" id="stat-success">–%</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Avg Response</div>
      <div class="stat-value" id="stat-avg">–ms</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Checks</div>
      <div class="stat-value" id="stat-checks">–</div>
    </div>
    <div class="stat-card red">
      <div class="stat-label">Failing Now</div>
      <div class="stat-value red" id="stat-failing">–</div>
    </div>
  </div>
 
  <!-- ── Response Time Chart ── -->
  <div class="chart-panel">
    <div class="chart-header">
      <div>
        <div class="chart-title">RESPONSE TIME HISTORY</div>
        <div class="chart-subtitle" id="chart-label">Click an API below to see its history</div>
      </div>
      <div id="chart-spinner" style="display:none"><div class="spinner"></div></div>
    </div>
    <canvas id="responseChart"></canvas>
  </div>
 
  <!-- ── Main Grid ── -->
  <div class="section-grid">
 
    <!-- API List -->
    <div class="panel">
      <h2>// Monitored APIs</h2>
      <div id="api-list-wrap">
        <div class="empty"><div class="spinner"></div></div>
      </div>
    </div>
 
    <!-- Add API -->
    <div class="panel">
      <h2>// Add New API</h2>
      <div class="add-form">
        <div class="form-group">
          <label>API Name</label>
          <input id="f-name" type="text" placeholder="e.g. My Weather API">
        </div>
        <div class="form-group">
          <label>URL</label>
          <input id="f-url" type="url" placeholder="https://api.example.com/health">
        </div>
        <div class="form-group">
          <label>Check Interval (seconds)</label>
          <input id="f-interval" type="number" value="30" min="10" max="3600">
        </div>
        <button class="btn-add" onclick="addApi()">+ ADD API</button>
        <div id="form-msg" class="form-msg"></div>
      </div>
    </div>
 
  </div>
 
</main>
 
<div id="toast"></div>
 
<script>
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Think of this JavaScript like the REMOTE CONTROL
// for our dashboard. It:
//  1. Asks the Flask server for data (fetch calls)
//  2. Updates the page with that data
//  3. Draws the charts
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
let chart = null;
let selectedApiId = null;
let refreshTimer = null;
 
// ── Clock ─────────────────────────────────────────────
function updateClock() {
  document.getElementById('clock').textContent =
    new Date().toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();
 
// ── Toast notification ─────────────────────────────────
function toast(msg, duration = 2500) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}
 
// ── Helpers ────────────────────────────────────────────
function msClass(ms) {
  if (!ms) return '';
  if (ms < 300) return 'ms-fast';
  if (ms < 800) return 'ms-ok';
  return 'ms-slow';
}
 
// ── Load Global Stats ──────────────────────────────────
async function loadStats() {
  const d = await fetch('/api/stats').then(r => r.json());
  document.getElementById('stat-apis').textContent    = d.total_apis;
  document.getElementById('stat-success').textContent = d.success_rate + '%';
  document.getElementById('stat-avg').textContent     = d.avg_response + 'ms';
  document.getElementById('stat-checks').textContent  = d.total_checks.toLocaleString();
  document.getElementById('stat-failing').textContent = d.failing_now;
}
 
// ── Load API Table ─────────────────────────────────────
async function loadApis() {
  const summary = await fetch('/api/summary').then(r => r.json());
  const wrap    = document.getElementById('api-list-wrap');
 
  if (!summary.length) {
    wrap.innerHTML = '<div class="empty">No APIs yet – add one →</div>';
    return;
  }
 
  const rows = summary.map(a => {
    const badge = a.last_success === null
      ? `<span class="badge unk">UNKNOWN</span>`
      : a.last_success
        ? `<span class="badge up">▲ UP</span>`
        : `<span class="badge down">▼ DOWN</span>`;
 
    const ms    = a.avg_ms
      ? `<span class="ms-value ${msClass(a.avg_ms)}">${a.avg_ms}ms</span>`
      : '<span style="color:var(--muted)">–</span>';
 
    const uptime = a.uptime_pct !== null
      ? `${a.uptime_pct}%`
      : '–';
 
    return `
      <tr onclick="selectApi(${a.id}, '${a.name}')"
          id="row-${a.id}" ${selectedApiId===a.id ? 'class="selected"' : ''}>
        <td>
          <span class="api-name">${a.name}</span>
          <span class="api-url">${a.url}</span>
        </td>
        <td>${badge}</td>
        <td>${ms}</td>
        <td style="font-family:var(--mono);font-size:.78rem">${uptime}</td>
        <td>
          <button class="btn-check" onclick="event.stopPropagation();manualCheck(${a.id})">CHECK</button>
          <button class="btn-del"   onclick="event.stopPropagation();deleteApi(${a.id})">✕</button>
        </td>
      </tr>`;
  }).join('');
 
  wrap.innerHTML = `
    <table class="api-table">
      <thead>
        <tr>
          <th>API</th><th>Status</th>
          <th>Avg Speed</th><th>Uptime</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}
 
// ── Select API → show chart ────────────────────────────
function selectApi(id, name) {
  selectedApiId = id;
  document.querySelectorAll('.api-table tr').forEach(r => r.classList.remove('selected'));
  const row = document.getElementById(`row-${id}`);
  if (row) row.classList.add('selected');
  loadChart(id, name);
}
 
// ── Draw Chart ─────────────────────────────────────────
async function loadChart(id, name) {
  document.getElementById('chart-label').textContent = `Showing last 40 checks for: ${name}`;
  document.getElementById('chart-spinner').style.display = 'flex';
 
  const history = await fetch(`/api/history/${id}?limit=40`).then(r => r.json());
  document.getElementById('chart-spinner').style.display = 'none';
 
  const labels = history.map(h =>
    new Date(h.checked_at + 'Z').toLocaleTimeString('en-US', { hour12: false })
  );
  const data = history.map(h => h.response_ms);
  const colors = history.map(h =>
    h.success ? 'rgba(0,255,136,.8)' : 'rgba(255,59,92,.8)'
  );
 
  if (chart) chart.destroy();
 
  chart = new Chart(document.getElementById('responseChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Response Time (ms)',
        data,
        backgroundColor: colors,
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.raw ? ctx.raw + ' ms' : 'Failed'}`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#64748b', font: { family: 'Space Mono', size: 10 }, maxRotation: 45 },
          grid: { color: 'rgba(30,45,66,.5)' }
        },
        y: {
          ticks: { color: '#64748b', font: { family: 'Space Mono', size: 10 } },
          grid: { color: 'rgba(30,45,66,.5)' },
          title: { display: true, text: 'ms', color: '#64748b',
                   font: { family: 'Space Mono', size: 11 } }
        }
      }
    }
  });
}
 
// ── Manual Check ──────────────────────────────────────
async function manualCheck(id) {
  toast('⏳ Checking...');
  const res = await fetch(`/api/check/${id}`, { method:'POST' }).then(r => r.json());
  if (res.success) {
    toast(`✅ OK – ${res.response_ms}ms`);
  } else {
    toast(`❌ Failed – ${res.error_msg || 'Unknown error'}`);
  }
  refresh();
}
 
// ── Add API ───────────────────────────────────────────
async function addApi() {
  const name     = document.getElementById('f-name').value.trim();
  const url      = document.getElementById('f-url').value.trim();
  const interval = parseInt(document.getElementById('f-interval').value) || 30;
  const msg      = document.getElementById('form-msg');
 
  if (!name || !url) { msg.textContent = '⚠ Name and URL are required'; msg.className = 'form-msg err'; return; }
 
  const res = await fetch('/api/apis', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, url, interval })
  });
  const data = await res.json();
 
  if (res.ok) {
    msg.textContent = '✅ ' + data.message;
    msg.className = 'form-msg ok';
    document.getElementById('f-name').value = '';
    document.getElementById('f-url').value  = '';
    refresh();
  } else {
    msg.textContent = '❌ ' + data.error;
    msg.className = 'form-msg err';
  }
  setTimeout(() => { msg.textContent = ''; }, 3500);
}
 
// ── Delete API ────────────────────────────────────────
async function deleteApi(id) {
  if (!confirm('Remove this API from monitoring?')) return;
  await fetch(`/api/apis/${id}`, { method: 'DELETE' });
  if (selectedApiId === id) selectedApiId = null;
  refresh();
  toast('🗑 Removed');
}
 
// ── Full refresh ──────────────────────────────────────
async function refresh() {
  await Promise.all([ loadStats(), loadApis() ]);
  if (selectedApiId) {
    const row = document.getElementById(`row-${selectedApiId}`);
    const name = row?.querySelector('.api-name')?.textContent || '';
    loadChart(selectedApiId, name);
  }
}
 
// Auto-refresh every 15 seconds
refresh();
setInterval(refresh, 15000);
</script>
</body>
</html>"""

register_routes(app)

if __name__ == "__main__":
    
    init_db()

    t = threading.Thread(target=background_monitor, daemon=True)
    t.start()

    print("\n🚀 Visit: https://localhost:0000\n")
    app.run(debug=True, host="0.0.0.0", use_reloader=False, port=5000)
