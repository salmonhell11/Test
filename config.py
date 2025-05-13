import os

HELLOSMS_CONFIG = {
    "username": os.getenv("HELLOSMS_USERNAME", "n6560t812a89486qq3ynzjr0"),
    "password": os.getenv("HELLOSMS_PASSWORD", "agYPySU5ynEQYty6YJy6"),
    "sender": os.getenv("HELLOSMS_SENDER", "TrafikInfo"),
    "default_timeout": int(os.getenv("HELLOSMS_TIMEOUT", "10")),
    "max_retries": int(os.getenv("HELLOSMS_MAX_RETRIES", "3")),
    "api_url": os.getenv("HELLOSMS_API_URL", "https://api.hellosms.se/api/v1/sms/send"),
    "max_message_length": int(os.getenv("HELLOSMS_MAX_LENGTH", "160")),
    "rate_limit": int(os.getenv("HELLOSMS_RATE_LIMIT", "100")),
    "retry_codes": [408, 500, 502, 503, 504]
}

EMAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.strato.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME", "trafikInformation@maddec.eu"),
    "password": os.getenv("SMTP_PASSWORD", "ckswejgf!$kk43"),
    "sender": os.getenv("EMAIL_SENDER", "trafikInformation@maddec.eu"),
    "max_retries": int(os.getenv("SMTP_MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("SMTP_RETRY_DELAY", "5"))
}
