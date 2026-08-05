#!/usr/bin/env python3
"""Safely render HTML artboards to PNG and/or PDF with staged output."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--selector", default="[data-artboard]")
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--png", action="store_true")
    p.add_argument("--pdf", action="store_true")
    p.add_argument("--allow-javascript", action="store_true")
    p.add_argument("--allow-network", action="store_true")
    p.add_argument("--allow-system-browser", action="store_true")
    return p.parse_args()


def launch_chromium(playwright, allow_system_browser: bool):
    failures = []
    try:
        return playwright.chromium.launch(headless=True), "playwright-bundled"
    except Exception as exc:
        failures.append(str(exc))
    if not allow_system_browser:
        raise RuntimeError("Pinned Playwright Chromium is unavailable. Run `python3 -m playwright install chromium`, or explicitly pass --allow-system-browser after accepting version drift.")
    for candidate in [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
        Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    ]:
        if candidate.exists():
            try:
                return playwright.chromium.launch(headless=True, executable_path=str(candidate)), str(candidate)
            except Exception as exc:
                failures.append(f"{candidate}: {exc}")
    raise RuntimeError("Chromium could not launch. Run `python3 -m playwright install chromium`. " + " | ".join(failures))


def run_source_preflight(source: Path, allow_javascript: bool, allow_network: bool) -> None:
    checker = Path(__file__).with_name("preflight_artifact.py")
    command = [sys.executable, str(checker), "--html", str(source)]
    if allow_javascript: command.append("--allow-javascript")
    if allow_network: command.append("--allow-external")
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError("Source preflight failed before rendering:\n" + result.stdout + result.stderr)


def main() -> int:
    args = parse_args()
    if (args.width is None) != (args.height is None):
        print("ERROR: --width and --height must be supplied together", file=sys.stderr); return 2
    if args.width is not None and (args.width < 100 or args.height < 100):
        print("ERROR: expected dimensions must each be at least 100 pixels", file=sys.stderr); return 2
    if not args.png and not args.pdf: args.png = True

    source = args.input.expanduser().resolve()
    if not source.is_file():
        print(f"ERROR: input not found: {source}", file=sys.stderr); return 2
    out_dir = args.output_dir.expanduser().resolve(); out_dir.mkdir(parents=True, exist_ok=True)
    stage_dir = None

    try:
        run_source_preflight(source, args.allow_javascript, args.allow_network)
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: install dependencies from scripts/requirements.txt", file=sys.stderr); return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 1

    artboard_sizes, blocked_requests, console_errors, page_errors = [], [], [], []
    final_pngs = []
    final_pdf = out_dir / f"{source.stem}.pdf" if args.pdf else None

    try:
        with sync_playwright() as p:
            browser, browser_source = launch_chromium(p, args.allow_system_browser)
            context = browser.new_context(
                viewport={"width": args.width or 1280, "height": args.height or 720},
                device_scale_factor=1,
                java_script_enabled=args.allow_javascript,
            )
            if not args.allow_network:
                def block_network(route):
                    if route.request.url.startswith(("http://", "https://")):
                        blocked_requests.append(route.request.url); route.abort()
                    else: route.continue_()
                context.route("**/*", block_network)

            page = context.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.goto(source.as_uri(), wait_until="load")
            page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
            page.wait_for_timeout(100)

            missing_images = page.locator("img").evaluate_all("els => els.filter(i => !i.complete || i.naturalWidth === 0).map(i => i.currentSrc || i.src)")
            if missing_images: raise RuntimeError("Broken image resources: " + ", ".join(missing_images))

            required_fonts = page.locator("html").get_attribute("data-required-fonts") or ""
            unavailable_fonts = []
            for font in [item.strip() for item in required_fonts.split(",") if item.strip()]:
                loaded = page.evaluate("""async font => {
                    const norm = value => String(value).replace(/^['\"]|['\"]$/g, '').trim().toLowerCase();
                    const faces = Array.from(document.fonts).filter(face => norm(face.family) === norm(font));
                    if (!faces.length) return false;
                    await document.fonts.load(`16px "${font}"`);
                    return faces.every(face => face.status === 'loaded') && document.fonts.check(`16px "${font}"`);
                }""", font)
                if not loaded: unavailable_fonts.append(font)
            if unavailable_fonts: raise RuntimeError("Required fonts were not declared and loaded: " + ", ".join(unavailable_fonts))

            artboards = page.locator(args.selector); count = artboards.count()
            if count == 0: raise RuntimeError(f"No artboards matched selector {args.selector!r}")

            # Validate the complete document before writing any deliverable.
            for index in range(count):
                board = artboards.nth(index)
                size = board.evaluate("el => ({width: el.getBoundingClientRect().width, height: el.getBoundingClientRect().height, scrollWidth: el.scrollWidth, scrollHeight: el.scrollHeight, clientWidth: el.clientWidth, clientHeight: el.clientHeight})")
                width, height = round(size["width"]), round(size["height"])
                if width < 1 or height < 1: raise RuntimeError(f"Artboard {index + 1} has invalid size {width}×{height}")
                if args.width is not None and (width != args.width or height != args.height):
                    raise RuntimeError(f"Artboard {index + 1} is {width}×{height}, expected {args.width}×{args.height}")
                if size["scrollWidth"] > size["clientWidth"] or size["scrollHeight"] > size["clientHeight"]:
                    raise RuntimeError(f"Artboard {index + 1} contains overflow: scroll {size['scrollWidth']}×{size['scrollHeight']} vs client {size['clientWidth']}×{size['clientHeight']}")
                artboard_sizes.append({"index": index + 1, "width": width, "height": height})
            if console_errors or page_errors:
                raise RuntimeError("Browser errors detected: " + json.dumps({"console": console_errors, "page": page_errors}))

            stage_dir = Path(tempfile.mkdtemp(prefix=f".{source.stem}-stage-", dir=out_dir))
            if args.png:
                for index in range(count):
                    suffix = "" if count == 1 else f"-{index + 1:02d}"
                    name = f"{source.stem}{suffix}.png"
                    artboards.nth(index).screenshot(path=str(stage_dir / name))
                    final_pngs.append(out_dir / name)
            if args.pdf:
                page.pdf(path=str(stage_dir / final_pdf.name), print_background=True, prefer_css_page_size=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})

            browser_version = browser.version
            context.close(); browser.close()

        final_manifest = out_dir / f"{source.stem}.render.json"
        manifest = {
            "source": str(source), "selector": args.selector, "artboards": artboard_sizes,
            "browser_source": browser_source, "browser_version": browser_version,
            "javascript_allowed": args.allow_javascript, "network_allowed": args.allow_network,
            "system_browser_allowed": args.allow_system_browser,
            "blocked_requests": blocked_requests, "rendered_at": datetime.now(timezone.utc).isoformat(),
            "outputs": {"png": [str(p) for p in final_pngs], "pdf": str(final_pdf) if final_pdf else None},
        }
        (stage_dir / final_manifest.name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        # Commit only after every validation and export succeeds.
        # Remove only this artifact's exact prior deliverables. Never use a broad prefix glob.
        stale_candidates = [
            out_dir / f"{source.stem}.png",
            out_dir / f"{source.stem}.pdf",
            out_dir / f"{source.stem}.render.json",
            *out_dir.glob(f"{source.stem}-[0-9][0-9].png"),
        ]
        for stale in stale_candidates:
            if stale.exists(): stale.unlink()
        for staged in stage_dir.iterdir():
            os.replace(staged, out_dir / staged.name)
        stage_dir.rmdir(); stage_dir = None
        print(json.dumps(manifest, indent=2)); return 0
    except Exception as exc:
        if stage_dir and stage_dir.exists(): shutil.rmtree(stage_dir, ignore_errors=True)
        print(f"ERROR: render failed: {exc}", file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())
