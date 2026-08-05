---
purpose: Audit checklist and test harness pattern for custom Jinja chat-templates
---

# Jinja Chat-Template Audit Checklist

Derived from a real audit session where 7 issues were found in a custom Hermes chat-template.

## The 7 checks

| # | Check | Symptom | Fix |
|---|-------|---------|-----|
| 1 | Top-level `{% set %}` overrides caller params | `enable_thinking` always false regardless of input | Guard with `{%- if var is not defined %}` |
| 2 | Image/video items emit no actual data | Model sees `\n\n` but no URL or base64 reference | Add `.get('image_url')`, `.get('url')`, `.get('image')` fallbacks |
| 3 | Multi-pass rendering double-counts vision items | Picture labels show wrong numbers (2x expected) | Ensure reverse-scan pass uses `do_vision_count=false` |
| 4 | Tool `arguments` may be JSON string, not dict | Parameter names are single characters instead of keys | Branch: `{%- if args is string %}` → `json.loads(args)` |
| 5 | Reverse-scan boundary heuristics fragile | User messages ending with tool-result markers break detection | Prefer role-based checks; keep content heuristics as fallback |
| 6 | Unknown roles crash without context | `"Unexpected message role"` tells you nothing | Append `+ message.role` to the error string |
| 7 | No test harness before deploy | Issues only surface in production conversations | Run DictLoader + representative payloads (see below) |

## Test harness pattern

```python
from jinja2 import Environment, DictLoader

jinja_text = open('path/to/template.j2').read()
env = Environment(loader=DictLoader({'t': jinja_text}))
template = env.get_template('t')

def raise_exception(msg):
 raise RuntimeError(f"Template error: {msg}")
env.globals['raise_exception'] = raise_exception
env.globals['json'] = __import__('json') # for json.loads() in template

# Minimal test cases to cover:
# 1. Basic user/assistant with tools
# 2. Multi-modal content (text + image array)
# 3. Tool call with JSON string arguments
# 4. enable_thinking=true from caller
# 5. Consecutive tool responses
# 6. Unknown message role
# 7. Assistant with reasoning_content
# 8. Image count correctness (no double-count)
```

## Deploy notes

- Patched template saved at a temp path (e.g. `/tmp/patched-template.j2`)
- Requires `json` module in Jinja globals for `json.loads()` on string arguments
- Role markers use `##system`, `##user`, `##assistant` convention (non-standard but consistent within this template)
