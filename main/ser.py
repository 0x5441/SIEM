from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/logs", methods=["POST"])
def receive_logs():
    event = request.json

    if event.get("event_id") == 4625:
        print("\n🚨 FAILED LOGIN DETECTED 🚨")
        print(f"Time     : {event.get('time')}")
        print(f"Machine  : {event.get('machine')}")
        print(f"RecordID : {event.get('recordId')}")
        print("-" * 30)

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
