import { useState, useEffect } from "react";
import type { FormEvent } from "react"
import { useSearchParams, useNavigate } from "react-router-dom";

function LoginForm(){
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("")

  const [searchParams] = useSearchParams();
  const clientId = searchParams.get("client_id");
  const redirectUrl = searchParams.get("redirect_url");

  const [CheckingSession, setCheckingSession] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    async function checkSession(){
      const params = new URLSearchParams({
        client_id: clientId ?? "",
        redirect_url: redirectUrl ?? ""
      });

      const res = await fetch(`http://localhost:8000/auth/session-check?${params.toString()}`,
        {credentials: "include"}
      );
      const data = await res.json();

      if (data.logged_in && data.needs_enrollment){
        navigate("/enroll");
      }
      else if (data.logged_in && !data.needs_enrollment){
        navigate("/confirm")
      }
      else{
        setCheckingSession(false);
      }
    }

    checkSession()
  }, [clientId, redirectUrl]);

  async function handleSubmit(e: FormEvent){
    e.preventDefault();

    const endpoint = isSignup ? "/auth/register" : "/auth/authorize";

    const params = new URLSearchParams({
      client_id: clientId ?? "",
      redirect_url: redirectUrl ?? ""
    });

    const res = await fetch(`http://localhost:8000${endpoint}?${params.toString()}`,
      {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      credentials: "include",
      body: JSON.stringify({ email, password })
      });

      if (!res.ok){
        setError("Invalid email or password.");
        return;
      }

      const data = await res.json()

      if (data.status == "needs_enrollment"){
        navigate("/enroll")
      }
      else{
        navigate("/confirm")
      }
  }

  if (CheckingSession){
    return (<p>Loading...</p>)
  }

  return (
    <div>
      <h1>{isSignup ? "Sign up" : "Log in"}</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type = "email"
            value = {email}
            onChange = {(e) => setEmail(e.target.value)}
            placeholder = "Email address"
          />
        </div>

        <div>
          <input
            type = "password"
            value = {password}
            onChange = {(e) => setPassword(e.target.value)}
            placeholder = "Password"
          />
        </div>
        <button type = "submit">{isSignup ? "Sign up" : "Log in"}</button>
      </form>
      {error && <p style = {{ color: "red"}}> {error} </p>}
            
      <button type = "button" onClick = {() => setIsSignup(!isSignup)}>
        {isSignup ? "Already have an account? Log in" : "Need an account? Sign up"}
      </button>
    </div>
  );
}

export default LoginForm;