from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

APP_NAME = "ComicCraft"
STATIC_DIR = ROOT_DIR / "static"
TEMPLATES_DIR = ROOT_DIR / "templates"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
COMICS_DIR = ROOT_DIR / "data" / "comics"
HERO_IMAGE = STATIC_DIR / "images" / "forest-fox-hero.webp"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_OUTLINE_MODEL = os.getenv("GEMINI_OUTLINE_MODEL", "gemini-3.8-flash").strip()
GEMINI_STORY_MODEL = os.getenv("GEMINI_STORY_MODEL", "gemini-3.1-pro-preview").strip()
HF_API_KEY = os.getenv("HF_API_KEY", "").strip()
HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL", "stabilityai/stable-diffusion-3-medium-diffusers"
).strip()
HF_IMAGE_PROVIDER = os.getenv("HF_IMAGE_PROVIDER", "hf-inference").strip()
APP_ENV = os.getenv("APP_ENV", "development").strip()

for directory in (PANELS_DIR, EXPORTS_DIR, COMICS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
