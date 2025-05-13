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

from flask import send_file

@app.route("/")
def index():
    return send_file("index.html")
