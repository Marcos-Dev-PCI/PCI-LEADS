import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Header } from "./components/Header";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950">
        <Header />
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Tudo aqui dentro exige login */}
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Home />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;