#!/usr/bin/env python3
"""Build the bento tiles in assets/ for the profile README.

Edit the DATA section, then run:  python3 scripts/build_cards.py
"""
import html
import os
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
CACHE = ROOT / "scripts" / ".icon-cache"

# ---------------------------------------------------------------- DATA

NAME = "xenu"
ROLE = "IT Student · Web Developer · Linux"
CHIPS = ["Philippines", "Fedora + Hyprland", "BSIT student"]

ABOUT = (
    "I'm an IT student from the Philippines. I build web apps with "
    "TypeScript and Laravel, write small tools for Linux, and occasionally "
    "put 3D things in a browser. I rice my desktop more than I sleep."
)

NOW = [
    ("Learning", "TypeScript · Laravel"),
    ("Automating", "Python scripts"),
    ("Building", "TakeNote"),
    ("Running", "Fedora + Hyprland"),
]

# icon names are simple-icons slugs: https://simpleicons.org
STACK = [
    ("Languages", ["typescript", "javascript", "php", "python", "c", "gnubash"]),
    ("Frameworks", ["nextdotjs", "react", "laravel", "tailwindcss", "nodedotjs"]),
    ("Data", ["postgresql", "mysql", "supabase", "sqlite"]),
    ("Tools & OS", ["git", "docker", "vercel", "visualstudiocode", "neovim", "fedora", "linux", "blender", "arduino"]),
]

# status: "public" | "private" ; live: url or None. Numbering follows this order.
PROJECTS = {
    "quest-runner": dict(
        title="Quest Runner", status="public", live=None,
        desc="Complete Discord play quests on Linux without installing the game. "
             "Spawns a tiny idle process with the right name so Discord counts the time. "
             "Works with native and Flatpak Discord.",
        tags=["Python", "C", "GTK4", "Shell"],
        terminal=["$ quest search terraria", "$ quest run terraria -m 16",
                  "▶ Playing Terraria · auto-stop in 16m", "$ quest status"],
    ),
    "takenote": dict(
        title="TakeNote", status="private", live="takenote.fun",
        desc="A free public wall where anyone can leave anonymous sticky notes or drawings. "
             "Create your wall, share the link, pin the ones that matter.",
        tags=["Next.js", "Tailwind", "Supabase"],
    ),
    "dtr": dict(
        title="DTR Salary Calculator", status="public", live="dtr-calculator-five.vercel.app",
        desc="Mobile-first salary calculator with OCR. Snap your daily time record, get your pay.",
        tags=["TypeScript", "OCR", "Mobile"],
    ),
    "geocrimemap": dict(
        title="GeoCrimeMap", status="private", live=None,
        desc="Web-based crime mapping with data analytics for Barangay San Roque.",
        tags=["Web GIS", "Analytics"],
    ),
    "lms": dict(
        title="Web LMS", status="private", live=None,
        desc="Learning management system for students, faculty, and administrators.",
        tags=["React", "Laravel", "PostgreSQL", "Docker"],
    ),
    "campus-essentials": dict(
        title="Campus Essentials", status="public", live=None,
        desc="Inventory system for a school supplies store: stock, suppliers, "
             "and reorder-level alerts.",
        tags=["Laravel", "Blade", "SQLite"],
    ),
}

# (simple-icons slug, label, value)
CONTACTS = [
    ("gmail", "Email", "edzel.wcc@gmail.com"),
    ("discord", "Discord", "xenumwa"),
    ("facebook", "Facebook", "idzill"),
]

# ---------------------------------------------------------------- THEME

BG = "#ffffff"
BORDER = "#e5e5e5"
LINE = "#d4d4d4"
TEXT = "#0a0a0a"
MUTED = "#6b6b6b"
TERM_BG = "#0a0a0a"
TERM_TEXT = "#fafafa"
TERM_LINE = "#3a3a3a"
RED = "#e11d2a"
FONT = "'Inter', 'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace"

BASE_CSS = f"""
text {{ font-family: {FONT}; }}
.mono {{ font-family: {MONO}; }}
.label {{ font-family: {MONO}; font-size: 13px; font-weight: 700; letter-spacing: 2px; fill: {RED}; }}
.fade {{ animation: fade .7s ease-out backwards; }}
@keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
.grow {{ transform-box: fill-box; transform-origin: left; animation: grow 1s cubic-bezier(.2,.8,.2,1) backwards; }}
@keyframes grow {{ from {{ transform: scaleX(0); }} }}
.cursor {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
"""


def esc(s):
    return html.escape(s, quote=True)


def wrap(s, n):
    lines, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def svg(w, h, body, css=""):
    if os.environ.get("STATIC"):  # preview renderers screenshot before animations run
        css += "* { animation: none !important; }"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<style>{BASE_CSS}{css}</style>"
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>'
        # red corner mark
        f'<rect x="1" y="1" width="48" height="4" fill="{RED}" class="grow"/>'
        f"{body}</svg>"
    )


