---
name: marketing-collateral-design
description: marketing-collateral-design — Use when designing, recreating, critiquing, or exporting static marketing collateral such as flyers, social graphics, postcards, brochures, business cards, print ads, and promotional one-sheets. Covers reference decomposition, original art direction, deterministic HTML/CSS/SVG typesetting, separate AI imagery, print/social production, and rendered visual QA.
version: 1.0.0
license: MIT
created_by: agent
platforms:
- macos
metadata:
 hermes:
 tags:
 - graphic-design
 - flyers
 - social-media
 - print-design
 - marketing
 - html
 - svg
 related_skills:
 - claude-design
 - pdf
 - powerpoint
---
# Marketing Collateral Design

## Overview

Use this skill to create professional static promotional graphics whose typography, claims, and contact details must remain exact. The core production rule is **hybrid, not one-shot**: generate or source imagery separately, then compose real text and vector elements deterministically in HTML/CSS/SVG. Image models are art departments, not typesetters.

The default deliverable is a self-contained HTML source plus rendered PNG and PDF when the format requires them. Use PowerPoint only when the user explicitly needs routine editing by nontechnical staff. Use a native design tool only when the user requests that source format or the printer requires it.

Read the supporting files when relevant:

- Production specifications
- Visual QA rubric
- Imagery and asset guidance
- [Archetype-neutral canvas](templates/canvas.html) — default starting point
- [Image-led flyer example](templates/flyer.html) — example only, not a universal layout
- [Rendering script](scripts/render_artifact.py)
- [HTML/raster preflight](scripts/preflight_artifact.py)
- [PDF preflight](scripts/preflight_pdf.py)
- [Pinned dependencies](scripts/requirements.txt)
- [Toolchain smoke tests](scripts/test_skill.py)

## When to Use

Use for:

- flyers and one-sheets
- social posts, story graphics, and digital ads
- postcards and direct-mail pieces
- brochures and rack cards
- business cards
- print advertisements
- promotional handouts and service menus
- recreating the general quality or posture of a supplied reference
- critiquing an existing marketing graphic

Do not use for:

- websites or product UI: use `claude-design`
- slide decks or `.pptx`: use `powerpoint`
- documents whose main value is editable prose: use `docx`
- logo identity systems as a casual add-on; logo work needs its own brief and usage tests
- exact copying of another company’s distinctive identity, copyrighted illustration, or proprietary campaign

## Required Inputs

Before designing, resolve the following from supplied material, existing brand files, or one concise question:

1. purpose and desired action
2. audience
3. distribution channel and final dimensions
4. exact required copy
5. logo, colors, fonts, imagery, and brand restrictions
6. required contact details, legal text, and offer dates
7. desired source format and export formats

Do not ask the user to repeat information that can be read from supplied files, a live site, or established brand material. Do not invent prices, guarantees, awards, service areas, testimonials, certifications, or contact details.

## Production Invariants

These rules are mandatory:

1. **One primary message.** A viewer should understand the subject and intended action within three seconds.
2. **Deterministic text.** All final wording, numbers, URLs, and legal details must be real HTML/SVG/PPT text—not pixels generated inside an image.
3. **Original composition.** Extract principles from references; do not trace or clone a competitor’s distinctive layout or branding.
4. **One focal system.** Choose image-led, type-led, or information-led dominance. Do not give every element equal visual weight.
5. **Real hierarchy before decoration.** Solve order with scale, spacing, alignment, contrast, and cropping before adding effects.
6. **One grid.** Establish margins, columns, baseline rhythm, and alignment anchors before styling individual elements.
7. **Brand truth.** Use approved assets and claims. Mark unknown content as draft rather than making it plausible.
8. **Rendered verification.** Source inspection is not visual QA. Render, inspect, repair, and render again.
9. **Context proof.** Evaluate social graphics at phone-thumbnail size and print pieces at intended physical size or a faithful proof.
10. **Editable master.** Preserve the deterministic source and assets alongside exports.

## Workflow

### 1. Inspect context

Use the available tools rather than designing from memory:

- `vision_analyze(image_url=..., question=...)` for supplied visual references
- `read_file(path=...)` for brand guidelines and copy
- `search_files(...)` for logos, photos, fonts, and prior collateral
- `web_extract(...)` for an official brand site when current source material is needed

Create a short reference decomposition covering:

- format and likely viewing context
- dominant focal element
- scan path
- grid and major alignments
- typographic roles, not merely font names
- color proportions
- image posture and crop
- CTA treatment
- what to keep as a principle
- what must change to remain original or improve clarity

### 2. Lock the content hierarchy

Sort every content item into one of four levels:

1. **Hook:** what this is or why it matters
2. **Support:** the value proposition or essential explanation
3. **Action:** the single next step
4. **Metadata:** contact details, dates, disclaimers, service area, partner line

If everything is “important,” the design has no hierarchy. Remove, combine, or demote content before shrinking type.

### 3. Choose one composition archetype

Commit to one archetype before choosing colors:

