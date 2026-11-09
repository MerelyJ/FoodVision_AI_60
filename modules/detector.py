
from pathlib import Path
from functools import lru_cache

import numpy as np
from PIL import Image
from ultralytics import YOLO


# ==========================================
# FOODVISION AI - FOOD DETECTOR
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "foodvision_8class_cpu_test_v1_best.pt"
)

IMAGE_SIZE = 416
CONFIDENCE = 0.25
DEVICE = "cpu"


# ==========================================
# LOAD MODEL
# ==========================================

@lru_cache(maxsize=1)
def load_detector():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ไม่พบโมเดล: {MODEL_PATH}"
        )

    model = YOLO(str(MODEL_PATH))

    return model


# ==========================================
# DETECT FOOD
# ==========================================

def detect_food(image):

    model = load_detector()

    # รองรับ PIL Image
    if isinstance(image, Image.Image):

        image = image.convert("RGB")

        image_array = np.array(image)

    # รองรับ NumPy Array
    elif isinstance(image, np.ndarray):

        image_array = image

    else:

        raise TypeError(
            "กรุณาส่งภาพชนิด PIL Image หรือ NumPy Array"
        )

    # ตรวจจับอาหาร
    results = model.predict(
        source=image_array,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE,
        device=DEVICE,
        verbose=False
    )

    result = results[0]

    # วาด Bounding Box
    annotated_image = result.plot()

    # แปลง BGR เป็น RGB
    annotated_image = annotated_image[:, :, ::-1].copy()

    # เก็บข้อมูลอาหาร
    detections = []

    if result.boxes is not None:

        for box in result.boxes:

            class_id = int(box.cls[0])

            confidence = float(box.conf[0])

            x1, y1, x2, y2 = (
                box.xyxy[0].cpu().tolist()
            )

            food_name = model.names[class_id]

            detections.append({
                "class_id": class_id,
                "name": food_name,
                "confidence": confidence,
                "bbox": [
                    round(x1, 2),
                    round(y1, 2),
                    round(x2, 2),
                    round(y2, 2)
                ]
            })

    return annotated_image, detections