def text_lines(lines, x, y, size, lh, fill=TEXT, weight=400, delay=0.0, step=0.08):
    return "".join(
        f'<text x="{x}" y="{y + i*lh}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'class="fade" style="animation-delay:{delay + i*step:.2f}s">{esc(line)}</text>'
        for i, line in enumerate(lines)
    )


def pills(x, y, labels, size=13, h=28, pad=12, gap=8, color=TEXT):
    out = []
    for lab in labels:
        w = int(len(lab) * size * 0.6) + pad * 2
        out.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{LINE}"/>'
            f'<text x="{x + w/2}" y="{y + h/2 + size*0.35}" font-size="{size}" fill="{color}" '
            f'text-anchor="middle" font-weight="600">{esc(lab)}</text>'
        )
        x += w + gap
    return "".join(out)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def icon_path(slug):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{slug}.path"
    if not f.exists():
        src = fetch(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{slug}.svg").decode()
        f.write_text(re.search(r'<path d="([^"]+)"', src).group(1))
    return f.read_text()


def icon_box(slug, x, y, size, extra=""):
    """Outlined square with a white simple-icons glyph (24x24 viewBox) centered in it."""
    g = size * 0.5
    off = (size - g) / 2
    return (
        f'<g {extra}><rect x="{x}" y="{y}" width="{size}" height="{size}" fill="none" stroke="{BORDER}" stroke-width="1.5"/>'
        f'<g transform="translate({x+off} {y+off}) scale({g/24:.4f})" fill="{TEXT}"><path d="{icon_path(slug)}"/></g></g>'
    )


# ---------------------------------------------------------------- TILES

def hero():
    w, h = 1200, 360
    body = f"""
<defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#000000" stroke-opacity=".05"/></pattern></defs>
<rect x="2" y="2" width="{w-4}" height="{h-4}" fill="url(#grid)"/>
<text x="64" y="84" class="label fade">~/xenutheflock</text>
<text x="58" y="196" font-size="128" font-weight="800" fill="{TEXT}" letter-spacing="-5" class="fade" style="animation-delay:.1s">{esc(NAME)}</text>
<rect x="{76 + len(NAME)*70}" y="174" width="22" height="22" fill="{RED}" class="cursor"/>
<rect x="64" y="226" width="120" height="3" fill="{RED}" class="grow" style="animation-delay:.3s"/>
{text_lines([ROLE], 64, 270, 26, 0, weight=500, delay=.25)}
<g class="fade" style="animation-delay:.4s">{pills(64, 294, CHIPS, size=14, h=32, gap=10, color=MUTED)}</g>
<g class="fade" style="animation-delay:.5s">
  <rect x="{w-184}" y="{h-80}" width="120" height="16" fill="{RED}" class="grow" style="animation-delay:.5s"/>
  <rect x="{w-184}" y="{h-58}" width="80" height="16" fill="{TEXT}" class="grow" style="animation-delay:.65s"/>
  <rect x="{w-184}" y="{h-36}" width="40" height="16" fill="{LINE}" class="grow" style="animation-delay:.8s"/>
</g>
"""
    return w, h, svg(w, h, body)


def about():
    w, h = 800, 300
    body = f"""
<text x="40" y="58" class="label fade">ABOUT</text>
<text x="40" y="106" font-size="32" font-weight="800" fill="{TEXT}" class="fade" style="animation-delay:.05s">Hey there<tspan fill="{RED}">.</tspan></text>
{text_lines(wrap(ABOUT, 70), 40, 152, 19, 30, fill=MUTED, delay=.15)}
"""
    return w, h, svg(w, h, body)


def now():
    w, h = 400, 300
    rows = []
    for i, (k, v) in enumerate(NOW):
        y = 108 + i * 48
        rows.append(
            f'<g class="fade" style="animation-delay:{.1 + i*.1:.2f}s">'
            f'<rect x="36" y="{y-22}" width="3" height="36" fill="{RED if i == 0 else LINE}"/>'
            f'<text x="54" y="{y-6}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{MUTED}" class="mono">{esc(k.upper())}</text>'
            f'<text x="54" y="{y+13}" font-size="17" fill="{TEXT}">{esc(v)}</text></g>'
        )
    body = f'<text x="36" y="58" class="label fade">RIGHT NOW</text>{"".join(rows)}'
    return w, h, svg(w, h, body)


def stack():
    w, h = 1200, 330
    size, gap = 52, 12
    out = ['<text x="40" y="58" class="label fade">STACK</text>']
    col_x = [40, 460]
    for i, (group, icons) in enumerate(STACK):
        x0 = col_x[i % 2]
        y0 = 96 + (i // 2) * 116
        out.append(f'<text x="{x0}" y="{y0 + 4}" font-size="13" font-weight="700" fill="{MUTED}" class="mono fade" style="animation-delay:{i*.1:.1f}s">{esc(group.upper())}</text>')
        for j, slug in enumerate(icons):
            out.append(icon_box(slug, x0 + j*(size+gap), y0 + 20, size,
                                extra=f'class="fade" style="animation-delay:{.15 + i*.1 + j*.05:.2f}s"'))
    return w, h, svg(w, h, "".join(out))


def num(key):
    return f"{list(PROJECTS).index(key) + 1:02d}"


def project_wide(key):
    p = PROJECTS[key]
    w, h = 1200, 340
    tx, ty, tw, th = 640, 50, 520, 240
    term = []
    for i, line in enumerate(p.get("terminal", [])):
        term.append(
            f'<text x="{tx+24}" y="{ty+84 + i*32}" font-size="16" fill="{RED if line.startswith("▶") else TERM_TEXT}" '
            f'class="mono pop" style="animation-delay:{.6 + i*.6:.1f}s">{esc(line)}</text>'
        )
    cursor_y = ty + 84 + len(term) * 32
    css = ".pop { animation: pop .1s linear backwards; } @keyframes pop { from { opacity: 0; } }"
    body = f"""
<text x="40" y="58" class="label fade">{num(key)} / FEATURED</text>
<text x="40" y="118" font-size="40" font-weight="800" fill="{TEXT}" letter-spacing="-1" class="fade" style="animation-delay:.05s">{esc(p['title'])}</text>
{text_lines(wrap(p['desc'], 58), 40, 166, 17, 26, fill=MUTED, delay=.15)}
<g class="fade" style="animation-delay:.4s">{pills(40, 270, p['tags'])}</g>
<g class="fade" style="animation-delay:.3s">
  <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{TERM_BG}" stroke="{TERM_BG}" stroke-width="1.5"/>
  <rect x="{tx+16}" y="{ty+16}" width="12" height="12" fill="{RED}"/><rect x="{tx+34}" y="{ty+16}" width="12" height="12" fill="{TERM_LINE}"/><rect x="{tx+52}" y="{ty+16}" width="12" height="12" fill="{TERM_LINE}"/>
  <text x="{tx+tw/2}" y="{ty+27}" font-size="13" fill="{MUTED}" text-anchor="middle" class="mono">quest — bash</text>
  <line x1="{tx}" y1="{ty+44}" x2="{tx+tw}" y2="{ty+44}" stroke="{TERM_LINE}"/>
</g>
{"".join(term)}
<rect x="{tx+24}" y="{cursor_y-15}" width="10" height="19" fill="{RED}" class="cursor"/>
"""
    return w, h, svg(w, h, body, css)


def project_card(key, w=600, h=340):
    p = PROJECTS[key]
    ncols = 58 if w == 600 else 110
    public = p["status"] == "public"
    body = f"""
<text x="36" y="58" class="label fade">{num(key)}</text>
<text x="{w-36}" y="58" font-size="12" font-weight="700" letter-spacing="1.5" text-anchor="end" fill="{TEXT if public else MUTED}" class="mono fade">{"OPEN SOURCE" if public else "PRIVATE"}</text>
<text x="36" y="118" font-size="30" font-weight="800" fill="{TEXT}" letter-spacing="-.5" class="fade" style="animation-delay:.05s">{esc(p['title'])}</text>
{text_lines(wrap(p['desc'], ncols)[:3], 36, 158, 16, 25, fill=MUTED, delay=.12)}
<g class="fade" style="animation-delay:.3s">{pills(36, h-100, p['tags'], size=12, h=26)}</g>
<line x1="36" y1="{h-54}" x2="{w-36}" y2="{h-54}" stroke="{BORDER}"/>
"""
    link = p["live"] or ("view repo" if public else None)
    if link:
        body += (f'<text x="{w-36}" y="{h-26}" font-size="13" font-weight="700" fill="{RED}" text-anchor="end" '
                 f'class="mono fade" style="animation-delay:.4s">{esc(link)} →</text>')
    return w, h, svg(w, h, body)


def contact(slug, label, value):
    w, h = 400, 130
    body = f"""
{icon_box(slug, 30, 33, 64)}
<text x="114" y="58" font-size="12" font-weight="700" letter-spacing="2" fill="{MUTED}" class="mono">{esc(label.upper())}</text>
<text x="114" y="86" font-size="{20 if len(value) < 20 else 17}" font-weight="700" fill="{TEXT}">{esc(value)}</text>
<text x="{w-30}" y="72" font-size="22" fill="{RED}" text-anchor="end">→</text>
"""
    return w, h, svg(w, h, body)


def main():
    OUT.mkdir(exist_ok=True)
    tiles = {
        "hero": hero(),
        "about": about(),
        "now": now(),
        "stack": stack(),
        "project-quest-runner": project_wide("quest-runner"),
        "project-takenote": project_card("takenote"),
        "project-dtr": project_card("dtr"),
        "project-geocrimemap": project_card("geocrimemap"),
        "project-lms": project_card("lms"),
        "project-campus-essentials": project_card("campus-essentials", w=1200, h=300),
    }
    for slug, label, value in CONTACTS:
        tiles[f"contact-{label.lower()}"] = contact(slug, label, value)
    for name, (_, _, data) in tiles.items():
        (OUT / f"{name}.svg").write_text(data, encoding="utf-8")
        print("wrote", f"assets/{name}.svg")


if __name__ == "__main__":
    main()
