import React, { useState } from "react";
import api from "../api/api";
import { useUser } from "../context/UserContext";

const ACTIVITY_LEVELS = [
  { value: "sedentary", label: "Sedentary (little/no exercise)" },
  { value: "light", label: "Light (exercise 1-3 days/week)" },
  { value: "moderate", label: "Moderate (exercise 3-5 days/week)" },
  { value: "active", label: "Active (exercise 6-7 days/week)" },
  { value: "extra_active", label: "Extra Active (hard exercise + physical job)" },
];

const GOALS = [
  { value: "loss", label: "Weight Loss" },
  { value: "maintain", label: "Maintain Weight" },
  { value: "gain", label: "Weight Gain / Muscle Gain" },
];

const emptyForm = {
  name: "",
  age: "",
  gender: "male",
  height_cm: "",
  weight_kg: "",
  activity_level: "moderate",
  goal: "loss",
  goal_weight_kg: "",
};

export default function Profile({ onSaved }) {
  const { user, userId, login, refreshUser } = useUser();
  const [form, setForm] = useState(
    user
      ? {
          name: user.name,
          age: user.age,
          gender: user.gender,
          height_cm: user.height_cm,
          weight_kg: user.weight_kg,
          activity_level: user.activity_level,
          goal: user.goal,
          goal_weight_kg: user.goal_weight_kg || "",
        }
      : emptyForm
  );
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const buildPayload = () => ({
    name: form.name,
    age: Number(form.age),
    gender: form.gender,
    height_cm: Number(form.height_cm),
    weight_kg: Number(form.weight_kg),
    activity_level: form.activity_level,
    goal: form.goal,
    goal_weight_kg: form.goal_weight_kg ? Number(form.goal_weight_kg) : null,
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = buildPayload();
      let saved;
      if (userId) {
        saved = await api.updateUser(userId, payload);
        await refreshUser(userId);
      } else {
        saved = await api.createUser(payload);
        login(saved.id);
      }
      const hm = await api.getHealthMetrics(saved.id);
      setMetrics(hm);
      if (onSaved) onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="page">
      <h2>{userId ? "Your Profile" : "Create Your Profile"}</h2>
      <p className="muted">
        Step 2 of the system: tell us about yourself and your goal. We'll use
        this to calculate your BMI, BMR, TDEE and daily calorie / macro
        targets.
      </p>

      <form className="card form-grid" onSubmit={handleSubmit}>
        <label>
          Name
          <input name="name" value={form.name} onChange={handleChange} required />
        </label>
        <label>
          Age
          <input type="number" name="age" value={form.age} onChange={handleChange} required min="1" max="119" />
        </label>
        <label>
          Gender
          <select name="gender" value={form.gender} onChange={handleChange}>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </label>
        <label>
          Height (cm)
          <input type="number" name="height_cm" value={form.height_cm} onChange={handleChange} required min="50" max="260" />
        </label>
        <label>
          Weight (kg)
          <input type="number" step="0.1" name="weight_kg" value={form.weight_kg} onChange={handleChange} required min="20" max="400" />
        </label>
        <label>
          Goal Weight (kg) <span className="muted">(optional)</span>
          <input type="number" step="0.1" name="goal_weight_kg" value={form.goal_weight_kg} onChange={handleChange} />
        </label>
        <label>
          Activity Level
          <select name="activity_level" value={form.activity_level} onChange={handleChange}>
            {ACTIVITY_LEVELS.map((a) => (
              <option key={a.value} value={a.value}>{a.label}</option>
            ))}
          </select>
        </label>
        <label>
          Goal
          <select name="goal" value={form.goal} onChange={handleChange}>
            {GOALS.map((g) => (
              <option key={g.value} value={g.value}>{g.label}</option>
            ))}
          </select>
        </label>

        <div className="form-actions">
          <button className="btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving..." : userId ? "Update Profile" : "Create Profile"}
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      {metrics && (
        <div className="card metrics-card">
          <h3>Your Health Snapshot</h3>
          <div className="metrics-grid">
            <Metric label="BMI" value={metrics.bmi} sub={metrics.bmi_category} />
            <Metric label="BMR" value={`${metrics.bmr} kcal`} sub="Basal Metabolic Rate" />
            <Metric label="TDEE" value={`${metrics.tdee} kcal`} sub="Total Daily Energy Expenditure" />
            <Metric label="Calorie Target" value={`${metrics.calorie_target} kcal/day`} sub={`Goal: ${form.goal}`} />
            <Metric label="Protein" value={`${metrics.protein_g} g`} />
            <Metric label="Carbs" value={`${metrics.carbs_g} g`} />
            <Metric label="Fat" value={`${metrics.fat_g} g`} />
          </div>
        </div>
      )}
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
