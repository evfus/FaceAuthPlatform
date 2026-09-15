import { useNavigate, useLocation } from "react-router-dom";
import useAuth from "./useAuth";

function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loggedIn, loading, logout } = useAuth();

  if (
    location.pathname === "/login" ||
    location.pathname === "/confirm" ||
    location.pathname === "/enroll" ||
    location.pathname.startsWith("/developer")
  ) {
    return null;
  }

  async function handleLogout() {
    await logout()
    navigate("/");
  }

  if (loading) {
    return <nav>FaceAuth</nav>;
  }

  return (
    <nav>
      <span onClick={() => navigate("/")}>FaceAuth</span>
      {loggedIn ? (
        <>
          <button onClick={() => navigate("/account")}>Account</button>
          <button onClick={handleLogout}>Log out</button>
        </>
      ) : (
        <button onClick={() => navigate("/login")}>Log in</button>
      )}
    </nav>
  );
}

export default NavBar;