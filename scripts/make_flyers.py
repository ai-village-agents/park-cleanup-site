#!/usr/bin/env python3
"""Generate printable park cleanup recruitment flyers (PNG + PDF).

Outputs to assets/flyers/
- flyer_general_letter.(png|pdf)
- flyer_mission_dolores_letter.(png|pdf)
- flyer_devoe_park_letter.(png|pdf)

No network calls.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
import qrcode
import img2pdf


LETTER_W_IN = 8.5
LETTER_H_IN = 11.0
DPI = 300
W = int(LETTER_W_IN * DPI)
H = int(LETTER_H_IN * DPI)

GREEN_DARK = (45, 80, 22)
GREEN_MID = (74, 124, 40)
GREEN_LIGHT = (124, 179, 66)
ORANGE = (245, 124, 0)
GRAY = (55, 55, 55)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Try common fonts available in Debian/Ubuntu images.
    candidates = []
    if bold:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]

    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)

    # Fallback: default bitmap font
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _qr(url: str, box_size: int = 14, border: int = 2) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img


@dataclass
class FlyerSpec:
    slug: str
    title: str
    subtitle: str
    primary_url: str
    primary_label: str
    secondary_url: str | None = None
    secondary_label: str | None = None


def render_letter(spec: FlyerSpec, out_dir: str) -> tuple[str, str]:
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Header band
    header_h = int(1.6 * DPI)
    draw.rectangle([0, 0, W, header_h], fill=GREEN_DARK)
    draw.rectangle([0, header_h - int(0.15 * DPI), W, header_h], fill=GREEN_LIGHT)

    pad = int(0.6 * DPI)

    title_font = _font(74, bold=True)
    sub_font = _font(36, bold=False)
    body_font = _font(32, bold=False)
    body_bold = _font(32, bold=True)
    small_font = _font(24, bold=False)

    # Title text
    title = spec.title
    tbox = draw.textbbox((0, 0), title, font=title_font)
    draw.text((pad, int(0.28 * DPI)), title, font=title_font, fill=(255, 255, 255))

    # Subtitle
    draw.text((pad, int(0.95 * DPI)), spec.subtitle, font=sub_font, fill=(235, 235, 235))

    # Big CTA
    y = header_h + int(0.55 * DPI)
    cta = "This weekend: 1–2 hours makes a difference."
    draw.text((pad, y), cta, font=body_bold, fill=GRAY)
    y += int(0.55 * DPI)

    bullets = [
        "Bring: gloves (optional), sturdy shoes. We'll take care of the plan.",
        "Do: pick up litter, fill 1–2 bags, take quick before/after photos.",
        "Post: comment on the linked GitHub issue to claim the cleanup and share results.",
    ]

    bullet_indent = int(0.25 * DPI)
    for b in bullets:
        lines = _wrap_text(draw, b, body_font, max_w=W - 2 * pad - int(3.2 * DPI))
        for li, line in enumerate(lines):
            prefix = "• " if li == 0 else "  "
            draw.text((pad + bullet_indent, y), prefix + line, font=body_font, fill=GRAY)
            y += int(0.43 * DPI)
        y += int(0.1 * DPI)

    # QR block
    qr_size_px = int(3.2 * DPI)
    qr_img = _qr(spec.primary_url, box_size=16, border=2)
    qr_img = qr_img.resize((qr_size_px, qr_size_px), Image.Resampling.NEAREST)

    qr_x = W - pad - qr_size_px
    qr_y = header_h + int(0.7 * DPI)

    # QR border
    border = int(0.06 * DPI)
    draw.rectangle([qr_x - border, qr_y - border, qr_x + qr_size_px + border, qr_y + qr_size_px + border], outline=GREEN_MID, width=border)
    img.paste(qr_img, (qr_x, qr_y))

    # QR label
    label_lines = _wrap_text(draw, spec.primary_label, small_font, max_w=qr_size_px)
    ly = qr_y + qr_size_px + int(0.15 * DPI)
    for line in label_lines:
        bbox = draw.textbbox((0, 0), line, font=small_font)
        draw.text((qr_x + (qr_size_px - bbox[2]) // 2, ly), line, font=small_font, fill=GRAY)
        ly += int(0.32 * DPI)

    # URL under label
    url_text = spec.primary_url.replace("https://", "")
    url_lines = _wrap_text(draw, url_text, small_font, max_w=qr_size_px)
    for line in url_lines:
        bbox = draw.textbbox((0, 0), line, font=small_font)
        draw.text((qr_x + (qr_size_px - bbox[2]) // 2, ly), line, font=small_font, fill=(90, 90, 90))
        ly += int(0.30 * DPI)

    # Secondary QR (optional)
    if spec.secondary_url and spec.secondary_label:
        qr2_size_px = int(2.05 * DPI)
        qr2 = _qr(spec.secondary_url, box_size=12, border=2)
        qr2 = qr2.resize((qr2_size_px, qr2_size_px), Image.Resampling.NEAREST)

        qr2_x = W - pad - qr2_size_px
        qr2_y = ly + int(0.35 * DPI)
        draw.rectangle([qr2_x - border, qr2_y - border, qr2_x + qr2_size_px + border, qr2_y + qr2_size_px + border], outline=(180, 180, 180), width=border)
        img.paste(qr2, (qr2_x, qr2_y))

        l2y = qr2_y + qr2_size_px + int(0.12 * DPI)
        l2_lines = _wrap_text(draw, spec.secondary_label, small_font, max_w=qr2_size_px)
        for line in l2_lines:
            bbox = draw.textbbox((0, 0), line, font=small_font)
            draw.text((qr2_x + (qr2_size_px - bbox[2]) // 2, l2y), line, font=small_font, fill=GRAY)
            l2y += int(0.30 * DPI)

    # Footer band
    footer_h = int(1.15 * DPI)
    draw.rectangle([0, H - footer_h, W, H], fill=(245, 245, 245))
    draw.rectangle([0, H - footer_h, W, H - footer_h + int(0.08 * DPI)], fill=ORANGE)

    footer_left = pad
    footer_y = H - footer_h + int(0.25 * DPI)

    footer_text = "More info + safety checklist: https://ai-village-agents.github.io/park-cleanup-site/"
    draw.text((footer_left, footer_y), footer_text, font=small_font, fill=GRAY)

    disclosure = "AI Village: a public project of AI Digest (theaidigest.org/village)."
    draw.text((footer_left, footer_y + int(0.32 * DPI)), disclosure, font=small_font, fill=(90, 90, 90))

    # Save
    out_png = os.path.join(out_dir, f"flyer_{spec.slug}_letter.png")
    out_pdf = os.path.join(out_dir, f"flyer_{spec.slug}_letter.pdf")

    img.save(out_png, dpi=(DPI, DPI))

    # Convert to PDF with explicit Letter page size
    layout_fun = img2pdf.get_layout_fun((img2pdf.in_to_pt(LETTER_W_IN), img2pdf.in_to_pt(LETTER_H_IN)))
    with open(out_png, "rb") as f_in:
        pdf_bytes = img2pdf.convert(f_in, layout_fun=layout_fun)
    with open(out_pdf, "wb") as f_out:
        f_out.write(pdf_bytes)

    return out_png, out_pdf


def main() -> None:
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "flyers")
    os.makedirs(out_dir, exist_ok=True)

    site = "https://ai-village-agents.github.io/park-cleanup-site/"
    issue_sf = "https://github.com/ai-village-agents/park-cleanups/issues/3"
    issue_nyc = "https://github.com/ai-village-agents/park-cleanups/issues/1"

    specs = [
        FlyerSpec(
            slug="general",
            title="AI Village Park Cleanup",
            subtitle="We need human volunteers in SF + NYC",
            primary_url=site,
            primary_label="Start here",
            secondary_url=issue_sf,
            secondary_label="Volunteer (SF)",
        ),
        FlyerSpec(
            slug="mission_dolores",
            title="Mission Dolores Park Cleanup",
            subtitle="San Francisco (Dolores St & 19th St)",
            primary_url=issue_sf,
            primary_label="Claim Mission Dolores",
            secondary_url=site,
            secondary_label="Project site",
        ),
        FlyerSpec(
            slug="devoe_park",
            title="Devoe Park Cleanup",
            subtitle="Bronx, NYC (W 188th St & University Ave)",
            primary_url=issue_nyc,
            primary_label="Claim Devoe Park",
            secondary_url=site,
            secondary_label="Project site",
        ),
    ]

    for s in specs:
        out_png, out_pdf = render_letter(s, out_dir)
        print("Wrote", out_png)
        print("Wrote", out_pdf)


if __name__ == "__main__":
    main()
