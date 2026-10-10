const API_BASE_URL = "http://127.0.0.1:5000/api";

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("heart_token");
  const headers = {"Content-Type": "application/json", ...(options.headers || {})};
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE_URL}${path}`, {...options, headers});
  const body = await response.json();
  if (!response.ok) throw new Error(body.details || body.error || "Request failed");
  return body;
}
