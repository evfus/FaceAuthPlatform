import { useEffect, useState } from "react";

interface UserInfo {
  email: string;
  needs_enrollment?: boolean;
}

function App() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const res = await fetch("http://localhost:8001/me",
        {
          credentials: "include",
        });
        
        if (!res.ok) throw new Error("Not logged in");
        
        const data = await res.json();
        setUser(data);
      } 
      catch {
        setUser(null);
      } 
      finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, []);

  const handleLogin = () => {
    const params = new URLSearchParams({
      client_id: "c992f5979aae354f0fc6de8c76c8d6a3",
      redirect_url: "http://localhost:8001/callback",
    });

    window.location.href = `http://localhost:5173/login?${params}`;
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h1>MyApp</h1>
      {user ? (
        <p>Logged in as {user.email}</p>
      ) : (
        <>
          <p>A demo client app using FaceAuth for login.</p>
          <button onClick={handleLogin}>Log in with FaceAuth</button>
        </>
      )}
    </div>
  );
}

export default App;