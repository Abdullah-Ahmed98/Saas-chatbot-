const BASE = "/api";

function token() {
  return localStorage.getItem("token") || "";
}

export async function api<T = unknown>(
  path: string,
  opts: { method?: string; body?: unknown; stream?: boolean } = {}
): Promise<T> {
  const res = await fetch(BASE + path, {
    method: opts.method || "GET",
    headers: {
      Authorization: `Bearer ${token()}`,
      "Content-Type": "application/json",
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

export async function register(body: {
  email: string;
  password: string;
  full_name?: string;
  tenant_name?: string;
}) {
  const data = await api<{ access_token: string; refresh_token: string; user_id: string }>(
    "/auth/register",
    { method: "POST", body }
  );
  localStorage.setItem("token", data.access_token);
  return data;
}

export async function login(body: { email: string; password: string }) {
  const data = await api<{ access_token: string; refresh_token: string }>(
    "/auth/login",
    { method: "POST", body }
  );
  localStorage.setItem("token", data.access_token);
  return data;
}

export function me() {
  return api<{ email: string; full_name: string; is_admin: boolean; tenant_id: string | null }>(
    "/auth/me"
  );
}

export function sessions() {
  return api<{ id: string; title: string; llm_provider: string }[]>("/chat/sessions");
}

export function sessionDetail(id: string) {
  return api<{ id: string; title: string; messages: { id: string; role: string; content: string }[] }>(
    `/chat/sessions/${id}`
  );
}

export function deleteSession(id: string) {
  return api(`/chat/sessions/${id}`, { method: "DELETE" });
}

export function billingStatus() {
  return api<{ active: boolean; plan: string; status: string | null }>("/billing/status");
}

export function adminTenants() {
  return api<{ id: string; name: string; plan: string; is_active: boolean }[]>("/admin/tenants");
}

export function adminUsers() {
  return api<{ id: string; email: string; full_name: string; is_admin: boolean }[]>("/admin/users");
}

export function checkout(successUrl?: string) {
  return api<{ url: string }>(
    "/billing/checkout",
    {
      method: "POST",
      body: {
        success_url: successUrl || "http://localhost:3000/billing?status=success",
        cancel_url: "http://localhost:3000/billing?status=canceled",
      },
    }
  );
}

export async function streamChat(
  sessionId: string | null,
  body: { content: string; provider?: string; system?: string; use_rag?: boolean },
  onDelta: (delta: string) => void,
  onDone: (finalSessionId: string) => void
): Promise<void> {
  const path = sessionId ? `/chat/stream/${sessionId}` : "/chat/stream/new";
  const res = await fetch(BASE + path, {
    method: "POST",
    headers: { Authorization: `Bearer ${token()}`, "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, session_id: sessionId }),
  });
  if (!res.ok || !res.body) {
    const text = await res.text();
    throw new Error(`stream ${res.status}: ${text}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n")) !== -1) {
      const line = buf.slice(0, idx).trim();
      buf = buf.slice(idx + 1);
      if (!line) continue;
      const obj = JSON.parse(line);
      if (obj.delta) onDelta(obj.delta);
      if (obj.done) {
        onDone(obj.session_id);
        return;
      }
    }
  }
  onDone(sessionId || "");
}
