import { Link } from "react-router-dom";

export default function Logout() {
  return (
    <main className="page center">
      <h1>Thank you for accessing the session</h1>
      <p className="lead">
        Your token has been removed from session storage and revoked on the
        server. It no longer grants access to the cloud.
      </p>
      <Link to="/" className="btn primary">
        Back home
      </Link>
    </main>
  );
}
