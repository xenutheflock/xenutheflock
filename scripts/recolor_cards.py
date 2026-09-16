#!/usr/bin/env python3
"""Copy the tokyonight summary cards to profile-summary-card-output/minimal/ in the profile palette."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "profile-summary-card-output" / "tokyonight"
DST = ROOT / "profile-summary-card-output" / "minimal"

COLORS = {
    'stroke="#1a1b27"': 'stroke="#e5e5e5"',  # card border
    "#1a1b27": "#ffffff",  # background
    "#70a5fd": "#0a0a0a",  # title
    "#bf91f3": "#262626",  # icons / bars
    "#38bdae": "#6b6b6b",  # text / axes
}

DST.mkdir(exist_ok=True)
for name in ("3-stats.svg", "4-productive-time.svg"):
    s = (SRC / name).read_text()
    for old, new in COLORS.items():
        s = s.replace(old, new)
    s = re.sub(r'\b(rx|ry)="\d+"', r'\1="0"', s)
    (DST / name).write_text(s)
    print("wrote", DST.relative_to(ROOT) / name)
