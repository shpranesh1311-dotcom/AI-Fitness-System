"""
Run this once (after installing requirements) to create tables and seed the
Indian/Tamil Nadu food database + exercise database.

    cd backend
    python seed_data.py
"""
import json
import os

from app.database import Base, engine, SessionLocal
from app import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Food).count() == 0:
            with open(os.path.join(BASE_DIR, "app", "data", "indian_food_database.json"), encoding="utf-8") as f:
                foods = json.load(f)
            for item in foods:
                db.add(models.Food(**item))
            db.commit()
            print(f"Seeded {len(foods)} food items.")
        else:
            print("Foods already seeded, skipping.")

        if db.query(models.Exercise).count() == 0:
            with open(os.path.join(BASE_DIR, "app", "data", "exercise_database.json"), encoding="utf-8") as f:
                exercises = json.load(f)
            for item in exercises:
                db.add(models.Exercise(**item))
            db.commit()
            print(f"Seeded {len(exercises)} exercises.")
        else:
            print("Exercises already seeded, skipping.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
