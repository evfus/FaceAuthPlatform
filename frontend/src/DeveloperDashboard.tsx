import { useEffect, useState } from "react";
import type { FormEvent } from "react"
import { useNavigate } from "react-router-dom";
import useDeveloperAuth from "./useDeveloperAuth"

interface AppItem {
  id: number;
  name: string;
  client_id: string;
  redirect_url: string;
}

function DeveloperDashboard() {
  const { loggedIn, email, loading, logout } = useDeveloperAuth();
  const navigate = useNavigate();

  const [apps, setApps] = useState<AppItem[]>([]);
  const [appsLoading, setAppsLoading] = useState(true);
  const [appsError, setAppsError] = useState("");

  const [newName, setNewName] = useState("");
  const [newRedirectUrl, setNewRedirectUrl] = useState("");
  const [createError, setCreateError] = useState("");
  const [revealedSecret, setRevealedSecret] = useState<string | null>(null);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editRedirectUrl, setEditRedirectUrl] = useState("");
  const [editError, setEditError] = useState("");

  useEffect(() => {
    if (!loading && !loggedIn) {
      navigate("/developer/login");
    }
  }, [loading, loggedIn]);

  useEffect(() => {
    if (loading || !loggedIn) return;

    async function fetchApps() {
      try {
        const res = await fetch("http://localhost:8000/developer/applications",
        {
          credentials: "include",
        });
        if (!res.ok) {
          setAppsError("Failed to load applications.");
          return;
        }
        const data = await res.json();
        setApps(data);
      } finally {
        setAppsLoading(false);
      }
    }

    fetchApps();
  }, [loading, loggedIn]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setCreateError("");

    const res = await fetch("http://localhost:8000/developer/applications",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name: newName, redirect_url: newRedirectUrl }),
    });

    if (!res.ok) {
      setCreateError("Both fields are required.");
      return;
    }

    const data = await res.json();
    setApps([...apps, { id: data.id, name: data.name, client_id: data.client_id, redirect_url: data.redirect_url }]);
    setRevealedSecret(data.client_secret);
    setNewName("");
    setNewRedirectUrl("");
  }

  async function handleDelete(id: number) {
    const res = await fetch(`http://localhost:8000/developer/applications/${id}`,
    {
      method: "DELETE",
      credentials: "include",
    });

    if (res.ok) {
      setApps(apps.filter((app) => app.id !== id));
    }
  }

  function startEditing(app: AppItem) {
    setEditingId(app.id);
    setEditName(app.name);
    setEditRedirectUrl(app.redirect_url);
    setEditError("");
  }

  function cancelEditing() {
    setEditingId(null);
    setEditError("");
  }

  async function handleSaveEdit(id: number) {
    setEditError("");

    const res = await fetch(`http://localhost:8000/developer/applications/${id}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name: editName, redirect_url: editRedirectUrl }),
    });

    if (!res.ok) {
      setEditError("Both fields are required.");
      return;
    }

    const data = await res.json();
    setApps(apps.map((app) => (app.id === id ? { ...app, name: data.name, redirect_url: data.redirect_url } : app)));
    setEditingId(null);
  }

  if (loading || !loggedIn) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Developer Dashboard</h1>
      <p>Logged in as {email}</p>

      {revealedSecret && (
        <div style={{ border: "1px solid orange", padding: "1em" }}>
          <p>Save this client secret now, it won't be shown again:</p>
          <code>{revealedSecret}</code>
          <button type="button" onClick={() => setRevealedSecret(null)}>Dismiss</button>
        </div>
      )}

      <h2>Your Applications</h2>
      {appsLoading && <p>Loading applications...</p>}
      {appsError && <p style={{ color: "red" }}>{appsError}</p>}
      {!appsLoading && !appsError && apps.length === 0 && <p>No applications yet.</p>}

      <ul>
        {apps.map((app) => (
          <li key={app.id}>
            {editingId === app.id ? (
              <>
                <input value={editName} onChange={(e) => setEditName(e.target.value)} />
                <input value={editRedirectUrl} onChange={(e) => setEditRedirectUrl(e.target.value)} />
                {editError && <p style={{ color: "red" }}>{editError}</p>}
                 <div>
                  <button type="button" onClick={() => handleSaveEdit(app.id)}>Save</button>
                  <button type="button" onClick={cancelEditing}>Cancel</button>
                </div>
              </>
            ) : (
              <>
                {app.name} — {app.client_id} — {app.redirect_url}
                <button type="button" onClick={() => startEditing(app)}>Edit</button>
                <button type="button" onClick={() => handleDelete(app.id)}>Delete</button>
              </>
            )}
          </li>
        ))}
      </ul>

      <h2>Create Application</h2>
      {createError && <p style={{ color: "red" }}>{createError}</p>}
      
      <form onSubmit={handleCreate}>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Application name"
        />
        <input
          type="text"
          value={newRedirectUrl}
          onChange={(e) => setNewRedirectUrl(e.target.value)}
          placeholder="Redirect URL"
        />
        <button type="submit">Create</button>
      </form>  

      <button type="button" onClick={async () => { await logout(); navigate("/developer/login"); }}>
        Log out
      </button>
    </div>
  );
}

export default DeveloperDashboard;