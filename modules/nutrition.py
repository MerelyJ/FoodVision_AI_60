
# ==========================================
# FOODVISION AI - NUTRITION DATABASE
# ==========================================

# ค่าทางโภชนาการโดยประมาณต่ออาหาร 100 กรัม
# kcal, protein, carbohydrates, fat

NUTRITION_DATABASE = {

    "hamburger": {
        "name": "Hamburger",
        "calories": 295,
        "protein": 17.0,
        "carbs": 24.0,
        "fat": 14.0
    },

    "french_fries": {
        "name": "French Fries",
        "calories": 312,
        "protein": 3.4,
        "carbs": 41.0,
        "fat": 15.0
    },

    "steak": {
        "name": "Steak",
        "calories": 271,
        "protein": 26.0,
        "carbs": 0.0,
        "fat": 18.0
    },

    "pad_thai": {
        "name": "Pad Thai",
        "calories": 180,
        "protein": 8.0,
        "carbs": 25.0,
        "fat": 6.0
    },

    "ramen": {
        "name": "Ramen",
        "calories": 150,
        "protein": 6.0,
        "carbs": 20.0,
        "fat": 5.0
    },

    "sashimi": {
        "name": "Sashimi",
        "calories": 140,
        "protein": 23.0,
        "carbs": 0.0,
        "fat": 5.0
    },

    "som_tam": {
        "name": "Som Tam",
        "calories": 60,
        "protein": 2.0,
        "carbs": 12.0,
        "fat": 1.0
    },

    "sushi": {
        "name": "Sushi",
        "calories": 150,
        "protein": 6.0,
        "carbs": 28.0,
        "fat": 2.0
    }

}


# ==========================================
# GET FOOD NUTRITION
# ==========================================

def get_nutrition(food_name):

    food_name = food_name.lower().strip()

    return NUTRITION_DATABASE.get(food_name)


# ==========================================
# CALCULATE NUTRITION
# ==========================================

def calculate_nutrition(food_name, weight_grams):

    nutrition = get_nutrition(food_name)

    if nutrition is None:
        raise ValueError(
            f"ไม่มีข้อมูลโภชนาการของ {food_name}"
        )

    if weight_grams <= 0:
        raise ValueError(
            "น้ำหนักอาหารต้องมากกว่า 0 กรัม"
        )

    ratio = weight_grams / 100

    return {
        "name": nutrition["name"],
        "weight": weight_grams,

        "calories": round(
            nutrition["calories"] * ratio, 2
        ),

        "protein": round(
            nutrition["protein"] * ratio, 2
        ),

        "carbs": round(
            nutrition["carbs"] * ratio, 2
        ),

        "fat": round(
            nutrition["fat"] * ratio, 2
        )
    }


# ==========================================
# CALCULATE TOTAL NUTRITION
# ==========================================

def calculate_total_nutrition(food_list):

    total = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }

    for food in food_list:

        total["calories"] += food["calories"]
        total["protein"] += food["protein"]
        total["carbs"] += food["carbs"]
        total["fat"] += food["fat"]

    return {
        key: round(value, 2)
        for key, value in total.items()
    }
