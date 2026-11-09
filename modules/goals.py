
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
GOALS_FILE = DATA_DIR / "nutrition_goals.json"

# ค่าเริ่มต้นเป็นตัวอย่าง ผู้ใช้สามารถแก้ไขได้
DEFAULT_GOALS = {
    "calories": 2000,
    "protein": 100,
    "carbs": 250,
    "fat": 65
}


def load_goals():
    """โหลดเป้าหมายจากไฟล์ JSON"""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not GOALS_FILE.exists():
        save_goals(DEFAULT_GOALS)
        return DEFAULT_GOALS.copy()

    try:
        with open(GOALS_FILE, "r", encoding="utf-8") as file:
            goals = json.load(file)

        # เติมค่าที่ขาดด้วยค่าเริ่มต้น
        for key, value in DEFAULT_GOALS.items():
            goals.setdefault(key, value)

        return goals

    except (json.JSONDecodeError, OSError):
        return DEFAULT_GOALS.copy()


def save_goals(goals):
    """บันทึกเป้าหมายลงไฟล์ JSON"""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(GOALS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            goals,
            file,
            ensure_ascii=False,
            indent=4
        )

    return True
