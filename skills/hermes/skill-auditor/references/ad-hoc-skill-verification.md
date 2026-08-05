# Ad-hoc verification for skill edits

When a skill edit has no canonical suite command, verify it with a temporary Python script instead of guessing.

## Standard pattern
1. Create a temporary script with `tempfile.NamedTemporaryFile(prefix='hermes-verify-', suffix='.py', delete=False, dir='/var/folders/...')`.
2. Put only the assertions needed to confirm the changed behavior.
3. Run `python3 <tempfile path>`.
4. Remove the script in `finally:` or immediately after success.
5. Report the result as **ad-hoc verification**, not as a full test suite pass.

## Good assertions for skill maintenance
- frontmatter name/description/content changed as intended
- generated indexes/reports exist and contain the expected entries
- empty directories were removed when cleanup is part of the change
- mirror files were updated when the workflow requires them

## Minimal skeleton
```python
import tempfile, os, subprocess
with tempfile.NamedTemporaryFile(prefix='hermes-verify-', suffix='.py', delete=False, dir='/var/folders/...') as f:
 f.write(b'print("ok")')
path = f.name
try:
 subprocess.run(['python3', path], check=True)
finally:
 os.unlink(path)
```
