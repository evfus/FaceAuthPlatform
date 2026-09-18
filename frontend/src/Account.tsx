import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "./useAuth";

interface Connection {
  application_id: number,
  name: string,
  connected_at: string
}

function Account() {
  const navigate = useNavigate();
  const { loggedIn, email, loading } = useAuth();
  const [connections, setConnections] = useState<Connection[]>([])

  useEffect(() => {
    if (!loading && !loggedIn) {
      navigate("/login");
    }
  }, [loading, loggedIn, navigate]);

  useEffect(() => {
    async function fetchConnections() {
      const res = await fetch("http://localhost:8000/auth/connections",
        {
          credentials: "include",
        });
      
      if (res.ok) {
        const data = await res.json();
        setConnections(data);
      }
    }

    if (loggedIn) {
      fetchConnections();
    }
  }, [loading, loggedIn]);

  async function handleDisconnect(applicationId: number) {
    const res = await fetch(`http://localhost:8000/auth/connections/${applicationId}`,
      {
        method: "DELETE",
        credentials: "include",
      });

    if (res.ok) {
      setConnections((prev) => prev.filter((c) => c.application_id !== applicationId));
    }
  }

  if (loading || !loggedIn) {
    return <p>Loading...</p>;
  }

  return (
    <div className="page">
      <h1>Account</h1>
      <p>Email: {email}</p>
      <button onClick={() => navigate(`/enroll?email=${new URLSearchParams({ email: email ?? "" }).toString()}`)}>
        Update Face Login
      </button>

      <h2>Connected Apps</h2>
      {connections.length === 0 ? (
        <p>No connected apps.</p>
      ) : (
        <ul>
          {connections.map((conn) => (
            <li key={conn.application_id}>
              {conn.name}
              <button onClick={() => handleDisconnect(conn.application_id)}>Disconnect</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Account;