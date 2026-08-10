"""
FastAPI application entry point.

Sets up CORS, includes all routers, and creates tables on startup.
Serves the frontend as static files from ../frontend/.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine
from app.models import Base


# ── Lifespan ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)

    # Auto-seed if database is brand new
    try:
        from app.database import SessionLocal
        from app.models import Skill
        from app.routers.ingestion import seed_database
        with SessionLocal() as db:
            if db.query(Skill).count() == 0:
                print("[*] Empty database detected. Auto-seeding initial skills and profiles...")
                seed_database(db)
                print("[+] Database auto-seeded successfully!")
    except Exception as e:
        print(f"[!] Auto-seed notice: {e}")

    yield


# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Unified Agentic Skill Manager",
    description="A living ecosystem for AI agent skills — ingest, propose, merge, audit, serve.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ─────────────────────────────────────────────────────────────────
from app.routers import skills, proposals, batches, audit, ingestion, graph  # noqa: E402

# Note: skills, batches, ingestion, and graph routers define their own prefix= internally.
# proposals and audit do not, so they get prefixed here.
app.include_router(skills.router,     prefix="/api",            tags=["Skills"])
app.include_router(proposals.router,  prefix="/api/proposals",  tags=["Proposals"])
app.include_router(batches.router,    prefix="/api",            tags=["Batches"])
app.include_router(audit.router,      prefix="/api/audit",      tags=["Audit"])
app.include_router(ingestion.router,  prefix="/api",            tags=["Ingestion"])
app.include_router(graph.router,      prefix="/api",            tags=["Neural Graph"])


# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok", "version": "0.1.0"}


# ── Static frontend ────────────────────────────────────────────────────────
_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
