# AI-Powered Adaptive Fitness and Nutrition Recommendation System

Full-stack project: **React** frontend + **Python FastAPI** backend + **SQLAlchemy**
database layer (SQLite by default, MySQL-ready) + **scikit-learn** adaptive engine.

Phases 1–2 (project structure, UI shell, profile, BMI/BMR/TDEE) are implemented
exactly as scoped, and phases 3–7 are built on top of them:

| Phase | Feature | Status |
|---|---|---|
| 1 | Project structure + UI | ✅ |
| 2 | User profile + BMI/BMR/TDEE | ✅ |
| 3 | Food database + calorie tracking | ✅ ⭐ |
| 4 | Exercise/activity tracking | ✅ |
| 5 | AI recommendation engine | ✅ ⭐ |
| 6 | ML / adaptive progress system | ✅ ⭐⭐⭐ |
| 7 | Dashboard + testing | ✅ |

---

## 1. Project structure

```
AI-Fitness-System/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── database.py             # SQLAlchemy engine/session (SQLite default, MySQL-ready)
│   │   ├── models.py               # ORM models: User, Food, FoodLog, Exercise, ActivityLog, WeightLog
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── data/
│   │   │   ├── indian_food_database.json   # Phase 3: Indian/Tamil Nadu food DB (64 items)
│   │   │   └── exercise_database.json      # Phase 4: exercise MET database (27 items)
│   │   ├── utils/
│   │   │   └── calculations.py     # Phase 2: BMI/BMR/TDEE/macro formulas
│   │   ├── ml/
│   │   │   ├── recommendation_engine.py  # Phase 5: AI meal/workout recommender
│   │   │   └── adaptive_engine.py        # Phase 6: scikit-learn adaptive progress model
│   │   └── routers/
│   │       ├── users.py            # Phase 2 endpoints
│   │       ├── food.py              # Phase 3 endpoints
│   │       ├── activity.py          # Phase 4 endpoints
│   │       ├── recommendations.py   # Phase 5 endpoints
│   │       ├── progress.py          # Phase 6 endpoints
│   │       └── dashboard.py         # Phase 7 endpoint
│   ├── seed_data.py                 # Creates tables + loads food/exercise DB
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── public/index.html
    └── src/
        ├── App.js / App.css         # Phase 1: shell + tab navigation
        ├── api/api.js                # REST client for the backend
        ├── context/UserContext.jsx   # current user session
        ├── components/Navbar.jsx
        └── pages/
            ├── Profile.jsx           # Phase 2
            ├── FoodTracking.jsx      # Phase 3
            ├── ActivityTracking.jsx  # Phase 4
            ├── Recommendations.jsx   # Phase 5
            ├── Progress.jsx          # Phase 6 (weight chart + analysis)
            └── Dashboard.jsx         # Phase 7
```

---

## 2. Running it in VS Code

You need two terminals (or use VS Code's split terminal) — one for the backend, one for the frontend.

### Backend (FastAPI)

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# create tables + load the Indian food & exercise database (run once)
python seed_data.py

# start the API server
uvicorn app.main:app --reload
```

The API is now running at **http://localhost:8000** (interactive docs at
`http://localhost:8000/docs`).

By default it uses a local SQLite file (`backend/fitness.db`) — zero config
needed. See section 4 below if you want to switch to MySQL as originally
planned.

### Frontend (React)

```bash
cd frontend
npm install
npm start
```

Opens at **http://localhost:3000** and talks to the backend at
`http://localhost:8000` automatically (see `frontend/package.json` `"proxy"`
field and `frontend/src/api/api.js`).

### First run walkthrough

1. Open http://localhost:3000 — you'll land on **Profile** since no user exists yet.
2. Fill in your details and goal → creates your profile and computes BMI/BMR/TDEE.
3. Go to **Food & Nutrition** → log a few meals from the Indian/Tamil Nadu database.
4. Go to **Activity** → log steps or an exercise.
5. Go to **AI Recommendations** → see meal/workout suggestions based on your remaining calories.
6. Go to **Progress** → log a couple of weight entries (on different dates) to see the
   adaptive analysis kick in (needs at least 3 data points for a trend).
7. Go to **Dashboard** for the full overview.

---

## 3. What each phase actually does

- **Phase 2 – Health & Calorie Engine** (`utils/calculations.py`): BMI, BMR
  (Mifflin-St Jeor equation), TDEE (activity multiplier), a safe calorie
  target for loss/maintain/gain, and macro targets (protein set relative to
  bodyweight, fat as a % of calories, carbs fill the remainder).
- **Phase 3 – Food & Nutrition Tracking**: a 64-item Indian/Tamil Nadu food
  database (English + Tamil names) with calories/protein/carbs/fat per
  serving, meal-wise logging (breakfast/lunch/dinner/snack), and a daily
  nutrition summary against your calorie target.
- **Phase 4 – Activity Tracking**: a 27-item exercise database with MET
  values, step logging, and calorie-burn estimates using the standard MET
  formula (`kcal = MET × 3.5 × weight(kg) / 200 × minutes`).
- **Phase 5 – AI Recommendation Engine** (`ml/recommendation_engine.py`): a
  greedy scoring/selection heuristic that picks food items to approximate
  your remaining calorie budget for each unlogged meal slot (favoring
  protein-density for a loss goal, calorie-density for a gain goal), plus
  workout suggestions sized to close your daily activity-calorie gap.
- **Phase 6 – Adaptive Progress System** (`ml/adaptive_engine.py`): fits a
  **scikit-learn `LinearRegression`** on your weight-log history (weight vs.
  day index) to estimate your *actual* weekly rate of change, compares it to
  the *expected* rate implied by your goal (~0.5 kg/week for loss, ~0.3 for
  gain, ~0 for maintain), and nudges your calorie target up or down when
  you're consistently off-track.
- **Phase 7 – Dashboard**: one aggregated endpoint/page combining today's
  calories, nutrition, activity, the weight graph (Chart.js), and the
  adaptive-progress verdict.

---

## 4. Switching from SQLite to MySQL

The project ships with SQLite for zero-config local development, but the
data layer (SQLAlchemy) makes MySQL a two-line change, matching the original
tech plan:

1. Create the database in MySQL:
   ```sql
   CREATE DATABASE ai_fitness_db;
   ```
2. Copy `backend/.env.example` to `backend/.env` and set:
   ```
   DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/ai_fitness_db
   ```
3. Re-run `python seed_data.py` to create tables and load the food/exercise data.

---

## 5. Testing

- Interactive API testing: `http://localhost:8000/docs` (Swagger UI) — every
  endpoint from Phases 2–7 can be exercised directly there.
- A full manual smoke test (create user → log food → log activity → get
  recommendations → log weight → get progress analysis → get dashboard) was
  run against this exact codebase before delivery and returned correct,
  goal-aware results end to end.

---

## 6. Notes / next steps you could add later

- Authentication (currently single-profile-per-browser via `localStorage`,
  no passwords) — fine for a personal/demo project, but add real auth
  (e.g. JWT) before deploying for multiple real users.
- More Indian regional dishes, or letting users add custom foods.
- A richer ML model (e.g. multiple regression incorporating logged calories
  and activity, not just weight) once you're collecting enough real data
  per user for it to be worth the complexity.
