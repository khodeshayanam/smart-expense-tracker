const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // دسته‌ها
  getCategories: () => request("/categories/"),
  createCategory: (data) =>
    request("/categories/", { method: "POST", body: JSON.stringify(data) }),

  // تراکنش‌ها
  getExpenses: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/expenses/${qs ? `?${qs}` : ""}`);
  },
  createExpense: (data) =>
    request("/expenses/", { method: "POST", body: JSON.stringify(data) }),
  updateExpense: (id, data) =>
    request(`/expenses/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteExpense: (id) => request(`/expenses/${id}`, { method: "DELETE" }),
  suggestCategory: (description) =>
    request(`/expenses/suggest-category?description=${encodeURIComponent(description)}`),

  // عادت‌ها
  getHabits: () => request("/habits/"),
  createHabit: (data) =>
    request("/habits/", { method: "POST", body: JSON.stringify(data) }),
  logHabit: (data) => request("/habits/log", { method: "POST", body: JSON.stringify(data) }),
  getHabitStreak: (id) => request(`/habits/${id}/streak`),
  deleteHabit: (id) => request(`/habits/${id}`, { method: "DELETE" }),

  // تحلیل‌ها
  getOverview: () => request("/analytics/overview"),
  getSummary: (months = 12) => request(`/analytics/summary?months=${months}`),
  getPrediction: () => request("/analytics/predict"),
  getPatternInsights: () => request("/analytics/insights"),

  // هوش مصنوعی مولد
  getSmartInsight: () => request("/ai/smart-insights"),
  askAI: (message) => request("/ai/chat", { method: "POST", body: JSON.stringify({ message }) }),
};
