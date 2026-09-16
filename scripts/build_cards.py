#!/usr/bin/env python3
"""Build the bento tiles in assets/ for the profile README.

Edit the DATA section, then run:  python3 scripts/build_cards.py
"""
import base64
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
ROLE = "IT Student · Web Developer · Linux Tinkerer"
CHIPS = ["📍 Philippines", "🐧 Fedora + Hyprland", "🎓 BSIT student"]

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

STACK = [
    ("Languages", ["ts", "js", "php", "python", "c", "bash"]),
    ("Frameworks", ["nextjs", "react", "laravel", "tailwind", "nodejs"]),
    ("Data", ["postgres", "mysql", "supabase", "sqlite"]),
    ("Tools & OS", ["git", "docker", "vercel", "vscode", "neovim", "fedora", "linux", "blender", "arduino"]),
]

# status: "public" | "private" ; live: url or None
PROJECTS = {
    "quest-runner": dict(
        emoji="🎮", title="Quest Runner", accent="#70a5fd", status="public", live=None,
        desc="Complete Discord play quests on Linux without installing the game. "
             "Spawns a tiny idle process with the right name so Discord counts the time. "
             "Works with native and Flatpak Discord.",
        tags=["Python", "C", "GTK4", "Shell"],
        terminal=["$ quest search terraria", "$ quest run terraria -m 16",
                  "▶ Playing Terraria · auto-stop in 16m", "$ quest status"],
    ),
    "takenote": dict(
        emoji="📝", title="TakeNote", accent="#bf91f3", status="private", live="takenote.fun",
        desc="A free public wall where anyone can leave anonymous sticky notes or drawings. "
             "Create your wall, share the link, pin the ones that matter.",
        tags=["Next.js", "Tailwind", "Supabase"],
    ),
    "dtr": dict(
        emoji="💸", title="DTR Salary Calculator", accent="#38bdae", status="public",
        live="dtr-calculator-five.vercel.app",
        desc="Mobile-first salary calculator with OCR. Snap your daily time record, get your pay.",
        tags=["TypeScript", "OCR", "Mobile"],
    ),
    "geocrimemap": dict(
        emoji="🗺️", title="GeoCrimeMap", accent="#ff7a93", status="private", live=None,
        desc="Web-based crime mapping with data analytics for Barangay San Roque.",
        tags=["Web GIS", "Analytics"],
    ),
    "lms": dict(
        emoji="📚", title="Web LMS", accent="#e0af68", status="private", live=None,
        desc="Learning management system for students, faculty, and administrators.",
        tags=["React", "Laravel", "PostgreSQL", "Docker"],
    ),
    "campus-essentials": dict(
        emoji="🏫", title="Campus Essentials", accent="#38bdae", status="public", live=None,
        desc="Inventory system for a school supplies store: stock, suppliers, "
             "and reorder-level alerts.",
        tags=["Laravel", "Blade", "SQLite"],
    ),
}

CONTACTS = [
    ("email", "Email", "edzel.wcc@gmail.com", "#ff7a93"),
    ("discord", "Discord", "xenumwa", "#70a5fd"),
    ("facebook", "Facebook", "idzill", "#bf91f3"),
]

# ---------------------------------------------------------------- THEME

BG = "#1a1b27"
BG2 = "#20223a"
BORDER = "#2e3150"
TEXT = "#c0caf5"
MUTED = "#737aa2"
BLUE, PURPLE, TEAL = "#70a5fd", "#bf91f3", "#38bdae"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace"

