import json
import re
from datetime import datetime

log_file = "data/logs.jsonl"
last_failed = None

with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        event = json.loads(line)
        if event.get("event_id") == 4625:
            last_failed = event

if not last_failed:
    print("No failed login found")
    exit()

# ===== معالجة الوقت =====
raw_time = last_failed.get("timestamp") or last_failed.get("@server_time")
formatted_time = "UNKNOWN"

# صيغة ويندوز: /Date(1766424956185)/
if isinstance(raw_time, str) and raw_time.startswith("/Date("):
    ms = int(raw_time.replace("/Date(", "").replace(")/", ""))
    formatted_time = datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M:%S")

# صيغة ISO
elif isinstance(raw_time, str):
    try:
        formatted_time = datetime.fromisoformat(raw_time.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
    except:
        formatted_time = raw_time

# ===== استخراج اليوزر =====
message = last_failed.get("message", "")
user = "UNKNOWN"

match = re.search(r"Account Name:\s+(\S+)", message)
if match:
    user = match.group(1)

print("=== Last Failed Login (from SIEM) ===")
print(f"User : {user}")
print(f"Time : {formatted_time}")
