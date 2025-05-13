from typing import Dict, Any, Optional

class AviseringService:
    def validate_request(self, to: str, message: str, subject: Optional[str] = None, from_: Optional[str] = None, **kwargs) -> bool:
        raise NotImplementedError

    def send_notification(self, to: str, message: str, subject: Optional[str] = None, from_: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError