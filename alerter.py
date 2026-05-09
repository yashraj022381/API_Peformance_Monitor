import sqlite3
import smtplib                          # Python's built-in email sender
from email.mime.text import MIMEText    # Helps format the email
from datetime import datetime, timedelta
from database import DB_PATH
 
 
def should_send_alert(api_id):
    """
    Check: did we ALREADY send an alert for this API in the last 10 minutes?
    If yes → don't send again (no spam!)
    If no  → ok to send
    
    Think of it like a snooze button on an alarm clock ⏰
    """
    conn = sqlite3.connect(DB_PATH)
    recent = conn.execute("""
        SELECT COUNT(*) FROM alert_log
        WHERE api_id = ?
          AND sent_at > datetime('now', '-10 minutes')
    """, (api_id,)).fetchone()[0]
    conn.close()
    return recent == 0   # True = ok to send, False = too soon
 
 
def send_alert_email(api_name, url, error_msg):
    """
    Send an email saying "Hey! This API is down!"
    
    Steps:
    1. Read email settings from the database
    2. Write the email message
    3. Connect to the email server (like a post office)
    4. Send it!
    """
    conn = sqlite3.connect(DB_PATH)
    settings = conn.execute(
        "SELECT to_email, smtp_host, smtp_port, smtp_user, smtp_pass FROM alert_settings WHERE enabled=1 LIMIT 1"
    ).fetchone()
    conn.close()
 
    if not settings:
        return False   # No email settings saved yet → skip
 
    to_email, smtp_host, smtp_port, smtp_user, smtp_pass = settings
 
    # Write the email body (what the email will say)
    body = f"""
    ⚠️  API ALERT — {api_name} is DOWN!
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    API Name : {api_name}
    URL      : {url}
    Error    : {error_msg or 'No response'}
    Time     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Login to your dashboard to see details:
    http://localhost:5000
    """
 
    # Build the email object (like putting a letter in an envelope)
    msg = MIMEText(body)
    msg["Subject"] = f"🚨 API Down: {api_name}"
    msg["From"]    = smtp_user
    msg["To"]      = to_email
 
    try:
        # Connect to the email server and send
        # smtplib is like walking to the post office 📮
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()                        # Secure the connection
        server.login(smtp_user, smtp_pass)       # Log in to email account
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
 
        # Write in alert_log so we don't spam
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO alert_log (api_id, api_name, message) VALUES (?, ?, ?)",
            (0, api_name, f"Alert sent: {error_msg}")
        )
        conn.commit()
        conn.close()
 
        print(f"  📧 Alert sent for {api_name} → {to_email}")
        return True
 
    except Exception as e:
        print(f"  ❌ Email failed: {e}")
        return False
 
 
def check_and_alert(api_id, api_name, url, check_result):
    """
    Called after every API check.
    Decides: should we send an alert right now?
    
    Rules:
    - Only alert if the check FAILED
    - Only alert if we haven't alerted in the last 10 minutes
    """
    if check_result["success"] == 0:           # API is down
        if should_send_alert(api_id):           # Not spamming?
            send_alert_email(
                api_name,
                url,
                check_result.get("error_msg")
            )
