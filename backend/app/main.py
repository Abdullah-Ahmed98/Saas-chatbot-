from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.database import engine
from app.models.schemas import Base
from app.models import knowledge as _knowledge_models  # noqa: F401  (register metadata)
from app.routers import admin, auth, billing, chat, chat_stream, knowledge, tenant

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(chat_stream.router)
app.include_router(billing.router)
app.include_router(tenant.router)
app.include_router(admin.router)
app.include_router(knowledge.router)


@app.on_event("startup")
async def on_startup() -> None:
    settings.validate()
    async with engine.begin() as conn:
        # pgvector extension MUST exist before creating the chunk table
        from sqlalchemy import text

        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
