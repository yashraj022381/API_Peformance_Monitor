import sqlite3
from flask import jsonify, render_template, request
from database import DB_PATH
from checker  import check_api
from exporter import export_checks_to_csv, export_summary_to_csv

HTML_FILE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>API Performance Monitor</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#070b14;--s1:#0d1424;--s2:#111d30;--s3:#162036;
  --border:#1a2d4a;--border2:#243d5e;
  --cyan:#00e5ff;--green:#00ff9d;--red:#ff3d6b;
  --yellow:#ffcc00;--orange:#ff7b29;--purple:#b366ff;
  --text:#ccd8f0;--muted:#4a6080;
  --mono:'IBM Plex Mono',monospace;--sans:'IBM Plex Sans',sans-serif;
}
html{scroll-behavior:smooth}
body{font-family:var(--sans);background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
body::after{content:'';position:fixed;inset:0;z-index:9999;pointer-events:none;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.05) 2px,rgba(0,0,0,.05) 4px)}
body::before{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;background-image:linear-gradient(rgba(0,229,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(0,229,255,.02) 1px,transparent 1px);background-size:48px 48px}
 
/* HEADER */
header{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 2rem;height:56px;background:rgba(7,11,20,.94);border-bottom:1px solid var(--border);backdrop-filter:blur(16px)}
.logo{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:.85rem;letter-spacing:.12em;color:var(--cyan);text-transform:uppercase}
.logo-pulse{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 10px var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.5)}}
.hdr-right{display:flex;align-items:center;gap:1.5rem}
.hdr-clock{font-family:var(--mono);font-size:.8rem;color:var(--cyan)}
.live-badge{display:flex;align-items:center;gap:6px;font-family:var(--mono);font-size:.7rem;color:var(--green);letter-spacing:.1em}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green);animation:pulse 1.4s infinite}
 
/* TABS */
.nav-tabs{display:flex;border-bottom:1px solid var(--border);background:var(--s1);padding:0 2rem}
.tab-btn{font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);background:transparent;border:none;padding:.85rem 1.4rem;cursor:pointer;border-bottom:2px solid transparent;transition:all .2s}
.tab-btn:hover{color:var(--text)}.tab-btn.active{color:var(--cyan);border-bottom-color:var(--cyan)}
 
/* LAYOUT */
main{position:relative;z-index:5;max-width:1440px;margin:0 auto;padding:1.8rem 2rem 4rem}
.tab-panel{display:none}.tab-panel.active{display:block}
.sec-label{font-family:var(--mono);font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);margin-bottom:1rem;display:flex;align-items:center;gap:.6rem}
.sec-label::after{content:'';flex:1;height:1px;background:var(--border)}
 
/* STAT CARDS */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:.9rem;margin-bottom:2rem}
.stat-card{background:var(--s1);border:1px solid var(--border);border-radius:10px;padding:1.2rem 1.4rem;position:relative;overflow:hidden;animation:fadeUp .5s ease both}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--cyan)}
.stat-card.g::before{background:var(--green)}.stat-card.r::before{background:var(--red)}
.stat-card.y::before{background:var(--yellow)}.stat-card.p::before{background:var(--purple)}
.stat-label{font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}
.stat-val{font-family:var(--mono);font-size:1.9rem;font-weight:600;line-height:1;color:var(--text)}
.stat-val.c{color:var(--cyan)}.stat-val.g{color:var(--green)}.stat-val.r{color:var(--red)}.stat-val.p{color:var(--purple)}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
 
/* PANELS */
.two-col{display:grid;grid-template-columns:1fr 380px;gap:1.2rem;margin-bottom:1.5rem}
@media(max-width:1100px){.two-col{grid-template-columns:1fr}}
.panel{background:var(--s1);border:1px solid var(--border);border-radius:12px;padding:1.5rem}
.panel-title{font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--cyan);margin-bottom:1.2rem;display:flex;align-items:center;justify-content:space-between}
 
/* API TABLE */
.api-table{width:100%;border-collapse:collapse}
.api-table th{font-family:var(--mono);font-size:.58rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--border)}
.api-table td{padding:.75rem .7rem;font-size:.83rem;border-bottom:1px solid rgba(26,45,74,.35);vertical-align:middle}
.api-table tr:last-child td{border-bottom:none}
.api-table tbody tr{cursor:pointer;transition:background .15s}
.api-table tbody tr:hover td{background:rgba(0,229,255,.04)}
.api-table tbody tr.sel td{background:rgba(0,229,255,.08)}
.api-table tbody tr.paused-row td{opacity:.5}
 
.api-name{font-weight:500;color:var(--text);display:block;margin-bottom:2px}
.api-url{font-family:var(--mono);font-size:.62rem;color:var(--muted)}
.api-meta{display:flex;gap:6px;margin-top:4px;flex-wrap:wrap}
 
/* BADGES */
.badge{display:inline-flex;align-items:center;gap:.3rem;padding:.2rem .55rem;border-radius:20px;font-family:var(--mono);font-size:.65rem;font-weight:600;white-space:nowrap}
.badge.up{background:rgba(0,255,157,.1);color:var(--green)}
.badge.dn{background:rgba(255,61,107,.1);color:var(--red)}
.badge.uk{background:rgba(74,96,128,.15);color:var(--muted)}
.badge.paused{background:rgba(179,102,255,.12);color:var(--purple)}
 
