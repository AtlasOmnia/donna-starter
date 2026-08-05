#!/usr/bin/env python3
"""Inspect PDF geometry, page boxes, fonts, and basic color-space signals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", required=True, type=Path)
    p.add_argument("--expected-width-in", type=float)
    p.add_argument("--expected-height-in", type=float)
    p.add_argument("--expected-pages", type=int)
    p.add_argument("--tolerance-in", type=float, default=0.02)
    p.add_argument("--require-basic-prepress-signals", action="store_true")
    return p.parse_args()


def box_inches(box):
    return {"width_in": float(box.width) / 72.0, "height_in": float(box.height) / 72.0}


def font_status(page):
    results = []
    resources = page.get("/Resources")
    if not resources: return results
    resources = resources.get_object()
    fonts = resources.get("/Font")
    if not fonts: return results
    for name, ref in fonts.get_object().items():
        font = ref.get_object()
        candidates = []
        if font.get("/Subtype") == "/Type0" and font.get("/DescendantFonts"):
            candidates = [item.get_object() for item in font["/DescendantFonts"]]
        else:
            candidates = [font]
        embedded = False
        base_font = str(font.get("/BaseFont", name))
        for candidate in candidates:
            descriptor = candidate.get("/FontDescriptor")
            if descriptor:
                descriptor = descriptor.get_object()
                embedded = any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3"))
        results.append({"resource": str(name), "base_font": base_font, "embedded": embedded})
    return results


def main() -> int:
    args = parse_args()
    if (args.expected_width_in is None) != (args.expected_height_in is None):
        print(json.dumps({"errors": ["Expected width and height must be supplied together"]}, indent=2))
        return 1
    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.is_file():
        print(json.dumps({"errors": [f"PDF not found: {pdf_path}"]}, indent=2)); return 1
    try:
        from pypdf import PdfReader
    except ImportError:
        print(json.dumps({"errors": ["pypdf is required; install scripts/requirements.txt"]}, indent=2)); return 1

    errors, warnings, pages = [], [], []
    reader = PdfReader(str(pdf_path))
    if args.expected_pages is not None and len(reader.pages) != args.expected_pages:
        errors.append(f"PDF has {len(reader.pages)} pages, expected {args.expected_pages}")
    raw = pdf_path.read_bytes()
    rgb_signal = b"/DeviceRGB" in raw

    for index, page in enumerate(reader.pages, 1):
        media = box_inches(page.mediabox)
        has_trim = "/TrimBox" in page
        has_bleed = "/BleedBox" in page
        fonts = font_status(page)
        unembedded = [font for font in fonts if not font["embedded"]]
        if args.expected_width_in is not None:
            if abs(media["width_in"] - args.expected_width_in) > args.tolerance_in:
                errors.append(f"Page {index} width {media['width_in']:.4f}in, expected {args.expected_width_in:.4f}in")
            if abs(media["height_in"] - args.expected_height_in) > args.tolerance_in:
                errors.append(f"Page {index} height {media['height_in']:.4f}in, expected {args.expected_height_in:.4f}in")
        if unembedded: warnings.append(f"Page {index} has unembedded fonts: {unembedded}")
        if args.require_basic_prepress_signals:
            if not has_trim: errors.append(f"Page {index} lacks an explicit TrimBox")
            if not has_bleed: errors.append(f"Page {index} lacks an explicit BleedBox")
            if has_trim and has_bleed:
                trim, bleed = page.trimbox, page.bleedbox
                if float(bleed.left) > float(trim.left) or float(bleed.bottom) > float(trim.bottom) or float(bleed.right) < float(trim.right) or float(bleed.top) < float(trim.top):
                    errors.append(f"Page {index} BleedBox does not contain TrimBox")
            if unembedded: errors.append(f"Page {index} has unembedded fonts")
            if rgb_signal: errors.append("DeviceRGB signal found; verified output intent/profile conversion required")
        pages.append({"page": index, "media_box": media, "has_trim_box": has_trim, "has_bleed_box": has_bleed, "fonts": fonts})

    report = {"pdf": str(pdf_path), "page_count": len(reader.pages), "device_rgb_signal": rgb_signal, "pages": pages, "errors": errors, "warnings": warnings, "status": "fail" if errors else "pass"}
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__": raise SystemExit(main())
