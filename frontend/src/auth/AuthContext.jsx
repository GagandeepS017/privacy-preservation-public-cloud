import { createContext, useContext, useEffect, useState } from "react";
import { api, tokenStore } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(tokenStore.get());
  const [user, setUser] = useState(null);

  // On load, sync the token from session storage (mirrors the report's
  // syncTokenFromSessionStore) and fetch the current user's profile.
  useEffect(() => {
    const stored = tokenStore.get();
    if (stored && stored !== "undefined") {
      setToken(stored);
      api.me().then(setUser).catch(() => logout());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(email, password) {
    const { access_token } = await api.login(email, password);
    tokenStore.set(access_token);
    setToken(access_token);
    const profile = await api.me();
    setUser(profile);
    return profile;
  }

  async function logout() {
    try {
      await api.logout();
    } catch {
      /* token may already be gone; clear locally regardless */
    }
    tokenStore.clear();
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
