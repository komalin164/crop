import os
from pathlib import Path

# Load .env from backend folder if present
_env_path = Path(__file__).resolve().parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass

# Set OPENWEATHER_API_KEY in .env or env; get a free key at https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
USE_SOILGRIDS = os.getenv("USE_SOILGRIDS", "0") == "1"
SECRET_KEY = os.getenv("SECRET_KEY", "crop-app-secret-change-in-production")
DB_PATH = os.path.join(os.path.dirname(__file__), "crop.db")

# Email (SMTP) for OTP - set in .env
MAIL_SERVER = os.getenv("MAIL_SERVER", "mail.heeltech.in")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "ai@heeltech.in")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "ai@heeltech.in")
