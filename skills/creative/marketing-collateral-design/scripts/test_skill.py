#!/usr/bin/env python3
"""Smoke and regression tests for the marketing-collateral toolchain."""

from __future__ import annotations

import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent; PYTHON=sys.executable

def run(*args,expected=0):
    result=subprocess.run([PYTHON,*map(str,args)],text=True,capture_output=True)
    if result.returncode!=expected: raise AssertionError(f"Expected {expected}, got {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result

def base_html(body,extra_head="",html_attrs=""):
    return f"<!doctype html><html lang='en' {html_attrs}><head><meta charset='utf-8'><title>Smoke</title>{extra_head}</head><body>{body}</body></html>"

def main():
    with tempfile.TemporaryDirectory(prefix="marketing-collateral-test-") as td:
        tmp=Path(td); exports=tmp/"exports"; html=tmp/"board.html"
        style="<style>*{box-sizing:border-box}html,body{margin:0}.board{width:320px;height:400px;overflow:hidden;background:#faf7ef;color:#18211d;padding:24px}@page{size:320px 400px;margin:0}</style>"
        html.write_text(base_html("<main class='board' data-artboard><h1>Verified layout</h1><p>Deterministic copy.</p></main>",style),encoding="utf-8")
        run(ROOT/"render_artifact.py","--input",html,"--output-dir",exports,"--png","--pdf","--width",320,"--height",400)
        run(ROOT/"preflight_artifact.py","--html",html,"--image",exports/"board.png","--expected-width",320,"--expected-height",400)
        run(ROOT/"preflight_pdf.py","--pdf",exports/"board.pdf","--expected-width-in",320/96,"--expected-height-in",400/96,"--expected-pages",1)
        run(ROOT/"preflight_pdf.py","--pdf",exports/"board.pdf","--require-basic-prepress-signals",expected=1)
        manifest=json.loads((exports/"board.render.json").read_text()); assert manifest["artboards"]==[{"index":1,"width":320,"height":400}]; assert not manifest["javascript_allowed"] and not manifest["network_allowed"] and not manifest["system_browser_allowed"]

        # Multi-artboard export and two-page PDF.
        multi=tmp/"multi.html"
        multi_style="<style>*{box-sizing:border-box}html,body{margin:0}.board{width:320px;height:400px;overflow:hidden;page-break-after:always}@page{size:320px 400px;margin:0}</style>"
        multi.write_text(base_html("<main class='board' data-artboard>Front</main><main class='board' data-artboard>Back</main>",multi_style),encoding="utf-8")
        run(ROOT/"render_artifact.py","--input",multi,"--output-dir",exports,"--png","--pdf","--width",320,"--height",400)
        assert (exports/"multi-01.png").is_file() and (exports/"multi-02.png").is_file()
        run(ROOT/"preflight_pdf.py","--pdf",exports/"multi.pdf","--expected-pages",2)

        # Required fonts must be declared through @font-face and loaded, not merely satisfied by fallback.
        missing_font=tmp/"missing-font.html"
        missing_font.write_text(base_html("<main data-artboard style='width:320px;height:400px'>Font</main>","", "data-required-fonts='DefinitelyMissingFont_9E7C'"),encoding="utf-8")
        run(ROOT/"render_artifact.py","--input",missing_font,"--output-dir",exports,"--png",expected=1)
        assert not (exports/"missing-font.png").exists()

        # Validate all artboards before committing output; a later failure must leave no partial files.
        partial=tmp/"partial.html"
        partial_style="<style>*{box-sizing:border-box}.ok,.bad{width:320px;height:400px;overflow:hidden}.bad>div{height:500px}</style>"
        partial.write_text(base_html("<main class='ok' data-artboard>OK</main><main class='bad' data-artboard><div>Overflow</div></main>",partial_style),encoding="utf-8")
        run(ROOT/"render_artifact.py","--input",partial,"--output-dir",exports,"--png",expected=1)
        assert not list(exports.glob("partial*.png")) and not (exports/"partial.render.json").exists()

        # Successful cleanup must not delete prefix-sharing files and must remove stale formats.
        ad=tmp/"ad.html"; ad.write_text(html.read_text(encoding="utf-8"),encoding="utf-8")
        run(ROOT/"render_artifact.py","--input",ad,"--output-dir",exports,"--png","--pdf","--width",320,"--height",400)
        unrelated=exports/"address.png"; unrelated.write_bytes(b"unrelated")
        run(ROOT/"render_artifact.py","--input",ad,"--output-dir",exports,"--png","--width",320,"--height",400)
        assert unrelated.exists(), "prefix-sharing unrelated file was deleted"
        assert not (exports/"ad.pdf").exists(), "stale PDF survived PNG-only rerender"
        ad_manifest=json.loads((exports/"ad.render.json").read_text())
        assert ad_manifest["outputs"]["pdf"] is None

        external=tmp/"external.html"; external.write_text(base_html("<main data-artboard style='width:320px;height:400px'><img alt='x' src='https://example.invalid/x.png'></main>"),encoding="utf-8"); run(ROOT/"preflight_artifact.py","--html",external,expected=1)
        scripted=tmp/"scripted.html"; scripted.write_text(base_html("<main data-artboard style='width:320px;height:400px'>Safe</main>","<script>document.title='changed'</script>"),encoding="utf-8"); run(ROOT/"preflight_artifact.py","--html",scripted,expected=1)
        placeholder=tmp/"placeholder.html"; placeholder.write_text(base_html("<main data-artboard style='width:320px;height:400px'>[[COPY]]</main>"),encoding="utf-8"); run(ROOT/"preflight_artifact.py","--html",placeholder,expected=1)

        # Linked CSS and SVG dependencies are recursively inspected before rendering.
        (tmp/"nested.css").write_text(".x{background:url('https://example.invalid/bg.png')}",encoding="utf-8")
        linked_css=tmp/"linked-css.html"; linked_css.write_text(base_html("<main class='x' data-artboard style='width:320px;height:400px'>CSS</main>","<link rel='stylesheet' href='nested.css'>"),encoding="utf-8"); run(ROOT/"preflight_artifact.py","--html",linked_css,expected=1)
        (tmp/"nested.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'><image href='https://example.invalid/a.png'/></svg>",encoding="utf-8")
        linked_svg=tmp/"linked-svg.html"; linked_svg.write_text(base_html("<main data-artboard style='width:320px;height:400px'><img alt='svg' src='nested.svg'></main>"),encoding="utf-8"); run(ROOT/"preflight_artifact.py","--html",linked_svg,expected=1)

        print("PASS: safe staged rendering, single/multi-artboard export, raster/PDF preflight, strict font declaration, overflow rejection, recursive dependencies, JavaScript rejection, and placeholder rejection")

if __name__=="__main__": main()