BASE_CSS = f"""
text {{ font-family: {FONT}; }}
.mono {{ font-family: {MONO}; }}
.label {{ font-size: 13px; font-weight: 700; letter-spacing: 2px; fill: {MUTED}; }}
.fade {{ animation: fade .7s ease-out backwards; }}
@keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
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
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<style>{BASE_CSS}{css}</style>"
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>'
        f"{body}</svg>"
    )


def text_lines(lines, x, y, size, lh, fill=TEXT, weight=400, delay=0.0, step=0.08, cls="fade"):
    out = []
    for i, line in enumerate(lines):
        out.append(
            f'<text x="{x}" y="{y + i*lh}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'class="{cls}" style="animation-delay:{delay + i*step:.2f}s">{esc(line)}</text>'
        )
    return "".join(out)


def pill(x, y, label, color, size=14, pad=12, h=28):
    w = int(len(label) * size * 0.58) + pad * 2
    return w, (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity=".12" '
        f'stroke="{color}" stroke-opacity=".45"/>'
        f'<text x="{x + w/2}" y="{y + h/2 + size*0.35}" font-size="{size}" fill="{color}" '
        f'text-anchor="middle" font-weight="600">{esc(label)}</text>'
    )


def pills(x, y, labels, color, gap=8, **kw):
    out = []
    for lab in labels:
        w, s = pill(x, y, lab, color, **kw)
        out.append(s)
        x += w + gap
    return "".join(out)


# icons skillicons.dev doesn't have: built from simple-icons in the same style
SIMPLE_ICONS = {"fedora": "#51A2DA"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def icon(name):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{name}.svg"
    if not f.exists() and name in SIMPLE_ICONS:
        src = fetch(f"https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{name}.svg").decode()
        path = re.search(r'<path d="([^"]+)"', src).group(1)
        f.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
            '<rect width="256" height="256" rx="60" fill="#242938"/>'
            f'<g transform="translate(48 48) scale(6.6667)" fill="{SIMPLE_ICONS[name]}"><path d="{path}"/></g></svg>'
        )
    if not f.exists():
        f.write_bytes(fetch(f"https://skillicons.dev/icons?i={name}&theme=dark"))
    return "data:image/svg+xml;base64," + base64.b64encode(f.read_bytes()).decode()


# ---------------------------------------------------------------- TILES

def hero():
    w, h = 1200, 360
    css = """
