from datetime import datetime
import requests

def log_crm_heartbeat():
    now = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    try:
        response = requests.post('http://localhost:8000/graphql', json={'query': '{ hello }'})
        status = "OK" if response.status_code == 200 else "FAIL"
    except Exception:
        status = "ERROR"
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(f"{now} CRM is alive - Status: {status}\n")
