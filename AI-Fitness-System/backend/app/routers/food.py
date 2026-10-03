from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.calculations import full_health_profile

router = APIRouter(prefix="/api/food", tags=["Food & Nutrition"])


# ---------------------------------------------------------------------------
# Food database browsing
# ---------------------------------------------------------------------------
@router.get("/database", response_model=list[schemas.FoodOut])
def browse_foods(
    category: Optional[str] = Query(None, description="breakfast/lunch/dinner/snack/beverage/dessert"),
    search: Optional[str] = Query(None, description="search by name (English or Tamil)"),
    vegetarian_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(models.Food)
    if category:
        query = query.filter(models.Food.category == category)
    if search:
        like = f"%{search}%"
        query = query.filter(
            (models.Food.name.ilike(like)) | (models.Food.name_ta.ilike(like))
        )
    if vegetarian_only:
        query = query.filter(models.Food.is_vegetarian == 1)
    return query.order_by(models.Food.category, models.Food.name).all()


@router.get("/database/{food_id}", response_model=schemas.FoodOut)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = db.query(models.Food).get(food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


# ---------------------------------------------------------------------------
# Food logging (meal-wise, daily tracking)
# ---------------------------------------------------------------------------
def _serialize_log(log: models.FoodLog) -> schemas.FoodLogOut:
    return schemas.FoodLogOut(
        id=log.id,
        user_id=log.user_id,
        food_id=log.food_id,
        food_name=log.food.name if log.food else None,
        meal_type=log.meal_type,
        quantity_servings=log.quantity_servings,
        log_date=log.log_date,
        calories=log.calories,
        protein_g=log.protein_g,
        carbs_g=log.carbs_g,
        fat_g=log.fat_g,
    )


@router.post("/log/{user_id}", response_model=schemas.FoodLogOut)
def log_food(user_id: int, payload: schemas.FoodLogCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    food = db.query(models.Food).get(payload.food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    qty = payload.quantity_servings
    log = models.FoodLog(
        user_id=user_id,
        food_id=food.id,
        meal_type=payload.meal_type,
        quantity_servings=qty,
        log_date=payload.log_date or date.today(),
        calories=round(food.calories * qty, 1),
        protein_g=round(food.protein_g * qty, 1),
        carbs_g=round(food.carbs_g * qty, 1),
        fat_g=round(food.fat_g * qty, 1),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _serialize_log(log)


@router.delete("/log/{log_id}")
def delete_food_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.FoodLog).get(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Food log not found")
    db.delete(log)
    db.commit()
    return {"detail": "Food log deleted"}


@router.get("/log/{user_id}/daily", response_model=schemas.DailyNutritionSummary)
def get_daily_summary(user_id: int, log_date: Optional[date] = None, db: Session = Depends(get_db)):
    """Phase 3: meal-wise and daily nutrition tracking summary."""
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    target_date = log_date or date.today()
    logs = (
        db.query(models.FoodLog)
        .filter(models.FoodLog.user_id == user_id, models.FoodLog.log_date == target_date)
        .all()
    )

    total_calories = sum(l.calories for l in logs)
    total_protein = sum(l.protein_g for l in logs)
    total_carbs = sum(l.carbs_g for l in logs)
    total_fat = sum(l.fat_g for l in logs)

    profile = full_health_profile(
        weight_kg=user.weight_kg, height_cm=user.height_cm, age=user.age,
        gender=user.gender, activity_level=user.activity_level, goal=user.goal,
    )
    calorie_target = profile["calorie_target"]

    return schemas.DailyNutritionSummary(
        log_date=target_date,
        total_calories=round(total_calories, 1),
        total_protein_g=round(total_protein, 1),
        total_carbs_g=round(total_carbs, 1),
        total_fat_g=round(total_fat, 1),
        calorie_target=calorie_target,
        calories_remaining=round(calorie_target - total_calories, 1),
        meals=[_serialize_log(l) for l in logs],
    )
