# backend/ml_engine.py

def calculate_fitness_metrics(age: int, weight: float, height: float, gender: str, activity_level: str, goal: str):
    # 1. Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    if gender.lower() == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # 2. Factor in Activity Level to get Total Daily Energy Expenditure (TDEE)
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725
    }
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)

    # 3. Adjust Calories based on Goal
    if goal == "weight_loss":
        target_calories = tdee - 500
        protein_ratio, fat_ratio, carb_ratio = 0.30, 0.30, 0.40  # Higher protein for retention
    elif goal == "muscle_gain":
        target_calories = tdee + 300
        protein_ratio, fat_ratio, carb_ratio = 0.25, 0.25, 0.50  # Higher carbs for energy
    else: # maintenance
        target_calories = tdee
        protein_ratio, fat_ratio, carb_ratio = 0.20, 0.30, 0.50

    # Calculate exact macronutrient grams (1g Protein/Carb = 4 cal, 1g Fat = 9 cal)
    protein_g = (target_calories * protein_ratio) / 4
    fat_g = (target_calories * fat_ratio) / 9
    carb_g = (target_calories * carb_ratio) / 4

    return {
        "target_calories": round(target_calories),
        "protein_g": round(protein_g),
        "fat_g": round(fat_g),
        "carb_g": round(carb_g)
    }