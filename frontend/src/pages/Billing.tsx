import { useEffect, useState } from "react";
import { billingStatus, checkout } from "../api/client";

export default function BillingPage() {
  const [bill, setBill] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    billingStatus().then(setBill).catch(() => {});
  }, []);

  async function subscribe() {
    setLoading(true);
    setErr("");
    try {
      const res = await checkout();
      window.location.href = res.url;
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Billing</h1>
        <p className="text-sm text-gray-500 mt-0.5">Manage your subscription</p>
      </div>

      {bill?.active ? (
        <div className="card p-6 border-green-200 bg-gradient-to-br from-green-50 to-white">
          <div className="flex items-center gap-3 mb-2">
            <span className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 text-xl">
              ✓
            </span>
            <div>
              <p className="font-semibold text-green-800">Active subscription</p>
              <p className="text-sm text-gray-600 capitalize">Plan: {bill.plan}</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="card p-6">
          <p className="font-semibold mb-1 text-gray-900">No active subscription</p>
          <p className="text-gray-600 mb-4 text-sm">
            Subscribe to unlock premium features and higher usage limits.
          </p>
          {err && <p className="text-red-500 text-sm mb-2">{err}</p>}
          <button onClick={subscribe} disabled={loading} className="btn-accent">
            {loading ? "Redirecting…" : "Upgrade plan"}
          </button>
        </div>
      )}
    </div>
  );
}
