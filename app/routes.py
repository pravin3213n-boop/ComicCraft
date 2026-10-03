from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.config import COMICS_DIR, EXPORTS_DIR, HF_API_KEY, GEMINI_API_KEY, STATIC_DIR, TEMPLATES_DIR
from app.schemas import ComicRequest, ImageTestRequest
from app.services.comic_service import generate_comic
from app.services.image_generator import generate_image
from app.services.repository import load_comic

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "ComicCraft", "hero_available": (STATIC_DIR / "images" / "forest-fox-hero.webp").is_file()},
    )


def _comic_or_error(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        validated = ComicRequest.model_validate(payload)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise HTTPException(status_code=422, detail=details) from exc
    try:
        return generate_comic(validated)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/generate", response_class=HTMLResponse, name="generate_form")
def generate_form(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form("adventurous"),
    art_style: str = Form("comic book"),
) -> HTMLResponse:
    values = {
        "prompt": prompt,
        "character_name": character_name,
        "setting": setting,
        "tone": tone,
        "art_style": art_style,
    }
    try:
        comic = _comic_or_error(values)
    except HTTPException as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"title": "ComicCraft", "form_values": values, "error": str(exc.detail), "hero_available": True},
            status_code=exc.status_code,
        )
    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={"comic": comic},
    )


@router.post("/generate-comic/json", name="generate_json")
def generate_json(payload: ComicRequest) -> JSONResponse:
    comic = _comic_or_error(payload.model_dump())
    return JSONResponse(
        {
            "id": comic["id"],
            "title": comic["title"],
            "created_at": comic["created_at"],
            "layout": [{key: value for key, value in panel.items() if key != "image_path"} for panel in comic["layout"]],
            "pdf_path": comic["pdf_url"],
            "export_path": comic["export_url"],
            "providers": comic["providers"],
            "warnings": comic["warnings"],
            "is_demo": comic["is_demo"],
        }
    )


@router.post("/test-image", name="test_image")
async def test_image(request: Request) -> JSONResponse:
    content_type = request.headers.get("content-type", "")
    try:
        if "application/json" in content_type:
            values = await request.json()
        else:
            form = await request.form()
            values = dict(form)
        validated = ImageTestRequest.model_validate(values)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = generate_image(validated.prompt, "image-test", 1)
    return JSONResponse(
        {
            "image_url": result["image_url"],
            "image_source": result["image_source"],
            "warning": result["warning"],
        }
    )


@router.get("/download/{comic_id}", name="download_pdf")
def download_pdf(comic_id: str) -> FileResponse:
    record = load_comic(comic_id)
    if not record:
        raise HTTPException(status_code=404, detail="Comic not found.")
    filename = str(record.get("pdf_filename", ""))
    # Keep downloads confined to this application's export directory.
    if not filename.startswith(f"comiccraft-{comic_id}") or not filename.endswith(".pdf"):
        raise HTTPException(status_code=404, detail="PDF not found.")
    pdf_path = EXPORTS_DIR / filename
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"comiccraft-{comic_id}.pdf",
    )


@router.get("/export-success", response_class=HTMLResponse, name="export_success")
def export_success(request: Request, comic_id: str | None = None) -> HTMLResponse:
    comic = load_comic(comic_id) if comic_id else None
    if comic_id and not comic:
        raise HTTPException(status_code=404, detail="Comic not found.")
    if comic:
        comic["pdf_url"] = f"/download/{comic['id']}"
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"comic": comic},
    )


@router.get("/export-success/{comic_id}", response_class=HTMLResponse, include_in_schema=False)
def export_success_by_id(request: Request, comic_id: str) -> HTMLResponse:
    return export_success(request, comic_id)


@router.get("/api/health", name="api_health")
def api_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "app": "ComicCraft",
        "panel_count": 5,
        "providers": {
            "gemini_configured": bool(GEMINI_API_KEY),
            "hugging_face_configured": bool(HF_API_KEY),
        },
        "demo_mode": not (GEMINI_API_KEY and HF_API_KEY),
    }
