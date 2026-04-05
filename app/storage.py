# сохранение/загрузка в JSON

import json
from pathlib import Path
from .models import Shortcut
import os

APP_DIR = Path(os.getenv("LOCALAPPDATA")) / "ParentLauncher"
DATA_FILE = APP_DIR / "apps.json"

APP_DIR.mkdir(parents=True, exist_ok=True)
#DATA_DIR = Path("data")
#DATA_FILE = DATA_DIR / "apps.json"

def save_apps(apps: list[Shortcut]):
    data = [vars(app) for app in apps]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_apps() -> list[Shortcut]:
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Shortcut(**item) for item in data]
    except:
        return []