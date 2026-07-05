import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <main className="page center">
      <div className="shield">🔐</div>
      <h1>Welcome to the Cloud System</h1>
      <p className="lead">
        An extra layer of authentication that keeps your cloud files private -
        so that not even the cloud host can read them without your token.
      </p>

      {user && (
        <div className="banner success">
          {user.email} is successfully logged in for cloud access.
        </div>
      )}

      <div className="links">
        <a href="https://github.com/exadel-inc/CompreFace" target="_blank" rel="noreferrer">
          Read documentation
        </a>
        <span className="dot">|</span>
        <a href="https://bmsce.ac.in" target="_blank" rel="noreferrer">
          About our college (BMSCE)
        </a>
      </div>

      {!user && (
        <Link to="/login" className="btn primary big">
          Get started
        </Link>
      )}
    </main>
  );
}
