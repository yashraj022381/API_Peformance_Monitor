# API_Peformance_Monitor
- A real-time API health tracking system with live dashboard, Grafana integration, email alerts, and data export.

- Built from scratch using Python, Flask, SQLite, and vanilla JavaScript.
- No paid APIs. No cloud dependencies. Runs entirely on your local machine.
- Features 
· Tech Stack 
· Architecture 
· Getting Started 
· API Reference
</div>


Try API and test it

  Try adding these real free APIs:
  
   Name                    URL                                        Tag
   ___________________________________________________________________________
   Dog Facts API           https://dog-api.kinduff.com/api/facts      Testing
   
   IP Info                 https://ipinfo.io/json                     General
   
   Chuck Norris Jokes      https://api.chucknorris.io/jokes/random    Testing


🚀 Live Demo

You can access the live application here:[https://uncoiled-eclipse-strobe.ngrok-free.dev]

Live Grafana Snapshots here:[http://localhost:3000/goto/bflmdne6tu680e?orgId=1]


📌 Project Overview

 - API Performance Monitor is a full-stack observability tool that tracks the health, response time, and uptime of any HTTP API in real time.
 - It was built entirely from scratch — no monitoring frameworks, no paid services — demonstrating core backend, database, and frontend skills.
 - The system runs a background worker that pings each API on a configurable schedule, stores every result in SQLite, and exposes a live dashboard with charts, heatmaps,       and export features.
 - It also integrates with Grafana for professional-grade visualizations.
   

✨ Features

 Feature                                      Description
 ________________________________________________________________________________________________________________________
 🔴 Live Dashboard                            Real-time stats — success rate, avg response, failing APIs, total checks.
 
 📊 Response Time Charts                      Bar chart showing last 40 checks per API — green = success, red = failure.
 
 📈 30-Day Uptime Heatmap                     GitHub-style heatmap showing daily uptime % for any API.
 
 📉 24-Hour Trend Line                        Hourly average response time over the last 24 hours.
 
 ⏱️ Custom Thresholds                         Per-API warn/critical ms limits with colour-coded speed badges.
 
 ⏸️ Pause / Resume                            Temporarily stop monitoring any API without deleting its history.
 
 📝 Notes & Tags                              Label APIs as Production / Testing / Staging with custom notes.
 
 📧 Email Alerts                              Gmail SMTP alerts when an API goes down, with recovery notification.
 
 📥 CSV Export                                Download all check history or summary report as Excel-compatible CSV.
 
 📊 Grafana Integration                       Connect SQLite datasource for professional dashboards.
 
 🌐 REST API                                  Full JSON API for all operations — queryable from any tool.
 
 🔁 Auto Refresh                              Dashboard auto-refreshes every 15 seconds.


🛠️ Tech Stack
 
  Layer                Technology                               Why
  ________________________________________________________________________________________________________
  Backend              Python 3.10+, Flask 3.0                  Lightweight REST API server.
  
  Database             SQLite 3                                 Zero-setup embedded database.
  
  HTTP Client          Requests                                 Industry-standard HTTP library.
  
  Concurrency          Python threading                         Background monitor alongside web server.
  
  Frontend             Vanilla JS, Chart.js 4                   No framework needed — fast and lightweight.
  
  Visualization        Grafana 10 + frser-sqlite-datasource     Professional dashboards from SQLite.
  
  Tunneling            ngrok                                    Instant public HTTPS URL for sharing.


🏗️ Architecture

  ┌─────────────────────────────────────────────────────────────┐
  │                   API Performance Monitor                   │
  │                                                             │
  │  ┌──────────────┐    HTTP GET     ┌─────────────────────┐   │
  │  │              │ ─────────────▶  │  External APIs      │   │
  │  │  checker.py  │ ◀─────────────  │  (GitHub, etc.)     │   │
  │  │  (Thread)    │  Response+Time  └─────────────────────┘   │
  │  └──────┬───────┘                                           │
  │         │ saves result                                      │
  │         ▼                                                   │
  │  ┌──────────────┐   SQL queries   ┌─────────────────────┐   │
  │  │  monitor.db  │ ◀────────────── │    routes.py        │  │
  │  │  (SQLite)    │ ──────────────▶ │    (Flask REST API) │  │
  │  └──────────────┘   JSON data     └──────────┬──────────┘   │
  │                                              │              │
  │                                    serves HTML+JSON         │
  │                                              ▼              │
  │                              ┌───────────────────────────┐  │
  │                              │     index.html            │  │
  │                              │     (Live Dashboard)      │  │
  │                              │     Chart.js charts       │  │
  │                              └───────────────────────────┘  │
  │                                                             │
  │  ┌──────────────┐   reads monitor.db directly               │
  │  │   Grafana    │ ──────────────────────────────────────▶  │
  │  │  (port 3000) │   frser-sqlite-datasource plugin          │
  │  └──────────────┘                                           │
  └─────────────────────────────────────────────────────────────┘


📂 File Structure

   api-performance-monitor/
   │
   ├── app.py              # 🔘 Entry point — starts Flask + background thread
   ├── database.py         # 📓 DB schema — creates all tables on first run
   ├── checker.py          # 📬 HTTP pinger — times APIs, saves results, patrol loop
   ├── routes.py           # 🌐 All REST API endpoints (15 routes)
   ├── exporter.py         # 📥 CSV export with correct Content-Disposition headers
   ├── alerter.py          # 📧 Gmail SMTP email alerts (down + recovery)
   ├── requirements.txt    # 📦 Python dependencies
   ├── grafana_setup.py    # 📊 Ready-to-use SQL queries for Grafana panels
   │
   └── templates/
       └── index.html      # 🖥️ Single-page dashboard (4 tabs, Chart.js, vanilla JS)


🗄️Database Schema

  sql
  
  -- APIs being monitored
  CREATE TABLE apis (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      name        TEXT NOT NULL,
      url         TEXT NOT NULL UNIQUE,
      interval    INTEGER DEFAULT 30,    -- check every N seconds
      active      INTEGER DEFAULT 1,
      paused      INTEGER DEFAULT 0,     -- pause without deleting history
      notes       TEXT    DEFAULT '',    -- custom notes per API
      tag         TEXT    DEFAULT 'General',  -- Production/Testing/Staging
      warn_ms     INTEGER DEFAULT 800,   -- yellow warning threshold
      critical_ms INTEGER DEFAULT 2000,  -- red critical threshold
      created     TEXT DEFAULT (datetime('now'))
  );

  -- Every single check result
  CREATE TABLE checks (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      api_id      INTEGER NOT NULL,
      status_code INTEGER,        -- HTTP status (200, 404, 500...)
      response_ms REAL,           -- milliseconds to respond
      success     INTEGER,        -- 1 = ok, 0 = failed
      error_msg   TEXT,           -- timeout / connection error message
      checked_at  TEXT DEFAULT (datetime('now'))
  );

  -- Email alert configuration
  CREATE TABLE alert_settings (
      id        INTEGER PRIMARY KEY,
      to_email  TEXT,
      smtp_host TEXT DEFAULT 'smtp.gmail.com',
      smtp_port INTEGER DEFAULT 587,
      smtp_user TEXT,
      smtp_pass TEXT,             -- Gmail App Password (not real password)
      enabled   INTEGER DEFAULT 1
  );

______________________________________________________________________________________

⚡ Getting Started

  Prerequisites
    - Python 3.10 or higher
    - pip (Python package manager)

  Installation
  1. Clone the repository
     bash
     git clone https://github.com/YOUR_USERNAME/api-performance-monitor.git
     cd api-performance-monitor
     
  2. Install dependencies
     bash
     pip install flask requests
     
  3. Start the application
     bash
     python app.py
     
  4. Open the dashboard
     http://localhost:5000
     
  That's it! The app will automatically create the database, add 4 example APIs, and start monitoring them in the background.
 ____________________________________________________________________________________________________________________________
 
   Share Publicly with ngrok
    bash
    # In a second terminal while app.py is running:
    ngrok http 5000
    # You get a public HTTPS link instantly
______________________________________________________________________________________________________________________________
  
   Grafana Integration (Optional)
    bash
    # Install SQLite plugin
    grafana-cli plugins install frser-sqlite-datasource
    sudo systemctl restart grafana-server

   # Open Grafana at http://localhost:3000
   # Add datasource → SQLite → set path to your monitor.db
   # Create panels using SQL from grafana_setup.py


📡 API Reference

  All endpoints return JSON. Base URL: http://localhost:5000

  Method        Endpoint                    Description
  ________________________________________________________________
  GET           /                           Serve the dashboard
  
  GET           /api/apis                   List all monitored APIs
  
  POST          /api/apis                   Add a new API
  
  DELETE        /api/apis/<id>              Remove an API
  
  POST          /api/check/<id>             Trigger an immediate check
  
  POST          /api/apis/<id>/pause        Toggle pause / resume
  
  POST          /api/apis/<id>/notes        Update notes and tag
  
  POST          /api/apis/<id>/thresholds   Update warn/critical ms
  
  GET           /api/stats                  Global stats
  
  GET           /api/summary                Per-API summary with uptime %
  
  GET           /api/history/<id>           Last N checks for one API
  
  GET           /api/heatmap/<id>           30-day daily uptime data
  
  GET           /api/trend/<id>             24-hour hourly avg response
  
  GET           /api/export/checks          Download all checks as CSV
  
  GET           /api/export/summary         Download summary as CSV


Example: Add a new API
   bash
   curl -X POST http://localhost:5000/api/apis \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My Production API",
       "url": "https://api.myapp.com/health",
       "interval": 30,
       "tag": "Production",
       "warn_ms": 500,
       "critical_ms": 1500,
       "notes": "Main backend — check if slow after deployments"
     }'
     
Example: Global stats response
 json
 {
    "total_apis": 4,
    "paused_count": 1,
    "total_checks": 847,
    "avg_response": 1243.5,
    "success_rate": 100.0,
    "failing_now": 0
 }


🧠 What This Project Demonstrates

   Skill                     How it's shown
   __________________________________________________________________________________________
   Python backend            Flask REST API with clean route separation.
   
   Database design           Normalised SQLite schema, migrations, aggregate queries.
   
   Concurrency               threading.Thread running background worker alongside web server.
   
   REST API design           HTTP methods, status codes, JSON, Content-Disposition headers.
   
   Frontend (no framework)   fetch API, Chart.js, DOM manipulation, modals, tab navigation.
   
   Data visualization        Bar charts, line charts, heatmap, Grafana panels.
   
   System design             Single-responsibility modules, separation of concerns.
   
   Problem solving           Fixed ngrok Content-Type, SQLite migration, HTTPS issues.
   

🤝 Contributing

  - Fork the repository
  - Create a feature branch (git checkout -b feature/your-feature)
  - Commit your changes (git commit -m 'Add: your feature description')
  - Push to the branch (git push origin feature/your-feature)
  - Open a Pull Request

  
📄 License
This project is licensed under the MIT License.


⭐ If this project helped you, please give it a star!
Built with Python 🐍 · Flask 🌶️ · SQLite 📓 · Chart.js 📊 · Grafana 📈
</div>
