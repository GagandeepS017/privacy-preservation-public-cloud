import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function Navbar() {
  const { token, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/logout");
  }

  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        Cloud System
      </Link>
      {token ? (
        <button className="btn" onClick={handleLogout}>
          Logout
        </button>
      ) : (
        <Link to="/login" className="btn">
          Login
        </Link>
      )}
    </nav>
  );
}
