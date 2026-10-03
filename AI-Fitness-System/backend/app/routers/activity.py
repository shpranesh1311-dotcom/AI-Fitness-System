from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/activity", tags=["Activity & Workout"])

# Rough steps -> calories conversion (assuming ~0.04 kcal/step, adjusted by weight below)
STEP_CAL_FACTOR = 0.0005  # kcal per step per kg of bodyweight


@router.get("/exercises", response_model=list[schemas.ExerciseOut])
def list_exercises(category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Exercise)
    if category:
        query = query.filter(models.Exercise.category == category)
    return query.order_by(models.Exercise.category, models.Exercise.name).all()


def _serialize_log(log: models.ActivityLog) -> schemas.ActivityLogOut:
    return schemas.ActivityLogOut(
        id=log.id,
        user_id=log.user_id,
        exercise_id=log.exercise_id,
        exercise_name=log.exercise.name if log.exercise else None,
        log_date=log.log_date,
        steps=log.steps,
        duration_min=log.duration_min,
        calories_burned=log.calories_burned,
        notes=log.notes,
    )


def calories_from_exercise(met: float, weight_kg: float, duration_min: float) -> float:
    """Standard MET formula: kcal = MET * 3.5 * weight(kg) / 200 * minutes."""
    return round(met * 3.5 * weight_kg / 200 * duration_min, 1)


@router.post("/log/{user_id}", response_model=schemas.ActivityLogOut)
def log_activity(user_id: int, payload: schemas.ActivityLogCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    calories_burned = 0.0
    exercise = None
    if payload.exercise_id:
        exercise = db.query(models.Exercise).get(payload.exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        calories_burned += calories_from_exercise(exercise.met_value, user.weight_kg, payload.duration_min)

    if payload.steps:
        calories_burned += round(payload.steps * user.weight_kg * STEP_CAL_FACTOR, 1)

    log = models.ActivityLog(
        user_id=user_id,
        exercise_id=payload.exercise_id,
        log_date=payload.log_date or date.today(),
        steps=payload.steps,
        duration_min=payload.duration_min,
        calories_burned=round(calories_burned, 1),
        notes=payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return _serialize_log(log)


@router.delete("/log/{log_id}")
def delete_activity_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.ActivityLog).get(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    db.delete(log)
    db.commit()
    return {"detail": "Activity log deleted"}


@router.get("/log/{user_id}/daily", response_model=schemas.DailyActivitySummary)
def get_daily_activity(user_id: int, log_date: Optional[date] = None, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    target_date = log_date or date.today()
    logs = (
        db.query(models.ActivityLog)
        .filter(models.ActivityLog.user_id == user_id, models.ActivityLog.log_date == target_date)
        .all()
    )

    return schemas.DailyActivitySummary(
        log_date=target_date,
        total_steps=sum(l.steps for l in logs),
        total_duration_min=sum(l.duration_min for l in logs),
        total_calories_burned=round(sum(l.calories_burned for l in logs), 1),
        logs=[_serialize_log(l) for l in logs],
    )
