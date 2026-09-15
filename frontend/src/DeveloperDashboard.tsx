import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useDeveloperAuth from "./useDeveloperAuth"

function DeveloperDashboard() {
  const { loggedIn, email, loading, logout } = useDeveloperAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if(!loading && !loggedIn){
      navigate("/developer/login");
    }
  }, [loading, loggedIn]);

  if (loading && !loggedIn) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Developer Dashboard</h1>
      <p>Logged in as {email}</p>
      <button
        type="button"
        onClick={async () => {
          await logout();
          navigate("/developer/login");
        }}
      >
        Log out
      </button>
    </div>
  );
}

export default DeveloperDashboard;