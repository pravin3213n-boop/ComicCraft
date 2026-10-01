from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from app.config import GEMINI_API_KEY, HF_API_KEY
from app.schemas import ComicRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.repository import save_comic


def generate_comic(request: ComicRequest) -> dict[str, Any]:
    comic_id = str(uuid4())
    outline = generate_outline(request)
    story = generate_story(outline, request)
    images = [
        generate_image(panel["image_prompt"], comic_id, index)
        for index, panel in enumerate(outline["panels"], 1)
    ]
    layout = build_comic_layout(outline, story, images)
    title = str(outline.get("title") or f"{request.character_name}'s adventure")
    pdf_file = save_pdf(comic_id, title, layout)
    warnings = [image["warning"] for image in images if image.get("warning")]
    providers = {
        "story": "Gemini API" if GEMINI_API_KEY else "local demo story",
        "images": "Hugging Face Inference Providers" if HF_API_KEY and not warnings else "local demo art",
    }
    record = {
        "id": comic_id,
        "title": title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request": request.model_dump(),
        "layout": layout,
        "pdf_filename": pdf_file.name,
        "providers": providers,
        "warnings": warnings,
    }
    save_comic(record)
    record["pdf_url"] = f"/download/{comic_id}"
    record["export_url"] = f"/export-success/{comic_id}"
    record["is_demo"] = not GEMINI_API_KEY or not HF_API_KEY or bool(warnings)
    return record
