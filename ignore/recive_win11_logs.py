from flask import Flask, request, jsonify

app = Flask(__name__)

def classify_event(event):
    if event == "failed_login":
        return "HIGH"
    elif event == "success_login":
        return "LOW"
    else:
        return "MEDIUM"

@app.route("/logs", methods=["POST"])
def receive_logs():
    data = request.get_json(force=True)

    event = data.get("event", "unknown")
    severity = classify_event(event)

    data["severity"] = severity

    print("LOG RECEIVED:")
    print(data)
    print("------------")

    return jsonify({"status": "ok", "severity": severity}), 200

app.run(host="0.0.0.0", port=8000)
