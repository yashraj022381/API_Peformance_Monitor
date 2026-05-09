import sqlite3, csv, io
from flask import Response
from database import DB_PATH
 

def _make_csv_response(csv_text: str, filename: str) -> Response:
    return Response(
        csv_text,
        status=200,
        mimetype="text/csv",
        headers={
            "Content-Type":       "text/csv; charset=utf-8",
            "Content-Disposition":  f"attachment; filename=\"{filename} \"",
            "X-Content-Type-Options": "nosniff",
        }
    )

def export_checks_to_csv() -> Response:
    """Export all check history as a downloadable CSV file."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT c.checked_at     AS "Time",
               a.name           AS "API Name",
               a.url            AS "URL",
               c.response_ms    AS "Response (ms)",
               c.status_code    AS "HTTP Status",
               CASE c.success
                   WHEN 1 THEN 'OK'
                   ELSE 'FAILED' END     AS "Result",
               COALESCE(c.error_msg, '') AS "Error Message"
        FROM checks c
        JOIN apis a ON a.id = c.api_id
        ORDER BY c.checked_at DESC
    """).fetchall()
    conn.close()
 
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Time","API Name","URL","Response (ms)",
                     "HTTP Status","Result","Error Message"])
    for row in rows:
        writer.writerow(row)
        
    return _make_csv_response(output.getvalue(), "api_checks_export.csv")
 
 
def export_summary_to_csv() -> Response:
    """Export one-row-per-API summary stats."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT
            a.name                      AS "API Name",
            a.url                       AS "URL",
            a.tag                       AS "Tag",
            COUNT(c.id)                 AS "Total Checks",
            ROUND(AVG(c.success)*100,1) AS "Uptime %",
            ROUND(AVG(c.response_ms),1) AS "Avg Response (ms)",
            ROUND(MIN(c.response_ms),1) AS "Fastest (ms)",
            ROUND(MAX(c.response_ms),1) AS "Slowest (ms)",
            MAX(c.checked_at)           AS "Last Checked",
            CASE a.paused
                WHEN 1 THEN 'Yes'
                ELSE 'No'
            END                         AS "Paused",
            COALESCE(a.notes, '')       AS "Notes"
        FROM apis a
        LEFT JOIN checks c ON a.id=c.api_id
        GROUP BY a.id
    """).fetchall()
    conn.close()
 
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["API Name","URL","Total Checks",
                     "Uptime %", "Avg Response ms","Fastest ms",
                     "Slowest ms","Last Checked", "Paused", "Notes"])
    for row in rows:
        writer.writerow(row)
    return _make_csv_response(output.getvalue(), "api_summary_export.csv")
