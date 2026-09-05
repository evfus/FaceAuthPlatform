import { BrowserRouter, Routes, Route } from "react-router-dom";
import LoginForm from "./LoginForm";

function App(){
    return(
    <BrowserRouter>
      <Routes>
        <Route path = "/login" element = {<LoginForm />} />
        <Route path = "/admin" element = {<h1>Admin placeholder</h1>}/>
      </Routes>
    </BrowserRouter>
    );
}

export default App;
