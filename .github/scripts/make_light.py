"""Generate light-mode copies of the profile panels.

Reads every SVG in assets/ (except the badge buttons, which stay dark in both
themes) and writes a recoloured copy to assets/light/ with the same path.
Run it after changing any dark panel:  python3 .github/scripts/make_light.py
"""
import pathlib, re

root = pathlib.Path(__file__).resolve().parents[2]
assets = root / "assets"
out = assets / "light"

COLORS = {
    # backgrounds and surfaces
    "#0B1220": "#FFFFFF", "#0F1E36": "#F3F6FA", "#0A2540": "#EAF1F8", "#0E2A47": "#E6EEF7",
    "#0E1B2E": "#F6F8FA", "#0B1525": "#EEF2F6",
    # borders
    "#26405F": "#D0D7DE", "#22344F": "#D8DEE4", "#2B4466": "#C8D1DA", "#1C2C44": "#E1E6EB",
    # text
    "#F5F8FC": "#1F2328", "#E3EAF4": "#24292F", "#DDE6F2": "#24292F", "#C9D4E3": "#32383F",
    "#FFFFFF": "#1F2328",
    "#9AAAC0": "#57606A", "#8A9BB3": "#57606A", "#6F82A0": "#6E7781", "#5D6E87": "#6E7781",
    "#4A5F7E": "#8C959F",
    # accents, darkened to stay readable on white
    "#36BCF7": "#0B7FC1", "#7FD8FF": "#0B7FC1", "#3DDC97": "#1A8F5A", "#7C9CFF": "#4F5FD9",
    "#F5B14C": "#B8740A", "#E879A6": "#BF3F78", "#2CC4B0": "#12877A", "#6C8AE0": "#4A63C4",
    "#2AA4D8": "#1679AD", "#F0505A": "#C9323D", "#6DB33F": "#3F7F1A", "#3D8BFF": "#1F66D6",
}
pattern = re.compile("|".join(re.escape(k) for k in COLORS), re.IGNORECASE)

count = 0
for svg in sorted(assets.rglob("*.svg")):
    rel = svg.relative_to(assets)
    if rel.parts[0] == "light" or svg.name.startswith("btn-"):
        continue
    text = pattern.sub(lambda m: COLORS[m.group(0).upper()], svg.read_text(encoding="utf-8"))
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")
    count += 1
print(f"Wrote {count} light-mode panels to {out.relative_to(root)}")
