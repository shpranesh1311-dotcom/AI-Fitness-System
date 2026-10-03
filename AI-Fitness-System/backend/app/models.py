from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from .database import Base


# ---------------------------------------------------------------------------
# Phase 2: User Profile & Goal
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)          # male / female / other
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)             # current weight, kept in sync
    activity_level = Column(String(30), nullable=False)   # sedentary..extra_active
    goal = Column(String(20), nullable=False)              # loss / maintain / gain
    goal_weight_kg = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    weight_logs = relationship("WeightLog", back_populates="user", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Phase 3: Food & Nutrition (Indian / Tamil Nadu food database)
# ---------------------------------------------------------------------------
class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    name_ta = Column(String(150), nullable=True)           # Tamil name
    category = Column(String(40), nullable=False)          # breakfast/lunch/dinner/snack/beverage/dessert
    serving_size_g = Column(Float, nullable=False, default=100.0)
    serving_desc = Column(String(80), nullable=True)       # e.g. "1 idli (approx 40g)"
    calories = Column(Float, nullable=False)                # per serving_size_g
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    is_vegetarian = Column(Integer, default=1)              # 1/0 boolean

    food_logs = relationship("FoodLog", back_populates="food")


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    meal_type = Column(String(20), nullable=False)          # breakfast/lunch/dinner/snack
    quantity_servings = Column(Float, nullable=False, default=1.0)
    log_date = Column(Date, default=date.today, index=True)

    # denormalized nutrition snapshot at time of logging (quantity applied)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)

    user = relationship("User", back_populates="food_logs")
    food = relationship("Food", back_populates="food_logs")


# ---------------------------------------------------------------------------
# Phase 4: Activity & Workout Tracking
# ---------------------------------------------------------------------------
class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(40), nullable=False)  # cardio/strength/yoga/sports
    met_value = Column(Float, nullable=False)       # metabolic equivalent of task


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    log_date = Column(Date, default=date.today, index=True)
    steps = Column(Integer, default=0)
    duration_min = Column(Float, default=0.0)
    calories_burned = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="activity_logs")
    exercise = relationship("Exercise")


# ---------------------------------------------------------------------------
# Phase 6: Adaptive Progress System
# ---------------------------------------------------------------------------
class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, default=date.today, index=True)
    weight_kg = Column(Float, nullable=False)

    user = relationship("User", back_populates="weight_logs")
