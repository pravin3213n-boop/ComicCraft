from pathlib import Path
from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text):
    if not text:
        return ""

    replacements = {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def save_pdf(panels, output_path=None):
    """Create the ComicCraft PDF."""

    if output_path is None:
        output_path = EXPORT_DIR / "comiccraft_comic.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for index, panel in enumerate(panels, start=1):

        pdf.add_page()

        # Title
        #pdf.set_font("Helvetica", "B", 16)
        pdf.set_font("Helvetica", ...)
        title = clean_text(
            panel.get("title", f"Panel {index}")
        )
        pdf.cell(0, 10, title, ln=True)

        # Image
        image_path = panel.get("image_path")

        if image_path:
            image_path = Path(image_path)

            if not image_path.is_absolute():
                image_path = BASE_DIR / image_path

            if image_path.exists():
                pdf.image(
                    str(image_path),
                    x=15,
                    y=30,
                    w=180
                )
                pdf.ln(125)

        # Scene
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Scene", ln=True)

        pdf.set_font("Helvetica", size=10)
        scene = clean_text(
            panel.get("scene", "")
        )
        pdf.multi_cell(0, 6, scene)

        pdf.ln(3)

        # Story / narration
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Story", ln=True)

        pdf.set_font("Helvetica", size=10)
        story = clean_text(
            panel.get("story", "")
            or panel.get("narration", "")
            or panel.get("caption", "")
        )
        pdf.multi_cell(0, 6, story)

    pdf.output(str(output_path))

    return str(output_path)