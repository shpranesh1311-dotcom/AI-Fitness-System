import React, { useEffect, useState } from "react";
import api from "../api/api";
import { useUser } from "../context/UserContext";

const CATEGORIES = ["breakfast", "lunch", "dinner", "snack", "beverage", "dessert"];
const MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"];

export default function FoodTracking() {
  const { userId } = useUser();
  const [foods, setFoods] = useState([]);
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [vegOnly, setVegOnly] = useState(false);
  const [summary, setSummary] = useState(null);
  const [logging, setLoggingId] = useState(null);
  const [mealType, setMealType] = useState("breakfast");
  const [quantity, setQuantity] = useState(1);
  const [error, setError] = useState(null);

  const loadFoods = async () => {
    try {
      const params = {};
      if (category) params.category = category;
      if (search) params.search = search;
      if (vegOnly) params.vegetarian_only = "true";
      const data = await api.browseFoods(params);
      setFoods(data);
    } catch (e) {
      setError(e.message);
    }
  };

  const loadSummary = async () => {
    if (!userId) return;
    try {
      const data = await api.getDailyNutrition(userId);
      setSummary(data);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadFoods();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category, vegOnly]);

  useEffect(() => {
    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleLog = async (foodId) => {
    if (!userId) {
      setError("Create your profile first.");
      return;
    }
    setLoggingId(foodId);
    setError(null);
    try {
      await api.logFood(userId, { food_id: foodId, meal_type: mealType, quantity_servings: Number(quantity) });
      await loadSummary();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoggingId(null);
    }
  };

  const handleDeleteLog = async (logId) => {
    try {
      await api.deleteFoodLog(logId);
      await loadSummary();
    } catch (e) {
      setError(e.message);
    }
  };

  const pct = summary && summary.calorie_target
    ? Math.min(100, Math.round((summary.total_calories / summary.calorie_target) * 100))
    : 0;

  return (
    <div className="page">
      <h2>Food &amp; Nutrition Tracking</h2>
      <p className="muted">
        Indian / Tamil Nadu food database with calories, protein, carbs and
        fat — logged meal-wise and tracked daily.
      </p>

      {summary && (
        <div className="card">
          <h3>Today's Nutrition</h3>
          <div className="progress-bar-wrap">
            <div className="progress-bar" style={{ width: `${pct}%` }} />
          </div>
          <p>
            <strong>{summary.total_calories}</strong> / {summary.calorie_target} kcal
            {"  "}(<span className={summary.calories_remaining >= 0 ? "positive" : "negative"}>
              {summary.calories_remaining >= 0 ? `${summary.calories_remaining} kcal left` : `${Math.abs(summary.calories_remaining)} kcal over`}
            </span>)
          </p>
          <div className="macro-row">
            <span>Protein: {summary.total_protein_g}g</span>
            <span>Carbs: {summary.total_carbs_g}g</span>
            <span>Fat: {summary.total_fat_g}g</span>
          </div>

          {summary.meals.length > 0 && (
            <table className="table">
              <thead>
                <tr><th>Meal</th><th>Food</th><th>Qty</th><th>kcal</th><th>P/C/F</th><th></th></tr>
              </thead>
              <tbody>
                {summary.meals.map((m) => (
                  <tr key={m.id}>
                    <td className="capitalize">{m.meal_type}</td>
                    <td>{m.food_name}</td>
                    <td>{m.quantity_servings}x</td>
                    <td>{m.calories}</td>
                    <td>{m.protein_g}/{m.carbs_g}/{m.fat_g}</td>
                    <td><button className="btn-link" onClick={() => handleDeleteLog(m.id)}>remove</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      <div className="card">
        <h3>Browse Food Database</h3>
        <div className="filters-row">
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <input placeholder="Search (English or Tamil)" value={search} onChange={(e) => setSearch(e.target.value)} />
          <button className="btn-secondary" onClick={loadFoods}>Search</button>
          <label className="checkbox-label">
            <input type="checkbox" checked={vegOnly} onChange={(e) => setVegOnly(e.target.checked)} /> Veg only
          </label>
        </div>

        <div className="log-controls">
          <label>
            Meal type
            <select value={mealType} onChange={(e) => setMealType(e.target.value)}>
              {MEAL_TYPES.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </label>
          <label>
            Servings
            <input type="number" step="0.5" min="0.5" value={quantity} onChange={(e) => setQuantity(e.target.value)} style={{ width: 70 }} />
          </label>
        </div>

        {error && <p className="error">{error}</p>}

        <div className="food-grid">
          {foods.map((f) => (
            <div key={f.id} className="food-card">
              <div className="food-card-header">
                <strong>{f.name}</strong>
                {f.name_ta && <span className="muted"> ({f.name_ta})</span>}
              </div>
              <div className="muted small">{f.serving_desc || `${f.serving_size_g}g`}</div>
              <div className="food-macros">
                {f.calories} kcal · P {f.protein_g}g · C {f.carbs_g}g · F {f.fat_g}g
              </div>
              <button className="btn-primary small" disabled={logging === f.id} onClick={() => handleLog(f.id)}>
                {logging === f.id ? "Logging..." : "+ Log"}
              </button>
            </div>
          ))}
          {foods.length === 0 && <p className="muted">No foods match your filters.</p>}
        </div>
      </div>
    </div>
  );
}
