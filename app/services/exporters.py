from __future__ import annotations

from pathlib import Path
from typing import Any

from fpdf import FPDF

from app.config import EXPORTS_DIR


# ---------------------------------------------------------
# Unicode font paths
# ---------------------------------------------------------

WINDOWS_FONT_PATH = Path(r"C:\Windows\Fonts\arial.ttf")
WINDOWS_BOLD_FONT_PATH = Path(r"C:\Windows\Fonts\arialbd.ttf")

LINUX_FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
LINUX_BOLD_FONT_PATH = Path(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
)


def get_unicode_fonts():
    """
    Find a Unicode-compatible font on the current operating system.
    """

    # Windows
    if WINDOWS_FONT_PATH.exists() and WINDOWS_BOLD_FONT_PATH.exists():
        return (
            WINDOWS_FONT_PATH,
            WINDOWS_BOLD_FONT_PATH,
            "Arial",
        )

    # Linux
    if LINUX_FONT_PATH.exists() and LINUX_BOLD_FONT_PATH.exists():
        return (
            LINUX_FONT_PATH,
            LINUX_BOLD_FONT_PATH,
            "DejaVu",
        )

    return None, None, None


def clean_text(value: Any) -> str:
    """
    Clean text before sending it to the PDF.

    Unicode quotation marks and punctuation are supported by
    Arial/DejaVu, but this also normalizes a few unusual characters.
    """

    if value is None:
        return ""

    text = str(value)

    replacements = {
        "\u00a0": " ",       # non-breaking space
        "\u201c": '"',       # left double quotation mark
        "\u201d": '"',       # right double quotation mark
        "\u2018": "'",       # left single quotation mark
        "\u2019": "'",       # right single quotation mark
        "\u2013": "-",       # en dash
        "\u2014": "-",       # em dash
        "\u2026": "...",     # ellipsis
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def save_pdf(
    comic_id: str,
    title: str,
    layout: list[dict[str, Any]],
) -> Path:
    """
    Export each panel's art and narrative to a printable A4 PDF.
    """

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=16,
    )

    # -----------------------------------------------------
    # Register Unicode font
    # -----------------------------------------------------

    font_path, bold_font_path, font_name = get_unicode_fonts()

    if font_path and bold_font_path:

        pdf.add_font(
            font_name,
            style="",
            fname=str(font_path),
        )

        pdf.add_font(
            font_name,
            style="B",
            fname=str(bold_font_path),
        )

        regular = font_name
        bold = font_name

    else:
        # Last fallback.
        regular = "Helvetica"
        bold = "Helvetica"

    # -----------------------------------------------------
    # Create pages
    # -----------------------------------------------------

    for index, panel in enumerate(layout, 1):

        pdf.add_page()

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        pdf.set_text_color(
            34,
            38,
            52,
        )

        pdf.set_font(
            bold,
            style="B",
            size=19,
        )

        page_title = (
            clean_text(title)
            if index == 1
            else f"{clean_text(title)} · Panel {index}"
        )

        pdf.multi_cell(
            0,
            10,
            page_title,
        )

        # -------------------------------------------------
        # Divider
        # -------------------------------------------------

        pdf.set_draw_color(
            235,
            112,
            73,
        )

        pdf.set_line_width(1.1)

        y = pdf.get_y() + 2

        pdf.line(
            14,
            y,
            196,
            y,
        )

        pdf.ln(7)

        # -------------------------------------------------
        # Panel title
        # -------------------------------------------------

        pdf.set_font(
            bold,
            style="B",
            size=14,
        )

        panel_title = clean_text(
            panel.get(
                "title",
                f"Panel {index}",
            )
        )

        pdf.multi_cell(
            0,
            8,
            f"{index:02d}  {panel_title}",
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Panel image
        # -------------------------------------------------

        image_path = Path(
            str(
                panel.get(
                    "image_path",
                    "",
                )
            )
        )

        if image_path.is_file():

            image_w = 182.0
            image_h = 121.33

            pdf.image(
                str(image_path),
                x=14,
                y=pdf.get_y(),
                w=image_w,
                h=image_h,
            )

            pdf.ln(
                image_h + 6
            )

        else:

            pdf.set_fill_color(
                238,
                233,
                222,
            )

            pdf.rect(
                14,
                pdf.get_y(),
                182,
                40,
                style="F",
            )

            pdf.set_font(
                regular,
                size=10,
            )

            pdf.cell(
                0,
                40,
                clean_text(
                    "Illustration unavailable"
                ),
                align="C",
            )

            pdf.ln(45)

        # -------------------------------------------------
        # Caption
        # -------------------------------------------------

        pdf.set_font(
            regular,
            size=10,
        )

        pdf.set_text_color(
            105,
            90,
            82,
        )

        pdf.multi_cell(
            0,
            6,
            clean_text(
                panel.get(
                    "caption",
                    "",
                )
            ),
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Scene description
        # -------------------------------------------------

        pdf.set_text_color(
            43,
            45,
            58,
        )

        pdf.set_font(
            regular,
            size=11,
        )

        pdf.multi_cell(
            0,
            6.4,
            clean_text(
                panel.get(
                    "scene_description",
                    "",
                )
            ),
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Narration
        # -------------------------------------------------

        pdf.multi_cell(
            0,
            6.4,
            clean_text(
                panel.get(
                    "narration",
                    "",
                )
            ),
        )

        pdf.ln(2)

        # -------------------------------------------------
        # Dialogue
        # -------------------------------------------------

        pdf.set_font(
            bold,
            style="B",
            size=10,
        )

        pdf.set_text_color(
            207,
            91,
            62,
        )

        pdf.multi_cell(
            0,
            6,
            clean_text(
                panel.get(
                    "dialogue",
                    "",
                )
            ),
        )

        pdf.set_text_color(
            43,
            45,
            58,
        )

    # -----------------------------------------------------
    # Save PDF
    # -----------------------------------------------------

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        EXPORTS_DIR
        / f"comiccraft-{comic_id}.pdf"
    )

    pdf.output(
        str(destination)
    )

    return destination