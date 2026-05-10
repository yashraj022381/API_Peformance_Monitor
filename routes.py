import sqlite3
from flask import jsonify, render_template, request
from database import DB_PATH
from checker  import check_api
from exporter import export_checks_to_csv, export_summary_to_csv

 
def register_routes(app):
 
    # ── Dashboard page ────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")
 
 
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
