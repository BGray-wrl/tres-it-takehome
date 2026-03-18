"""
Generate synthetic alcohol label images for TTB verification testing.

Usage:
    uv run --with pillow tests/generate_labels.py

Outputs PNG files to tests/labels/ and writes tests/manifest.json.
"""

import json
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Paths ───────────────────────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent / "labels"
OUT_DIR.mkdir(exist_ok=True)
MANIFEST_PATH = Path(__file__).parent / "manifest.json"

# ── Fonts ───────────────────────────────────────────────────────────────────
FONT_DIR = Path("/System/Library/Fonts")

def load(name, size):
    try:
        return ImageFont.truetype(str(FONT_DIR / name), size)
    except Exception:
        return ImageFont.load_default()

FONT_BRAND   = load("HelveticaNeue.ttc", 52)
FONT_HEADING = load("HelveticaNeue.ttc", 26)
FONT_BODY    = load("HelveticaNeue.ttc", 22)
FONT_SMALL   = load("HelveticaNeue.ttc", 14)
FONT_TINY    = load("HelveticaNeue.ttc", 10)
FONT_BOLD    = load("Helvetica.ttc",     20)

# ── Government Warning ───────────────────────────────────────────────────────
CORRECT_WARNING = (
    "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK "
    "ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS. "
    "(2) CONSUMPTION OF ALCOHOLIC BEVERAGES IMPAIRS YOUR ABILITY TO DRIVE A CAR OR "
    "OPERATE MACHINERY, AND MAY CAUSE HEALTH PROBLEMS."
)

TITLECASE_WARNING = (
    "Government Warning: (1) According To The Surgeon General, Women Should Not Drink "
    "Alcoholic Beverages During Pregnancy Because Of The Risk Of Birth Defects. "
    "(2) Consumption Of Alcoholic Beverages Impairs Your Ability To Drive A Car Or "
    "Operate Machinery, And May Cause Health Problems."
)

TRUNCATED_WARNING = (
    "GOVERNMENT WARNING: (1) ACCORDING TO THE SURGEON GENERAL, WOMEN SHOULD NOT DRINK "
    "ALCOHOLIC BEVERAGES DURING PREGNANCY BECAUSE OF THE RISK OF BIRTH DEFECTS."
    # (2) clause missing
)

WRONG_WARNING = (
    "HEALTH NOTICE: Drinking alcohol may be hazardous to your health. "
    "Please drink responsibly and do not operate heavy machinery."
)

# ── Drawing helpers ──────────────────────────────────────────────────────────
W, H = 600, 900
MARGIN = 36

def new_label(bg="#FFFFF8", border="#222"):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, W - 5, H - 5], outline=border, width=3)
    d.rectangle([12, 12, W - 13, H - 13], outline=border, width=1)
    return img, d

def fit_font(text, preferred_font, max_width=W - MARGIN * 2):
    """Return preferred_font if text fits, else fall back to smaller sizes."""
    bbox = preferred_font.getbbox(text)
    if bbox[2] - bbox[0] <= max_width:
        return preferred_font
    for size in (44, 36, 30, 24):
        f = load("HelveticaNeue.ttc", size)
        bbox = f.getbbox(text)
        if bbox[2] - bbox[0] <= max_width:
            return f
    return load("HelveticaNeue.ttc", 20)

def centered(d, y, text, font, color="#111"):
    bbox = d.textbbox((0, 0), text, font=font)
    x = (W - (bbox[2] - bbox[0])) // 2
    d.text((x, y), text, font=font, fill=color)
    return y + (bbox[3] - bbox[1]) + 6

