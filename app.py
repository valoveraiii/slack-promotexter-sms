from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime 

app = Flask(__name__)

def log_to_google_sheets(direction, user, phone, message):
    webhook_url = os.environ.get("GOOGLE_SHEET_WEBHOOK")

    if not webhook_url:
        print("⚠️ No Google Sheet webhook URL set.")
        return

    payload = {
        "direction": direction,
        "user": user,
        "phone": phone,
        "message": message,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    response = requests.post(webhook_url, json=payload)
    print(f"📋 Google Sheet log status: {response.status_code}")


@app.route('/slack', methods=['POST'])
def send_sms():
    text = request.form.get('text', '')
    user = request.form.get('user_name')

    if not text or ' ' not in text:
        return jsonify({'text': '❌ Usage: /sendsms <number> <message>'}), 200

    number, message = text.split(' ', 1)

    payload = {
        "apiKey": os.environ['PROMOTEXTER_API_KEY'],
        "apiSecret": os.environ['PROMOTEXTER_API_SECRET'],
        "from": "09221200615",
        "to": number,
        "text": message
    }
    print(payload)

    res = requests.post('https://api.promotexter.com/sms/send', json=payload)

    if res.status_code == 200:
        log_to_google_sheets("outbound", user, number, message)
        return jsonify({'text': f'✅ SMS sent to {number} by {user}'}), 200
    else:
        return jsonify({'text': f'❌ Failed to send SMS. {res.text}'}), 200

@app.route('/')
def home():
    return 'Promotexter SMS Bot is live!'

@app.route('/inbound', methods=['GET', 'POST'])
def receive_sms():
    print("🟡 Raw query string:", request.query_string)
    print("🟡 Full request args:", request.args)

    sender = request.args.get('from')
    message = request.args.get('message')

    print(f"📩 Incoming SMS from {sender}: {message}")

    slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
    if slack_webhook_url and sender and message:
        slack_payload = {
            "text": f"📨 *New SMS from {sender}:*\n>{message}"
        }
        slack_response = requests.post(slack_webhook_url, json=slack_payload)
        print(f"📤 Slack webhook response: {slack_response.status_code} - {slack_response.text}")
    else:
        print("⚠️ Missing sender or message — not sent to Slack")

    return jsonify({'status': 'received'}), 200


if __name__ == '__main__':
    app.run()
