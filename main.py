import os
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine
from config import settings
from routers import auth_api, games_api, chat_api, admin_api, web

# Create tables
models.Base.metadata.create_all(bind=engine)

# Lightweight auto-migration for new columns (SQLite)
def _ensure_columns():
    from sqlalchemy import text
    with engine.connect() as conn:
        cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(board_games)").fetchall()]
        if "category" not in cols:
            conn.exec_driver_sql("ALTER TABLE board_games ADD COLUMN category VARCHAR(50)")
            conn.commit()
            print("[migrate] added board_games.category")
        conv_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(conversations)").fetchall()]
        if "is_pinned" not in conv_cols:
            conn.exec_driver_sql("ALTER TABLE conversations ADD COLUMN is_pinned BOOLEAN DEFAULT 0")
            conn.commit()
            print("[migrate] added conversations.is_pinned")
try:
    _ensure_columns()
except Exception as e:
    print(f"[migrate] skipped: {e}")

# Ensure upload dir exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Board Game Rulebook Assistant with RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(web.router)
app.include_router(auth_api.router)
app.include_router(games_api.router)
app.include_router(chat_api.router)
app.include_router(admin_api.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print("\n===== UNHANDLED EXCEPTION =====")
    print(f"Path: {request.url.path}")
    print(tb)
    print("================================\n")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__, "path": request.url.path},
    )
