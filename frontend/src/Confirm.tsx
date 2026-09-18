import { useSearchParams, useNavigate } from "react-router-dom";
import { useState } from "react";

function Confirm() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email");
  const clientId = searchParams.get("client_id");
  const redirectUrl = searchParams.get("redirect_url");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleContinue() {
    setError("");

    const params = new URLSearchParams();

    if (clientId) params.set("client_id", clientId);
    if (redirectUrl) params.set("redirect_url", redirectUrl);
    const query = params.toString();

    const res = await fetch(`http://localhost:8000/auth/authorize${query ? `?${query}` : ""}`,
      {
        method: "POST",
        credentials: "include"
      }
    );

    if (!res.ok) {
      setError("Something went wrong. Please try again.");
      return;
    }

    const data = await res.json();
    if (data.redirect_url) {
      window.location.href = data.redirect_url;
    }
    else {
      navigate("/account");
    }
  }

  async function handleDifferentAccount() {
    await fetch(`http://localhost:8000/auth/logout`,
      {
        method: "POST",
        credentials: "include"
      }
    );

    const params = new URLSearchParams();

    if (clientId) params.set("client_id", clientId);
    if (redirectUrl) params.set("redirect_url", redirectUrl);
    const query = params.toString();

    navigate(`/login${query ? `?${query}` : ""}`);
  }

  return (
    <div className="page">
      <div>
        <h1>Continue as {email}?</h1>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div>
        <button type="button" onClick={handleContinue}>
          Continue
        </button>
      </div>

      <div>
        <button type="button" onClick={handleDifferentAccount}>
          Log in as someone else
        </button>
      </div>
    </div>
  );
}

export default Confirm;