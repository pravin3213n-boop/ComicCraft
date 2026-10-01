from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Tone = Literal["light-hearted", "dramatic", "poetic", "funny", "mysterious", "adventurous"]
ArtStyle = Literal["anime", "pixel art", "comic book", "realistic", "storybook"]


class ComicRequest(BaseModel):
    prompt: str = Field(min_length=12, max_length=600, description="The comic story idea")
    character_name: str = Field(min_length=1, max_length=60)
    setting: str = Field(min_length=2, max_length=100)
    tone: Tone = "adventurous"
    art_style: ArtStyle = "comic book"

    @field_validator("prompt", "character_name", "setting")
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class ImageTestRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=500)

    @field_validator("prompt")
    @classmethod
    def trim_prompt(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Please enter an image prompt.")
        return value
