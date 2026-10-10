"""Weekly health check for the profile README.

Fails (and GitHub emails the owner) when an image is missing or invalid,
or when a link is clearly broken (404/410, DNS failure, repeated 5xx).
Sites that block automated checks (403/429/999) are reported as warnings only.
"""
import re, sys, time, pathlib, urllib.request, urllib.error
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[2]
readme = (root / "README.md").read_text(encoding="utf-8")
errors, warnings = [], []

# 1. Every local image exists and is valid SVG
for src in sorted(set(re.findall(r'src="\./([^"]+)"', readme))):
    path = root / src
    if not path.exists():
        errors.append(f"Missing image: {src}")
        continue
    if path.suffix == ".svg":
        try:
            ET.parse(path)
        except ET.ParseError as e:
            errors.append(f"Invalid SVG {src}: {e}")

# 2. No image is loaded from another website
for src in re.findall(r'<img[^>]*src="(https?://[^"]+)"', readme):
    warnings.append(f"External image (could break if that site changes): {src}")

# 3. Every link still works
BLOCKING = {401, 403, 406, 429, 999}
def status(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile-link-check)", "Accept": "text/html,application/pdf,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)

for url in sorted(set(re.findall(r'href="(https?://[^"]+)"', readme))):
    code, info = status(url)
    if code is None or (code >= 500):
        time.sleep(5)
        code, info = status(url)
    if code is None:
        errors.append(f"Unreachable: {url} ({info})")
    elif code in BLOCKING:
        warnings.append(f"Site blocks automated checks ({code}), verify by hand: {url}")
    elif code >= 400:
        errors.append(f"Broken link ({code}): {url}")
    elif url.endswith(".pdf") and "pdf" not in info.lower():
        errors.append(f"Expected a PDF but got '{info}': {url}")
    else:
        print(f"OK {code} {url}")

for w in warnings:
    print(f"::warning::{w}")
for e in errors:
    print(f"::error::{e}")
print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
