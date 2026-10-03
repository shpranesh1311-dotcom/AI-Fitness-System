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

export default function Dashboard({ onGoToProfile }) {
  const { userId } = useUser();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    if (!userId) return;
    try {
      const res = await api.getDashboard(userId);
      setData(res);
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  if (!userId) {
    return (
      <div className="page">
        <div className="card empty-state">
          <h2>Welcome 👋</h2>
          <p>Create your profile to see your personalized dashboard.</p>
          <button className="btn-primary" onClick={onGoToProfile}>Create Profile</button>
        </div>
      </div>
    );
  }

  if (error) return <div className="page"><p className="error">{error}</p></div>;
  if (!data) return <div className="page"><p className="muted">Loading dashboard...</p></div>;

  const { health_metrics: hm, today_nutrition: nut, today_activity: act, weight_trend, progress } = data;
  const pct = hm.calorie_target ? Math.min(100, Math.round((nut.total_calories / hm.calorie_target) * 100)) : 0;

  const chartData = {
    labels: weight_trend.map((w) => w.log_date),
    datasets: [
      {
        label: "Weight (kg)",
        data: weight_trend.map((w) => w.weight_kg),
        borderColor: "#1f6f5c",
        backgroundColor: "rgba(31,111,92,0.15)",
        tension: 0.3,
        fill: true,
      },
    ],
  };

  return (
    <div className="page">
      <h2>Hi {data.user.name} 👋</h2>
      <p className="muted">Goal: <span className="capitalize">{data.user.goal}</span> · Activity: {data.user.activity_level}</p>

      <div className="metrics-grid">
        <Metric label="BMI" value={hm.bmi} sub={hm.bmi_category} />
        <Metric label="Calorie Target" value={`${hm.calorie_target} kcal`} />
        <Metric label="Consumed Today" value={`${nut.total_calories} kcal`} />
        <Metric label="Burned Today" value={`${act.total_calories_burned} kcal`} />
        <Metric label="Steps Today" value={act.total_steps} />
        <Metric label="Current Weight" value={`${data.user.weight_kg} kg`} />
      </div>

      <div className="card">
        <h3>Today's Calories</h3>
        <div className="progress-bar-wrap">
          <div className="progress-bar" style={{ width: `${pct}%` }} />
        </div>
        <p>{nut.total_calories} / {hm.calorie_target} kcal ({nut.calories_remaining >= 0 ? `${nut.calories_remaining} left` : `${Math.abs(nut.calories_remaining)} over`})</p>
        <div className="macro-row">
          <span>Protein: {nut.total_protein_g}g / {hm.protein_g}g</span>
          <span>Carbs: {nut.total_carbs_g}g / {hm.carbs_g}g</span>
          <span>Fat: {nut.total_fat_g}g / {hm.fat_g}g</span>
        </div>
      </div>

      {weight_trend.length > 0 && (
        <div className="card">
          <h3>Weight Progress</h3>
          <Line data={chartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
        </div>
      )}

      <div className="card">
        <h3>Adaptive Progress</h3>
        <p>{progress.message}</p>
        <p className="muted small">Adjusted calorie target suggestion: <strong>{progress.adjusted_calorie_target} kcal/day</strong></p>
      </div>
    </div>
  );
}

function Metric({ label, value, sub }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  );
}
