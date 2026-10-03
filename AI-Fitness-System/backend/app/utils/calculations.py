"""
Phase 2: Health & Calorie Engine.

Pure functions for BMI, BMR (Mifflin-St Jeor), TDEE, calorie targets and
macro targets. Kept isolated so Phase 3+ modules can import and reuse them
without touching this logic.
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,        # little or no exercise
    "light": 1.375,          # light exercise 1-3 days/week
    "moderate": 1.55,        # moderate exercise 3-5 days/week
    "active": 1.725,         # hard exercise 6-7 days/week
    "extra_active": 1.9,     # very hard exercise & physical job
}

MIN_SAFE_CALORIES = 1200


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal weight"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor Equation."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender.lower() == "male":
        return round(base + 5, 1)
    if gender.lower() == "female":
        return round(base - 161, 1)
    # 'other' -> average of male/female offsets
    return round(base - 78, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 1)


def calculate_calorie_target(tdee: float, goal: str) -> float:
    if goal == "loss":
        target = tdee - 500
    elif goal == "gain":
        target = tdee + 400
    else:  # maintain
        target = tdee
    return round(max(target, MIN_SAFE_CALORIES), 1)


def calculate_macros(calorie_target: float, weight_kg: float, goal: str):
    """
    Protein set relative to bodyweight (supports muscle retention during a
    deficit / muscle growth during a surplus). Fat as a percentage of total
    calories. Carbs fill the remainder.
    """
    if goal == "loss":
        protein_per_kg = 2.0
        fat_pct = 0.25
    elif goal == "gain":
        protein_per_kg = 1.8
        fat_pct = 0.25
    else:
        protein_per_kg = 1.6
        fat_pct = 0.28

    protein_g = round(protein_per_kg * weight_kg, 1)
    protein_cal = protein_g * 4

    fat_cal = calorie_target * fat_pct
    fat_g = round(fat_cal / 9, 1)

    carbs_cal = max(calorie_target - protein_cal - fat_cal, 0)
    carbs_g = round(carbs_cal / 4, 1)

    return protein_g, carbs_g, fat_g


def full_health_profile(weight_kg: float, height_cm: float, age: int,
                         gender: str, activity_level: str, goal: str):
    bmi = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    calorie_target = calculate_calorie_target(tdee, goal)
    protein_g, carbs_g, fat_g = calculate_macros(calorie_target, weight_kg, goal)
    return {
        "bmi": bmi,
        "bmi_category": bmi_category(bmi),
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie_target,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
    }
