from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.calculations import full_health_profile
from ..ml.adaptive_engine import analyze_progress

router = APIRouter(prefix="/api/progress", tags=["Adaptive Progress"])


@router.post("/{user_id}/weight", response_model=schemas.WeightLogOut)
def log_weight(user_id: int, payload: schemas.WeightLogCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    log = models.WeightLog(
        user_id=user_id,
        weight_kg=payload.weight_kg,
        log_date=payload.log_date or date.today(),
    )
    db.add(log)

    # keep the user's "current weight" (used in BMR/TDEE) in sync with the latest entry
    if not payload.log_date or payload.log_date >= date.today():
        user.weight_kg = payload.weight_kg

    db.commit()
    db.refresh(log)
    return log


@router.get("/{user_id}/weight-history", response_model=list[schemas.WeightLogOut])
def weight_history(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == user_id)
        .order_by(models.WeightLog.log_date)
        .all()
    )


@router.get("/{user_id}/analysis", response_model=schemas.ProgressAnalysis)
def get_progress_analysis(user_id: int, db: Session = Depends(get_db)):
    """
    Phase 6: Adaptive Progress System.
    Fits the actual weight trend (scikit-learn linear regression) and
    compares it to the expected trend, dynamically adjusting the calorie
    recommendation.
    """
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    weight_logs = (
        db.query(models.WeightLog)
        .filter(models.WeightLog.user_id == user_id)
        .order_by(models.WeightLog.log_date)
        .all()
    )

    profile = full_health_profile(
        weight_kg=user.weight_kg, height_cm=user.height_cm, age=user.age,
        gender=user.gender, activity_level=user.activity_level, goal=user.goal,
    )

    result = analyze_progress(weight_logs, user.goal, profile["calorie_target"])
    result["trend"] = weight_logs
    return result
