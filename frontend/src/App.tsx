import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginForm from "./LoginForm";
import Enroll from "./Enroll"
import Confirm from "./Confirm"
import AuthEvent from "./AuthEvents";
import Home from "./Home"
import NavBar from "./NavBar";
import Account from "./Account";
import DeveloperDashboard from "./DeveloperDashboard";
import DeveloperLoginForm from "./DeveloperLoginForm"
import DeveloperNavBar from "./DeveloperNavBar";

function App() {
  return (
    <BrowserRouter>
    <NavBar />
    <DeveloperNavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/enroll" element={<Enroll />} />
        <Route path="/confirm" element={<Confirm />} />
        <Route path="/admin" element={<AuthEvent />} />
        <Route path="/account" element={<Account />} />
        <Route path="/developer/login" element={<DeveloperLoginForm />} />
        <Route path="/developer/dashboard" element={<DeveloperDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
