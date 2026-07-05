import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    // Every request carries the token in its Authorization header (see api.js).
    api.hello().then((d) => setMessage(d.message)).catch((e) => setError(e.message));
    api.files().then((d) => setFiles(d.files)).catch((e) => setError(e.message));
  }, []);

  return (
    <main className="page center">
      <div className="shield">☁️</div>
      <h1>Welcome to the Cloud System</h1>

      {error && <div className="banner error">{error}</div>}
      {message && <div className="banner success">{message}</div>}

      <section className="card wide">
        <h3>Your private files</h3>
        {files.length === 0 ? (
          <p className="hint">No files yet.</p>
        ) : (
          <ul className="file-list">
            {files.map((f) => (
              <li key={f.id}>
                <span className="file-name">📄 {f.name}</span>
                <span className="file-date">{f.created_at}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="hint">
        Signed in as <strong>{user?.email}</strong>. Your access token lives only
        in this browser session and is revoked the moment you log out.
      </p>
    </main>
  );
}
