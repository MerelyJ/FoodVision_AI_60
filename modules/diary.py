
from pathlib import Path
from datetime import datetime
import uuid
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DIARY_FILE = DATA_DIR / "food_diary.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "id",
    "datetime",
    "date",
    "meal_type",
    "food_name",
    "weight",
    "calories",
    "protein",
    "carbs",
    "fat"
]


def load_food_diary():
    if not DIARY_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)

    try:
        df = pd.read_csv(DIARY_FILE)

        if df.empty:
            return pd.DataFrame(columns=COLUMNS)

        # รองรับข้อมูลเก่าที่ไม่มี id
        if "id" not in df.columns:
            df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]

        # รองรับข้อมูลเก่าที่ไม่มีประเภทมื้ออาหาร
        if "meal_type" not in df.columns:
            df["meal_type"] = "ไม่ระบุ"

        # เพิ่มคอลัมน์ที่อาจไม่มีในข้อมูลเก่า
        for column in COLUMNS:
            if column not in df.columns:
                df[column] = 0 if column in [
                    "weight", "calories", "protein", "carbs", "fat"
                ] else ""

        df = df[COLUMNS]

        # แปลงชนิดข้อมูลตัวเลข
        for column in [
            "weight", "calories", "protein", "carbs", "fat"
        ]:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            ).fillna(0)

        # บันทึกโครงสร้างใหม่เพื่อให้รองรับข้อมูลเก่า
        df.to_csv(
            DIARY_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        return df

    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=COLUMNS)


def save_food_diary(food_list, meal_type="ไม่ระบุ"):
    if not food_list:
        return 0

    now = datetime.now()
    new_rows = []

    for food in food_list:
        new_rows.append({
            "id": str(uuid.uuid4()),
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "meal_type": meal_type,
            "food_name": food["name"],
            "weight": food["weight"],
            "calories": food["calories"],
            "protein": food["protein"],
            "carbs": food["carbs"],
            "fat": food["fat"]
        })

    new_df = pd.DataFrame(new_rows, columns=COLUMNS)

    old_df = load_food_diary()

    updated_df = pd.concat(
        [old_df, new_df],
        ignore_index=True
    )

    updated_df.to_csv(
        DIARY_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    return len(new_rows)


def update_food_diary(food_id, updated_food):
    df = load_food_diary()

    if df.empty:
        return False

    indexes = df.index[df["id"] == food_id].tolist()

    if not indexes:
        return False

    index = indexes[0]

    allowed_fields = [
        "meal_type",
        "food_name",
        "weight",
        "calories",
        "protein",
        "carbs",
        "fat"
    ]

    for field in allowed_fields:
        if field in updated_food:
            df.at[index, field] = updated_food[field]

    df.to_csv(
        DIARY_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    return True


def delete_food_diary(food_id):
    df = load_food_diary()

    if df.empty:
        return False

    new_df = df[df["id"] != food_id]

    if len(new_df) == len(df):
        return False

    new_df.to_csv(
        DIARY_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    return True


def get_daily_summary(selected_date):
    df = load_food_diary()

    if df.empty:
        return {
            "items": 0,
            "weight": 0,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        }

    daily_df = df[
        df["date"] == str(selected_date)
    ]

    if daily_df.empty:
        return {
            "items": 0,
            "weight": 0,
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        }

    return {
        "items": len(daily_df),
        "weight": round(daily_df["weight"].sum(), 2),
        "calories": round(daily_df["calories"].sum(), 2),
        "protein": round(daily_df["protein"].sum(), 2),
        "carbs": round(daily_df["carbs"].sum(), 2),
        "fat": round(daily_df["fat"].sum(), 2)
    }
