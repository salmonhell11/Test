import re
import smtplib
import ssl
import socket
import time
import logging
from email.message import EmailMessage
from typing import Dict, Any, Optional
from config import EMAIL_CONFIG
from avisering_interface import AviseringService

class EmailService(AviseringService):
    def __init__(self, config=None):
        self.config = config or EMAIL_CONFIG
        self.logger = logging.getLogger(__name__)
        self.max_retries = self.config["max_retries"]
        self.retry_delay = self.config["retry_delay"]

        if not self.config["username"] or not self.config["password"]:
            raise ValueError("SMTP credentials missing")

    def validate_request(self, to: str, message: str, subject: Optional[str] = None, from_: Optional[str] = None, **kwargs) -> bool:
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(email_pattern, to)) and bool(message)

    def send_notification(self, to: str, message: str, subject: Optional[str] = None, from_: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        msg = EmailMessage()
        msg["From"] = from_ or self.config["sender"]
        msg["To"] = to
        msg["Subject"] = subject or "Notifiering"
        msg.set_content(message)

        retries = 0
        while retries < self.max_retries:
            try:
                with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"], timeout=30) as server:
                    context = ssl._create_unverified_context()
                    server.starttls(context=context)
                    server.login(self.config["username"], self.config["password"])
                    server.send_message(msg)
                return {"status": "success", "response": f"E-post skickad till {to}"}
            except (smtplib.SMTPServerDisconnected, socket.timeout, ssl.SSLError, TimeoutError) as e:
                retries += 1
                self.logger.warning("Connection error (%d/%d): %s", retries, self.max_retries, str(e))
                time.sleep(self.retry_delay)
            except smtplib.SMTPAuthenticationError as e:
                return {"status": "error", "error": f"SMTP-autentisering misslyckades: {str(e)}"}
            except smtplib.SMTPException as e:
                return {"status": "error", "error": f"SMTP-fel: {str(e)}"}
            except (OSError, ValueError) as e:
                return {"status": "error", "error": f"Oväntat fel: {str(e)}"}

        return {"status": "error", "error": "Maximalt antal försök överskridet"}
