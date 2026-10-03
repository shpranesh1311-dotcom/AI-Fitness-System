from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.calculations import full_health_profile

router = APIRouter(prefix="/api/users", tags=["Users & Profile"])


@router.post("", response_model=schemas.UserOut)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    # First weight log entry so the progress trend has a starting point
    db.add(models.WeightLog(user_id=user.id, weight_kg=user.weight_kg))
    db.commit()
    return user


@router.get("", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_unset=True)
    weight_changed = "weight_kg" in data and data["weight_kg"] != user.weight_kg

    for key, value in data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)

    # Keep the weight trend in sync when weight is updated directly
    if weight_changed:
        db.add(models.WeightLog(user_id=user.id, weight_kg=user.weight_kg))
        db.commit()

    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


@router.get("/{user_id}/health-metrics", response_model=schemas.HealthMetrics)
def get_health_metrics(user_id: int, db: Session = Depends(get_db)):
    """Phase 2: BMI, BMR, TDEE, calorie target, macro targets."""
    user = db.query(models.User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = full_health_profile(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        activity_level=user.activity_level,
        goal=user.goal,
    )
    return profile
