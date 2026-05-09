# Panel 1 — Average Response Time per API (Bar chart)
QUERY_AVG_RESPONSE = """
SELECT
    a.name           AS metric,
    AVG(c.response_ms) AS "Avg Response (ms)"
FROM checks c
JOIN apis a ON a.id = c.api_id
WHERE c.checked_at > datetime('now', '-1 hour')
  AND c.response_ms IS NOT NULL
GROUP BY a.name
ORDER BY AVG(c.response_ms) DESC;
"""
 
# Panel 2 — Uptime Percentage (Stat / Gauge)
QUERY_UPTIME = """
SELECT
    a.name AS metric,
    ROUND(AVG(c.success) * 100, 1) AS "Uptime %"
FROM checks c
JOIN apis a ON a.id = c.api_id
WHERE c.checked_at > datetime('now', '-24 hours')
GROUP BY a.name;
"""
 
# Panel 3 — Response Time Over Time (Time series)
QUERY_TIMESERIES = """
SELECT
    strftime('%Y-%m-%dT%H:%M:%SZ', c.checked_at) AS time,
    c.response_ms                                  AS value,
    a.name                                         AS metric
FROM checks c
JOIN apis a ON a.id = c.api_id
WHERE c.checked_at > datetime('now', '-3 hours')
  AND c.response_ms IS NOT NULL
ORDER BY c.checked_at;
"""
 
# Panel 4 — Error Count Last Hour (Stat)
QUERY_ERRORS = """
SELECT COUNT(*) AS "Errors (last hour)"
FROM checks
WHERE success = 0
  AND checked_at > datetime('now', '-1 hour');
"""
 
# Panel 5 — Recent Checks Log (Table)
QUERY_LOG = """
SELECT
    c.checked_at        AS "Time",
    a.name              AS "API",
    c.status_code       AS "HTTP Code",
    c.response_ms       AS "Response (ms)",
    CASE c.success WHEN 1 THEN '✅ OK' ELSE '❌ FAIL' END AS "Status",
    c.error_msg         AS "Error"
FROM checks c
JOIN apis a ON a.id = c.api_id
ORDER BY c.checked_at DESC
LIMIT 50;
"""
 
print("📊 Grafana SQL queries ready!")
