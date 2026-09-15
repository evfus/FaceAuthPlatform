import { useNavigate, useLocation } from "react-router-dom";
import useDeveloperAuth from "./useDeveloperAuth";

function DeveloperNavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loggedIn, loading, logout } = useDeveloperAuth();

  if (location.pathname !== "/developer/dashboard") {
    return null;
  }

  async function handleLogout() {
    await logout();
    navigate("/developer/login");
  }

  if (loading) {
    return <nav>FaceAuth Developers</nav>;
  }

  return (
    <nav>
      <span onClick={() => navigate("/developer/dashboard")}>FaceAuth Developers</span>
      {loggedIn && <button onClick={handleLogout}>Log out</button>}
    </nav>
  );
}

export default DeveloperNavBar;