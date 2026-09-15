import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

interface DeveloperAuthState {
  loggedIn: boolean;
  email: string | null;
  loading: boolean;
  logout: () => Promise<void>;
}

function useDeveloperAuth(): DeveloperAuthState {
  const location = useLocation();
  const [loggedIn, setLoggedIn] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      try {
        const res = await fetch("http://localhost:8000/developer/me", {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          setLoggedIn(true);
          setEmail(data.email);
        } else {
          setLoggedIn(false);
          setEmail(null);
        }
      } finally {
        setLoading(false);
      }
    }
    checkAuth();
  }, [location.pathname]);

  async function logout() {
    await fetch("http://localhost:8000/developer/logout", {
      method: "POST",
      credentials: "include",
    });
    setLoggedIn(false);
    setEmail(null);
  }

  return { loggedIn, email, loading, logout };
}

export default useDeveloperAuth;