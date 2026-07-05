import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

// Guards routes that require a valid session token. Without one, bounce to login.
export default function ProtectedRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" replace />;
}
