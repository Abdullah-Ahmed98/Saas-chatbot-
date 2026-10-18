# Acme Assistant — AI Chatbot SaaS

Full-stack, multi-tenant SaaS with an AI chatbot: JWT auth, Stripe billing,
provider-agnostic LLM abstraction (mock / Claude / OpenAI), NDJSON streaming,
and a local-embedding RAG knowledge base built on pgvector.

## Quick start

```bash
cp backend/.env.example backend/.env   # add your API keys (LLM / Stripe)
docker compose up -d
```

- Frontend: http://localhost:3000
- Backend / API docs: http://localhost:8000/docs

Create an admin account with the bundled script (adjust `DATABASE_URL` to
`localhost` when running outside Docker):

```bash
cd backend
DATABASE_URL="postgresql+asyncpg://saas:saas@localhost:5432/saas" \
python -m scripts.create_admin test@admin.com 123456
```

## Tech stack

- **Backend:** Python 3.12 · FastAPI · SQLAlchemy 2 (async) · PostgreSQL + pgvector · Redis · Stripe
- **Frontend:** React 18 · TypeScript · Vite · Tailwind CSS
- **Auth:** JWT access + refresh, bcrypt password hashing
- **LLM:** abstraction layer — `mock`, `claude`, `openai` (switch via `LLM_PROVIDER`)
- **RAG:** `sentence-transformers` embeddings (all-MiniLM-L6-v2, 384-d) stored in pgvector, top-k cosine retrieval
- **Billing:** Stripe Checkout + webhook

## Key endpoints

- `POST /api/chat/stream/{session_id}` — streaming chat (NDJSON)
- `POST /api/knowledge/ingest` — index a document for RAG
- `POST /api/knowledge/search` — retrieve top-k chunks
- `GET  /api/admin/tenants` / `GET /api/admin/users` — admin console

## Notes

- Tables and the `vector` extension auto-create on backend startup.
- Chat history is isolated per tenant; a `use_rag` flag on chat requests pulls
  knowledge-base context into the LLM prompt.
- See `backend/.env.example` for all configuration (LLM provider, Stripe keys, CORS).
