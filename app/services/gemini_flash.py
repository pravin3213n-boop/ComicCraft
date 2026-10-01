from __future__ import annotations

import json
from typing import Any

from app.config import GEMINI_API_KEY, GEMINI_OUTLINE_MODEL
from app.schemas import ComicRequest

OUTLINE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "panels": {
            "type": "array",
            "minItems": 5,
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "panel_number": {"type": "integer"},
                    "title": {"type": "string"},
                    "scene_description": {"type": "string"},
                    "image_prompt": {"type": "string"},
                },
                "required": ["panel_number", "title", "scene_description", "image_prompt"],
            },
        },
    },
    "required": ["title", "panels"],
}


def _demo_outline(request: ComicRequest) -> dict[str, Any]:
    name, setting = request.character_name, request.setting
    idea = request.prompt.strip().rstrip(".!?")
    if len(idea) > 140:
        idea = idea[:137].rsplit(" ", 1)[0] + "…"
    beats = [
        ("The first glimmer", f"{name} enters {setting} carrying a bold idea: “{idea}.” The first clue hints at a way to make it real."),
        ("A clue in the wild", f"Following the strange light, {name} finds a clue hidden just beyond the familiar path."),
        ("Into the unknown", f"{name} steps deeper into {setting}; the world becomes larger, stranger, and more beautiful."),
        ("The brave choice", f"A sudden challenge tests {name}, who solves it with courage and an unexpected kindness."),
        ("A new beginning", f"As the mystery settles, {name} returns changed, carrying a small wonder from the journey."),
    ]
    panels = []
    for index, (title, scene) in enumerate(beats, 1):
        panels.append(
            {
                "panel_number": index,
                "title": title,
                "scene_description": scene,
                "image_prompt": (
                    f"{request.art_style} comic illustration, {scene} The consistent main character is "
                    f"{name}; setting: {setting}; tone: {request.tone}; expressive composition, "
                    "bold readable silhouettes, cinematic lighting, no text, no lettering."
                ),
            }
        )
    return {"title": f"{name} and the {setting.title()} Mystery", "panels": panels}


def generate_outline(request: ComicRequest) -> dict[str, Any]:
    """Create the five-panel outline. Uses the Google GenAI Interactions API when keyed."""
    if not GEMINI_API_KEY:
        return _demo_outline(request)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""Create a cohesive five-panel comic outline.
Story idea: {request.prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Return exactly five chronological panels. Each scene description should be vivid and concise.
Each image_prompt must repeat the character identity and art style so images remain cohesive,
and must not ask the image model to render words, captions, logos, or watermarks."""
        result = client.interactions.create(
            model=GEMINI_OUTLINE_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": OUTLINE_SCHEMA,
            },
        )
        payload = json.loads(result.output_text)
        panels = payload.get("panels", [])
        if len(panels) != 5:
            raise ValueError("Gemini returned an outline that did not contain exactly five panels.")
        for index, panel in enumerate(panels, 1):
            panel["panel_number"] = index
        return {"title": str(payload.get("title") or "A ComicCraft Adventure"), "panels": panels}
    except Exception as exc:
        raise RuntimeError(f"Gemini outline generation failed: {exc}") from exc
