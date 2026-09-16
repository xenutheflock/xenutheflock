#!/usr/bin/env python3
"""Copy the tokyonight summary cards to profile-summary-card-output/minimal/ in the profile palette."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "profile-summary-card-output" / "tokyonight"
DST = ROOT / "profile-summary-card-output" / "minimal"

COLORS = {
    'stroke="#1a1b27"': 'stroke="#262626"',  # card border
    "#1a1b27": "#0a0a0a",  # background
    "#70a5fd": "#fafafa",  # title
    "#bf91f3": "#737373",  # icons / bars
    "#38bdae": "#8a8a8a",  # text / axes
}

DST.mkdir(exist_ok=True)
for name in ("3-stats.svg", "4-productive-time.svg"):
    s = (SRC / name).read_text()
    for old, new in COLORS.items():
        s = s.replace(old, new)
    s = re.sub(r'\b(rx|ry)="\d+"', r'\1="0"', s)
    (DST / name).write_text(s)
    print("wrote", DST.relative_to(ROOT) / name)
