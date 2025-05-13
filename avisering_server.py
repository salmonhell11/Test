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

@app.route("/")
def index():
    return '''
    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Aviseringstjänst – SMS & E-post</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"/>
        <style>
            body {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
            }
            .container {
                max-width: 800px;
                background-color: #1e1e1e;
                padding: 2rem;
                margin: 3rem auto;
                border-radius: 12px;
                box-shadow: 0 0 20px rgba(0,0,0,0.6);
            }
            input, textarea, select {
                background-color: #2c2c2c;
                color: #fff;
                border: 1px solid #444;
            }
            .form-label {
                margin-top: 1rem;
            }
            pre {
                background-color: #2c2c2c;
                padding: 1rem;
                border-radius: 8px;
                color: #ccc;
            }
            .spinner-border {
                display: none;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="text-info mb-3">📬 Aviseringstjänst</h1>
            <p class="lead">Skicka SMS eller e-post via ett enkelt API-anrop. Endast <code>POST</code>-anrop med JSON stöds.</p>

            <h4>🧪 Testformulär</h4>
            <form id="notifyForm">
                <label class="form-label" for="action">Typ av utskick</label>
                <select id="action" class="form-select" required>
                    <option value="sms">SMS</option>
                    <option value="email">E-post</option>
                </select>

                <label class="form-label" for="to">Mottagare (to)</label>
                <input type="text" class="form-control" id="to" placeholder="+46701234567 eller mail@ex.se" required>

                <label class="form-label" for="from">Avsändare (from)</label>
                <input type="text" class="form-control" id="from" placeholder="TrafikInfo eller epost@avsandare.se" required>

                <div id="subjectGroup">
                    <label class="form-label" for="subject">Ämne (endast e-post)</label>
                    <input type="text" class="form-control" id="subject" placeholder="Rubrik (frivillig)">
                </div>

                <label class="form-label" for="message">Meddelande</label>
                <textarea class="form-control" id="message" rows="3" required>Hej! Detta är ett test.</textarea>

                <button type="submit" class="btn btn-primary mt-3">📤 Skicka avisering</button>
                <div class="spinner-border text-info" id="spinner" role="status">
                    <span class="visually-hidden">Skickar...</span>
                </div>
            </form>

            <div id="responseBox" class="mt-4"></div>

            <hr/>
            <h5>📦 API-användning</h5>
            <p>Skicka ett <strong>POST</strong>-anrop till <code>/send</code> med följande JSON:</p>
            <pre>{
  "action": "sms" eller "email",
  "to": "+46701234567" eller "e-postadress",
  "from": "TrafikInfo",
  "message": "Meddelandetext",
  "subject": "Rubrik (valfritt, endast e-post)"
}</pre>

            <p class="text-muted small mt-4">Byggd med Flask, HelloSMS och SMTP. © 2025</p>
        </div>

        <script>
            const actionField = document.getElementById("action");
            const subjectGroup = document.getElementById("subjectGroup");

            actionField.addEventListener("change", () => {
                subjectGroup.style.display = actionField.value === "email" ? "block" : "none";
            });

            document.getElementById("notifyForm").addEventListener("submit", async function (e) {
                e.preventDefault();

                const action = document.getElementById("action").value;
                const to = document.getElementById("to").value;
                const from = document.getElementById("from").value;
                const subject = document.getElementById("subject").value;
                const message = document.getElementById("message").value;

                const payload = {
                    action, to, from, message
                };
                if (action === "email") payload.subject = subject;

                document.getElementById("spinner").style.display = "inline-block";

                try {
                    const res = await fetch("/send", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });
                    const json = await res.json();
                    document.getElementById("spinner").style.display = "none";
                    document.getElementById("responseBox").innerHTML = `
                        <div class="alert alert-${json.status === 'success' ? 'success' : 'danger'}">
                            <strong>${json.status.toUpperCase()}:</strong> ${json.response || json.error}
                        </div>`;
                } catch (err) {
                    document.getElementById("spinner").style.display = "none";
                    document.getElementById("responseBox").innerHTML = `
                        <div class="alert alert-danger">❌ Ett tekniskt fel uppstod.</div>`;
                }
            });

            // Init state
            window.onload = () => {
                subjectGroup.style.display = actionField.value === "email" ? "block" : "none";
            };
        </script>
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
