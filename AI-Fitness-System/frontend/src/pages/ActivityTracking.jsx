import React, { useEffect, useState } from "react";
import api from "../api/api";
import { useUser } from "../context/UserContext";

export default function ActivityTracking() {
  const { userId } = useUser();
  const [exercises, setExercises] = useState([]);
  const [exerciseId, setExerciseId] = useState("");
  const [duration, setDuration] = useState(30);
  const [steps, setSteps] = useState(0);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const loadExercises = async () => {
    try {
      const data = await api.listExercises();
      setExercises(data);
      if (data.length) setExerciseId(String(data[0].id));
    } catch (e) {
      setError(e.message);
    }
  };

  const loadSummary = async () => {
    if (!userId) return;
    try {
      const data = await api.getDailyActivity(userId);
      setSummary(data);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    loadExercises();
  }, []);

  useEffect(() => {
    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleLogExercise = async () => {
    if (!userId) { setError("Create your profile first."); return; }
    setSaving(true);
    setError(null);
    try {
      await api.logActivity(userId, { exercise_id: Number(exerciseId), duration_min: Number(duration) });
      await loadSummary();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleLogSteps = async () => {
    if (!userId) { setError("Create your profile first."); return; }
    setSaving(true);
    setError(null);
    try {
      await api.logActivity(userId, { steps: Number(steps) });
      await loadSummary();
      setSteps(0);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (logId) => {
    try {
      await api.deleteActivityLog(logId);
      await loadSummary();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="page">
      <h2>Activity &amp; Workout Tracking</h2>
      <p className="muted">Log steps, exercises and workout duration to estimate calories burned.</p>

      {error && <p className="error">{error}</p>}

      <div className="card grid-2">
        <div>
          <h3>Log Exercise</h3>
          <label>
            Exercise
            <select value={exerciseId} onChange={(e) => setExerciseId(e.target.value)}>
              {exercises.map((ex) => (
                <option key={ex.id} value={ex.id}>{ex.name} ({ex.category})</option>
              ))}
            </select>
          </label>
          <label>
            Duration (minutes)
            <input type="number" min="1" value={duration} onChange={(e) => setDuration(e.target.value)} />
          </label>
          <button className="btn-primary" disabled={saving} onClick={handleLogExercise}>
            {saving ? "Saving..." : "+ Log Exercise"}
          </button>
        </div>

        <div>
          <h3>Log Steps</h3>
          <label>
            Steps today
            <input type="number" min="0" value={steps} onChange={(e) => setSteps(e.target.value)} />
          </label>
          <button className="btn-secondary" disabled={saving} onClick={handleLogSteps}>
            {saving ? "Saving..." : "+ Log Steps"}
          </button>
        </div>
      </div>

      {summary && (
        <div className="card">
          <h3>Today's Activity</h3>
          <div className="macro-row">
            <span>Steps: {summary.total_steps}</span>
            <span>Duration: {summary.total_duration_min} min</span>
            <span>Calories burned: {summary.total_calories_burned} kcal</span>
          </div>

          {summary.logs.length > 0 && (
            <table className="table">
              <thead>
                <tr><th>Exercise</th><th>Steps</th><th>Duration</th><th>kcal burned</th><th></th></tr>
              </thead>
              <tbody>
                {summary.logs.map((l) => (
                  <tr key={l.id}>
                    <td>{l.exercise_name || "-"}</td>
                    <td>{l.steps || 0}</td>
                    <td>{l.duration_min} min</td>
                    <td>{l.calories_burned}</td>
                    <td><button className="btn-link" onClick={() => handleDelete(l.id)}>remove</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
