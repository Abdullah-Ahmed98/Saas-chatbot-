import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api/client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      await login({ email, password });
      navigate("/chat");
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-violet-50">
      <form
        onSubmit={onSubmit}
        className="card p-8 w-full max-w-sm bg-white/90 backdrop-blur"
      >
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4 shadow-lg">
            A
          </div>
          <h1 className="text-xl font-bold text-gray-900">Welcome back</h1>
          <p className="text-sm text-gray-500 mt-1">Sign in to your workspace</p>
        </div>
        {err && (
          <div className="bg-red-50 text-red-600 text-sm rounded-lg px-3 py-2 mb-3">{err}</div>
        )}
        <div className="space-y-3">
          <input
            type="email"
            placeholder="Email"
            className="input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button className="btn-primary w-full mt-5" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </button>
        <p className="text-sm text-gray-500 mt-5 text-center">
          No account?{" "}
          <Link to="/register" className="text-indigo-600 font-medium hover:underline">
            Create one
          </Link>
        </p>
      </form>
    </div>
  );
}
