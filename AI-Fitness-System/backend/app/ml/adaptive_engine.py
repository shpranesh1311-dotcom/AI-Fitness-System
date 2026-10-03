"""
Phase 6: Adaptive Progress System.

Uses scikit-learn's LinearRegression to fit the user's actual weight trend
over time, compares it against the expected trend implied by their calorie
target and goal, and nudges the calorie target up or down accordingly.

This is intentionally simple and explainable (a linear fit + a rule-based
adjustment) rather than a black box, since the input signal (a handful of
weight log points) is too small for a more complex model to be meaningful.
"""
from datetime import date
from typing import List, Optional

import numpy as np
from sklearn.linear_model import LinearRegression

from .. import models

# Expected weekly weight change implied by a sensible calorie target.
# ~7700 kcal deficit/surplus ≈ 1 kg body weight.
EXPECTED_WEEKLY_RATE_KG = {
    "loss": -0.5,     # ~500 kcal/day deficit
    "maintain": 0.0,
    "gain": 0.3,       # lean gain, avoid excess fat gain
}

MIN_POINTS_FOR_TREND = 3
CALORIE_STEP = 100  # kcal adjustment increment
MIN_SAFE_CALORIES = 1200


def _fit_weekly_rate(weight_logs: List[models.WeightLog]) -> Optional[float]:
    """Fit weight (kg) vs day-index with linear regression; return kg/week slope."""
    if len(weight_logs) < MIN_POINTS_FOR_TREND:
        return None

    sorted_logs = sorted(weight_logs, key=lambda w: w.log_date)
    base_date = sorted_logs[0].log_date
    X = np.array([(w.log_date - base_date).days for w in sorted_logs]).reshape(-1, 1)
    y = np.array([w.weight_kg for w in sorted_logs])

    model = LinearRegression()
    model.fit(X, y)
    daily_rate = model.coef_[0]
    return round(daily_rate * 7, 3)


def analyze_progress(
    weight_logs: List[models.WeightLog],
    goal: str,
    current_calorie_target: float,
) -> dict:
    expected_rate = EXPECTED_WEEKLY_RATE_KG.get(goal, 0.0)
    actual_rate = _fit_weekly_rate(weight_logs)

    if actual_rate is None:
        return {
            "data_points": len(weight_logs),
            "actual_weekly_rate_kg": None,
            "expected_weekly_rate_kg": expected_rate,
            "status": "insufficient_data",
            "message": (
                f"Log at least {MIN_POINTS_FOR_TREND} weight entries "
                "(ideally weekly) so the system can learn your real trend."
            ),
            "adjusted_calorie_target": current_calorie_target,
        }

    diff = actual_rate - expected_rate
    tolerance = 0.15  # kg/week wiggle room before we intervene
    adjusted_target = current_calorie_target

    if goal == "loss":
        if diff > tolerance:
            # losing slower than expected (diff positive means less negative / weight higher than expected)
            adjusted_target = current_calorie_target - CALORIE_STEP
            status = "slower_than_expected"
            message = (
                f"You're losing about {abs(actual_rate):.2f} kg/week, "
                f"slower than the ~{abs(expected_rate):.2f} kg/week target. "
                f"Trimming your calorie target by {CALORIE_STEP} kcal/day."
            )
        elif diff < -tolerance:
            adjusted_target = current_calorie_target + CALORIE_STEP
            status = "faster_than_expected"
            message = (
                f"You're losing about {abs(actual_rate):.2f} kg/week, "
                f"faster than the ~{abs(expected_rate):.2f} kg/week target. "
                f"Adding {CALORIE_STEP} kcal/day back to keep it sustainable."
            )
        else:
            status = "on_track"
            message = f"Great consistency — losing about {abs(actual_rate):.2f} kg/week, right on target."
    elif goal == "gain":
        if diff < -tolerance:
            adjusted_target = current_calorie_target + CALORIE_STEP
            status = "slower_than_expected"
            message = (
                f"You're gaining about {actual_rate:.2f} kg/week, slower than the "
                f"~{expected_rate:.2f} kg/week target. Adding {CALORIE_STEP} kcal/day."
            )
        elif diff > tolerance:
            adjusted_target = current_calorie_target - CALORIE_STEP
            status = "faster_than_expected"
            message = (
                f"You're gaining about {actual_rate:.2f} kg/week, faster than the "
                f"~{expected_rate:.2f} kg/week target (risk of excess fat gain). "
                f"Trimming {CALORIE_STEP} kcal/day."
            )
        else:
            status = "on_track"
            message = f"Nice — gaining about {actual_rate:.2f} kg/week, right on target for lean gains."
    else:  # maintain
        if abs(actual_rate) > tolerance:
            adjusted_target = current_calorie_target - CALORIE_STEP if actual_rate > 0 else current_calorie_target + CALORIE_STEP
            status = "slower_than_expected" if actual_rate > 0 else "faster_than_expected"
            message = (
                f"Your weight is drifting by about {actual_rate:+.2f} kg/week while aiming to maintain. "
                f"Adjusting your calorie target by {'-' if actual_rate > 0 else '+'}{CALORIE_STEP} kcal/day."
            )
        else:
            status = "on_track"
            message = "Your weight is stable — right where a maintenance goal should be."

    adjusted_target = max(adjusted_target, MIN_SAFE_CALORIES)

    return {
        "data_points": len(weight_logs),
        "actual_weekly_rate_kg": actual_rate,
        "expected_weekly_rate_kg": expected_rate,
        "status": status,
        "message": message,
        "adjusted_calorie_target": round(adjusted_target, 1),
    }
