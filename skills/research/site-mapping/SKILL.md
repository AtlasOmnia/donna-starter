---
name: site-mapping
description: site-mapping — Map out a website's full structure — sitemaps, navigation, URL taxonomy, content inventory.
version: 1.0.0
platforms:
- linux
- macos
- windows
metadata:
 hermes:
 tags:
 - Web-Audit
 - Site-Structure
 - Sitemap-Analysis
 - Content-Inventory
---
# Site Mapping

Map the complete structure of a website: extract all URLs from sitemaps, analyze navigation hierarchy, classify content by section, and produce a structured overview.

## When to Use

- User asks to "map out," "audit," or "review" a website's structure
- Need to understand a site's URL taxonomy, content sections, or SEO footprint
- Preparing competitive analysis, content gap assessment, or migration planning

## Workflow

### 1. Discover sitemaps

Check these in order:
- `https://site.com/sitemap.xml` (may redirect to `sitemap_index.xml`)
- `https://site.com/robots.txt` — look for `Sitemap:` directive
- Common patterns: `/page-sitemap.xml`, `/post-sitemap.xml`, numbered variants (`sitemap2.xml`)

### 2. Extract URLs programmatically

Use `browser_console` with JS to fetch and parse XML sitemaps — DO NOT rely on reading rendered HTML tables (they truncate):

```js
(async()=>{
 const urls=[];
 for(const sm of ['page-sitemap.xml','post-sitemap.xml']){
 const r=await fetch('https://site.com/'+sm);
 const t=await r.text();
 const parser=new DOMParser();
 const doc=parser.parseFromString(t,'text/xml');
 doc.querySelectorAll('loc').forEach(l=>urls.push(l.textContent));
 }
 return urls;
})()
```

### 3. Classify by path segments

Group URLs by first/second path segment to identify sections:

```js
const paths={};
urls.forEach(u=>{
 const path=u.replace('https://site.com/','');
 const parts=path.split('/').filter(Boolean);
 // Group by [product][section] pattern
});
```

### 4. Extract navigation structure

From the homepage, pull:
- Primary nav menu items (expand dropdowns)
- Footer links
- Use `document.querySelectorAll('nav .sub-menu li a')` and `footer a`

### 5. Produce structured output

Deliver as a table or hierarchy showing:
- Section name | URL prefix | Page count | Notes

## Pitfalls

- **Don't guess the URL** — if the user says "I have a site" without naming it, ask for the URL first. Do not assume based on context (e.g., assuming `acme.com` because the user works at Acme Corp).
- **Reddit is not sitemap-mappable in the normal sense** — `old.reddit.com/robots.txt` currently disallows `/`, and Reddit's useful structure is operational surfaces (`old.reddit` HTML, `.json` endpoints, new Reddit SPA verification), not public XML sitemaps. For Reddit, load a Reddit-specific browsing skill (e.g. reddit-browse-and-post) and use it instead of crawling sitemaps.
- **Sitemap HTML tables truncate** — Yoast-generated sitemaps render as HTML tables but cut off after ~100 rows. Always fetch raw XML via `fetch()` + DOMParser in browser_console.
- **Image/media URLs pollute counts** — filter out `/wp-content/uploads/` and similar asset paths when counting "pages."
- **Multiple sitemap files** — Yoast commonly splits into numbered variants (`page-sitemap.xml`, `page-sitemap2.xml`). Check the index file to find all sub-sitemaps.
- **web_extract on XML returns summarized markdown, not raw data** — for sitemaps specifically, use browser_console fetch instead.

## Output Format

User expects a concise structured overview — table or hierarchy with section names, URL prefixes, page counts, and brief notes. No narrative preamble beyond the total scale.
