"""
Phase 5: AI Recommendation Engine.

Rule-based / greedy-scoring recommender (lightweight "AI" suitable for a
constrained calorie/macro budget problem — this is effectively a bounded
knapsack heuristic). Two responsibilities:

1. Recommend food items for a meal slot that fit the user's remaining
   calorie/protein budget and goal.
2. Recommend workouts to help the user hit an activity/calorie-burn target
   based on their goal.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from .. import models

MEAL_CALORIE_SPLIT = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "snack": 0.10,
    "dinner": 0.30,
}

# Daily active-calorie-burn goals layered on top of NEAT, by user goal
WORKOUT_CALORIE_GOAL = {
    "loss": 350,
    "maintain": 200,
    "gain": 150,
}


def _score_food(food: models.Food, goal: str) -> float:
    """Higher score = better fit for the goal. Avoids div-by-zero."""
    cal = max(food.calories, 1)
    protein_density = food.protein_g / cal  # protein per calorie
    if goal == "loss":
        # favor high protein-per-calorie, penalize fat-heavy items
        return protein_density * 100 - (food.fat_g / cal) * 20
    if goal == "gain":
        # favor calorie-dense, still protein-conscious
        return (cal / 100) + protein_density * 50
    # maintain: balanced
    return protein_density * 60


def recommend_meal(
    db: Session,
    meal_type: str,
    target_calories: float,
    goal: str,
    vegetarian_only: bool = False,
    exclude_food_ids: Optional[List[int]] = None,
    max_items: int = 3,
) -> List[models.Food]:
    """Greedily pick foods for a meal slot to approximate target_calories."""
    exclude_food_ids = exclude_food_ids or []

    query = db.query(models.Food).filter(models.Food.category == meal_type)
    if vegetarian_only:
        query = query.filter(models.Food.is_vegetarian == 1)
    candidates = [f for f in query.all() if f.id not in exclude_food_ids]

    # Fallback: if this meal category is sparse, widen the pool
    if len(candidates) < 3:
        query = db.query(models.Food)
        if vegetarian_only:
            query = query.filter(models.Food.is_vegetarian == 1)
        candidates = [f for f in query.all() if f.id not in exclude_food_ids]

    candidates.sort(key=lambda f: _score_food(f, goal), reverse=True)

    selected: List[models.Food] = []
    remaining = target_calories
    for food in candidates:
        if len(selected) >= max_items:
            break
        if food.calories <= remaining + (target_calories * 0.20):  # 20% tolerance
            selected.append(food)
            remaining -= food.calories
        if remaining <= target_calories * 0.10:  # close enough, stop
            break

    if not selected and candidates:
        selected = [candidates[0]]

    return selected


def recommend_workouts(
    db: Session,
    goal: str,
    calories_already_burned: float,
    max_items: int = 2,
) -> List[dict]:
    """Suggest exercises + duration to help close the day's activity gap."""
    calorie_goal = WORKOUT_CALORIE_GOAL.get(goal, 200)
    remaining_goal = max(calorie_goal - calories_already_burned, 0)

    if remaining_goal <= 0:
        return []

    exercises = db.query(models.Exercise).all()
    if not exercises:
        return []

    # Prefer a mix: one cardio-ish, one strength-ish
    cardio = [e for e in exercises if e.category in ("cardio", "sports")]
    strength = [e for e in exercises if e.category in ("strength", "yoga")]

    cardio.sort(key=lambda e: e.met_value, reverse=True)
    strength.sort(key=lambda e: e.met_value, reverse=True)

    picks = []
    pool = (cardio[:4] + strength[:4]) or exercises
    # pick middling-intensity options rather than always the most extreme
    pool = sorted(pool, key=lambda e: e.met_value)
    mid = len(pool) // 2
    ordered = pool[mid:] + pool[:mid]

    per_item_goal = remaining_goal / max_items
    for exercise in ordered[:max_items]:
        # duration (min) to burn per_item_goal kcal, assuming ~70kg reference,
        # actual calories recalculated per-user by the caller using real weight
        picks.append({"exercise": exercise, "target_kcal": per_item_goal})

    return picks
