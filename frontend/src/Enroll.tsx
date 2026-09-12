import { useRef, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Enroll() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [samples, setSamples] = useState<string[]>([]);
  const [error, setError] = useState("");
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
      setError("Enrollment failed. Please try again.");
      return;
    }

    const data = await res.json();

    if (data.redirect_url) {
      window.location.href = data.redirect_url;
    }
    else {
      console.log("Enrollment updated successfully.");
    }
  }

  function removeSample(index: number) {
    setSamples((prev) => prev.filter((_: string, i: number) => i !== index))
  }

  return (
    <div>
      <div>
        <h1>Face Enrollment</h1>
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
          onClick={captureSample}
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
              <button type="button" onClick={() => removeSample(index)}>
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

    </div>
  )
}

export default Enroll;