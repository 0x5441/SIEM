import json
import re
import time
from datetime import datetime

LOG_FILE = "data/logs.jsonl"
CHECK_INTERVAL = 10  # ثواني

print("\n\033[94m[SIEM] Live Failed Login Monitor Started\033[0m")
print("\033[94m[SIEM] Monitoring from now (no old logs)\033[0m\n")

# وقت تشغيل السكربت (نقطة البداية)
start_time = datetime.utcnow()

def parse_time(raw_time):
    if not raw_time:
        return None

    # Windows format: /Date(1766424956185)/
    if isinstance(raw_time, str) and raw_time.startswith("/Date("):
        ms = int(raw_time.replace("/Date(", "").replace(")/", ""))
        return datetime.fromtimestamp(ms / 1000)

    # ISO format
    try:
        return datetime.fromisoformat(raw_time.replace("Z", ""))
    except:
        return None


last_seen_line = 0

while True:
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = lines[last_seen_line:]
        last_seen_line = len(lines)

        for line in new_lines:
            event = json.loads(line)

            # نركز فقط على Failed Login
            if event.get("event_id") != 4625:
                continue

            raw_time = event.get("timestamp") or event.get("@server_time")
            event_time = parse_time(raw_time)

            # تجاهل أي شيء قبل تشغيل السكربت
            if not event_time or event_time < start_time:
                continue

            # استخراج اسم المستخدم
            message = event.get("message", "")
            user = "UNKNOWN"
            match = re.search(r"Account Name:\s+(\S+)", message)
            if match:
                user = match.group(1)

            formatted_time = event_time.strftime("%Y-%m-%d %H:%M:%S")

            # ===== ALERT =====
            print("\n\033[91m" + "=" * 60)
            print("🚨🚨🚨  SECURITY ALERT  🚨🚨🚨")
            print("=" * 60)
            print(f"User : {user}")
            print(f"Time : {formatted_time}")
            print("Event: FAILED LOGIN DETECTED")
            print("=" * 60 + "\033[0m\n")

    except Exception as e:
        print("\033[93m[SIEM WARNING]\033[0m Error reading logs:", e)

    time.sleep(CHECK_INTERVAL)
