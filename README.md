# ComicCraft

A local FastAPI + Jinja2 app that turns a story idea into a five-panel comic preview and a downloadable PDF. It follows the supplied ComicCraft brief and is designed to run locally without Manus-managed services.

## What it includes

- Prompt form for story idea, character, setting, tone, and visual style.
- Five-panel outline and narration pipeline, with Gemini Flash for structured outlines and a Gemini Pro model for expanded narration when `GEMINI_API_KEY` is configured.
- Hugging Face text-to-image generation when `HF_API_KEY` is configured; otherwise, ComicCraft creates polished local demo illustrations so the app remains usable without provider credentials.
- Panel-by-panel preview with title, illustration, scene description, caption, narration, dialogue, and image prompt.
- PDF export, JSON generation API, direct image-test endpoint, and FastAPI `/docs`.
- No accounts or persistent user library, matching the brief's single-session scope.

## Run locally

Requirements: Python 3.10+.

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. Interactive API docs are at <http://127.0.0.1:8000/docs>.

The app works in **demo mode** if no keys are supplied. For live provider generation, add keys to `.env` (never commit that file):

```dotenv
GEMINI_API_KEY=your_google_ai_studio_key
HF_API_KEY=your_hugging_face_inference_token
```

Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey). For Hugging Face, use a token with permission to call Inference Providers. Provider usage may have separate availability, quota, or billing requirements.

Model IDs and provider behavior are configurable in `.env.example`. Defaults use currently documented Gemini models and a Stable Diffusion 3 model exposed through Hugging Face Inference Providers. The brief's Gemini 1.5 and Stable Diffusion 1.5 identifiers are preserved as design intent, but those older identifiers may no longer be active; update the model settings if your account requires different available IDs.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Comic creator form |
| POST | `/generate` | Generate and render a comic from form data |
| POST | `/generate-comic/json` | Generate a comic from a validated JSON request |
| POST | `/test-image` | Generate a single image from a prompt (JSON or form) |
| GET | `/download/{comic_id}` | Download a comic PDF |
| GET | `/export-success/{comic_id}` | PDF export confirmation page |
| GET | `/api/health` | Runtime and provider-configuration status |
| GET | `/docs` | FastAPI's interactive API documentation |

Generated metadata, panel images, and PDFs are stored locally in `data/comics/`, `static/panels/`, and `static/exports/` respectively. This is a development project: files are not automatically purged. Keep the app private if you add personal or sensitive story content.

## Project layout

```text
app/
  main.py                 FastAPI app and static mount
  routes.py               HTML and JSON endpoints
  schemas.py              Request/response data validation
  services/
    comic_service.py      End-to-end generation orchestration
    gemini_flash.py       Outline generation and demo outline
    gemini_pro.py         Story/dialogue generation and demo story
    image_generator.py    Hugging Face integration and local demo art
    layout_builder.py    Panel/story/image binding
    exporters.py          Multi-page PDF export
    repository.py         Local JSON persistence for generated comics
templates/                Jinja2 pages
static/css, static/js/   Responsive UI and form interactions
static/images/            Original ComicCraft hero artwork
static/panels/            Locally generated panel images
static/exports/           Downloadable PDF output
tests/                    Automated route and pipeline tests
```

## Run tests

```bash
python -m pytest -q
```

## Notes

- API keys stay server-side in environment variables. They are never sent to the browser.
- The project uses current provider SDKs rather than old API identifiers shown in the brief. Refer to the official [Gemini structured output documentation](https://ai.google.dev/gemini-api/docs/structured-output), [Gemini model catalog](https://ai.google.dev/gemini-api/docs/models), and [Hugging Face text-to-image guide](https://huggingface.co/docs/inference-providers/en/tasks/text-to-image) when changing model IDs.
- This app is intended for local development, not hardened multi-user production. It has no authentication, remote storage, queue, or rate limiting.
