import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "./useAuth";

function Account() {
  const navigate = useNavigate();
  const { loggedIn, email, loading } = useAuth();

  useEffect(() => {
    if (!loading && !loggedIn) {
      navigate("/login");
    }
  }, [loading, loggedIn, navigate]);

  if (loading || !loggedIn) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Account</h1>
      <p>Email: {email}</p>
      <button onClick={() => navigate(`/enroll?email=${encodeURIComponent(email ?? "")}`)}>
        Update Face Login
      </button>
    </div>
  );
}

export default Account;