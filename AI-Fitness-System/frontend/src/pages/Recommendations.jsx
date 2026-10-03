import React, { useEffect, useState } from "react";
import api from "../api/api";
import { useUser } from "../context/UserContext";

export default function Recommendations() {
  const { userId } = useUser();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRecommendations(userId);
      setData(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  if (!userId) return <div className="page"><p className="muted">Create your profile first.</p></div>;

  return (
    <div className="page">
      <h2>AI Recommendation Engine</h2>
      <p className="muted">
        Personalized meal and workout suggestions based on your goal and how
        many calories you have left today.
      </p>

      <button className="btn-secondary" onClick={load} disabled={loading}>
        {loading ? "Refreshing..." : "Refresh Recommendations"}
      </button>

      {error && <p className="error">{error}</p>}

      {data && (
        <>
          <div className="card">
            <p><strong>{data.calories_remaining}</strong> kcal remaining today ({data.log_date})</p>
            {data.notes.map((n, i) => <p key={i} className="muted">💡 {n}</p>)}
          </div>

          <h3>Meal Suggestions</h3>
          {data.meal_recommendations.length === 0 && <p className="muted">No meal suggestions right now — you may have hit your target already, or check the Food tab directly.</p>}
          <div className="rec-grid">
            {data.meal_recommendations.map((meal) => (
              <div key={meal.meal_type} className="card">
                <h4 className="capitalize">{meal.meal_type} <span className="muted">(~{Math.round(meal.target_calories)} kcal target)</span></h4>
                <ul className="rec-list">
                  {meal.items.map((item) => (
                    <li key={item.id}>
                      <strong>{item.name}</strong> — {item.calories} kcal, P{item.protein_g}/C{item.carbs_g}/F{item.fat_g}
                    </li>
                  ))}
                </ul>
                <div className="muted small">
                  Total: {meal.total_calories} kcal · P {meal.total_protein_g}g · C {meal.total_carbs_g}g · F {meal.total_fat_g}g
                </div>
              </div>
            ))}
          </div>

          <h3>Workout Suggestions</h3>
          {data.workout_recommendations.length === 0 && <p className="muted">No extra workout needed — you've already hit today's activity goal 🎉</p>}
          <div className="rec-grid">
            {data.workout_recommendations.map((w, i) => (
              <div key={i} className="card">
                <h4>{w.exercise.name} <span className="muted">({w.exercise.category})</span></h4>
                <p>Suggested duration: <strong>{w.suggested_duration_min} min</strong></p>
                <p className="muted small">Estimated burn: ~{w.estimated_calories_burned} kcal</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
