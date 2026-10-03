from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.calculations import full_health_profile
from ..ml.adaptive_engine import analyze_progress
from .food import _serialize_log as serialize_food_log
from .activity import _serialize_log as serialize_activity_log

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/{user_id}", response_model=schemas.DashboardOut)
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """
    Phase 7: single aggregated payload for the dashboard UI —
    daily calories, nutrition, activity, weight graph, goal progress,
    and a peek at today's AI recommendation notes.
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

    food_logs = (
        db.query(models.FoodLog)
        .filter(models.FoodLog.user_id == user_id, models.FoodLog.log_date == today)
        .all()
    )
    total_calories = sum(l.calories for l in food_logs)
    nutrition_summary = schemas.DailyNutritionSummary(
        log_date=today,
        total_calories=round(total_calories, 1),
        total_protein_g=round(sum(l.protein_g for l in food_logs), 1),
        total_carbs_g=round(sum(l.carbs_g for l in food_logs), 1),
        total_fat_g=round(sum(l.fat_g for l in food_logs), 1),
        calorie_target=calorie_target,
        calories_remaining=round(calorie_target - total_calories, 1),
        meals=[serialize_food_log(l) for l in food_logs],
    )

    activity_logs = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.user_id == user_id, models.ActivityLog.log_date == today)
        .all()
    )
    activity_summary = schemas.DailyActivitySummary(
        log_date=today,
        total_steps=sum(l.steps for l in activity_logs),
        total_duration_min=sum(l.duration_min for l in activity_logs),
        total_calories_burned=round(sum(l.calories_burned for l in activity_logs), 1),
        logs=[serialize_activity_log(l) for l in activity_logs],
    )

    weight_logs = (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == user_id)
        .order_by(models.WeightLog.log_date)
        .all()
    )
    progress = analyze_progress(weight_logs, user.goal, calorie_target)
    progress["trend"] = weight_logs

    return schemas.DashboardOut(
        user=user,
        health_metrics=profile,
        today_nutrition=nutrition_summary,
        today_activity=activity_summary,
        weight_trend=weight_logs,
        progress=progress,
    )
