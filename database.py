import sqlite3

DB_PATH = "monitor.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS apis (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            url         TEXT NOT NULL UNIQUE,
            interval    INTEGER DEFAULT 30,
            active      INTEGER DEFAULT 1,
            paused      INTEGER DEFAULT 0,
            notes       TEXT    DEFAULT '',
            tag         TEXT    DEFAULT 'General',
            warn_ms     INTEGER DEFAULT 800,
            critical_ms INTEGER DEFAULT 2000,
            created     TEXT DEFAULT (datetime('now'))
        )
    """)

    for col, definition in [
        ("paused",      "INTEGER DEFAULT 0"),
        ("notes",       "TEXT DEFAULT '' "),
        ("tag",         "TEXT DEFAULT 'General'"),    
        ("warn_ms",     "INTEGER DEFAULT 800"),
        ("critical_ms", "INTEGER DEFAULT 2000"),
    ]:
        try:
            conn.execute(f"ALTER TABLE apis ADD COLUMN {col} {definition}")
        except Exception:
            pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id      INTEGER NOT NULL,
            status_code INTEGER,
            response_ms REAL,
            success     INTEGER,
            error_msg   TEXT,
            checked_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alert_settings (
            id        INTEGER PRIMARY KEY,
            to_email  TEXT,
            smtp_host TEXT DEFAULT 'smtp.gmail.com',
            smtp_port INTEGER DEFAULT 587,
            smtp_user TEXT,
            smtp_pass TEXT,
            enabled   INTEGER DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alert_log (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id   INTEGER,
            api_name TEXT,
            message  TEXT,
            sent_at  TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.execute("""
        INSERT OR IGNORE INTO apis (name, url, interval, tag, warn_ms, critical_ms) VALUES
        ('JSONPlaceholder', 'https://jsonplaceholder.typicode.com/posts/1', 30, 'Testing', 800, 2000),
        ('HTTPBin',         'https://httpbin.org/status/200',               45, 'Testing', 800, 2000),
        ('GitHub API',      'https://api.github.com',                       60, 'Production', 1000, 3000),
        ('Public IP',       'https://api.ipify.org?format=json',            30, 'General', 800, 2000)
    """)

    conn.commit()
    conn.close()
    print("✅ Database ready!")
