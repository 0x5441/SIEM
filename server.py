from flask import Flask, request, jsonify
import json, os, datetime

app = Flask(__name__)

LOG_DIR = "data"
LOG_FILE = os.path.join(LOG_DIR, "logs.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)

@app.route("/logs", methods=["POST"])
def receive_logs():
    data = request.get_json(force=True)

    # أضف timestamp من السيرفر لو ما موجود
    if "server_time" not in data:
        data["server_time"] = datetime.datetime.utcnow().isoformat() + "Z"

    # احفظ كسطر JSON
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
