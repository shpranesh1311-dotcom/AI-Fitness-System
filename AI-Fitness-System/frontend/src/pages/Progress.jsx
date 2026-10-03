import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../api/api";
import { useUser } from "../context/UserContext";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function Progress() {
  const { userId } = useUser();
  const [weight, setWeight] = useState("");
  const [logDate, setLogDate] = useState("");
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const load = async () => {
    if (!userId) return;
    try {
      const [h, a] = await Promise.all([
        api.getWeightHistory(userId),
        api.getProgressAnalysis(userId),
      ]);
      setHistory(h);
      setAnalysis(a);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  const handleLogWeight = async (e) => {
    e.preventDefault();
    if (!userId || !weight) return;
    setSaving(true);
    setError(null);
    try {
      await api.logWeight(userId, { weight_kg: Number(weight), log_date: logDate || undefined });
      setWeight("");
      setLogDate("");
      await load();
    } catch (e2) {
      setError(e2.message);
    } finally {
      setSaving(false);
    }
  };

  if (!userId) return <div className="page"><p className="muted">Create your profile first.</p></div>;

  const chartData = {
    labels: history.map((h) => h.log_date),
    datasets: [
      {
        label: "Weight (kg)",
        data: history.map((h) => h.weight_kg),
        borderColor: "#1f6f5c",
        backgroundColor: "rgba(31,111,92,0.15)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  const statusLabel = {
    on_track: "✅ On Track",
    slower_than_expected: "🐢 Slower Than Expected",
    faster_than_expected: "⚡ Faster Than Expected",
    insufficient_data: "📉 Need More Data",
  };

  return (
    <div className="page">
      <h2>Adaptive Progress System</h2>
      <p className="muted">
        Weight trend is fit with a linear regression model and compared
        against your expected rate — your calorie target adapts automatically.
      </p>

      {error && <p className="error">{error}</p>}

      <form className="card form-row" onSubmit={handleLogWeight}>
        <label>
          Weight (kg)
          <input type="number" step="0.1" value={weight} onChange={(e) => setWeight(e.target.value)} required />
        </label>
        <label>
          Date <span className="muted">(optional, defaults to today)</span>
          <input type="date" value={logDate} onChange={(e) => setLogDate(e.target.value)} />
        </label>
        <button className="btn-primary" disabled={saving} type="submit">
          {saving ? "Saving..." : "Log Weight"}
        </button>
      </form>

      {history.length > 0 && (
        <div className="card">
          <h3>Weight Trend</h3>
          <Line data={chartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
        </div>
      )}

      {analysis && (
        <div className="card">
          <h3>Analysis: {statusLabel[analysis.status] || analysis.status}</h3>
          <p>{analysis.message}</p>
          <div className="macro-row">
            <span>Data points: {analysis.data_points}</span>
            {analysis.actual_weekly_rate_kg !== null && <span>Actual: {analysis.actual_weekly_rate_kg} kg/week</span>}
            <span>Expected: {analysis.expected_weekly_rate_kg} kg/week</span>
            <span>Adjusted target: <strong>{analysis.adjusted_calorie_target} kcal/day</strong></span>
          </div>
        </div>
      )}
    </div>
  );
}
