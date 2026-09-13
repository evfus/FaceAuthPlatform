import { useRef, useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

function Enroll() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [samples, setSamples] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email");

  const navigate = useNavigate()

  useEffect(() => {
    async function startCamera() {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    }

    startCamera()
  }, []);

  function captureSample() {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (!video || !canvas) {
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d")
    if (!ctx) {
      return;
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");
    setSamples((prev) => [...prev, imageData]);
  }

  async function handleEnrollSubmit() {
    const formData = new FormData();

    for (const sample of samples) {
      const blob = await (await fetch(sample)).blob();
      formData.append("files", blob, "sample.jpg")
    }

    const res = await fetch("http://localhost:8000/face/enroll", {
      method: "POST",
      credentials: "include",
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json();
      const ERROR_MESSAGES: Record<string, string> = {
        "No face detected": "No face detected. Make sure your face is crearly visible.",
        "Multiple faces detected": "Multiple faces detected. Make sure you are alone in the face capture."
      }
      setError(ERROR_MESSAGES[errData.detail] ?? "Enrollment failed. Please try again.");
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

  function removeSample(index: number) {
    setSamples((prev) => prev.filter((_: string, i: number) => i !== index))
  }

  return (
    <div>
      <div>
        <h1>Face Enrollment</h1>
        {email && <p>Setting up face login for {email}</p>}
        <video
          ref={videoRef}
          autoPlay
          playsInline
          width={400}
          height={300}
          style={{ transform: "scaleX(-1)" }}
        />

        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      <div>
        <button
          type="button"
          onClick={() => { captureSample(); setError(""); }}
          style={{
            width: "70px",
            height: "70px",
            borderRadius: "50%",
            backgroundColor: "white",
            border: "4px solide #333",
            cursor: "pointer"
          }}
        />
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        {samples.map((sample, index) => (
          <div key={index}>
            <img src={sample} width={80} height={60} alt={`Sample ${index + 1}`} />
            <div>
              <button type="button" onClick={() => { removeSample(index); setError(""); }}>
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      <div>
        <button type="button" onClick={handleEnrollSubmit} disabled={samples.length === 0}>
          Finish Enrollment
        </button>
      </div>

      <div>
        {error && <p style={{ color: "red" }}> {error} </p>}
      </div>

    </div>
  )
}

export default Enroll;