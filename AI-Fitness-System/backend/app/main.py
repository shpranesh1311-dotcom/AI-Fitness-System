import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import Base, engine
from .routers import users, food, activity, recommendations, progress, dashboard

load_dotenv()

app = FastAPI(
    title="AI-Powered Adaptive Fitness and Nutrition Recommendation System",
    description=(
        "Backend for the fitness/nutrition system: profile & goals, "
        "health metrics (BMI/BMR/TDEE), Indian/Tamil Nadu food tracking, "
        "activity tracking, AI meal/workout recommendations, an adaptive "
        "progress system, and a dashboard."
    ),
    version="1.0.0",
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (safe no-op if they already exist).
# Food/exercise seed data still needs `python seed_data.py` run once.
Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(food.router)
app.include_router(activity.router)
app.include_router(recommendations.router)
app.include_router(progress.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "message": "AI Fitness System API is running.",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
