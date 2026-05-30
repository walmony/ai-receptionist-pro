const API_URL = import.meta.env.VITE_API_URL || "";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Errore richiesta");
  return data;
}

export const api = {
  health: () => request("/health"),
  assistants: () => request("/assistants"),
  createAssistant: (payload) => request("/assistants", { method: "POST", body: JSON.stringify(payload) }),
  updateAssistant: (id, payload) => request(`/assistants/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteAssistant: (id) => request(`/assistants/${id}`, { method: "DELETE" }),
  faqs: (assistantId) => request(`/faqs${assistantId ? `?assistant_id=${assistantId}` : ""}`),
  createFaq: (payload) => request("/faqs", { method: "POST", body: JSON.stringify(payload) }),
  deleteFaq: (id) => request(`/faqs/${id}`, { method: "DELETE" }),
  calls: () => request("/calls"),
  testChat: (payload) => request("/test-chat", { method: "POST", body: JSON.stringify(payload) }),
};
