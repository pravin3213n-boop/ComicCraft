from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, ROOT_DIR, STATIC_DIR
from app.routes import router

app = FastAPI(
    title=APP_NAME,
    description="Create a five-panel comic from a story idea, then preview and export it as a PDF.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)


@app.get("/health", include_in_schema=False)
def root_health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME}
