import { useState, useEffect, useRef } from "react";
import type { FormEvent } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

type Stage = "email" | "face" | "password";

function LoginForm() {
  const [searchParams] = useSearchParams();
  const clientId = searchParams.get("client_id");
  const redirectUrl = searchParams.get("redirect_url");
  const mode = searchParams.get("mode");

  const [CheckingSession, setCheckingSession] = useState(false);
  const [isSignup, setIsSignup] = useState(mode === "signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [stage, setStage] = useState<Stage>("email");

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const navigate = useNavigate();

  useEffect(() => {
    async function checkSession() {
      const params = new URLSearchParams();

      if (clientId) params.set("client_id", clientId);
      if (redirectUrl) params.set("redirect_url", redirectUrl);
      const query = params.toString();

      const res = await fetch(`http://localhost:8000/auth/session-check${query ? `?${query}` : ""}`,
        { credentials: "include" }
      );
      const data = await res.json();

      if (data.logged_in && data.needs_enrollment) {
        navigate(`/enroll?${new URLSearchParams({ email: data.email }).toString()}`);
      }
      else if (data.logged_in && !data.needs_enrollment) {
        const params = new URLSearchParams({ email: data.email });

        if (clientId) params.set("client_id", clientId);
        if (redirectUrl) params.set("redirect_url", redirectUrl);
        const query = params.toString();

        navigate(`/confirm${query ? `?${query}` : ""}`);
      }
      else {
        setCheckingSession(false);
      }
    }

    checkSession();
  }, [clientId, redirectUrl]);

  useEffect(() => {
    if (stage !== "face") return;

    async function startCamera() {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    }

    startCamera();
  }, [stage]);

  async function handleEmailSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    const params = new URLSearchParams({ email });

    const res = await fetch(`http://localhost:8000/auth/email-exists?${params.toString()}`,
      { credentials: "include" }
    );

    const data = await res.json();

    if (isSignup) {
      if (data.exists) {
        setError("Email already exists.");
        return;
      }
      setStage("password");
      return;
    }

    if (!data.exists) {
      setError("No account found with this email.");
      return;
    }

    setStage(data.needs_enrollment ? "password" : "face");
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const endpoint = isSignup ? "/auth/register" : "/auth/authorize";

    const params = new URLSearchParams();

    if (clientId) params.set("client_id", clientId);
    if (redirectUrl) params.set("redirect_url", redirectUrl);
    const query = params.toString();

    const res = await fetch(`http://localhost:8000${endpoint}${query ? `?${query}` : ""}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password })
      });

    if (!res.ok) {
      const errData = await res.json();

      setError(errData.detail ?? "Something went wrong. Please try again.");
      return;
    }

    const data = await res.json();

    if (data.status == "needs_enrollment") {
      navigate(`/enroll?${new URLSearchParams({ email }).toString()}`);
    }
    else if (data.redirect_url){
      window.location.href = data.redirect_url;
    }
    else{
      navigate("/account");
    }
  }

  async function handleFaceCapture() {
    setError("");

    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpg");

    const blob = await (await fetch(imageData)).blob();

    const formData = new FormData();

    formData.append("email", email);
    if (clientId) formData.append("client_id", clientId);
    if (redirectUrl) formData.append("redirect_url", redirectUrl);
    formData.append("file", blob, "capture.jpg");

    const res = await fetch("http://localhost:8000/auth/login/face",
      {
        method: "POST",
        credentials: "include",
        body: formData
      }
    );

    if (!res.ok) {
      setError("Something went wrong. Please try again.");
      return;
    }

    const data = await res.json()

    const REASON_MESSAGES: Record<string, string> = {
      no_face_detected: "No face detected. Make sure your face is clearly visible.",
      multiple_faces_detected: "Multiple faces detected. Make sure you are alone in the face capture.",
      below_threshold: "Face did not match. Please try again."
    }

    if (!data.matched) {
      setError(REASON_MESSAGES[data.reason] ?? "Face did not match. Pleasy try again.");
      return;
    }

    if(data.redirect_url){
      window.location.href = data.redirect_url;
    }
    else{
      navigate("/account")
    }
  }

  if (CheckingSession) {
    return (<p>Loading...</p>);
  }

  if (stage === "email") {
    return (
      <div>
        <h1>{isSignup ? "Sign up" : "Log in"}</h1>
        <form onSubmit={handleEmailSubmit}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email address"
          />
          <div>
            <button type="submit">Continue</button>
          </div>
        </form>

        {error && <p style={{ color: "red" }}> {error} </p>}
        
        <button type="button" onClick={() => { setIsSignup(!isSignup); setError(""); }}>
          {isSignup ? "Already have an account? Log in" : "Need an account? Sign up"}
        </button>
      </div>
    );
  }

  if (stage === "password") {
    return (
      <div>
        <h1>{isSignup ? "Sign up" : "Log in"}</h1>
        {error && <p style={{ color: "red" }}>{error}</p>}

        <form onSubmit={handleSubmit}>
          <input type="email" value={email} disabled />
          <div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
            />
          </div>

          <div>
            <button type="submit">{isSignup ? "Sign up" : "Log in"}</button>
          </div>

          <div>
            <button type="button" onClick={() => { setStage("email"); setError(""); setPassword(""); }}>
              Use a different email
            </button>
          </div>
        </form>
      </div>
    );
  }

  if (stage === "face") {
    return (
      <div>
        <h1>Face Login</h1>
        {error && <p style={{ color: "red" }}> {error} </p>}

        <video
          ref={videoRef}
          autoPlay
          playsInline
          width={400}
          height={300}
          style={{ transform: "scaleX(-1)" }}
        />

        <canvas ref={canvasRef} style={{ display: "none" }} />
        <div>
          <button
            type="button"
            onClick={handleFaceCapture}
            style={{
              width: "70px",
              height: "70px",
              borderRadius: "50%",
              backgroundColor: "white",
              border: "4px solid #333",
              cursor: "pointer",
            }}
          />
        </div>

        {error && (
          <button type="button" onClick={() => { setStage("password"); setError(""); }}>
            Try password instead
          </button>
        )}
      </div>
    );
  }
}

export default LoginForm;