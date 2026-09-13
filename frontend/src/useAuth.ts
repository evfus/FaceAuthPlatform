import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

interface AuthState {
  loggedIn: boolean;
  email: string | null;
  needsEnrollment: boolean;
  loading: boolean;
  logout: () => Promise<void>;
}

function useAuth(): AuthState {
  const location = useLocation();
  const [loggedIn, setLoggedIn] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const [needsEnrollment, setNeedsEnrollment] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      try {
        const res = await fetch("http://localhost:8000/auth/me",
        {
          credentials: "include",
        });
        const data = await res.json();
        
        setLoggedIn(data.logged_in);
        
        if (data.logged_in) {
          setEmail(data.email);
          setNeedsEnrollment(data.needs_enrollment);
        }
      } 
      finally {
        setLoading(false);
      }
    }
    checkAuth();
  }, [location.pathname]);

  async function logout() {
    await fetch("http://localhost:8000/auth/logout", {
      method: "POST",
      credentials: "include",
    });
    setLoggedIn(false);
    setEmail(null);
    setNeedsEnrollment(false);
  }

  return { loggedIn, email, needsEnrollment, loading, logout };
}

export default useAuth;