- **Image-led split:** strong photograph paired with a quiet text field
- **Full-bleed focal:** one image with deliberately protected text zones
- **Type-led editorial:** typography carries the concept; imagery is secondary
- **Modular information:** structured service/details grid with one dominant module
- **Object-led cutout:** isolated product/person/object creates the visual anchor
- **Sequential panel:** brochure or multi-panel piece with a controlled reading order

Do not default every flyer to “hero image, headline, three equal icons, footer.” Composition should follow the message, not a template habit.

### 4. Produce three composition directions

For externally facing work, default to:

- **Conservative:** closest to established brand patterns
- **Strong-fit:** the best interpretation of the brief
- **Divergent:** a credible alternative with meaningfully different composition

Variations must differ in hierarchy, crop, density, or scan path—not just color. For low-stakes or explicitly rapid work, one strong direction is acceptable.

### 5. Build assets separately

Use supplied photography first. When imagery must be generated, make the tool call explicit:

```text
image_generate(
 prompt="Documentary-style commercial service scene ... Leave low-detail negative space on the left. No words, logos, watermarks, pseudo-text, impossible reflections, or stock-photo polish.",
 aspect_ratio="portrait"
)
```

Then:

1. save or copy the returned image path into the project’s `assets/` directory; never leave the master dependent on an expiring URL or `/tmp`
2. record the prompt and returned asset path in the project manifest
3. generate three candidates when the image carries the campaign
4. inspect each candidate with `vision_analyze(image_url="/absolute/path/to/candidate.png", question="Audit realism, composition, artifacts, and usable negative space for this campaign.")`
5. reject impossible architecture, fake lettering, distorted tools/hands, over-polished stock posture, and brand-inappropriate scenes
6. retain the accepted source asset without baking final wording into it

Read imagery-and-assets.md for prompts and acceptance criteria.

### 6. Compose deterministically

Default to a self-contained HTML file using CSS variables, CSS Grid/Flexbox, SVG for simple vector marks, and local asset paths. Resolve the skill’s absolute directory from `skill_view(name="marketing-collateral-design").skill_dir`; do not assume the current working directory is the skill root.

Start from `templates/canvas.html`, which is intentionally archetype-neutral. `templates/flyer.html` is one image-led example and must not become the default composition. For two-sided or multi-page work, represent each side/page as a separate `[data-artboard]` element, give each an explicit CSS page break, and verify exported page count and ordering. Folded brochures additionally require a printer dieline and a manual fold-order proof.

Required source characteristics:

- each page/side has one `[data-artboard]` root with an explicit size
- explicit canvas size or print `@page` size
- local or embedded assets for final delivery
- CSS custom properties for palette, spacing, and type scale
- semantic content order matching visual reading order
- no placeholder tokens in the final
- no externally hosted font or image dependency unless the user accepts that dependency
- `overflow: hidden` only at the artboard boundary or intentionally cropped image frames—not as a way to conceal text overflow
- print background enabled during PDF export

The included fonts are system fallbacks and are not byte-for-byte deterministic across machines. For controlled output, package appropriately licensed WOFF2 files, declare them with `@font-face`, set `data-required-fonts="Font Name"` on `<html>`, and let the renderer fail if they do not load.

### 7. Preflight source, then render exports

Resolve the absolute directory returned by `skill_view` and use it in every command:

```bash
SKILL_DIR="/absolute/path/from/skill_view/skill_dir"
python3 -m pip install -r "$SKILL_DIR/scripts/requirements.txt" # only when dependencies are missing and installation is approved
python3 -m playwright install chromium # fresh setup; pins the bundled browser to Playwright
python3 "$SKILL_DIR/scripts/preflight_artifact.py" \
 --html /absolute/path/to/artifact.html
python3 "$SKILL_DIR/scripts/render_artifact.py" \
 --input /absolute/path/to/artifact.html \
 --output-dir /absolute/path/to/exports \
 --png --pdf --width 1080 --height 1350
```

The renderer repeats source preflight before opening Chromium, requires Playwright’s pinned bundled browser by default, disables JavaScript, blocks HTTP/HTTPS requests, waits for fonts, rejects broken images and artboard overflow, stages all outputs, and commits them only after the complete render succeeds. It records the browser version plus security settings in its manifest. Dimensions are derived from each artboard; `--width` and `--height` are optional exact assertions, not clipping instructions.

JavaScript, network access, or an unpinned system browser requires explicit overrides:

```bash
python3 "$SKILL_DIR/scripts/render_artifact.py" ... --allow-javascript --allow-network
python3 "$SKILL_DIR/scripts/render_artifact.py" ... --allow-system-browser
```

Use those flags only after reviewing the source and accepting the dependency or browser-version drift. The package is verified on macOS. Other platforms should use Playwright’s bundled Chromium and must run the smoke test before relying on output.

### 8. Run raster and PDF preflight

```bash
python3 "$SKILL_DIR/scripts/preflight_artifact.py" \
 --html /absolute/path/to/artifact.html \
 --image /absolute/path/to/exports/artifact.png \
 --expected-width 1080 --expected-height 1350
```

