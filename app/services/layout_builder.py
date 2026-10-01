from __future__ import annotations

from typing import Any


def build_comic_layout(
    outline: dict[str, Any],
    story: list[dict[str, Any]],
    images: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Bind each outline beat to its corresponding story and illustration."""
    story_by_number = {int(panel.get("panel_number", i + 1)): panel for i, panel in enumerate(story)}
    image_by_number = {int(image.get("panel_number", i + 1)): image for i, image in enumerate(images)}
    layout: list[dict[str, Any]] = []
    for index, outline_panel in enumerate(outline.get("panels", []), 1):
        number = int(outline_panel.get("panel_number", index))
        narrative = story_by_number.get(number, {})
        image = image_by_number.get(number, {})
        layout.append(
            {
                "panel_number": number,
                "title": str(outline_panel.get("title", f"Panel {number}")),
                "scene_description": str(outline_panel.get("scene_description", "")),
                "image_prompt": str(outline_panel.get("image_prompt", "")),
                "image_url": str(image.get("image_url", "")),
                "image_path": str(image.get("image_path", "")),
                "image_source": str(image.get("image_source", "demo")),
                "caption": str(narrative.get("caption", "")),
                "narration": str(narrative.get("narration", "")),
                "dialogue": str(narrative.get("dialogue", "")),
            }
        )
    return layout