def wrapped_text(d, y, text, font, color="#111", max_width=W - MARGIN * 2, line_spacing=4):
    """Draw word-wrapped text, return new y."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test_line = " ".join(current + [word])
        bbox = d.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))

    for line in lines:
        d.text((MARGIN, y), line, font=font, fill=color)
        bbox = d.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y

def divider(d, y, color="#888"):
    d.line([(MARGIN, y + 8), (W - MARGIN, y + 8)], fill=color, width=1)
    return y + 20

def build_label(
    filename,
    brand="OLD TOM DISTILLERY",
    style="Kentucky Straight Bourbon Whiskey",
    abv="45% Alc./Vol. (90 Proof)",
    net_contents="750 mL",
    bottler="Bottled by Old Tom Distillery, Louisville, KY 40201",
    warning_text=CORRECT_WARNING,
    warning_font=FONT_SMALL,
    warning_label="GOVERNMENT WARNING",  # prefix bolded separately
    include_warning=True,
    note="",
):
    img, d = new_label()
    y = 30

    # Decorative header band
    d.rectangle([12, 12, W - 13, 70], fill="#1a1a2e")
    d.text((MARGIN, 22), "EST. 1987  ·  AMERICAN CRAFT SPIRITS", font=FONT_TINY, fill="#aab")

    y = 80
    brand_font = fit_font(brand, FONT_BRAND)
    y = centered(d, y, brand, brand_font, color="#1a1a2e")
    y += 4
    y = centered(d, y, style, FONT_HEADING, color="#444")
    y = divider(d, y)

    # Decorative crest — initials from brand
    initials = "".join(w[0] for w in brand.split()[:3]).upper()
    crest_y = y
    d.ellipse([W // 2 - 40, crest_y, W // 2 + 40, crest_y + 80], outline="#1a1a2e", width=2)
    init_bbox = d.textbbox((0, 0), initials, font=FONT_BOLD)
    ix = W // 2 - (init_bbox[2] - init_bbox[0]) // 2
    d.text((ix, crest_y + 28), initials, font=FONT_BOLD, fill="#1a1a2e")
    y = crest_y + 90

    y = divider(d, y)

    y = centered(d, y, abv, FONT_HEADING, color="#1a1a2e")
    y += 6
    y = centered(d, y, net_contents, FONT_BODY, color="#555")
    y = divider(d, y)

    y = wrapped_text(d, y, bottler, FONT_SMALL, color="#555")
    y += 8

    if note:
        y = divider(d, y)
        y = wrapped_text(d, y + 4, f"[TEST NOTE: {note}]", FONT_TINY, color="#999")

    # Government warning — always near bottom
    if include_warning:
        warn_y = H - 140
        d.rectangle([MARGIN - 4, warn_y - 6, W - MARGIN + 4, H - 20], outline="#555", width=1)
        y = warn_y
        y = wrapped_text(d, y, warning_text, warning_font, color="#222",
                         max_width=W - MARGIN * 2 - 8, line_spacing=2)

    img.save(OUT_DIR / filename)
    print(f"  wrote {filename}")
    return str(OUT_DIR / filename)


# ── Test cases ───────────────────────────────────────────────────────────────
cases = []

def case(filename, expected, description, **kwargs):
    build_label(filename, **kwargs)
    cases.append({
        "file": f"tests/labels/{filename}",
        "description": description,
        "verify_with": {
            "brand": kwargs.get("brand", "OLD TOM DISTILLERY"),
            "abv": "45",
        },
        "expected": expected,
    })


print("Generating test labels…")

# 1. All pass
case(
    "pass_all.png",
    {"brand": True, "abv": True, "warning": True},
    "All three checks should pass. Correct brand, correct ABV, correct warning in all-caps.",
)

# 2. Brand mismatch (label says different distillery)
case(
    "fail_brand.png",
    {"brand": False, "abv": True, "warning": True},
    "Brand should FAIL — label shows 'MOUNTAIN RIDGE SPIRITS', not 'OLD TOM DISTILLERY'.",
    brand="MOUNTAIN RIDGE SPIRITS",
    style="Tennessee Sour Mash Whiskey",
    bottler="Bottled by Mountain Ridge Spirits Co., Nashville, TN 37201",
    note="Wrong brand — label says MOUNTAIN RIDGE SPIRITS",
)

# 3. ABV mismatch (38% instead of 45%)
case(
    "fail_abv.png",
    {"brand": True, "abv": False, "warning": True},
    "ABV should FAIL — label shows 38%, expected 45%.",
    abv="38% Alc./Vol. (76 Proof)",
    note="Wrong ABV — label shows 38%, form says 45%",
)

# 4. Warning missing entirely
case(
    "fail_warning_missing.png",
    {"brand": True, "abv": True, "warning": False},
    "Warning should FAIL — no government warning statement on the label.",
    include_warning=False,
    note="No government warning present",
)

# 5. Warning in title case (not all caps)
case(
    "fail_warning_titlecase.png",
    {"brand": True, "abv": True, "warning": False},
    "Warning should FAIL — 'Government Warning:' is title case, not all caps.",
    warning_text=TITLECASE_WARNING,
    note="Warning in title case — 'Government Warning:' not all caps",
)

# 6. Warning truncated — missing (2) clause
case(
    "fail_warning_truncated.png",
    {"brand": True, "abv": True, "warning": False},
    "Warning should FAIL — only clause (1) present; clause (2) about driving is missing.",
    warning_text=TRUNCATED_WARNING,
    note="Warning truncated — missing clause (2)",
)

# 7. Wrong warning text entirely
case(
    "fail_warning_wrong_text.png",
    {"brand": True, "abv": True, "warning": False},
    "Warning should FAIL — paraphrased health notice instead of mandated exact text.",
    warning_text=WRONG_WARNING,
    note="Wrong warning — informal paraphrase instead of mandated text",
)

# 8. All three fail
case(
    "fail_all.png",
    {"brand": False, "abv": False, "warning": False},
    "All three checks should FAIL — wrong brand, wrong ABV, no warning.",
    brand="BLUE RIDGE MOUNTAIN WINERY",
    style="Cabernet Sauvignon",
    abv="13.5% Alc./Vol.",
    include_warning=False,
    bottler="Bottled by Blue Ridge Mountain Winery, Charlottesville, VA 22902",
    note="Wrong brand, wrong ABV, no warning",
)

# 9. Brand capitalization variant — should still PASS
case(
    "pass_brand_caps_variant.png",
    {"brand": True, "abv": True, "warning": True},
    "Brand should PASS despite mixed-case 'Old Tom Distillery' on label (case-insensitive match).",
    brand="Old Tom Distillery",
    bottler="Bottled by Old Tom Distillery, Louisville, KY 40201",
    note="Brand in mixed case — should pass (case-insensitive)",
)

# Write manifest
manifest = {
    "description": (
        "Test dataset for TTB Label Verification App. "
        "All labels verify against brand='OLD TOM DISTILLERY', abv='45' "
        "unless noted in verify_with."
    ),
    "cases": cases,
}
MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
print(f"  wrote manifest.json ({len(cases)} cases)")
print("Done.")
