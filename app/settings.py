import json
import os
from pathlib import Path
from pydantic import BaseModel

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
SETTINGS_FILE = DATA_DIR / "settings.json"
LAST_RUN_FILE = DATA_DIR / "last_run.json"


class Settings(BaseModel):
    # Shaarli
    shaarli_url: str = ""
    shaarli_api_secret: str = ""
    exclude_tags: str = ""
    show_descriptions: bool = True
    send_if_empty: bool = False

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    mail_from: str = ""
    mail_to: str = ""
    subject_prefix: str = "📰 Ma veille du"

    # Planification
    send_time: str = "07:00"
    timezone: str = "Europe/Paris"
    enabled: bool = True

    # Apparence
    theme: str = "journal"

    # Météo
    weather_enabled: bool = False
    weather_city: str = ""
    weather_label: str = ""
    weather_lat: float | None = None
    weather_lon: float | None = None


def load_settings() -> Settings:
    if SETTINGS_FILE.exists():
        return Settings(**json.loads(SETTINGS_FILE.read_text()))
    return Settings()


def save_settings(settings: Settings) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(settings.model_dump_json(indent=2))


def load_last_run() -> dict | None:
    if LAST_RUN_FILE.exists():
        return json.loads(LAST_RUN_FILE.read_text())
    return None


def save_last_run(ok: bool, message: str, at: str) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LAST_RUN_FILE.write_text(json.dumps({"ok": ok, "message": message, "at": at}, indent=2))