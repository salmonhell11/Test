import os
import time
import logging
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from datetime import datetime
from typing import List, Dict, Any, Union

from sms_service import SMSService
from email_service import EmailService

app = Flask(__name__)
sms = SMSService()
email = EmailService()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <title>SMS-tjänst</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                color: #333;
                max-width: 700px;
                margin: 40px auto;
                padding: 20px;
                border-radius: 10px;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #198754;
            }
            code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 4px;
            }
            ul {
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <h1>✅ SMS-tjänsten är igång!</h1>
        <p>För att skicka ett SMS, gör ett anrop till <code>/send</code> med följande URL-parametrar:</p>
        <ul>
            <li><b>telnr</b>: Telefonnummer i internationellt format (ex: 46701234567)</li>
            <li><b>message</b>: Själva meddelandet</li>
            <li><b>action</b>: Måste vara <code>sms</code></li>
            <li><b>subject</b>: (valfritt) Ämnesrad</li>
            <li><b>id</b>: (valfritt) Identifierare för avsändaren</li>
        </ul>
        <p><b>Exempel:</b></p>
        <code>/send?telnr=46701234567&message=Test&action=sms</code>
        <p style="margin-top: 30px; font-size: 0.9em; color: #666;">Powered by Flask & HelloSMS</p>
    </body>
    </html>
    '''

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, f'avisering_log_{datetime.now().strftime("%Y%m%d")}.log'),
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

request_times: List[float] = []
RATE_WINDOW = 60

def check_rate_limit(limit: int) -> bool:
    current_time = time.time()
    request_times[:] = [t for t in request_times if current_time - t < RATE_WINDOW]
    if len(request_times) >= limit:
        return False
    request_times.append(current_time)
    return True

@app.route('/send', methods=['POST'])
def send_notification() -> Union[Dict[str, Any], tuple[Dict[str, Any], int]]:
    data = request.get_json(force=True)
    action = data.get("action")
    to = data.get("to", "").strip()
    from_ = data.get("from", "").strip()
    message = data.get("message")
    subject = data.get("subject", "Notifiering")
    sender_id = data.get("id", "anonymous")

    if not check_rate_limit(sms.config["rate_limit"]):
        return jsonify({"status": "error", "error": "Rate limit exceeded"}), 429

    if not action or not to or not message:
        return jsonify({"status": "error", "error": "Fält saknas (to, message, action)"}), 400

    if action == "sms":
        if not sms.validate_request(to, message, subject, from_):
            return jsonify({"status": "error", "error": "Ogiltigt telefonnummer eller meddelande"}), 400
        result = sms.send_notification(to, message, subject, from_)
    elif action == "email":
        if not email.validate_request(to, message, subject, from_):
            return jsonify({"status": "error", "error": "Ogiltig e-postadress eller meddelande"}), 400
        result = email.send_notification(to, message, subject, from_)
    else:
        return jsonify({"status": "error", "error": "Ogiltig åtgärd"}), 400

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "to": to,
        "from": from_,
        "subject": subject,
        "status": result.get("status"),
        "id": sender_id
    }

    logging.info("Avisering: %s", log_entry)
    return jsonify({**result, "log": log_entry})
