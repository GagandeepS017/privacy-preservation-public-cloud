// Thin API client. In development every request goes to /api and Vite proxies
// it to the Flask backend; VITE_API_URL can override this for production.
const BASE = import.meta.env.VITE_API_URL || "";

const TOKEN_KEY = "token";

export const tokenStore = {
  get: () => sessionStorage.getItem(TOKEN_KEY),
  set: (token) => sessionStorage.setItem(TOKEN_KEY, token),
  clear: () => sessionStorage.removeItem(TOKEN_KEY),
};

async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = tokenStore.get();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const error = new Error(data.msg || `Request failed (${res.status})`);
    error.status = res.status;
    throw error;
  }
  return data;
}

export const api = {
  login: (email, password) =>
    request("/api/token", { method: "POST", body: { email, password } }),
  register: (email, password, display_name) =>
    request("/api/register", {
      method: "POST",
      body: { email, password, display_name },
    }),
  logout: () => request("/api/logout", { method: "POST", auth: true }),
  me: () => request("/api/me", { auth: true }),
  hello: () => request("/api/hello", { auth: true }),
  files: () => request("/api/files", { auth: true }),
  faceStatus: () => request("/api/face/status"),
};
