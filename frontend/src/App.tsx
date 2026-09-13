import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginForm from "./LoginForm";
import Enroll from "./Enroll"
import Confirm from "./Confirm"
import AuthEvent from "./AuthEvents";
import Home from "./Home"
import NavBar from "./NavBar";

function App() {
  return (
    <BrowserRouter>
    <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/enroll" element={<Enroll />} />
        <Route path="/confirm" element={<Confirm />} />
        <Route path="/admin" element={<AuthEvent />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
