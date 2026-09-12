import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginForm from "./LoginForm";
import Enroll from "./Enroll"
import Confirm from "./Confirm"

function App(){
    return(
    <BrowserRouter>
      <Routes>
        <Route path = "/login" element = {<LoginForm />} />
        <Route path = "/enroll" element = {<Enroll />} />
        <Route path = "/confirm" element = {<Confirm />} />
        <Route path = "/admin" element = {<h1>Admin placeholder</h1>} />
      </Routes>
    </BrowserRouter>
    );
}

export default App;
