import { useEffect, useState } from "react";
import { adminTenants, adminUsers } from "../api/client";

export default function AdminPage() {
  const [tenants, setTenants] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    adminTenants().then(setTenants).catch((e) => setErr(e.message));
    adminUsers().then(setUsers).catch(() => {});
  }, []);

  if (err && err.includes("403")) {
    return (
      <div className="card p-8 text-center max-w-md mx-auto mt-10">
        <p className="text-gray-500">🔒 You do not have admin access.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin</h1>
        <p className="text-sm text-gray-500 mt-0.5">Manage tenants and users</p>
      </div>
      {err && !err.includes("403") && <p className="text-red-500 text-sm">{err}</p>}

      <section className="card overflow-hidden">
        <h2 className="font-semibold mb-3 px-5 py-4 border-b border-gray-100 text-gray-900">
          Tenants
        </h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
              <th className="p-4">Name</th>
              <th className="p-4">Plan</th>
              <th className="p-4">Active</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((t) => (
              <tr key={t.id} className="border-b border-gray-50 last:border-0">
                <td className="p-4 font-medium text-gray-800">{t.name}</td>
                <td className="p-4 text-gray-600 capitalize">{t.plan}</td>
                <td className="p-4">
                  <span
                    className={`badge ${
                      t.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {t.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
              </tr>
            ))}
            {tenants.length === 0 && (
              <tr>
                <td colSpan={3} className="p-5 text-gray-400">No tenants</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <section className="card overflow-hidden">
        <h2 className="font-semibold mb-3 px-5 py-4 border-b border-gray-100 text-gray-900">
          Users
        </h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
              <th className="p-4">Email</th>
              <th className="p-4">Name</th>
              <th className="p-4">Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-gray-50 last:border-0">
                <td className="p-4 font-medium text-gray-800">{u.email}</td>
                <td className="p-4 text-gray-600">{u.full_name || "—"}</td>
                <td className="p-4">
                  <span
                    className={`badge ${
                      u.is_admin ? "bg-indigo-50 text-indigo-700" : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {u.is_admin ? "Admin" : "Member"}
                  </span>
                </td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr>
                <td colSpan={3} className="p-5 text-gray-400">No users</td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
