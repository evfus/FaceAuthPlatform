import { useState, useEffect } from "react";

interface AuthEvent {
  id: number;
  created_at: string;
  result: string;
  confidence: number | null;
  reason: string | null;
  user_email: string | null;
  application_name: string | null;
}

function AuthEvents() {
  const [events, setEvents] = useState<AuthEvent[]>([]);
  const [resultFilter, setResultFilter] = useState("all");
  const [appFilter, setAppFilter] = useState("all");
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest">("newest");

  const filteredEvents = events
    .filter((event) => resultFilter === "all" || event.result === resultFilter)
    .filter((event) => appFilter === "all" || event.application_name === appFilter)
    .sort((a, b) => {
      const diff = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      return sortOrder === "newest" ? -diff : diff;
    });

  useEffect(() => {
    async function fetchEvents() {
      const res = await fetch("http://localhost:8000/admin/auth-events");
      const data = await res.json();
      setEvents(data);
    }

    fetchEvents();
  }, []);

  return (
    <div className="page">
      <h1>Authentication Events</h1>
      <div>
        <select value={resultFilter} onChange={(e) => setResultFilter(e.target.value)}>
          <option value="all">All results</option>
          <option value="success">Success</option>
          <option value="failure">Failure</option>
        </select>

        <select value={appFilter} onChange={(e) => setAppFilter(e.target.value)}>
          <option value="all">All apps</option>
          {[...new Set(events.map((e) => e.application_name).filter(Boolean))].map((name) => (
            <option key={name} value={name ?? ""}>
              {name}
            </option>
          ))}
        </select>

        <button type="button" onClick={() => setSortOrder(sortOrder === "newest" ? "oldest" : "newest")}>
          Sort: {sortOrder === "newest" ? "Newest first" : "Oldest first"}
        </button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>User</th>
            <th>App</th>
            <th>Result</th>
            <th>Confidence</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {filteredEvents.map((event) => (
            <tr key={event.id}>
              <td>{new Date(event.created_at).toLocaleString()}</td>
              <td>{event.user_email ?? "—"}</td>
              <td>{event.application_name ?? "—"}</td>
              <td>{event.result}</td>
              <td>{event.confidence?.toFixed(2) ?? "—"}</td>
              <td>{event.reason ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AuthEvents;