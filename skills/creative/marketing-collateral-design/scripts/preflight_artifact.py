#!/usr/bin/env python3
"""Static and raster preflight checks for marketing collateral."""

from __future__ import annotations

import argparse, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

PLACEHOLDER_PATTERNS = [r"\[\[[^\]]+\]\]", r"\{\{[^}]+\}\}", r"\b(?:lorem ipsum|todo|tbd|replace me)\b", r"\bexample\.(?:com|org|net)\b", r"\b555[- .]?\d{3}[- .]?\d{4}\b"]
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.I)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\()?\s*['\"]?([^'\")\s;]+)", re.I)
SVG_HREF_RE = re.compile(r"(?:href|xlink:href)\s*=\s*['\"]([^'\"]+)['\"]", re.I)


def is_external(value): return urlparse(value).scheme in {"http", "https"}
def is_ignorable(value): return not value or value.startswith(("data:", "blob:", "#", "mailto:", "tel:"))

def css_resources(text):
    values = [m.group(2).strip() for m in CSS_URL_RE.finditer(text)]
    values.extend(m.group(1).strip() for m in CSS_IMPORT_RE.finditer(text))
    return values

def resolve_local(base_file: Path, value: str):
    parsed = urlparse(value)
    if parsed.scheme == "file": return Path(unquote(parsed.path))
    if parsed.scheme: return None
    clean = unquote(parsed.path)
    return (base_file.parent / clean).resolve() if clean else None


class ArtifactParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.has_title=False; self.in_title=False; self.in_style=False; self.title_text=""; self.style_text=[]; self.html_lang=None; self.resource_refs=[]; self.images_without_alt=[]; self.scripts=[]
    def add_resource(self, value, source):
        if value and not is_ignorable(value): self.resource_refs.append({"value":value.strip(),"source":source})
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="html": self.html_lang=a.get("lang")
        if tag=="title": self.has_title,self.in_title=True,True
        if tag=="style": self.in_style=True
        if tag=="script":
            self.scripts.append(a.get("src") or "<inline script>")
            if a.get("src"): self.add_resource(a["src"],"script[src]")
        if tag=="img":
            if not a.get("alt","").strip(): self.images_without_alt.append(a.get("src","<missing src>"))
            self.add_resource(a.get("src"),"img[src]")
            for item in (a.get("srcset") or "").split(","):
                if item.strip(): self.add_resource(item.strip().split()[0],"img[srcset]")
        if tag in {"source","video","audio","iframe","embed","input"}: self.add_resource(a.get("src"),f"{tag}[src]"); self.add_resource(a.get("poster"),f"{tag}[poster]")
        if tag=="object": self.add_resource(a.get("data"),"object[data]")
        if tag=="link" and set((a.get("rel") or "").lower().split()).intersection({"stylesheet","preload","icon","manifest"}): self.add_resource(a.get("href"),"link[href]")
        if tag in {"image","use"}: self.add_resource(a.get("href") or a.get("xlink:href"),f"svg {tag}[href]")
        if a.get("style"): self.style_text.append(a["style"])
    def handle_endtag(self,tag):
        if tag=="title": self.in_title=False
        if tag=="style": self.in_style=False
    def handle_data(self,data):
        if self.in_title: self.title_text+=data
        if self.in_style: self.style_text.append(data)


def parse_args():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--html",required=True,type=Path); p.add_argument("--image",type=Path); p.add_argument("--expected-width",type=int); p.add_argument("--expected-height",type=int); p.add_argument("--allow-external",action="store_true"); p.add_argument("--allow-javascript",action="store_true"); return p.parse_args()


def collect_recursive_resources(html_path: Path, parser: ArtifactParser):
    for value in css_resources("\n".join(parser.style_text)): parser.add_resource(value,"inline CSS url/@import")
    queue=list(parser.resource_refs); seen=set(); missing=[]
    while queue:
        ref=queue.pop(0); value=ref["value"]
        if is_external(value) or is_ignorable(value): continue
        local=resolve_local(html_path if ref.get("base") is None else Path(ref["base"]),value)
        if local is None: continue
        key=str(local)
        if not local.exists(): missing.append({**ref,"resolved":key}); continue
        if key in seen: continue
        seen.add(key)
        try:
            content=local.read_text(encoding="utf-8")
        except (UnicodeDecodeError,OSError): continue
        discovered=[]
        if local.suffix.lower()==".css": discovered=css_resources(content)
        elif local.suffix.lower()==".svg": discovered=css_resources(content)+SVG_HREF_RE.findall(content)
        for child in discovered:
            child_ref={"value":child,"source":f"{local.name} nested resource","base":str(local)}
            parser.resource_refs.append(child_ref); queue.append(child_ref)
    return missing


def main():
    args=parse_args(); errors=[]; warnings=[]
    if (args.expected_width is None)!=(args.expected_height is None): errors.append("--expected-width and --expected-height must be supplied together")
    if args.expected_width is not None and args.image is None: errors.append("Expected image dimensions require --image")
    html_path=args.html.expanduser().resolve()
    if not html_path.is_file(): print(json.dumps({"errors":[f"HTML not found: {html_path}"]},indent=2)); return 1
    text=html_path.read_text(encoding="utf-8"); parser=ArtifactParser(); parser.feed(text)
    unresolved=[]
    for pattern in PLACEHOLDER_PATTERNS: unresolved.extend(re.findall(pattern,text,flags=re.I))
    if unresolved: errors.append("Unresolved or suspicious placeholder content: "+", ".join(sorted(set(unresolved))[:20]))
    if not parser.html_lang: warnings.append("Missing html lang attribute")
    if not parser.has_title or not parser.title_text.strip(): warnings.append("Missing or empty document title")
    if parser.images_without_alt: warnings.append("Images missing alt text: "+", ".join(parser.images_without_alt))
    if parser.scripts and not args.allow_javascript: errors.append("JavaScript present but not allowed: "+", ".join(parser.scripts))

    missing=collect_recursive_resources(html_path,parser)
    external=[r for r in parser.resource_refs if is_external(r["value"])]
    if external and not args.allow_external: errors.append("External rendering dependencies found: "+json.dumps(external))
    if missing: errors.append("Missing local rendering dependencies: "+json.dumps(missing))

    image_info=None
    if args.image:
        image_path=args.image.expanduser().resolve()
        if not image_path.is_file(): errors.append(f"Rendered image not found: {image_path}")
        else:
            try: from PIL import Image
            except ImportError: errors.append("Pillow is required for raster preflight; install scripts/requirements.txt")
            else:
                try:
                    with Image.open(image_path) as image:
                        image_info={"path":str(image_path),"format":image.format,"width":image.width,"height":image.height,"mode":image.mode}
                        if args.expected_width and image.width!=args.expected_width: errors.append(f"Image width {image.width} does not match expected {args.expected_width}")
                        if args.expected_height and image.height!=args.expected_height: errors.append(f"Image height {image.height} does not match expected {args.expected_height}")
                except Exception as exc: errors.append(f"Could not inspect rendered image: {exc}")
    report={"html":str(html_path),"image":image_info,"resources":parser.resource_refs,"external_dependencies":external,"missing_local_dependencies":missing,"javascript":parser.scripts,"errors":errors,"warnings":warnings,"status":"fail" if errors else "pass"}
    print(json.dumps(report,indent=2)); return 1 if errors else 0


if __name__=="__main__": raise SystemExit(main())
