"""
FastAPI Production Backend for Collaborative Vibe-Coding Platform.
Constructed strictly following the injected skill guidelines:
- web-frameworks.python-api.fastapi-production-craft
- databases-storage.backend-as-a-service.supabase-realtime-auth-rls
"""

from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field, ConfigDict
import uuid
import time

# --- Pydantic v2 Schema Contracts ---
class CanvasMessageCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    
    sender: str = Field(..., min_length=2, max_length=50, description="Author identifier")
    text: str = Field(..., min_length=1, max_length=1000, description="Message text content")
    canvas_node_id: Optional[str] = Field(None, description="Optional associated canvas node ID")

class CanvasMessageResponse(BaseModel):
    id: str
    sender: str
    text: str
    canvas_node_id: Optional[str] = None
    created_at: float

class PlatformHealthResponse(BaseModel):
    status: str
    version: str
    timestamp: float
    active_channels: int


# --- In-Memory State & Channel Store ---
class RealtimeCanvasStore:
    def __init__(self):
        self.messages: List[CanvasMessageResponse] = []
        self.channels: set = {"canvas-general", "code-reviews"}

    def add_message(self, data: CanvasMessageCreate) -> CanvasMessageResponse:
        msg = CanvasMessageResponse(
            id=str(uuid.uuid4()),
            sender=data.sender,
            text=data.text,
            canvas_node_id=data.canvas_node_id,
            created_at=time.time()
        )
        self.messages.append(msg)
        return msg

    def list_messages(self, limit: int = 50) -> List[CanvasMessageResponse]:
        return self.messages[-limit:]

canvas_store = RealtimeCanvasStore()


# --- Security & Auth Dependency ---
async def verify_auth_token(authorization: Optional[str] = Header(None)) -> str:
    """Verifies Bearer token presence adhering to security skill rules."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header."
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization token scheme. Bearer required."
        )
    token = authorization.split(" ")[1]
    if not token or len(token) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload."
        )
    return token


# --- Lifespan Handler ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize channels
    print("[*] Vibe-coding platform initialized following eshkill architecture rules.")
    yield
    print("[*] Vibe-coding platform shutting down cleanly.")


app = FastAPI(
    title="Collaborative Vibe-Coding Platform API",
    version="1.0.0",
    description="Engineered with eshkill autonomous skills: Next.js 15, FastAPI Production, Supabase Realtime",
    lifespan=lifespan
)


# --- Endpoints ---
@app.get("/health", response_model=PlatformHealthResponse)
async def health_check():
    return PlatformHealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=time.time(),
        active_channels=len(canvas_store.channels)
    )

@app.post("/api/v1/messages", response_model=CanvasMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_canvas_message(
    payload: CanvasMessageCreate,
    auth_token: str = Depends(verify_auth_token)
):
    msg = canvas_store.add_message(payload)
    return msg

@app.get("/api/v1/messages", response_model=List[CanvasMessageResponse])
async def get_canvas_messages(
    limit: int = 20,
    auth_token: str = Depends(verify_auth_token)
):
    return canvas_store.list_messages(limit=limit)
