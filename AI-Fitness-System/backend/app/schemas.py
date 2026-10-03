from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# User (Phase 2)
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    name: str
    age: int = Field(gt=0, lt=120)
    gender: str  # male / female / other
    height_cm: float = Field(gt=50, lt=260)
    weight_kg: float = Field(gt=20, lt=400)
    activity_level: str  # sedentary, light, moderate, active, extra_active
    goal: str  # loss, maintain, gain
    goal_weight_kg: Optional[float] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    goal_weight_kg: Optional[float] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class HealthMetrics(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    calorie_target: float
    protein_g: float
    carbs_g: float
    fat_g: float


# ---------------------------------------------------------------------------
# Food (Phase 3)
# ---------------------------------------------------------------------------
class FoodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    name_ta: Optional[str] = None
    category: str
    serving_size_g: float
    serving_desc: Optional[str] = None
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    is_vegetarian: int


class FoodLogCreate(BaseModel):
    food_id: int
    meal_type: str  # breakfast/lunch/dinner/snack
    quantity_servings: float = 1.0
    log_date: Optional[date] = None


class FoodLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    food_id: int
    food_name: Optional[str] = None
    meal_type: str
    quantity_servings: float
    log_date: date
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class DailyNutritionSummary(BaseModel):
    log_date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    calorie_target: float
    calories_remaining: float
    meals: List[FoodLogOut]


# ---------------------------------------------------------------------------
# Activity (Phase 4)
# ---------------------------------------------------------------------------
class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    met_value: float


class ActivityLogCreate(BaseModel):
    exercise_id: Optional[int] = None
    steps: int = 0
    duration_min: float = 0.0
    log_date: Optional[date] = None
    notes: Optional[str] = None


class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    exercise_id: Optional[int] = None
    exercise_name: Optional[str] = None
    log_date: date
    steps: int
    duration_min: float
    calories_burned: float
    notes: Optional[str] = None


class DailyActivitySummary(BaseModel):
    log_date: date
    total_steps: int
    total_duration_min: float
    total_calories_burned: float
    logs: List[ActivityLogOut]


# ---------------------------------------------------------------------------
# Weight / Progress (Phase 6)
# ---------------------------------------------------------------------------
class WeightLogCreate(BaseModel):
    weight_kg: float
    log_date: Optional[date] = None


class WeightLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    log_date: date
    weight_kg: float


class ProgressAnalysis(BaseModel):
    data_points: int
    actual_weekly_rate_kg: Optional[float]
    expected_weekly_rate_kg: float
    status: str  # on_track / faster_than_expected / slower_than_expected / insufficient_data
    message: str
    adjusted_calorie_target: float
    trend: List[WeightLogOut]


# ---------------------------------------------------------------------------
# Recommendations (Phase 5)
# ---------------------------------------------------------------------------
class MealRecommendation(BaseModel):
    meal_type: str
    target_calories: float
    items: List[FoodOut]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


class WorkoutRecommendation(BaseModel):
    exercise: ExerciseOut
    suggested_duration_min: float
    estimated_calories_burned: float


class RecommendationsOut(BaseModel):
    log_date: date
    calories_remaining: float
    meal_recommendations: List[MealRecommendation]
    workout_recommendations: List[WorkoutRecommendation]
    notes: List[str]


# ---------------------------------------------------------------------------
# Dashboard (Phase 7)
# ---------------------------------------------------------------------------
class DashboardOut(BaseModel):
    user: UserOut
    health_metrics: HealthMetrics
    today_nutrition: DailyNutritionSummary
    today_activity: DailyActivitySummary
    weight_trend: List[WeightLogOut]
    progress: ProgressAnalysis
