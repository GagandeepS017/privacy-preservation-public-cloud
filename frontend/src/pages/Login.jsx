import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.status === 401 ? "Bad email or password" : err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page center">
      <form className="card" onSubmit={handleSubmit}>
        <h2>Login</h2>
        {error && <div className="banner error">{error}</div>}
        <input
          type="text"
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoFocus
        />
        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="btn primary" type="submit" disabled={busy}>
          {busy ? "Signing in..." : "Login"}
        </button>
        <p className="hint">
          Demo account: <code>test</code> / <code>test</code>
        </p>
      </form>
    </main>
  );
}
