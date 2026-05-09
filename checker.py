import time
import sqlite3
import requests
from database import DB_PATH
#from alerter import check_and_alert

def check_api(api_id, url):
    
    start = time.time()

    try:
        response = requests.get(url, timeout=10)
        elapsed_ms = (time.time() - start) * 1000

        result = {
            "api_id": api_id,
            "status_code": response.status_code,
            "response_ms": round(elapsed_ms, 2),
            "success": 1 if response.status_code < 400 else 0,
            "error_msg": None,
        }

    except requests.exceptions.Timeout:
        result = {
            "api_id": api_id, "status_code": None,
            "response_ms": 10000, "success": 0,
            "error_msg": "Timeout - took to long"
        }

    except requests.exceptions.ConnectionError:
        result = {
            "api_id": api_id, "status_code": None,
            "response_ms": 0, "success": 0,
            "error_msg": "Connection Error - couldn't reach API"
        }

    except Exception as e:
        result = {
            "api_id": api_id, "status_code": None,
            "response_ms": 0, "success": 0,
            "error_msg": str(e)}

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
       INSERT INTO checks (api_id, status_code, response_ms, success, error_msg)
       VALUES (:api_id, :status_code, :response_ms, :success, :error_msg)
       """, result)

    conn.commit()
    conn.close()

    return result

def background_monitor():
    counters = {}

    print("🔄 Background monitoring started...")

    while True:
        conn = sqlite3.connect(DB_PATH)
        apis = conn.execute(
            "SELECT id, name, url, interval FROM apis WHERE active=1"
        ).fetchall()
        conn.close()


        for api_id, name, url, interval in apis:
            counters[api_id] = counters.get(api_id, 0) + 1

            if counters[api_id] >= interval:
                counters[api_id] = 0
                result = check_api(api_id, url)

                icon = "✅" if result["success"] else "❌"
                ms = f"{result['response_ms']}ms" if result["response_ms"] else "N/A"
                print(f"  {icon} {name} -> {ms}")
                
                #check_and_alert(api_id, name, url, result)
        time.sleep(1) 
