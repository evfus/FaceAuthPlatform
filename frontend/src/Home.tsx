import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div>
      <h1>FaceAuth</h1>
      <p>
        FaceAuth is a face-authentication identity provider. Apps can let
        their users log in with their face instead of (or alongside) a
        password.
      </p>
      <button onClick={() => navigate("/login")}>Log In</button>
      <button onClick={() => navigate("/login?mode=signup")}>Sign Up</button>
    </div>
  );
}

export default Home;