For PDFs, verify geometry and page count:

```bash
python3 "$SKILL_DIR/scripts/preflight_pdf.py" \
 --pdf /absolute/path/to/exports/artifact.pdf \
 --expected-width-in 8.5 --expected-height-in 11 \
 --expected-pages 1
```

Add `--require-basic-prepress-signals` only to test for explicit TrimBox/BleedBox containment, embedded-font signals, and obvious DeviceRGB usage. This is deliberately **not** a complete press-readiness or PDF/X gate: output intents, ICC profiles, separations, total ink, and printer-specific conformance still require proper prepress software and the printer’s specifications.

Preflight checks exact raster dimensions, unresolved template markers, suspicious placeholder copy, missing local assets, CSS and HTML rendering dependencies, JavaScript, PDF page geometry/boxes, font embedding signals, and basic color-space signals. Fix errors; treat warnings as review items rather than suppressing them.

Before relying on the package after dependency or browser changes, run:

```bash
python3 "$SKILL_DIR/scripts/test_skill.py"
```

The smoke suite exercises safe rendering, exact PNG dimensions, PDF geometry, external-resource rejection, JavaScript rejection, and placeholder rejection.

### 9. Perform visual QA

Load the rendered PNG with:

```text
vision_analyze(
 image_url="/absolute/path/to/exports/artifact.png",
 question="Audit this rendered marketing graphic using the marketing-collateral visual QA rubric. Identify clipping, overlap, weak hierarchy, unreadable small text, poor contrast, awkward crops, generic AI design tells, and inaccurate-looking imagery. Be critical."
)
```

Then inspect at least:

- full canvas
- thumbnail size for social collateral
- print proof or pixel dimensions for print collateral

Use visual-qa-rubric.md. Complete at least one fix-and-rerender cycle. A first render with “no issues” is not credible QA.

### 10. Deliver and preserve

Deliver:

- editable master (`.html` plus local assets, or requested source format)
- PNG in the requested dimensions
- PDF for print when applicable
- brief list of verified dimensions and caveats

Keep claims, dates, contact information, and source assets traceable. Do not claim “print-ready” if color mode, bleed, fonts, or printer specifications were not verified.

## Anti-Slop and Critique Gate

Use the full scoring rubric and critique-only format in visual-qa-rubric.md. Record triggered items before repair and the score after rerendering. Composition failures, competing CTAs, unreadable metadata, or reference imitation block delivery; cosmetic preferences do not.

## Common Pitfalls

1. **Generating the whole flyer as one image.** Text and contact details become unreliable. Generate the scene separately and typeset it in HTML/SVG.
2. **Using CSS pixels as proof of print resolution.** PDF page size and raster DPI are separate concerns. Verify the printer’s requirements.
3. **Calling browser RGB output “press-ready CMYK.”** Browser PDF/PNG exports are normally RGB. Use the printer’s conversion/profile workflow when CMYK or PDF/X is required.
4. **Copying a reference too closely.** Preserve only general principles such as editorial contrast or image/text balance.
5. **Loading many overlapping design skills.** Use this class-level skill plus one output-format skill when necessary. Conflicting rules produce average work.
6. **Remote fonts disappearing in final delivery.** Use licensed local fonts or embed approved webfont files.
7. **QA at only full resolution.** Social designs often fail when reduced; print designs often fail when physically proofed.
8. **Fixing clutter by shrinking everything.** Reduce content or change the composition.
9. **Trusting the first generated photograph.** Inspect hands, reflections, signage, equipment, architecture, and brand realism.
10. **Rendering before source preflight.** Unreviewed HTML can execute scripts or fetch remote resources. Keep JavaScript and network blocked by default.
11. **Treating one template as the design system.** Start from the neutral canvas and choose a composition from the brief; examples are not mandates.
12. **Declaring success from valid HTML.** Valid source can still render badly. Rendered inspection is mandatory.

## Verification Checklist

- [ ] Purpose, audience, channel, dimensions, and exact copy resolved
- [ ] Reference principles separated from elements that must not be copied
- [ ] One composition archetype selected
- [ ] Required wording and claims verified
- [ ] Final text remains deterministic and selectable in the master
- [ ] Assets are local/embedded and provenance is retained
- [ ] HTML source preflight passed before rendering
- [ ] JavaScript and network remained blocked unless explicitly reviewed and allowed
- [ ] PNG dimensions verified
- [ ] PDF page count, page size, bleed, and printer requirements verified when applicable
- [ ] Package smoke test passed after renderer/dependency changes
- [ ] Deterministic preflight completed
- [ ] Rendered visual critique completed
- [ ] At least one fix-and-rerender cycle completed
- [ ] Anti-slop score recorded before and after repair
- [ ] Editable source and final exports delivered
## Public support files

- `scripts/preflight_artifact.py`
- `scripts/preflight_pdf.py`
- `scripts/render_artifact.py`
- `scripts/requirements.txt`
- `scripts/test_skill.py`
- `templates/canvas.html`
- `templates/flyer.html`