/* FEATURE 3 — Tag badge */
.tag-badge{display:inline-block;padding:.15rem .55rem;border-radius:4px;font-family:var(--mono);font-size:.6rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.tag-Production{background:rgba(0,255,157,.12);color:var(--green);border:1px solid rgba(0,255,157,.2)}
.tag-Testing   {background:rgba(0,229,255,.1); color:var(--cyan); border:1px solid rgba(0,229,255,.2)}
.tag-Staging   {background:rgba(255,204,0,.12);color:var(--yellow);border:1px solid rgba(255,204,0,.2)}
.tag-General   {background:rgba(74,96,128,.15);color:var(--muted);border:1px solid rgba(74,96,128,.2)}
.tag-Internal  {background:rgba(255,123,41,.12);color:var(--orange);border:1px solid rgba(255,123,41,.2)}
 
/* FEATURE 1 — Speed warning badges */
.spd-ok{font-family:var(--mono);font-size:.8rem;color:var(--green)}
.spd-warn{font-family:var(--mono);font-size:.8rem;color:var(--yellow)}
.spd-warn::before{content:'⚠ '}
.spd-crit{font-family:var(--mono);font-size:.8rem;color:var(--red)}
.spd-crit::before{content:'🔴 '}
 
/* BUTTONS */
.btn{font-family:var(--mono);font-size:.65rem;letter-spacing:.05em;padding:.26rem .65rem;border-radius:5px;cursor:pointer;transition:all .18s;border:1px solid var(--border2)}
.btn-check{background:transparent;color:var(--cyan)}.btn-check:hover{background:var(--cyan);color:var(--bg)}
.btn-pause{background:transparent;color:var(--purple)}.btn-pause:hover{background:var(--purple);color:var(--bg)}
.btn-note{background:transparent;color:var(--yellow)}.btn-note:hover{background:var(--yellow);color:var(--bg)}
.btn-del{background:transparent;border-color:transparent;color:var(--muted)}.btn-del:hover{border-color:var(--red);color:var(--red)}
.btn-primary{background:var(--cyan);color:var(--bg);border:none;padding:.72rem;border-radius:7px;width:100%;font-family:var(--mono);font-weight:600;font-size:.82rem;cursor:pointer;transition:opacity .2s}
.btn-primary:hover{opacity:.85}
.btn-save{background:var(--green);color:var(--bg);border:none;padding:.6rem 1.3rem;border-radius:6px;font-family:var(--mono);font-size:.75rem;font-weight:600;cursor:pointer;transition:opacity .2s}
.btn-save:hover{opacity:.85}
.btn-export{display:inline-flex;align-items:center;gap:.5rem;background:transparent;border:1px solid var(--border2);color:var(--yellow);padding:.4rem 1rem;border-radius:6px;font-family:var(--mono);font-size:.72rem;cursor:pointer;transition:all .2s;text-decoration:none}
.btn-export:hover{background:var(--yellow);color:var(--bg)}
 
/* FORMS */
.form-group{margin-bottom:.9rem}
.form-group label{display:block;font-family:var(--mono);font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:.4rem}
.form-group input,.form-group select,.form-group textarea{width:100%;background:var(--s2);border:1px solid var(--border);color:var(--text);padding:.6rem .85rem;border-radius:6px;font-family:var(--mono);font-size:.8rem;transition:border-color .2s}
.form-group textarea{resize:vertical;min-height:70px;font-family:var(--sans);font-size:.82rem}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{outline:none;border-color:var(--cyan);box-shadow:0 0 0 3px rgba(0,229,255,.08)}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:.8rem}
.form-msg{font-size:.75rem;margin-top:.4rem;min-height:1.1em}
.form-msg.ok{color:var(--green)}.form-msg.err{color:var(--red)}
 
/* CHARTS */
.chart-wrap{background:var(--s1);border:1px solid var(--border);border-radius:12px;padding:1.5rem;margin-bottom:1.2rem}
.chart-header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1.2rem}
.chart-ttl{font-family:var(--mono);font-size:.75rem;color:var(--cyan);letter-spacing:.1em;text-transform:uppercase}
.chart-sub{font-size:.7rem;color:var(--muted);margin-top:.25rem}
 
/* HEATMAP */
.heatmap-grid{display:flex;flex-wrap:wrap;gap:3px;margin-top:.8rem}
.hm-cell{width:18px;height:18px;border-radius:3px;background:var(--s2);border:1px solid var(--border);cursor:default;transition:transform .1s;position:relative}
.hm-cell:hover{transform:scale(1.3);z-index:10}
.hm-100{background:rgba(0,255,157,.9)}.hm-90{background:rgba(0,255,157,.55)}
.hm-70{background:rgba(255,204,0,.5)}.hm-50{background:rgba(255,123,41,.5)}.hm-0{background:rgba(255,61,107,.5)}
 
/* MODAL */
.modal-bg{display:none;position:fixed;inset:0;z-index:500;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);align-items:center;justify-content:center}
.modal-bg.open{display:flex}
.modal{background:var(--s1);border:1px solid var(--border2);border-radius:14px;padding:1.8rem;width:420px;max-width:95vw;animation:fadeUp .25s ease}
.modal-title{font-family:var(--mono);font-size:.8rem;color:var(--cyan);letter-spacing:.1em;text-transform:uppercase;margin-bottom:1.2rem}
.modal-footer{display:flex;gap:.7rem;justify-content:flex-end;margin-top:1.2rem}
.btn-cancel{background:transparent;border:1px solid var(--border2);color:var(--muted);padding:.55rem 1.2rem;border-radius:6px;font-family:var(--mono);font-size:.75rem;cursor:pointer}
.btn-cancel:hover{border-color:var(--text);color:var(--text)}
 
/* EXPORT + ALERT TABS */
.export-grid{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-top:.8rem}
.export-card{background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:1rem;text-align:center}
.export-icon{font-size:1.6rem;margin-bottom:.4rem}
.export-title{font-family:var(--mono);font-size:.7rem;color:var(--text);margin-bottom:.2rem;text-transform:uppercase;letter-spacing:.08em}
.export-desc{font-size:.72rem;color:var(--muted);margin-bottom:.7rem}
.toggle-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem}
.toggle-label{font-family:var(--mono);font-size:.75rem;color:var(--text)}
.toggle{position:relative;display:inline-block;width:44px;height:24px}
.toggle input{opacity:0;width:0;height:0}
.slider{position:absolute;inset:0;border-radius:24px;background:var(--s2);border:1px solid var(--border);cursor:pointer;transition:.3s}
.slider::before{content:'';position:absolute;width:16px;height:16px;left:3px;bottom:3px;border-radius:50%;background:var(--muted);transition:.3s}
input:checked+.slider{background:rgba(0,255,157,.2);border-color:var(--green)}
input:checked+.slider::before{transform:translateX(20px);background:var(--green)}
 
