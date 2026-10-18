import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api/client";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [tenantName, setTenantName] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      await register({ email, password, full_name: fullName, tenant_name: tenantName });
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
          <h1 className="text-xl font-bold text-gray-900">Create your account</h1>
          <p className="text-sm text-gray-500 mt-1">Start your AI workspace</p>
        </div>
        {err && (
          <div className="bg-red-50 text-red-600 text-sm rounded-lg px-3 py-2 mb-3">{err}</div>
        )}
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Full name"
            className="input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
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
            placeholder="Password (min 6)"
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
          <input
            type="text"
            placeholder="Workspace name (optional)"
            className="input"
            value={tenantName}
            onChange={(e) => setTenantName(e.target.value)}
          />
        </div>
        <button className="btn-primary w-full mt-5" disabled={loading}>
          {loading ? "Creating…" : "Create account"}
        </button>
        <p className="text-sm text-gray-500 mt-5 text-center">
          Already registered?{" "}
          <Link to="/login" className="text-indigo-600 font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
