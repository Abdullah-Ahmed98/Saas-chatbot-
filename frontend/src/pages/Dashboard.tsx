import { useEffect, useState } from "react";
import { billingStatus, me, sessions } from "../api/client";

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [bill, setBill] = useState<any>(null);
  const [sessionCount, setSessionCount] = useState(0);

  useEffect(() => {
    me().then(setUser).catch(() => {});
    billingStatus().then(setBill).catch(() => {});
    sessions().then((s) => setSessionCount(s.length)).catch(() => {});
  }, []);

  const cards = [
    { label: "Plan", value: bill?.plan || "free", icon: "💎" },
    { label: "Subscription", value: bill?.active ? "Active" : "Not active", icon: "⚡" },
    { label: "Chat sessions", value: sessionCount, icon: "💬" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">Your workspace at a glance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="card p-5 hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <p className="text-gray-500 text-sm font-medium">{c.label}</p>
              <span className="text-xl">{c.icon}</span>
            </div>
            <p className="text-3xl font-bold mt-2 text-gray-900">{c.value}</p>
          </div>
        ))}
      </div>

      {user && (
        <div className="card p-5">
          <h2 className="font-semibold mb-3 text-gray-900">Account</h2>
          <div className="space-y-1">
            <p className="text-sm text-gray-700">{user.email}</p>
            <span
              className={`badge ${
                user.is_admin ? "bg-indigo-50 text-indigo-700" : "bg-gray-100 text-gray-600"
              }`}
            >
              {user.is_admin ? "Admin" : "Member"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
