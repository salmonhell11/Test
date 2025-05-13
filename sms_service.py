import base64
import requests
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from config import HELLOSMS_CONFIG
from avisering_interface import AviseringService

class SMSService(AviseringService):
    def __init__(self, config=None):
        self.config = config or HELLOSMS_CONFIG
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=self.config["max_retries"])
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.auth = base64.b64encode(f"{self.config['username']}:{self.config['password']}".encode()).decode()

    def validate_request(self, to: str, message: str, subject: Optional[str] = None, from_: Optional[str] = None, **kwargs) -> bool:
        if not to or not message:
            return False
        if len(message) > self.config["max_message_length"]:
            return False
        return to.startswith("+") and to[1:].isdigit()

    def send_notification(self, to: str, message: str, subject: Optional[str] = None, from_: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Basic {self.auth}",
            "Content-Type": "application/json"
        }

        payload = {
            "to": [to],
            "from": from_ or self.config["sender"],
            "message": message,
            "priority": "high"
        }

        try:
            response = self.session.post(self.config["api_url"], json=payload, headers=headers, timeout=self.config["default_timeout"])
            response.raise_for_status()
            return {"status": "success", "response": response.json()}
        except requests.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "response": getattr(e.response, "json", lambda: {})()
            }