.blob { transform-box: fill-box; transform-origin: center; }
.b1 { animation: drift1 14s ease-in-out infinite alternate; }
.b2 { animation: drift2 18s ease-in-out infinite alternate; }
.b3 { animation: drift3 16s ease-in-out infinite alternate; }
@keyframes drift1 { to { transform: translate(140px, 60px) scale(1.25); } }
@keyframes drift2 { to { transform: translate(-160px, -40px) scale(.85); } }
@keyframes drift3 { to { transform: translate(-80px, 70px) scale(1.2); } }
.cursor { animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
"""
    body = f"""
<defs>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
  <clipPath id="clip"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22"/></clipPath>
  <linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{BLUE}"/><stop offset=".55" stop-color="{PURPLE}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity=".035"/></pattern>
</defs>
<g clip-path="url(#clip)">
  <g filter="url(#blur)" opacity=".55">
    <circle class="blob b1" cx="880" cy="90" r="150" fill="{PURPLE}"/>
    <circle class="blob b2" cx="1080" cy="280" r="140" fill="{BLUE}"/>
    <circle class="blob b3" cx="700" cy="300" r="110" fill="{TEAL}"/>
  </g>
  <rect width="{w}" height="{h}" fill="url(#grid)"/>
</g>
<text x="64" y="84" class="label fade mono">~/xenutheflock</text>
<text x="60" y="190" font-size="120" font-weight="800" fill="url(#name)" letter-spacing="-3" class="fade" style="animation-delay:.1s">{esc(NAME)}</text>
<rect x="{66 + len(NAME)*66}" y="108" width="14" height="92" rx="3" fill="{TEAL}" class="cursor"/>
{text_lines([ROLE], 64, 240, 26, 0, fill=TEXT, weight=500, delay=.25)}
<g class="fade" style="animation-delay:.4s">{pills(64, 272, CHIPS, BLUE, size=15, h=32, gap=10)}</g>
"""
    return w, h, svg(w, h, body, css)


def about():
    w, h = 800, 300
    body = f"""
<text x="40" y="54" class="label fade">ABOUT</text>
<text x="40" y="100" font-size="30" font-weight="700" fill="{TEXT}" class="fade" style="animation-delay:.05s">Hey there 👋</text>
{text_lines(wrap(ABOUT, 70), 40, 146, 19, 30, fill=MUTED, delay=.15)}
"""
    return w, h, svg(w, h, body)


def now():
    w, h = 400, 300
    css = """
.bar { transform-box: fill-box; transform-origin: left; animation: grow 1.2s ease-out backwards; }
@keyframes grow { from { transform: scaleY(0); } }
"""
    rows = []
    colors = [BLUE, PURPLE, TEAL, "#e0af68"]
    for i, (k, v) in enumerate(NOW):
        y = 104 + i * 48
        c = colors[i % len(colors)]
        rows.append(
            f'<g class="fade" style="animation-delay:{.1 + i*.1:.2f}s">'
            f'<rect x="36" y="{y-22}" width="4" height="36" rx="2" fill="{c}" class="bar"/>'
            f'<text x="54" y="{y-6}" font-size="12" font-weight="700" letter-spacing="1.5" fill="{c}">{esc(k.upper())}</text>'
            f'<text x="54" y="{y+13}" font-size="17" fill="{TEXT}">{esc(v)}</text></g>'
        )
    body = f'<text x="36" y="54" class="label fade">RIGHT NOW</text>{"".join(rows)}'
    return w, h, svg(w, h, body, css)


def stack():
    w, h = 1200, 330
    size, gap = 52, 14
    out = [f'<text x="40" y="54" class="label fade">STACK</text>']
    col_x = [40, 460]
    for i, (group, icons) in enumerate(STACK):
        x0 = col_x[i % 2]
        y0 = 90 + (i // 2) * 116
        out.append(f'<text x="{x0}" y="{y0 + 4}" font-size="15" font-weight="700" fill="{TEXT}" class="fade" style="animation-delay:{i*.1:.1f}s">{esc(group)}</text>')
        for j, name in enumerate(icons):
            out.append(
                f'<image x="{x0 + j*(size+gap)}" y="{y0 + 20}" width="{size}" height="{size}" href="{icon(name)}" '
                f'class="fade" style="animation-delay:{.15 + i*.1 + j*.05:.2f}s"/>'
            )
    return w, h, svg(w, h, "".join(out))


def project_wide(key):
    p = PROJECTS[key]
    w, h = 1200, 340
    a = p["accent"]
    term = p.get("terminal", [])
    css = """
.typing { animation: pop .1s linear backwards; }
@keyframes pop { from { opacity: 0; } }
.cursor { animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
"""
    tx, ty, tw, th = 640, 50, 520, 240
    term_lines = []
    for i, line in enumerate(term):
        color = TEAL if line.startswith("▶") else TEXT
        term_lines.append(
            f'<text x="{tx+24}" y="{ty+84 + i*32}" font-size="16" fill="{color}" class="mono typing" '
            f'style="animation-delay:{.6 + i*.6:.1f}s">{esc(line)}</text>'
        )
    cursor_y = ty + 84 + len(term) * 32
    body = f"""
<defs><linearGradient id="glow" x1="0" x2="1"><stop offset="0" stop-color="{a}" stop-opacity=".18"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></linearGradient></defs>
<rect x="2" y="2" width="600" height="{h-4}" rx="20" fill="url(#glow)"/>
<text x="40" y="54" class="label fade">FEATURED PROJECT</text>
<rect x="40" y="80" width="56" height="56" rx="14" fill="{a}" fill-opacity=".15" stroke="{a}" stroke-opacity=".5" class="fade"/>
<text x="68" y="118" font-size="28" text-anchor="middle" class="fade">{p['emoji']}</text>
<text x="112" y="120" font-size="34" font-weight="800" fill="{TEXT}" class="fade" style="animation-delay:.05s">{esc(p['title'])}</text>
{text_lines(wrap(p['desc'], 58), 40, 176, 17, 26, fill=MUTED, delay=.15)}
<g class="fade" style="animation-delay:.4s">{pills(40, 270, p['tags'], a, size=13, h=28)}</g>
<g class="fade" style="animation-delay:.3s">
  <rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="14" fill="#11121d" stroke="{BORDER}"/>
  <circle cx="{tx+22}" cy="{ty+22}" r="6" fill="#ff5f57"/><circle cx="{tx+42}" cy="{ty+22}" r="6" fill="#febc2e"/><circle cx="{tx+62}" cy="{ty+22}" r="6" fill="#28c840"/>
  <text x="{tx+tw/2}" y="{ty+27}" font-size="13" fill="{MUTED}" text-anchor="middle" class="mono">quest — bash</text>
  <line x1="{tx}" y1="{ty+44}" x2="{tx+tw}" y2="{ty+44}" stroke="{BORDER}"/>
</g>
{"".join(term_lines)}
<rect x="{tx+24}" y="{cursor_y-15}" width="10" height="19" fill="{a}" class="cursor"/>
"""
    return w, h, svg(w, h, body, css)


def project_card(key, w=600, h=340):
    p = PROJECTS[key]
    a = p["accent"]
    if p["status"] == "public":
        foot = ("● open source", TEAL)
    else:
        foot = ("● private repo", MUTED)
    live = p["live"]
    ncols = 58 if w == 600 else 110
    body = f"""
<defs><radialGradient id="g" cx="1" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity=".28"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22"/></clipPath></defs>
<rect width="{w}" height="{h}" fill="url(#g)" clip-path="url(#c)"/>
<rect x="36" y="36" width="56" height="56" rx="14" fill="{a}" fill-opacity=".15" stroke="{a}" stroke-opacity=".5" class="fade"/>
<text x="64" y="74" font-size="28" text-anchor="middle" class="fade">{p['emoji']}</text>
<text x="36" y="136" font-size="28" font-weight="800" fill="{TEXT}" class="fade" style="animation-delay:.05s">{esc(p['title'])}</text>
{text_lines(wrap(p['desc'], ncols)[:3], 36, 172, 16, 25, fill=MUTED, delay=.12)}
<g class="fade" style="animation-delay:.3s">{pills(36, h-92, p['tags'], a, size=13, h=26)}</g>
<text x="36" y="{h-30}" font-size="13" font-weight="600" fill="{foot[1]}" class="fade" style="animation-delay:.4s">{foot[0]}</text>
"""
    if live:
        body += f'<text x="{w-36}" y="{h-30}" font-size="13" font-weight="700" fill="{a}" text-anchor="end" class="fade" style="animation-delay:.4s">↗ {esc(live)}</text>'
    elif p["status"] == "public":
        body += f'<text x="{w-36}" y="{h-30}" font-size="13" font-weight="700" fill="{a}" text-anchor="end" class="fade" style="animation-delay:.4s">↗ view repo</text>'
    return w, h, svg(w, h, body)


def contact(kind, label, value, color):
    w, h = 400, 130
    glyph = {"email": "✉", "discord": "💬", "facebook": "f"}[kind]
    body = f"""
<rect x="30" y="33" width="64" height="64" rx="16" fill="{color}" fill-opacity=".15" stroke="{color}" stroke-opacity=".5"/>
<text x="62" y="76" font-size="30" font-weight="800" fill="{color}" text-anchor="middle">{glyph}</text>
<text x="114" y="58" font-size="13" font-weight="700" letter-spacing="2" fill="{MUTED}">{esc(label.upper())}</text>
<text x="114" y="86" font-size="{20 if len(value) < 20 else 17}" font-weight="700" fill="{TEXT}">{esc(value)}</text>
<text x="{w-30}" y="72" font-size="22" fill="{color}" text-anchor="end">→</text>
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
    for kind, label, value, color in CONTACTS:
        tiles[f"contact-{kind}"] = contact(kind, label, value, color)
    for name, (_, _, data) in tiles.items():
        (OUT / f"{name}.svg").write_text(data, encoding="utf-8")
        print("wrote", f"assets/{name}.svg")


if __name__ == "__main__":
    main()
