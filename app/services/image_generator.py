from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from app.config import HF_API_KEY, HF_IMAGE_MODEL, HF_IMAGE_PROVIDER, PANELS_DIR


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _make_demo_art(prompt: str, panel_number: int, destination: Path) -> None:
    """Draw a lightweight comic-like scene locally when no image API is configured."""
    width, height = 960, 640
    digest = hashlib.sha256(f"{prompt}:{panel_number}".encode("utf-8")).digest()
    palettes = [
        ((23, 35, 76), (113, 111, 168), (255, 185, 106)),
        ((20, 54, 72), (94, 154, 138), (255, 208, 116)),
        ((57, 33, 81), (171, 91, 112), (255, 185, 123)),
        ((22, 57, 65), (97, 127, 97), (246, 210, 123)),
    ]
    top, horizon, glow = palettes[digest[0] % len(palettes)]
    image = Image.new("RGB", (width, height), top)
    pixels = image.load()
    for y in range(height):
        t = y / height
        color = tuple(int(top[c] * (1 - t) + horizon[c] * t) for c in range(3))
        for x in range(width):
            pixels[x, y] = color
    draw = ImageDraw.Draw(image, "RGBA")

    # Moon / luminous story token and a scattered field of stars.
    moon_x, moon_y = int(width * (0.68 + (panel_number % 2) * 0.08)), 150
    radius = 54 + digest[1] % 18
    draw.ellipse((moon_x-radius, moon_y-radius, moon_x+radius, moon_y+radius), fill=(*glow, 235))
    draw.ellipse((moon_x-radius+12, moon_y-radius+12, moon_x+radius-12, moon_y+radius-12), fill=(255, 239, 190, 200))
    for i in range(34):
        x = int(digest[(i + 3) % 32] / 255 * (width - 32))
        y = int(digest[(i + 11) % 32] / 255 * 300)
        r = 2 + digest[(i + 19) % 32] % 4
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(255, 241, 207, 190))

    # Layered hills and stylized evergreen silhouettes.
    draw.polygon([(0, 420), (160, 310), (315, 424), (510, 300), (690, 420), (835, 315), (960, 410), (960, 640), (0, 640)], fill=(38, 79, 80, 255))
    draw.polygon([(0, 500), (190, 405), (345, 500), (580, 395), (790, 495), (960, 410), (960, 640), (0, 640)], fill=(23, 61, 64, 255))
    for side in (-1, 1):
        for i in range(5):
            x = int((i / 4) * 300) if side < 0 else width - int((i / 4) * 300)
            tree_h = 170 + digest[(i + (0 if side < 0 else 8)) % 32] % 115
            base_y = 545 + (i % 2) * 20
            draw.rectangle((x-10, base_y-50, x+10, base_y+90), fill=(31, 40, 53, 255))
            for layer in range(3):
                apex = base_y - tree_h + layer * 52
                half = 34 + layer * 14
                draw.polygon([(x, apex), (x-half, apex+78), (x+half, apex+78)], fill=(20+layer*4, 46+layer*8, 58+layer*4, 245))

    # A warm wandering path leading to the focal point.
    draw.polygon([(370, 640), (585, 640), (545, 520), (508, 468), (466, 449), (429, 520)], fill=(235, 178, 111, 190))
    draw.line([(475, 640), (485, 565), (470, 510), (485, 472)], fill=(255, 229, 177, 205), width=9)

    # Friendly fox-like protagonist, drawn as a clean silhouette with expressive details.
    cx, cy = 405 + (panel_number % 3) * 24, 470
    fox = (224, 116 + digest[2] % 42, 75, 255)
    draw.ellipse((cx-83, cy-48, cx+44, cy+65), fill=fox, outline=(31, 30, 44, 255), width=8)
    # Tail, head, ears and paws.
    draw.ellipse((cx-126, cy-54, cx-27, cy+14), fill=fox, outline=(31, 30, 44, 255), width=8)
    draw.ellipse((cx-139, cy-45, cx-99, cy+1), fill=(255, 220, 183, 255))
    draw.ellipse((cx+13, cy-107, cx+118, cy-5), fill=fox, outline=(31, 30, 44, 255), width=8)
    draw.polygon([(cx+24, cy-81), (cx+35, cy-141), (cx+68, cy-93)], fill=fox, outline=(31, 30, 44, 255))
    draw.polygon([(cx+73, cy-92), (cx+109, cy-142), (cx+108, cy-55)], fill=fox, outline=(31, 30, 44, 255))
    draw.ellipse((cx+76, cy-57, cx+88, cy-45), fill=(27, 27, 40, 255))
    draw.ellipse((cx+111, cy-22, cx+125, cy-11), fill=(35, 29, 41, 255))
    draw.ellipse((cx-48, cy+41, cx-14, cy+72), fill=(247, 185, 133, 255))
    draw.ellipse((cx+8, cy+39, cx+43, cy+71), fill=(247, 185, 133, 255))
    # Ink frame and warm halftone flecks.
    for i in range(7):
        x = 45 + i * 19 + digest[i] % 12
        y = 565 + digest[i + 12] % 35
        draw.ellipse((x, y, x+5, y+5), fill=(255, 225, 174, 120))
    draw.rounded_rectangle((12, 12, width-12, height-12), radius=22, outline=(22, 24, 37, 245), width=12)
    image.save(destination, "JPEG", quality=91, optimize=True)


def generate_image(prompt: str, comic_id: str, panel_number: int) -> dict[str, Any]:
    """Generate an image through Hugging Face, or create local demo art without a key."""
    filename = f"{comic_id}-panel-{panel_number}.jpg"
    destination = PANELS_DIR / filename
    warning = None
    source = "local demo art"

    if HF_API_KEY:
        try:
            from huggingface_hub import InferenceClient

            client = InferenceClient(
                provider=HF_IMAGE_PROVIDER,
                api_key=HF_API_KEY,
                timeout=150,
            )
            generated = client.text_to_image(
                prompt,
                model=HF_IMAGE_MODEL,
                negative_prompt="text, letters, watermark, logo, extra limbs, blurry faces",
                width=768,
                height=512,
                guidance_scale=7.0,
                num_inference_steps=24,
            )
            generated.convert("RGB").save(destination, "JPEG", quality=92, optimize=True)
            source = f"Hugging Face · {HF_IMAGE_MODEL}"
        except Exception as exc:
            warning = f"Image provider unavailable; a local demo illustration was used ({type(exc).__name__})."
            _make_demo_art(prompt, panel_number, destination)
    else:
        _make_demo_art(prompt, panel_number, destination)

    return {
        "panel_number": panel_number,
        "image_url": f"/static/panels/{filename}",
        "image_path": str(destination),
        "image_source": source,
        "warning": warning,
    }
