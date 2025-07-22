from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

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
        "to": number,
        "text": message
    }
    print(payload)

    res = requests.post('https://api.promotexter.com/sms/send', json=payload)

    if res.status_code == 200:
        return jsonify({'text': f'✅ SMS sent to {number} by {user}'}), 200
    else:
        return jsonify({'text': f'❌ Failed to send SMS. {res.text}'}), 200

@app.route('/')
def home():
    return 'Promotexter SMS Bot is live!'

if __name__ == '__main__':
    app.run()
