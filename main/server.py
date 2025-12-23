from flask import Flask, request, jsonify
import json
import os
from threading import Lock

app = Flask(__name__)

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "logs.jsonl")

# إنشاء مجلد data إذا ما كان موجود
os.makedirs(DATA_DIR, exist_ok=True)

# Lock لمنع التعارض بين الطلبات
file_lock = Lock()

# نخزن record_id اللي انحفظت (runtime dedup)
seen_record_ids = set()

def save_event(event: dict):
    """
    حفظ الحدث مباشرة في logs.jsonl بدون تكرار
    """
    record_id = event.get("record_id") or event.get("recordId")

    # لو ما فيه record_id نخزنه على مسؤوليتنا
    if record_id is not None:
        if record_id in seen_record_ids:
            return
        seen_record_ids.add(record_id)

    with file_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


@app.route("/logs", methods=["POST"])
def receive_logs():
    event = request.get_json(silent=True)

    if not event:
        return jsonify({"status": "invalid json"}), 400

    # 🔒 نحفظ الحدث فورًا (قبل أي منطق)
    save_event(event)

    # 🛑 منطقك الحالي (ما تغير)
    if event.get("event_id") == 4625:
        print("\n🚨 FAILED LOGIN DETECTED 🚨")
        print(f"Time     : {event.get('timestamp') or event.get('time')}")
        print(f"Machine  : {event.get('machine')}")
        print(f"RecordID : {event.get('record_id') or event.get('recordId')}")
        print("-" * 30)

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
