from flask import Flask, request, jsonify
import os
import json
import datetime

app = Flask(__name__)

# ===== Paths =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "logs.jsonl")

os.makedirs(DATA_DIR, exist_ok=True)

# ===== Index (اختياري للتأكد إن السيرفر شغال) =====
@app.route("/", methods=["GET"])
def index():
    return "SIEM Server Running", 200

# ===== Logs Endpoint =====
@app.route("/logs", methods=["POST"])
def receive_logs():
    try:
        data = request.get_json(force=True)

        saved_count = 0

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            # لو جا Array من PowerShell
            if isinstance(data, list):
                for event in data:
                    event["@server_time"] = datetime.datetime.utcnow().isoformat() + "Z"
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
                    saved_count += 1
            # لو جا Event واحد
            elif isinstance(data, dict):
                data["@server_time"] = datetime.datetime.utcnow().isoformat() + "Z"
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
                saved_count = 1
            else:
                raise ValueError("Unsupported JSON format")

        print(f"[INFO] Saved {saved_count} log(s)")
        return jsonify({"status": "ok", "saved": saved_count}), 200

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"status": "error", "message": str(e)}), 500


# ===== Main =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
