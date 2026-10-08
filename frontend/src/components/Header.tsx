import { useNavigate, Link } from "react-router-dom";

export function Header() {
  const navigate = useNavigate();
  const isAuthenticated = Boolean(localStorage.getItem("pcleads_token"));

  function handleLogout() {
    localStorage.removeItem("pcleads_token");
    navigate("/login");
  }

  return (
    <header className="border-b border-slate-800 bg-slate-950 px-6 py-4">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        <Link to="/" className="text-xl font-bold text-white hover:opacity-90">
          PCI-LEADS
        </Link>

        <nav>
          {isAuthenticated ? (
            <button
              onClick={handleLogout}
              className="rounded-md border border-slate-800 bg-slate-900 px-3 py-1.5 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
            >
              Sair
            </button>
          ) : (
            <Link
              to="/login"
              className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Entrar
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}