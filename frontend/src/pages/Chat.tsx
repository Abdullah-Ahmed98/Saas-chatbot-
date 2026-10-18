import { FormEvent, useEffect, useRef, useState } from "react";
import { deleteSession, me, sessionDetail, sessions, streamChat } from "../api/client";

interface Msg {
  role: "user" | "assistant";
  content: string;
}

interface Session {
  id: string;
  title: string;
}

export default function ChatPage() {
  const [user, setUser] = useState<{ email: string; is_admin: boolean } | null>(null);
  const [sessionList, setSessionList] = useState<Session[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [provider, setProvider] = useState("mock");
  const [useRag, setUseRag] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    me().then((u) => setUser(u)).catch(() => {});
    sessions().then(setSessionList).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs]);

  async function openSession(id: string) {
    setActiveId(id);
    try {
      const data = await sessionDetail(id);
      setMsgs(data.messages.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })));
    } catch {
      setMsgs([]);
    }
  }

  async function newSession() {
    setActiveId(null);
    setMsgs([]);
  }

  async function removeSession(id: string) {
    await deleteSession(id);
    if (id === activeId) newSession();
    setSessionList(await sessions());
  }

  async function send(e?: FormEvent) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || streaming) return;
    setInput("");
    setMsgs((prev) => [...prev, { role: "user", content: text }]);
    setStreaming(true);
    let assistantAcc = "";
    setMsgs((prev) => [...prev, { role: "assistant", content: "" }]);

    const doneHandler = async (finalId: string) => {
      setStreaming(false);
      if (finalId && finalId !== "undefined" && finalId !== "") {
        setActiveId(finalId);
        setSessionList(await sessions());
      }
    };

    try {
      await streamChat(
        activeId,
        { content: text, provider, use_rag: useRag },
        (delta) => {
          assistantAcc += delta;
          setMsgs((prev) => {
            const copy = [...prev];
            copy[copy.length - 1] = { role: "assistant", content: assistantAcc };
            return copy;
          });
        },
        doneHandler
      );
    } catch (e: any) {
      setMsgs((prev) => {
        const copy = [...prev];
        copy[copy.length - 1] = { role: "assistant", content: "⚠️ " + e.message };
        return copy;
      });
      setStreaming(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-7.5rem)]">
      {/* Sessions sidebar */}
      <aside className="w-72 border-r border-gray-200 flex flex-col bg-white">
        <button onClick={newSession} className="btn-accent m-4">
          <span>＋</span> New chat
        </button>
        <div className="flex-1 overflow-y-auto px-3 pb-3">
          {sessionList.length === 0 && (
            <p className="text-gray-400 text-sm px-2 py-4">No chats yet</p>
          )}
          {sessionList.map((s) => (
            <div
              key={s.id}
              className={`group flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer mb-0.5 transition-colors ${
                activeId === s.id ? "bg-indigo-50" : "hover:bg-gray-50"
              }`}
              onClick={() => openSession(s.id)}
            >
              <span className={`truncate text-sm font-medium ${activeId === s.id ? "text-indigo-700" : "text-gray-700"}`}>
                {s.title}
              </span>
              <button
                onClick={(ev) => {
                  ev.stopPropagation();
                  removeSession(s.id);
                }}
                className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 text-xs ml-2 transition"
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        <div className="p-4 border-t border-gray-200 space-y-3">
          <div>
            <label className="text-xs font-medium text-gray-500 block mb-1.5">Provider</label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="input"
            >
              <option value="mock">mock</option>
              <option value="claude">claude</option>
              <option value="openai">openai</option>
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={useRag}
              onChange={(e) => setUseRag(e.target.checked)}
              className="w-4 h-4 rounded accent-indigo-600"
            />
            Use my knowledge base
          </label>
        </div>
      </aside>

      {/* Chat area */}
      <section className="flex-1 flex flex-col bg-gray-50">
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {msgs.length === 0 && (
            <div className="text-center text-gray-400 mt-24">
              <div className="text-5xl mb-4">👋</div>
              <p className="text-lg font-medium text-gray-600">Start a conversation</p>
              <p className="text-sm mt-1 max-w-sm mx-auto">
                {provider === "mock"
                  ? "Mock provider is active — add ANTHROPIC_API_KEY / OPENAI_API_KEY and switch provider for real LLM."
                  : `Provider: ${provider}`}
                {useRag && " · Knowledge base enabled"}
              </p>
            </div>
          )}
          {msgs.map((m, i) => (
            <div key={i} className="mb-4 flex">
              <div
                className={`p-4 rounded-2xl max-w-2xl whitespace-pre-wrap text-sm leading-relaxed shadow-sm ${
                  m.role === "user"
                    ? "ml-auto bg-gray-900 text-white rounded-br-md"
                    : "mr-auto bg-white border border-gray-200 rounded-bl-md"
                }`}
              >
                {m.content ||
                  (streaming && i === msgs.length - 1 ? (
                    <span className="inline-flex gap-1 text-gray-400">
                      <span className="typing-dot">●</span>
                      <span className="typing-dot" style={{ animationDelay: "0.2s" }}>●</span>
                      <span className="typing-dot" style={{ animationDelay: "0.4s" }}>●</span>
                    </span>
                  ) : "…")}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={send} className="p-4 bg-white border-t border-gray-200">
          <div className="flex gap-2 max-w-3xl mx-auto">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Message…"
              className="input flex-1"
              disabled={streaming}
            />
            <button
              type="submit"
              disabled={streaming || !input.trim()}
              className="btn-accent disabled:opacity-40 disabled:cursor-not-allowed min-w-[88px]"
            >
              {streaming ? "…" : "Send ➤"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
