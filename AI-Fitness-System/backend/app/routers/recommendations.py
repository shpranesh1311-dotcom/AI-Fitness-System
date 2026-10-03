from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.calculations import full_health_profile
from ..ml.recommendation_engine import (
    MEAL_CALORIE_SPLIT,
    recommend_meal,
    recommend_workouts,
)
from .activity import calories_from_exercise

router = APIRouter(prefix="/api/recommendations", tags=["AI Recommendations"])


@router.get("/{user_id}", response_model=schemas.RecommendationsOut)
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """
    Phase 5: AI Recommendation Engine.
    Personalized meal + workout suggestions based on the user's goal and
    how many calories/macros they have left today.
    """
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()
    profile = full_health_profile(
        weight_kg=user.weight_kg, height_cm=user.height_cm, age=user.age,
        gender=user.gender, activity_level=user.activity_level, goal=user.goal,
    )
    calorie_target = profile["calorie_target"]

    food_logs_today = (
        db.query(models.FoodLog)
        .filter(models.FoodLog.user_id == user_id, models.FoodLog.log_date == today)
        .all()
    )
    consumed_calories = sum(l.calories for l in food_logs_today)
    calories_remaining = round(calorie_target - consumed_calories, 1)
    logged_meal_types = {l.meal_type for l in food_logs_today}
    already_eaten_food_ids = [l.food_id for l in food_logs_today]

    notes = []
    meal_recs = []

    if calories_remaining <= 0:
        notes.append(
            "You've already reached (or exceeded) today's calorie target. "
            "Consider a light activity instead of another meal."
        )
    else:
        # Only recommend meal slots not yet logged today
        pending_meals = [m for m in MEAL_CALORIE_SPLIT if m not in logged_meal_types]
        if not pending_meals:
            pending_meals = list(MEAL_CALORIE_SPLIT.keys())

        split_total = sum(MEAL_CALORIE_SPLIT[m] for m in pending_meals) or 1
        for meal_type in pending_meals:
            meal_target = calories_remaining * (MEAL_CALORIE_SPLIT[meal_type] / split_total)
            if meal_target < 50:
                continue
            items = recommend_meal(
                db, meal_type, meal_target, user.goal,
                exclude_food_ids=already_eaten_food_ids,
            )
            if not items:
                continue
            meal_recs.append(schemas.MealRecommendation(
                meal_type=meal_type,
                target_calories=round(meal_target, 1),
                items=[schemas.FoodOut.model_validate(i) for i in items],
                total_calories=round(sum(i.calories for i in items), 1),
                total_protein_g=round(sum(i.protein_g for i in items), 1),
                total_carbs_g=round(sum(i.carbs_g for i in items), 1),
                total_fat_g=round(sum(i.fat_g for i in items), 1),
            ))

    # Workout recommendations
    activity_logs_today = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.user_id == user_id, models.ActivityLog.log_date == today)
        .all()
    )
    calories_burned_today = sum(l.calories_burned for l in activity_logs_today)

    workout_picks = recommend_workouts(db, user.goal, calories_burned_today)
    workout_recs = []
    for pick in workout_picks:
        exercise = pick["exercise"]
        target_kcal = pick["target_kcal"]
        # duration such that MET formula yields target_kcal for this user's weight
        duration_min = target_kcal / (exercise.met_value * 3.5 * user.weight_kg / 200)
        duration_min = round(max(duration_min, 5), 0)
        estimated_kcal = calories_from_exercise(exercise.met_value, user.weight_kg, duration_min)
        workout_recs.append(schemas.WorkoutRecommendation(
            exercise=schemas.ExerciseOut.model_validate(exercise),
            suggested_duration_min=duration_min,
            estimated_calories_burned=estimated_kcal,
        ))

    if not meal_recs and calories_remaining > 0:
        notes.append("No close-fitting meal matches found — browse the food database directly.")
    if user.goal == "loss" and calories_remaining > 0:
        notes.append("Prioritizing higher-protein, lower-fat options to support fat loss while preserving muscle.")
    elif user.goal == "gain":
        notes.append("Prioritizing calorie-dense, protein-rich options to support a lean bulk.")

    return schemas.RecommendationsOut(
        log_date=today,
        calories_remaining=calories_remaining,
        meal_recommendations=meal_recs,
        workout_recommendations=workout_recs,
        notes=notes,
    )
