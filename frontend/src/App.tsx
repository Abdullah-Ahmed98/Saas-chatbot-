import { Outlet, NavLink, useNavigate } from "react-router-dom";

const links = [
  { to: "/chat", label: "Chat", icon: "💬" },
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/billing", label: "Billing", icon: "💳" },
  { to: "/admin", label: "Admin", icon: "⚙️" },
];

export default function App() {
  const navigate = useNavigate();
  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <nav className="sticky top-0 z-20 bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-lg font-bold shadow-md">
              A
            </div>
            <div>
              <p className="font-bold text-gray-900 leading-none">Acme Assistant</p>
              <p className="text-[11px] text-gray-400 mt-0.5">AI Chatbot SaaS</p>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-1">
            {links.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={({ isActive }) =>
                  `px-3.5 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-indigo-50 text-indigo-700"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-100"
                  }`
                }
              >
                <span className="mr-1.5">{l.icon}</span>
                {l.label}
              </NavLink>
            ))}
          </div>

          <button
            onClick={logout}
            className="ml-3 px-3.5 py-2 rounded-lg text-sm font-medium text-gray-600 bg-gray-100 hover:bg-red-50 hover:text-red-600 transition-all"
          >
            Log out
          </button>
        </div>
      </nav>

      <main className="flex-1 max-w-7xl w-full mx-auto p-5">
        <Outlet />
      </main>
    </div>
  );
}
