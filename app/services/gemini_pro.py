from __future__ import annotations

import json
from typing import Any

from app.config import GEMINI_API_KEY, GEMINI_STORY_MODEL
from app.schemas import ComicRequest

STORY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "panels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "panel_number": {"type": "integer"},
                    "caption": {"type": "string"},
                    "narration": {"type": "string"},
                    "dialogue": {"type": "string"},
                },
                "required": ["panel_number", "caption", "narration", "dialogue"],
            },
        }
    },
    "required": ["panels"],
}


def _demo_story(outline: dict[str, Any], request: ComicRequest) -> list[dict[str, Any]]:
    name = request.character_name
    idea = request.prompt.strip().rstrip(".!?")
    if len(idea) > 140:
        idea = idea[:137].rsplit(" ", 1)[0] + "…"
    dialogue_by_tone = {
        "funny": ["Well, that was not on the map.", "I knew my curiosity would get me into something."],
        "light-hearted": ["I wonder where this little light leads.", "The best surprises are shared."],
        "dramatic": ["There is no turning back now.", "I have to see this through."],
        "poetic": ["Even the dark has a way of holding light.", "Some journeys keep glowing after they end."],
        "mysterious": ["Someone wanted this clue to be found.", "The forest is keeping one more secret."],
        "adventurous": ["Onward. The trail is only getting stranger.", "One more step, and we change everything."],
    }
    dialogue = dialogue_by_tone.get(request.tone, dialogue_by_tone["adventurous"])
    story_beats = [
        (f"At the edge of {request.setting}, {name} takes the first step toward: “{idea}.”", "Every adventure begins as a what if."),
        (f"A silver mark on an old sign points away from the safe trail. {name} follows it anyway.", "A clue is an invitation."),
        (f"The idea begins to take shape in {request.setting}; {name} finds an unexpected turn beyond the original plan.", "Wonder waits beyond the map."),
        (f"When a small problem interrupts the plan, {name} finds a kinder, cleverer way forward.", "Courage can be gentle."),
        (f"By the time {name} returns, the original idea has become a story worth carrying home.", "Some magic travels with you."),
    ]
    result = []
    for index, (narration, caption) in enumerate(story_beats, 1):
        line = dialogue[0] if index in (1, 3) else dialogue[1]
        result.append(
            {
                "panel_number": index,
                "caption": caption,
                "narration": narration,
                "dialogue": f'{name}: “{line}”',
            }
        )
    return result


def generate_story(
    outline: dict[str, Any], request: ComicRequest
) -> list[dict[str, Any]]:
    """Expand an outline into panel captions, narration, and character dialogue."""
    if not GEMINI_API_KEY:
        return _demo_story(outline, request)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"""Expand this five-panel comic outline into concise, polished story text.
Character: {request.character_name}; tone: {request.tone}.
Preserve the outline's events and panel order. Give every panel a short atmospheric caption,
2-3 sentences of narration, and one short spoken line by the main character.
Outline JSON:\n{json.dumps(outline, ensure_ascii=False)}"""
        result = client.interactions.create(
            model=GEMINI_STORY_MODEL,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": STORY_SCHEMA,
            },
        )
        payload = json.loads(result.output_text)
        panels = payload.get("panels", [])
        if len(panels) != 5:
            raise ValueError("Gemini returned story text for a different number of panels.")
        for index, panel in enumerate(panels, 1):
            panel["panel_number"] = index
        return panels
    except Exception as exc:
        raise RuntimeError(f"Gemini story generation failed: {exc}") from exc