/* MISC */
#toast{position:fixed;bottom:2rem;right:2rem;z-index:9998;background:var(--s2);border:1px solid var(--border2);border-radius:8px;padding:.8rem 1.3rem;font-family:var(--mono);font-size:.78rem;color:var(--text);transform:translateY(120%);transition:transform .3s;box-shadow:0 8px 32px rgba(0,0,0,.5);max-width:300px}
#toast.show{transform:translateY(0)}#toast.ok{border-color:var(--green);color:var(--green)}#toast.err{border-color:var(--red);color:var(--red)}
.spin{display:inline-block;width:14px;height:14px;border:2px solid var(--border);border-top-color:var(--cyan);border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
 
<!-- HEADER -->
<header>
  <div class="logo"><div class="logo-pulse"></div>API Performance Monitor</div>
  <div class="hdr-right">
    <span class="hdr-clock" id="clock">--:--:--</span>
    <div class="live-badge"><div class="live-dot"></div>LIVE</div>
  </div>
</header>
 
<!-- TABS -->
<div class="nav-tabs">
  <button class="tab-btn active" onclick="switchTab('dashboard',this)">📊 Dashboard</button>
  <button class="tab-btn" onclick="switchTab('history',this)">📈 History</button>
  <button class="tab-btn" onclick="switchTab('export',this)">📥 Export</button>
  <button class="tab-btn" onclick="switchTab('alerts',this)">🔔 Alerts</button>
</div>
 
<main>
 
<!-- ═══ TAB 1: DASHBOARD ═══ -->
<div class="tab-panel active" id="tab-dashboard">
  <div class="sec-label">// overview</div>
 
  <!-- Stat cards — now includes paused count -->
  <div class="stats-grid">
    <div class="stat-card">      <div class="stat-label">APIs Active</div>    <div class="stat-val c" id="s-apis">–</div></div>
    <div class="stat-card g">    <div class="stat-label">Success Rate (1h)</div><div class="stat-val g" id="s-rate">–%</div></div>
    <div class="stat-card">      <div class="stat-label">Avg Response</div>   <div class="stat-val"  id="s-avg">–ms</div></div>
    <div class="stat-card">      <div class="stat-label">Total Checks</div>   <div class="stat-val"  id="s-checks">–</div></div>
    <div class="stat-card r">    <div class="stat-label">Failing Now</div>    <div class="stat-val r" id="s-fail">–</div></div>
    <div class="stat-card p">    <div class="stat-label">Paused</div>         <div class="stat-val p" id="s-paused">–</div></div>
  </div>
 
  <!-- Response bar chart -->
  <div class="chart-wrap">
    <div class="chart-header">
      <div><div class="chart-ttl">Response Time History</div><div class="chart-sub" id="chart-sub">Click an API row below to see its chart</div></div>
      <div id="chart-spin" style="display:none"><div class="spin"></div></div>
    </div>
    <canvas id="responseChart" style="max-height:210px"></canvas>
  </div>
 
  <div class="two-col">
    <!-- API Table -->
    <div class="panel">
      <div class="panel-title">
        // Monitored APIs
        <span id="tbl-spin" style="display:none"><div class="spin"></div></span>
      </div>
      <div id="api-list"><div style="text-align:center;padding:2rem;color:var(--muted)"><div class="spin"></div></div></div>
    </div>
 
    <!-- Add API Form — now has tag, warn_ms, critical_ms -->
    <div class="panel">
      <div class="panel-title">// Add New API</div>
      <div class="form-group"><label>API Name</label><input id="f-name" type="text" placeholder="e.g. My Weather API"></div>
      <div class="form-group"><label>URL</label><input id="f-url" type="url" placeholder="https://api.example.com/health"></div>
 
      <!-- FEATURE 3: Tag selector -->
      <div class="form-group">
        <label>Tag / Environment</label>
        <select id="f-tag">
          <option value="Production">🟢 Production</option>
          <option value="Testing" selected>🔵 Testing</option>
          <option value="Staging">🟡 Staging</option>
          <option value="Internal">🟠 Internal</option>
          <option value="General">⚪ General</option>
        </select>
      </div>
 
      <!-- FEATURE 1: Threshold inputs -->
      <div class="form-row">
        <div class="form-group">
          <label>⚠ Warn above (ms)</label>
          <input id="f-warn" type="number" value="800" min="100">
        </div>
        <div class="form-group">
          <label>🔴 Critical above (ms)</label>
          <input id="f-crit" type="number" value="2000" min="100">
        </div>
      </div>
 
      <!-- FEATURE 3: Notes -->
      <div class="form-group">
        <label>Notes (optional)</label>
        <textarea id="f-notes" placeholder="e.g. Main production endpoint, owned by backend team"></textarea>
      </div>
 
      <div class="form-group"><label>Check Interval (seconds)</label><input id="f-int" type="number" value="30" min="10" max="3600"></div>
      <button class="btn-primary" onclick="addApi()">+ ADD API</button>
      <div id="add-msg" class="form-msg"></div>
    </div>
  </div>
</div><!-- end dashboard -->
 
 
<!-- ═══ TAB 2: HISTORY ═══ -->
<div class="tab-panel" id="tab-history">
  <div class="sec-label">// 30-day heatmap + 24h trend</div>
  <div class="panel" style="margin-bottom:1.2rem">
    <div class="panel-title">// Select API to inspect</div>
    <select id="hm-select" onchange="loadHeatmap()" style="width:100%;background:var(--s2);border:1px solid var(--border);color:var(--text);padding:.6rem .85rem;border-radius:6px;font-family:var(--mono);font-size:.8rem">
      <option value="">— choose an API —</option>
    </select>
  </div>
  <div class="panel" style="margin-bottom:1.2rem">
    <div class="panel-title">// Daily Uptime — Last 30 Days</div>
    <div style="display:flex;gap:10px;font-family:var(--mono);font-size:.63rem;color:var(--muted);margin-bottom:.8rem;flex-wrap:wrap">
      <span><span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:rgba(0,255,157,.9);margin-right:3px;vertical-align:middle"></span>100%</span>
      <span><span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:rgba(0,255,157,.5);margin-right:3px;vertical-align:middle"></span>≥90%</span>
      <span><span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:rgba(255,204,0,.5);margin-right:3px;vertical-align:middle"></span>≥70%</span>
      <span><span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:rgba(255,61,107,.5);margin-right:3px;vertical-align:middle"></span>&lt;70%</span>
    </div>
    <div id="heatmap-grid" class="heatmap-grid"></div>
  </div>
  <div class="chart-wrap">
    <div class="chart-header"><div><div class="chart-ttl">24-Hour Speed Trend</div><div class="chart-sub" id="trend-sub">Select an API above</div></div></div>
    <canvas id="trendChart" style="max-height:200px"></canvas>
  </div>
</div>
 
 
<!-- ═══ TAB 3: EXPORT ═══ -->
<div class="tab-panel" id="tab-export">
  <div class="sec-label">// download your data</div>
  <div class="panel" style="max-width:620px">
    <div class="panel-title">// Export as CSV</div>
    <p style="font-size:.82rem;color:var(--muted);margin-bottom:1.2rem;line-height:1.7">Click below to download. Opens directly in Excel or Google Sheets.</p>
    <div class="export-grid">
      <div class="export-card">
        <div class="export-icon">📋</div>
        <div class="export-title">All Check Results</div>
        <div class="export-desc">Every ping — time, status, speed, errors</div>
        <a class="btn-export" href="/api/export/checks" download>⬇ Download Checks CSV</a>
      </div>
      <div class="export-card">
        <div class="export-icon">📊</div>
        <div class="export-title">Summary Report</div>
        <div class="export-desc">One row per API — uptime%, avg/min/max</div>
        <a class="btn-export" href="/api/export/summary" download>⬇ Download Summary CSV</a>
      </div>
    </div>
  </div>
</div>
 
 
<!-- ═══ TAB 4: ALERTS ═══ -->
<div class="tab-panel" id="tab-alerts">
  <div class="sec-label">// email alert settings</div>
  <div class="two-col">
    <div class="panel">
      <div class="panel-title">// Configure Email Alerts</div>
      <p style="font-size:.8rem;color:var(--muted);margin-bottom:1.2rem;line-height:1.7">When an API goes <span style="color:var(--red)">DOWN</span>, you get an email. Uses Gmail App Password.</p>
      <div class="toggle-row">
        <span class="toggle-label">Enable email alerts</span>
        <label class="toggle"><input type="checkbox" id="alert-enabled" checked><span class="slider"></span></label>
      </div>
      <div class="form-group"><label>Send TO this email</label><input id="a-to" type="email" placeholder="you@example.com"></div>
      <div class="form-group"><label>Your Gmail (sender)</label><input id="a-user" type="email" placeholder="yourname@gmail.com"></div>
      <div class="form-group"><label>Gmail App Password</label><input id="a-pass" type="password" placeholder="xxxx xxxx xxxx xxxx"></div>
      <div class="form-row">
        <div class="form-group"><label>SMTP Host</label><input id="a-host" type="text" value="smtp.gmail.com"></div>
        <div class="form-group"><label>SMTP Port</label><input id="a-port" type="number" value="587"></div>
      </div>
      <button class="btn-save" onclick="saveAlerts()">💾 Save Settings</button>
      <div id="alert-msg" class="form-msg"></div>
    </div>
    <div class="panel">
      <div class="panel-title">// Gmail App Password Steps</div>
      <div style="font-family:var(--mono);font-size:.72rem;color:var(--muted);line-height:2.1">
        <div><span style="color:var(--yellow)">1.</span> myaccount.google.com</div>
        <div><span style="color:var(--yellow)">2.</span> Security → 2-Step Verification</div>
        <div><span style="color:var(--yellow)">3.</span> Search "App passwords"</div>
        <div><span style="color:var(--yellow)">4.</span> Select Mail → Create</div>
        <div><span style="color:var(--yellow)">5.</span> Copy the 16-char password</div>
        <div><span style="color:var(--yellow)">6.</span> Paste in the form ←</div>
        <div style="margin-top:1rem;padding:.8rem;background:var(--s2);border:1px solid var(--border);border-radius:6px">⚠️ Never use your normal Gmail password here.</div>
      </div>
    </div>
  </div>
</div>
 
</main><!-- end main -->
 
 
<!-- ═══════════════════════════════════════
     MODAL — Edit Notes & Tag (Feature 3)
     + Threshold settings (Feature 1)
═══════════════════════════════════════ -->
<div class="modal-bg" id="modal-notes">
  <div class="modal">
    <div class="modal-title">📝 Edit Notes & Tag</div>
    <input type="hidden" id="mn-id">
    <div class="form-group">
      <label>Tag / Environment</label>
      <select id="mn-tag">
        <option value="Production">🟢 Production</option>
        <option value="Testing">🔵 Testing</option>
        <option value="Staging">🟡 Staging</option>
        <option value="Internal">🟠 Internal</option>
        <option value="General">⚪ General</option>
      </select>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea id="mn-notes" placeholder="e.g. Owned by backend team. Check on Mondays."></textarea>
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal('modal-notes')">Cancel</button>
      <button class="btn-save" onclick="saveNotes()">💾 Save</button>
    </div>
  </div>
</div>
 
<!-- MODAL — Edit Thresholds (Feature 1) -->
<div class="modal-bg" id="modal-thresh">
  <div class="modal">
    <div class="modal-title">⏱️ Response Time Thresholds</div>
    <input type="hidden" id="mt-id">
    <p style="font-size:.8rem;color:var(--muted);margin-bottom:1.2rem;line-height:1.7">
      Set when to show a <span style="color:var(--yellow)">⚠ warning</span> or a <span style="color:var(--red)">🔴 critical</span> badge on the response time.
    </p>
    <div class="form-row">
      <div class="form-group">
        <label>⚠ Warn above (ms)</label>
        <input id="mt-warn" type="number" value="800" min="100">
      </div>
      <div class="form-group">
        <label>🔴 Critical above (ms)</label>
        <input id="mt-crit" type="number" value="2000" min="100">
      </div>
    </div>
    <div style="display:flex;gap:.7rem;padding:.8rem;background:var(--s2);border:1px solid var(--border);border-radius:6px;font-family:var(--mono);font-size:.68rem;color:var(--muted);margin-bottom:.5rem">
      <span style="color:var(--green)">✅ Fast</span> = below warn_ms &nbsp;|&nbsp;
      <span style="color:var(--yellow)">⚠ Slow</span> = above warn_ms &nbsp;|&nbsp;
      <span style="color:var(--red)">🔴 Critical</span> = above critical_ms
    </div>
    <div class="modal-footer">
      <button class="btn-cancel" onclick="closeModal('modal-thresh')">Cancel</button>
      <button class="btn-save" onclick="saveThresholds()">💾 Save</button>
    </div>
  </div>
</div>
 
<div id="toast"></div>
 
<script>
// ════════════════════════════════════════════════════════
// JavaScript — Dashboard Controller
// 3 new features wired up here:
//   Feature 1: threshold colour coding on avg_ms
//   Feature 2: pause/resume toggle button per row
//   Feature 3: notes + tag shown in table + edit modal
// ════════════════════════════════════════════════════════
 
let barChart=null, trendChart=null, selApiId=null, selApiName='';
 
// Clock
setInterval(()=>{document.getElementById('clock').textContent=new Date().toLocaleTimeString('en-US',{hour12:false})},1000);
 
// Tab switching
function switchTab(n,b){
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(x=>x.classList.remove('active'));
  document.getElementById('tab-'+n).classList.add('active'); b.classList.add('active');
  if(n==='history') populateHmSelect();
  if(n==='alerts')  loadAlertSettings();
}
 
// Toast
function toast(msg,type,ms=2800){
  const el=document.getElementById('toast');
  el.textContent=msg; el.className='show '+(type||'');
  clearTimeout(el._t); el._t=setTimeout(()=>el.className='',ms);
}
 
// Modal helpers
function openModal(id){document.getElementById(id).classList.add('open')}
function closeModal(id){document.getElementById(id).classList.remove('open')}
document.querySelectorAll('.modal-bg').forEach(m=>m.addEventListener('click',e=>{if(e.target===m)m.classList.remove('open')}));
 
// ── FEATURE 1: Speed class based on thresholds ────────
// Each API has its own warn_ms and critical_ms.
// We compare avg_ms to those values to pick the colour.
function speedClass(ms, warn, crit){
  if(!ms) return '';
  if(ms >= crit) return 'spd-crit';
  if(ms >= warn) return 'spd-warn';
  return 'spd-ok';
}
 
// ── Load stats cards ──────────────────────────────────
async function loadStats(){
  const d=await fetch('/api/stats').then(r=>r.json()).catch(()=>({}));
  document.getElementById('s-apis').textContent   = d.total_apis??'–';
  document.getElementById('s-rate').textContent   = (d.success_rate??'–')+'%';
  document.getElementById('s-avg').textContent    = (d.avg_response??'–')+'ms';
  document.getElementById('s-checks').textContent = (d.total_checks??0).toLocaleString();
  document.getElementById('s-fail').textContent   = d.failing_now??'–';
  document.getElementById('s-paused').textContent = d.paused_count??'0';
}
 
// ── Load API table ────────────────────────────────────
async function loadApis(){
  document.getElementById('tbl-spin').style.display='inline-block';
  const s=await fetch('/api/summary').then(r=>r.json()).catch(()=>[]);
  document.getElementById('tbl-spin').style.display='none';
 
  if(!s.length){
    document.getElementById('api-list').innerHTML='<div style="text-align:center;padding:2.5rem;color:var(--muted)">No APIs yet — add one →</div>';
    return;
  }
 
  const rows=s.map(a=>{
    // FEATURE 2: Status badge shows PAUSED if paused
    const badge = a.paused
      ? '<span class="badge paused">⏸ PAUSED</span>'
      : a.last_success===null
        ? '<span class="badge uk">UNKNOWN</span>'
        : a.last_success
          ? '<span class="badge up">▲ UP</span>'
          : '<span class="badge dn">▼ DOWN</span>';
 
    // FEATURE 1: colour avg_ms by threshold
    const sc  = speedClass(a.avg_ms, a.warn_ms, a.critical_ms);
    const ms  = a.avg_ms
      ? `<span class="${sc}">${a.avg_ms}ms</span>`
      : '<span style="color:var(--muted)">–</span>';
 
    // FEATURE 3: tag badge + notes tooltip
    const tagCls = 'tag-badge tag-'+(a.tag||'General');
    const tagBadge = `<span class="${tagCls}">${a.tag||'General'}</span>`;
    const notesSnip = a.notes ? `<span style="font-size:.65rem;color:var(--muted);font-family:var(--sans)">📝 ${a.notes.slice(0,40)}${a.notes.length>40?'…':''}</span>` : '';
 
    // Pause button text changes based on state
    const pauseLabel = a.paused ? '▶' : '⏸';
    const pauseTip   = a.paused ? 'Resume' : 'Pause';
 
    // Dim the whole row if paused
    const rowClass = a.paused ? 'paused-row' : '';
 
    return `<tr id="row-${a.id}" class="${rowClass}" onclick="selectApi(${a.id},'${a.name.replace(/'/g,"\\'")}')">
      <td>
        <span class="api-name">${a.name}</span>
        <span class="api-url">${a.url}</span>
        <div class="api-meta">${tagBadge}${notesSnip}</div>
      </td>
      <td>${badge}</td>
      <td>${ms}</td>
      <td style="font-family:var(--mono);font-size:.75rem">${a.uptime_pct!=null?a.uptime_pct+'%':'–'}</td>
      <td style="white-space:nowrap">
        <button class="btn btn-check" title="Check now"  onclick="event.stopPropagation();pingNow(${a.id})">CHECK</button>
        <button class="btn btn-pause" title="${pauseTip}" onclick="event.stopPropagation();togglePause(${a.id})">${pauseLabel}</button>
        <button class="btn btn-note"  title="Edit notes"  onclick="event.stopPropagation();openNotes(${a.id},'${a.tag||'General'}','${(a.notes||'').replace(/'/g,"\\'")}')">📝</button>
        <button class="btn btn-check" title="Thresholds"  onclick="event.stopPropagation();openThresh(${a.id},${a.warn_ms||800},${a.critical_ms||2000})" style="color:var(--yellow)">⏱</button>
        <button class="btn btn-del"   title="Delete"      onclick="event.stopPropagation();removeApi(${a.id})">✕</button>
      </td>
    </tr>`;
  }).join('');
 
  document.getElementById('api-list').innerHTML=`
    <table class="api-table">
      <thead><tr><th>API / Tag / Notes</th><th>Status</th><th>Avg Speed</th><th>Uptime</th><th>Actions</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
 
  if(selApiId) document.getElementById('row-'+selApiId)?.classList.add('sel');
}
 
// ── Select API row → show chart ───────────────────────
function selectApi(id,name){
  selApiId=id; selApiName=name;
  document.querySelectorAll('.api-table tbody tr').forEach(r=>r.classList.remove('sel'));
  document.getElementById('row-'+id)?.classList.add('sel');
  loadBarChart(id,name);
}
 
// ── Bar chart ─────────────────────────────────────────
async function loadBarChart(id,name){
  document.getElementById('chart-sub').textContent='Loading '+name+'...';
  document.getElementById('chart-spin').style.display='flex';
  const h=await fetch(`/api/history/${id}?limit=40`).then(r=>r.json()).catch(()=>[]);
  document.getElementById('chart-spin').style.display='none';
  document.getElementById('chart-sub').textContent=`Last ${h.length} checks for: ${name}`;
  if(barChart)barChart.destroy();
  barChart=new Chart(document.getElementById('responseChart'),{
    type:'bar',
    data:{
      labels:h.map(x=>new Date(x.checked_at+'Z').toLocaleTimeString('en-US',{hour12:false})),
      datasets:[{label:'ms',data:h.map(x=>x.response_ms),
        backgroundColor:h.map(x=>x.success?'rgba(0,255,157,.75)':'rgba(255,61,107,.75)'),
        borderRadius:3,borderSkipped:false}]
    },
    options:{responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>c.raw?c.raw+'ms':'Failed'}}},
      scales:{x:{ticks:{color:'#4a6080',font:{family:'IBM Plex Mono',size:9},maxRotation:45},grid:{color:'rgba(26,45,74,.4)'}},
              y:{ticks:{color:'#4a6080',font:{family:'IBM Plex Mono',size:9}},grid:{color:'rgba(26,45,74,.4)'},title:{display:true,text:'ms',color:'#4a6080'}}}}
  });
}
 
// ── Ping now ──────────────────────────────────────────
async function pingNow(id){
  toast('⏳ Checking...');
  const r=await fetch(`/api/check/${id}`,{method:'POST'}).then(r=>r.json()).catch(()=>({}));
  r.success?toast(`✅ OK — ${r.response_ms}ms`,'ok'):toast(`❌ ${r.error_msg||'Failed'}`,'err');
  refresh();
}
 
// ── FEATURE 2: Pause / Resume ─────────────────────────
// Sends a POST to /api/apis/{id}/pause which toggles the
// paused column in the database. Background monitor skips
// paused APIs automatically.
async function togglePause(id){
  const r=await fetch(`/api/apis/${id}/pause`,{method:'POST'}).then(r=>r.json()).catch(()=>({}));
  toast(r.message||'Done');
  refresh();
}
 
// ── FEATURE 3: Open notes modal ───────────────────────
function openNotes(id, tag, notes){
  document.getElementById('mn-id').value    = id;
  document.getElementById('mn-tag').value   = tag;
  document.getElementById('mn-notes').value = notes;
  openModal('modal-notes');
}
 
async function saveNotes(){
  const id    = document.getElementById('mn-id').value;
  const tag   = document.getElementById('mn-tag').value;
  const notes = document.getElementById('mn-notes').value;
  const r=await fetch(`/api/apis/${id}/notes`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tag,notes})}).then(r=>r.json()).catch(()=>({}));
  closeModal('modal-notes');
  toast(r.message||'Saved','ok');
  refresh();
}
 
// ── FEATURE 1: Open threshold modal ───────────────────
function openThresh(id, warn, crit){
  document.getElementById('mt-id').value   = id;
  document.getElementById('mt-warn').value = warn;
  document.getElementById('mt-crit').value = crit;
  openModal('modal-thresh');
}
 
async function saveThresholds(){
  const id   = document.getElementById('mt-id').value;
  const warn = parseInt(document.getElementById('mt-warn').value)||800;
  const crit = parseInt(document.getElementById('mt-crit').value)||2000;
  const r=await fetch(`/api/apis/${id}/thresholds`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({warn_ms:warn,critical_ms:crit})}).then(r=>r.json()).catch(()=>({}));
  closeModal('modal-thresh');
  toast(r.message||'Saved','ok');
  refresh();
}
 
// ── Add API ───────────────────────────────────────────
async function addApi(){
  const name=document.getElementById('f-name').value.trim();
  const url =document.getElementById('f-url').value.trim();
  const tag =document.getElementById('f-tag').value;
  const warn=parseInt(document.getElementById('f-warn').value)||800;
  const crit=parseInt(document.getElementById('f-crit').value)||2000;
  const notes=document.getElementById('f-notes').value.trim();
  const intv=parseInt(document.getElementById('f-int').value)||30;
  const msg=document.getElementById('add-msg');
  if(!name||!url){msg.textContent='⚠ Name and URL required';msg.className='form-msg err';return}
  const res=await fetch('/api/apis',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name,url,interval:intv,tag,warn_ms:warn,critical_ms:crit,notes})});
  const d=await res.json();
  if(res.ok){msg.textContent='✅ '+d.message;msg.className='form-msg ok';
    document.getElementById('f-name').value='';document.getElementById('f-url').value='';document.getElementById('f-notes').value='';
    refresh();}
  else{msg.textContent='❌ '+d.error;msg.className='form-msg err'}
  setTimeout(()=>{msg.textContent=''},3500);
}
 
// ── Remove API ────────────────────────────────────────
async function removeApi(id){
  if(!confirm('Remove this API from monitoring?'))return;
  await fetch(`/api/apis/${id}`,{method:'DELETE'});
  if(selApiId===id)selApiId=null;
  refresh(); toast('🗑 Removed');
}
 
// ── History tab ───────────────────────────────────────
async function populateHmSelect(){
  const apis=await fetch('/api/apis').then(r=>r.json()).catch(()=>[]);
  const sel=document.getElementById('hm-select');
  sel.innerHTML='<option value="">— choose an API —</option>';
  apis.forEach(a=>{const o=document.createElement('option');o.value=a.id;o.textContent=a.name+(a.paused?' (paused)':'');sel.appendChild(o)});
}
 
async function loadHeatmap(){
  const id=document.getElementById('hm-select').value;
  if(!id)return;
  const name=document.getElementById('hm-select').selectedOptions[0].text;
  const data=await fetch(`/api/heatmap/${id}`).then(r=>r.json()).catch(()=>[]);
  const dayMap={};data.forEach(d=>{dayMap[d.day]={pct:d.uptime_pct,total:d.total_checks}});
  const cells=[];
  for(let i=29;i>=0;i--){
    const d=new Date();d.setDate(d.getDate()-i);
    const key=d.toISOString().slice(0,10);const val=dayMap[key];
    let cls='hm-cell';
    if(val){if(val.pct>=100)cls+=' hm-100';else if(val.pct>=90)cls+=' hm-90';else if(val.pct>=70)cls+=' hm-70';else if(val.pct>0)cls+=' hm-50';else cls+=' hm-0'}
    cells.push(`<div class="${cls}" title="${val?key+': '+val.pct+'% ('+val.total+' checks)':key+': No data'}"></div>`);
  }
  document.getElementById('heatmap-grid').innerHTML=cells.join('');
  const trend=await fetch(`/api/trend/${id}`).then(r=>r.json()).catch(()=>[]);
  if(trendChart)trendChart.destroy();
  if(trend.length){
    document.getElementById('trend-sub').textContent='24h avg response for: '+name;
    trendChart=new Chart(document.getElementById('trendChart'),{type:'line',
      data:{labels:trend.map(t=>t.hour.slice(11,16)),datasets:[{label:'Avg ms',data:trend.map(t=>t.avg_ms),borderColor:'rgba(0,229,255,.8)',backgroundColor:'rgba(0,229,255,.06)',pointBackgroundColor:'rgba(0,229,255,.9)',tension:.4,fill:true,pointRadius:4}]},
      options:{responsive:true,plugins:{legend:{display:false}},
        scales:{x:{ticks:{color:'#4a6080',font:{family:'IBM Plex Mono',size:9}},grid:{color:'rgba(26,45,74,.4)'}},
                y:{ticks:{color:'#4a6080',font:{family:'IBM Plex Mono',size:9}},grid:{color:'rgba(26,45,74,.4)'},title:{display:true,text:'ms',color:'#4a6080'}}}}
    });
  }else{document.getElementById('trend-sub').textContent='Not enough data yet'}
}
 
// ── Alerts ────────────────────────────────────────────
async function saveAlerts(){
  const payload={to_email:document.getElementById('a-to').value.trim(),smtp_user:document.getElementById('a-user').value.trim(),smtp_pass:document.getElementById('a-pass').value,smtp_host:document.getElementById('a-host').value.trim(),smtp_port:parseInt(document.getElementById('a-port').value)||587,enabled:document.getElementById('alert-enabled').checked?1:0};
  const msg=document.getElementById('alert-msg');
  if(!payload.to_email||!payload.smtp_user||!payload.smtp_pass){msg.textContent='⚠ Fill all required fields';msg.className='form-msg err';return}
  const res=await fetch('/api/alerts/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const d=await res.json();
  res.ok?(msg.textContent='✅ '+d.message,msg.className='form-msg ok'):(msg.textContent='❌ '+(d.error||'Error'),msg.className='form-msg err');
  setTimeout(()=>{msg.textContent=''},3500);
}
 
async function loadAlertSettings(){
  const d=await fetch('/api/alerts/settings').then(r=>r.json()).catch(()=>({}));
  if(d.to_email){document.getElementById('a-to').value=d.to_email||'';document.getElementById('a-user').value=d.smtp_user||'';document.getElementById('a-host').value=d.smtp_host||'smtp.gmail.com';document.getElementById('a-port').value=d.smtp_port||587;document.getElementById('alert-enabled').checked=!!d.enabled}
}
 
// ── Full refresh ──────────────────────────────────────
async function refresh(){
  await Promise.all([loadStats(),loadApis()]);
  if(selApiId)loadBarChart(selApiId,selApiName);
}
 
refresh();
setInterval(refresh,15000);
</script>
</body>
</html>"""
 
def register_routes(app):
 
    # ── Dashboard page ────────────────────────────────────────
    @app.route("/")
    def index():
        return HTML_FILE
 
 
    # ── Get all APIs (now includes paused, notes, tag, thresholds) ──
    @app.route("/api/apis", methods=["GET"])
    def get_apis():
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT id, name, url, interval, active, paused, notes, tag, warn_ms, critical_ms, created FROM apis ORDER BY name"
        ).fetchall()
        conn.close()
        cols = ["id","name","url","interval","active","paused","notes","tag","warn_ms","critical_ms","created"]
        return jsonify([dict(zip(cols, r)) for r in rows])
 
 
    # ── Add a new API (accepts notes, tag, thresholds) ────────
    @app.route("/api/apis", methods=["POST"])
    def add_api():
        data = request.get_json()
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""
                INSERT INTO apis (name, url, interval, notes, tag, warn_ms, critical_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"],
                data["url"],
                data.get("interval",    30),
                data.get("notes",       ""),
                data.get("tag",         "General"),
                data.get("warn_ms",     800),
                data.get("critical_ms", 2000),
            ))
            conn.commit()
            conn.close()
            return jsonify({"message": "API added! 🎉"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "URL already exists"}), 400
 
 
    # ── Delete an API ─────────────────────────────────────────
    @app.route("/api/apis/<int:api_id>", methods=["DELETE"])
    def delete_api(api_id):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM checks WHERE api_id=?", (api_id,))
        conn.execute("DELETE FROM apis   WHERE id=?",     (api_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Removed ✅"})
 
 
    # ── FEATURE 2: Pause or Resume an API ─────────────────────
    # When paused=1, the background monitor SKIPS this API.
    # Think of it like pressing "pause" on a video — nothing
    # gets deleted, just temporarily stopped.
    @app.route("/api/apis/<int:api_id>/pause", methods=["POST"])
    def pause_api(api_id):
        # Read current paused state
        conn = sqlite3.connect(DB_PATH)
        row  = conn.execute("SELECT paused, name FROM apis WHERE id=?", (api_id,)).fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "API not found"}), 404
 
        current_paused, name = row
        new_paused = 0 if current_paused else 1   # Toggle: 0→1 or 1→0
 
        conn.execute("UPDATE apis SET paused=? WHERE id=?", (new_paused, api_id))
        conn.commit()
        conn.close()
 
        action = "Paused ⏸️" if new_paused else "Resumed ▶️"
        return jsonify({"message": f"{action} — {name}", "paused": new_paused})
 
 
    # ── FEATURE 3: Update notes and tag for an API ────────────
    # Like adding a sticky note to an API card.
    @app.route("/api/apis/<int:api_id>/notes", methods=["POST"])
    def update_notes(api_id):
        data  = request.get_json()
        notes = data.get("notes", "")
        tag   = data.get("tag",   "General")
        conn  = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE apis SET notes=?, tag=? WHERE id=?", (notes, tag, api_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Notes saved! 📝"})
 
 
    # ── FEATURE 1: Update thresholds for an API ───────────────
    # warn_ms     = orange warning badge (e.g. >800ms)
    # critical_ms = red critical badge   (e.g. >2000ms)
    @app.route("/api/apis/<int:api_id>/thresholds", methods=["POST"])
    def update_thresholds(api_id):
        data        = request.get_json()
        warn_ms     = int(data.get("warn_ms",     800))
        critical_ms = int(data.get("critical_ms", 2000))
        conn        = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE apis SET warn_ms=?, critical_ms=? WHERE id=?",
            (warn_ms, critical_ms, api_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Thresholds updated! ⏱️"})
 
 
    # ── Manual check now ──────────────────────────────────────
    @app.route("/api/check/<int:api_id>", methods=["POST"])
    def manual_check(api_id):
        conn = sqlite3.connect(DB_PATH)
        row  = conn.execute("SELECT url FROM apis WHERE id=?", (api_id,)).fetchone()
        conn.close()
        if not row:
            return jsonify({"error": "API not found"}), 404
        result = check_api(api_id, row[0])
        return jsonify(result)
 
 
    # ── Global stats cards ────────────────────────────────────
    @app.route("/api/stats")
    def global_stats():
        conn = sqlite3.connect(DB_PATH)
        total_apis   = conn.execute("SELECT COUNT(*) FROM apis WHERE active=1").fetchone()[0]
        paused_count = conn.execute("SELECT COUNT(*) FROM apis WHERE paused=1").fetchone()[0]
        total_checks = conn.execute("SELECT COUNT(*) FROM checks").fetchone()[0]
        avg_response = conn.execute(
            "SELECT AVG(response_ms) FROM checks WHERE response_ms IS NOT NULL"
        ).fetchone()[0]
        success_rate = conn.execute(
            "SELECT ROUND(AVG(success)*100,1) FROM checks WHERE checked_at > datetime('now','-1 hour')"
        ).fetchone()[0]
        failing = conn.execute("""
            SELECT COUNT(DISTINCT api_id) FROM checks
            WHERE success=0 AND checked_at > datetime('now','-10 minutes')
        """).fetchone()[0]
        conn.close()
        return jsonify({
            "total_apis":   total_apis,
            "paused_count": paused_count,
            "total_checks": total_checks,
            "avg_response": round(avg_response, 1) if avg_response else 0,
            "success_rate": success_rate or 100,
            "failing_now":  failing,
        })
 
 
    # ── API summary table (now includes paused, tag, thresholds) ──
    @app.route("/api/summary")
    def api_summary():
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT
                a.id, a.name, a.url,
                a.paused, a.notes, a.tag,
                a.warn_ms, a.critical_ms,
                COUNT(c.id)                  AS total_checks,
                ROUND(AVG(c.success)*100, 1) AS uptime_pct,
                ROUND(AVG(c.response_ms), 1) AS avg_ms,
                ROUND(MIN(c.response_ms), 1) AS min_ms,
                ROUND(MAX(c.response_ms), 1) AS max_ms,
                MAX(c.checked_at)            AS last_checked,
                (SELECT success     FROM checks WHERE api_id=a.id ORDER BY id DESC LIMIT 1) AS last_success,
                (SELECT status_code FROM checks WHERE api_id=a.id ORDER BY id DESC LIMIT 1) AS last_status
            FROM apis a
            LEFT JOIN checks c ON a.id = c.api_id
            WHERE a.active = 1
            GROUP BY a.id
        """).fetchall()
        conn.close()
        cols = ["id","name","url","paused","notes","tag","warn_ms","critical_ms",
                "total_checks","uptime_pct","avg_ms","min_ms","max_ms",
                "last_checked","last_success","last_status"]
        return jsonify([dict(zip(cols, r)) for r in rows])
 
 
    # ── History (chart data) ──────────────────────────────────
    @app.route("/api/history/<int:api_id>")
    def api_history(api_id):
        limit = request.args.get("limit", 50, type=int)
        conn  = sqlite3.connect(DB_PATH)
        rows  = conn.execute("""
            SELECT status_code, response_ms, success, error_msg, checked_at
            FROM checks WHERE api_id=? ORDER BY checked_at DESC LIMIT ?
        """, (api_id, limit)).fetchall()
        conn.close()
        cols = ["status_code","response_ms","success","error_msg","checked_at"]
        return jsonify([dict(zip(cols, r)) for r in reversed(rows)])
 
 
    # ── Heatmap (30-day uptime) ───────────────────────────────
    @app.route("/api/heatmap/<int:api_id>")
    def api_heatmap(api_id):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT DATE(checked_at) AS day,
                   ROUND(AVG(success)*100,0) AS uptime_pct,
                   COUNT(*) AS total_checks
            FROM checks WHERE api_id=?
              AND checked_at >= DATE('now', '-30 days')
            GROUP BY DATE(checked_at) ORDER BY day ASC
        """, (api_id,)).fetchall()
        conn.close()
        return jsonify([dict(zip(["day","uptime_pct","total_checks"], r)) for r in rows])
 
 
    # ── 24h trend line ────────────────────────────────────────
    @app.route("/api/trend/<int:api_id>")
    def api_trend(api_id):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("""
            SELECT strftime('%Y-%m-%d %H:00', checked_at) AS hour,
                   ROUND(AVG(response_ms), 1) AS avg_ms,
                   COUNT(*) AS total_checks,
                   ROUND(AVG(success)*100,1) AS success_rate
            FROM checks
            WHERE api_id=?
              AND checked_at > datetime('now', '-24 hours')
              AND response_ms IS NOT NULL
            GROUP BY strftime('%Y-%m-%d %H', checked_at)
            ORDER BY hour
        """, (api_id,)).fetchall()
        conn.close()
        return jsonify([dict(zip(["hour","avg_ms","total_checks","success_rate"], r)) for r in rows])
 
 
    # ── Export CSV ────────────────────────────────────────────
    # These routes return proper CSV responses with headers that
    # force the browser to download a .csv file, not open as HTML.
    @app.route("/api/export/checks")
    def export_checks():
        resp = export_checks_to_csv()
        resp.headers["Content-Disposition"] = 'attachment; filename="api_checks_export.csv"'
        resp.headers["Content-Type"]        = "text/csv; charset=utf-8"
        return resp
 
    @app.route("/api/export/summary")
    def export_summary():
        resp = export_summary_to_csv()
        resp.headers["Content-Disposition"] = 'attachment; filename="api_summary_export.csv"'
        resp.headers["Content-Type"]        = "text/csv; charset=utf-8"
        return resp
 
 
    # ── Alert settings (save) ─────────────────────────────────
    @app.route("/api/alerts/settings", methods=["POST"])
    def save_alert_settings():
        data = request.get_json()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM alert_settings")
        conn.execute("""
            INSERT INTO alert_settings (to_email, smtp_host, smtp_port, smtp_user, smtp_pass, enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["to_email"], data.get("smtp_host","smtp.gmail.com"),
              data.get("smtp_port",587), data["smtp_user"], data["smtp_pass"],
              data.get("enabled",1)))
        conn.commit()
        conn.close()
        return jsonify({"message": "Alert settings saved! 📧"})
 
 
    # ── Alert settings (get) ──────────────────────────────────
    @app.route("/api/alerts/settings", methods=["GET"])
    def get_alert_settings():
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT to_email, smtp_host, smtp_port, smtp_user, enabled FROM alert_settings LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return jsonify({})
        return jsonify(dict(zip(["to_email","smtp_host","smtp_port","smtp_user","enabled"], row)))
