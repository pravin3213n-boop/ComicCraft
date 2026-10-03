from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
SAMPLE = {
    "prompt": "A brave fox discovers a lantern that reveals a hidden path through the forest.",
    "character_name": "Fern",
    "setting": "Moonlit forest",
    "tone": "adventurous",
    "art_style": "storybook",
}


def test_homepage_renders_creator_form() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "The story spark" in response.text
    assert "/static/images/forest-fox-hero.webp" in response.text
    assert 'name="character_name"' in response.text
    assert 'name="art_style"' in response.text


def test_json_generation_builds_five_panels_and_pdf() -> None:
    response = client.post("/generate-comic/json", json=SAMPLE)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload["layout"]) == 5
    assert "image_path" not in payload["layout"][0]
    assert [panel["panel_number"] for panel in payload["layout"]] == [1, 2, 3, 4, 5]
    assert payload["pdf_path"].startswith("/download/")
    assert all(panel["image_url"].startswith("/static/panels/") for panel in payload["layout"])
    assert all(panel["narration"] and panel["caption"] and panel["dialogue"] for panel in payload["layout"])

    comic_id = payload["id"]
    download = client.get(payload["pdf_path"])
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content[:5] == b"%PDF-"

    success = client.get(f"/export-success/{comic_id}")
    assert success.status_code == 200
    assert "ready to keep" in success.text
    assert f"/download/{comic_id}" in success.text


def test_form_generation_renders_preview() -> None:
    response = client.post("/generate", data=SAMPLE)
    assert response.status_code == 200, response.text
    assert "FRAME 01 / 05" in response.text
    assert "FRAME 05 / 05" in response.text
    assert "Download your comic" in response.text


def test_json_schema_rejects_invalid_request() -> None:
    response = client.post(
        "/generate-comic/json",
        json={**SAMPLE, "prompt": "tiny", "tone": "not-a-tone"},
    )
    assert response.status_code == 422


def test_image_test_route_generates_an_illustration() -> None:
    response = client.post("/test-image", json={"prompt": "A glowing mushroom beneath a moonlit tree"})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["image_url"].startswith("/static/panels/")
    image = client.get(payload["image_url"])
    assert image.status_code == 200
    assert image.headers["content-type"].startswith("image/")


def test_health_route_reports_demo_status_shape() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["panel_count"] == 5
    assert "gemini_configured" in payload["providers"]
    assert "hugging_face_configured" in payload["providers"]
