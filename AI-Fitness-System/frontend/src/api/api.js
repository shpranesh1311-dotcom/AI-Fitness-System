const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch (_) {
      /* ignore parse errors */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Users / Profile (Phase 2)
  createUser: (data) => request("/api/users", { method: "POST", body: JSON.stringify(data) }),
  getUser: (id) => request(`/api/users/${id}`),
  updateUser: (id, data) => request(`/api/users/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  getHealthMetrics: (id) => request(`/api/users/${id}/health-metrics`),

  // Food & Nutrition (Phase 3)
  browseFoods: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/food/database${qs ? `?${qs}` : ""}`);
  },
  logFood: (userId, data) => request(`/api/food/log/${userId}`, { method: "POST", body: JSON.stringify(data) }),
  deleteFoodLog: (logId) => request(`/api/food/log/${logId}`, { method: "DELETE" }),
  getDailyNutrition: (userId, logDate) =>
    request(`/api/food/log/${userId}/daily${logDate ? `?log_date=${logDate}` : ""}`),

  // Activity (Phase 4)
  listExercises: () => request("/api/activity/exercises"),
  logActivity: (userId, data) => request(`/api/activity/log/${userId}`, { method: "POST", body: JSON.stringify(data) }),
  deleteActivityLog: (logId) => request(`/api/activity/log/${logId}`, { method: "DELETE" }),
  getDailyActivity: (userId, logDate) =>
    request(`/api/activity/log/${userId}/daily${logDate ? `?log_date=${logDate}` : ""}`),

  // AI Recommendations (Phase 5)
  getRecommendations: (userId) => request(`/api/recommendations/${userId}`),

  // Adaptive Progress (Phase 6)
  logWeight: (userId, data) => request(`/api/progress/${userId}/weight`, { method: "POST", body: JSON.stringify(data) }),
  getWeightHistory: (userId) => request(`/api/progress/${userId}/weight-history`),
  getProgressAnalysis: (userId) => request(`/api/progress/${userId}/analysis`),

  // Dashboard (Phase 7)
  getDashboard: (userId) => request(`/api/dashboard/${userId}`),
};

export default api;
