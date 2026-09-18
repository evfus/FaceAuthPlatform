import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

function DeveloperLoginForm() {
  const [checkingSession, setCheckingSession] = useState(true);
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    async function checkSession() {
      const res = await fetch("http://localhost:8000/developer/me", {
        credentials: "include",
      });

      if (res.ok) {
        navigate("/developer/dashboard");
      } else {
        setCheckingSession(false);
      }
    }

    checkSession();
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    const endpoint = isSignup ? "/developer/register" : "/developer/login";

    const res = await fetch(`http://localhost:8000${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const errData = await res.json();
      setError(errData.detail ?? "Something went wrong. Please try again.");
      return;
    }

    navigate("/developer/dashboard");
  }

  if (checkingSession) {
    return <p>Loading...</p>;
  }

  return (
    <div className="page">
      <h1>{isSignup ? "Sign up as Developer" : "Log in as Developer"}</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}

      <form onSubmit={handleSubmit}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email address"
        />
        
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
          />
          <button type="submit">{isSignup ? "Sign up" : "Log in"}</button>
      </form>

      <button type="button" onClick={() => { setIsSignup(!isSignup); setError(""); }}>
        {isSignup ? "Already have an account? Log in" : "Need an account? Sign up"}
      </button>
    </div>
  );
}

export default DeveloperLoginForm;