#!/usr/bin/env python3
# dynamic github stats / top-langs / achievements cards (win95 style)
# -> img/y2k-win-stats.svg, img/y2k-top-langs.svg, img/y2k-win-achievements.svg
import base64, json, os, re, sys, urllib.request
from datetime import datetime, timezone
from math import ceil

USER = "ARCANGEL0"
STATS_OUT = "img/y2k-win-stats.svg"
LANGS_OUT = "img/y2k-top-langs.svg"
ACH_OUT = "img/y2k-win-achievements.svg"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"}
TOKEN = os.environ.get("TOKEN") or os.environ.get("GITHUB_TOKEN")
if TOKEN:
    UA["Authorization"] = f"token {TOKEN}"

SANS = "MS Sans Serif,Verdana,sans-serif"
MONO = "'Courier New',Courier,monospace"


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def get_json(url):
    return json.loads(fetch(url).decode())


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- win95 chrome ----------
def frame(w, h, title):
    """window frame + titlebar with correctly-placed min/max/close buttons"""
    bx = [w - 54, w - 36, w - 18]          # 846/864/882 for w=900
    b = f'  <rect x="1" y="1" width="{w-2}" height="18" fill="#000080"/>\n'
    b += f'  <text x="5" y="13" font-family="{SANS}" font-weight="bold" font-size="11" fill="#FFFFFF">{esc(title)}</text>\n'
    for x in bx:
        b += (f'  <rect x="{x}" y="3" width="16" height="14" fill="#C0C0C0"/>\n'
              f'  <rect x="{x}" y="3" width="16" height="1" fill="#FFFFFF"/>\n'
              f'  <rect x="{x}" y="3" width="1" height="14" fill="#FFFFFF"/>\n'
              f'  <rect x="{x}" y="16" width="16" height="1" fill="#404040"/>\n'
              f'  <rect x="{x+15}" y="3" width="1" height="14" fill="#404040"/>\n')
    b += f'  <rect x="{w-50}" y="12" width="6" height="2" fill="#000000"/>\n'                       # minimize dash
    b += f'  <rect x="{w-31}" y="7" width="7" height="6" fill="none" stroke="#000000" stroke-width="1"/>\n'
    b += f'  <rect x="{w-31}" y="7" width="7" height="2" fill="#000000"/>\n'                        # maximize square
    b += f'  <path d="M{w-13.5},6.5 L{w-6.5},13.5 M{w-6.5},6.5 L{w-13.5},13.5" stroke="#000000" stroke-width="2"/>\n'  # close X
    return (f'<rect width="{w}" height="{h}" fill="#C0C0C0"/>\n'
            f'<rect x="0" y="0" width="{w}" height="1" fill="#FFFFFF"/>\n'
            f'<rect x="0" y="0" width="1" height="{h}" fill="#FFFFFF"/>\n'
            f'<rect x="0" y="{h-1}" width="{w}" height="1" fill="#404040"/>\n'
            f'<rect x="{w-1}" y="0" width="1" height="{h}" fill="#404040"/>\n' + b)


def pane(w, h, y=23):
    ph = h - y - 9
    return (f'  <rect x="8" y="{y}" width="{w-16}" height="{ph}" fill="#FFFFFF"/>\n'
            f'  <rect x="8" y="{y}" width="{w-16}" height="1" fill="#808080"/>\n'
            f'  <rect x="8" y="{y}" width="1" height="{ph}" fill="#808080"/>\n'
            f'  <rect x="8" y="{h-9}" width="{w-16}" height="1" fill="#DFDFDF"/>\n'
            f'  <rect x="{w-8}" y="{y}" width="1" height="{ph}" fill="#DFDFDF"/>\n')


def cell(x, y, w, h):
    return (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>\n'
            f'  <rect x="{x}" y="{y}" width="{w}" height="1" fill="#FFFFFF"/>\n'
            f'  <rect x="{x}" y="{y}" width="1" height="{h}" fill="#FFFFFF"/>\n'
            f'  <rect x="{x}" y="{y+h-1}" width="{w}" height="1" fill="#404040"/>\n'
            f'  <rect x="{x+w-1}" y="{y}" width="1" height="{h}" fill="#404040"/>\n')


# ---------- fetch live data ----------
try:
    profile = get_json(f"https://api.github.com/users/{USER}")
    repos = get_json(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")
    prof_html = fetch(f"https://github.com/{USER}").decode()
except Exception as e:
    print(f"fetch failed, keeping old cards: {e}", file=sys.stderr)
    sys.exit(0)

total_stars = sum(r.get("stargazers_count", 0) for r in repos)
total_forks = sum(r.get("forks_count", 0) for r in repos)
repo_count = len([r for r in repos if not r.get("fork")])
langs = {}
for r in repos:
    l = r.get("language")
    if l:
        langs[l] = langs.get(l, 0) + 1
lang_sorted = sorted(langs.items(), key=lambda x: -x[1])
top_langs = lang_sorted[:5]
lang_total = sum(c for _, c in lang_sorted) or 1

created = datetime.strptime(profile["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
member_since = created.strftime("%b %d, %Y")
followers = profile.get("followers", 0)
following = profile.get("following", 0)

# ---------- achievements: scrape profile HTML ----------
# tier/mult map: slug -> (tier, mult) from the label spans
tier_map = {}
for m in re.finditer(r'achievement=([a-z0-9-]+)&amp;tab=achievements.{0,600}?achievement-tier-label--(\w+)[^>]*>(x?\d*)</span>', prof_html, re.S):
    slug, tier, mult = m.groups()
    tier_map[slug] = (tier, mult or "")
# every achievement badge img, in order
achievements = []
seen = set()
for m in re.finditer(r'<img[^>]*data-hovercard-type="achievement"[^>]*>', prof_html):
    tag = m.group(0)
    src = re.search(r'src="([^"]+)"', tag)
    alt = re.search(r'alt="Achievement: ([^"]+)"', tag)
    hover = re.search(r'achievements/([a-z0-9-]+)/detail', tag)
    if not (src and alt):
        continue
    slug = hover.group(1) if hover else "?"
    if src.group(1) in seen:
        continue
    seen.add(src.group(1))
    tier, mult = tier_map.get(slug, ("default", ""))
    achievements.append({"slug": slug, "tier": tier, "mult": mult, "src": src.group(1), "name": alt.group(1)})

# download badge images, base64-embed (external URLs are blocked inside camo'd SVGs)
for a in achievements:
    try:
        data = fetch(a["src"])
        mime = "image/png" if a["src"].lower().endswith(".png") else "image/svg+xml"
        a["data"] = base64.b64encode(data).decode()
        a["mime"] = mime
    except Exception:
        a["data"] = None
        a["mime"] = "image/png"

# ---------- stats.svg ----------
w, h = 900, 160
s = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="stats.exe — GitHub stats for {USER}, Win95 style">\n'
s += frame(w, h, f"STATS.exe — {USER}") + pane(w, h)
s += f'  <text x="18" y="44" font-family="{SANS}" font-weight="bold" font-size="11" fill="#000080">GitHub statistics</text>\n'
stats_cells = [(repo_count, "public repos"), (total_stars, "stars"), (total_forks, "forks"), (followers, "followers")]
cw = (w - 36 - 3 * 12) // 4
for i, (val, label) in enumerate(stats_cells):
    x = 18 + i * (cw + 12)
    s += cell(x, 60, cw, 50)
    s += f'  <text x="{x+10}" y="80" font-family="{SANS}" font-size="13" fill="#000000">{val}</text>\n'
    s += f'  <text x="{x+10}" y="99" font-family="{SANS}" font-size="9" fill="#404040">{label}</text>\n'
s += cell(18, 120, 264, 22)
s += f'  <text x="28" y="135" font-family="{SANS}" font-size="9" fill="#000000">since {member_since} · {followers} followers · {following} following</text>\n'
s += cell(294, 120, w - 294 - 8, 22)
s += f'  <text x="304" y="135" font-family="{SANS}" font-size="9" fill="#000000">top languages: {" · ".join(l for l, _ in top_langs) if top_langs else "none"}</text>\n'
s += '</svg>\n'
open(STATS_OUT, "w").write(s)

# ---------- top-langs.svg ----------
w2, h2 = 460, 150
t = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w2}" height="{h2}" viewBox="0 0 {w2} {h2}" role="img" aria-label="top languages — {USER}, Win95 style">\n'
t += frame(w2, h2, "TOP-LANGS.exe") + pane(w2, h2)
t += f'  <text x="16" y="42" font-family="{SANS}" font-weight="bold" font-size="10" fill="#000080">Most used languages</text>\n'
maxc = max((c for _, c in top_langs), default=1)
for i, (lang, c) in enumerate(top_langs):
    y = 52 + i * 19
    pct = c * 100 // lang_total
    bw = int((w2 - 200) * c / maxc)
    t += f'  <text x="16" y="{y+10}" font-family="{MONO}" font-size="9" fill="#000000">{esc(lang)}</text>\n'
    t += f'  <rect x="150" y="{y}" width="{w2-200}" height="11" fill="#FFFFFF" stroke="#808080" stroke-width="1"/>\n'
    t += f'  <rect x="151" y="{y+1}" width="{max(bw,2)}" height="9" fill="#000080"/>\n'
    t += f'  <text x="{w2-44}" y="{y+10}" font-family="{MONO}" font-size="9" fill="#404040">{pct}%</text>\n'
t += '</svg>\n'
open(LANGS_OUT, "w").write(t)

# ---------- achievements.svg ----------
n = len(achievements)
per_row = 4
rows = max(1, ceil(n / per_row)) if n else 1
ah = 168 + rows * 60
w3, h3 = 900, ah
av = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w3}" height="{h3}" viewBox="0 0 {w3} {h3}" role="img" aria-label="achievements.exe — GitHub profile achievements for {USER}, Win95 style">\n'
av += frame(w3, h3, f"ACHIEVEMENTS.exe — {USER}") + pane(w3, h3)
av += f'  <text x="18" y="46" font-family="{SANS}" font-weight="bold" font-size="11" fill="#000080">Profile achievements</text>\n'
av += f'  <text x="18" y="64" font-family="{MONO}" font-size="10" fill="#404040">account · created {member_since}</text>\n'
av += f'  <text x="18" y="82" font-family="{MONO}" font-size="10" fill="#404040">public repositories · {repo_count}</text>\n'
av += f'  <text x="18" y="100" font-family="{MONO}" font-size="10" fill="#404040">stars · {total_stars} · forks · {total_forks}</text>\n'
av += f'  <text x="18" y="118" font-family="{MONO}" font-size="10" fill="#404040">followers · {followers} · following · {following}</text>\n'
av += f'  <rect x="18" y="130" width="{w3-36}" height="1" fill="#C0C0C0"/>\n'
av += f'  <text x="18" y="150" font-family="{SANS}" font-size="10" fill="#000080">badges: {n} unlocked</text>\n'
if n:
    for i, a in enumerate(achievements[:8]):
        col = 18 + (i % per_row) * 130
        row = 162 + (i // per_row) * 60
        av += cell(col, row, 120, 50)
        if a.get("data"):
            av += f'  <image href="data:{a["mime"]};base64,{a["data"]}" x="{col+4}" y="{row+5}" width="40" height="40" image-rendering="pixelated"><title>{esc(a["name"])} ({esc(a["tier"])} {esc(a["mult"])})</title></image>\n'
            av += f'  <text x="{col+50}" y="{row+20}" font-family="{SANS}" font-size="9" fill="#000000">{esc(a["name"])}</text>\n'
            av += f'  <text x="{col+50}" y="{row+34}" font-family="{SANS}" font-size="8" fill="#404040">{esc(a["tier"])} {esc(a["mult"])}</text>\n'
        else:
            av += f'  <text x="{col+60}" y="{row+29}" text-anchor="middle" font-family="{SANS}" font-size="9" fill="#000000">{esc(a["name"])}</text>\n'
else:
    av += cell(18, 162, 120, 50)
    av += f'  <text x="78" y="191" text-anchor="middle" font-family="{SANS}" font-size="9" fill="#000000">none</text>\n'
    av += f'  <text x="150" y="190" font-family="{SANS}" font-size="10" fill="#000000">· no achievements yet ·</text>\n'
av += '</svg>\n'
open(ACH_OUT, "w").write(av)

print(f"written: stats(repos={repo_count} stars={total_stars} forks={total_forks}) langs={len(top_langs)} achievements={n} " +
      ",".join(a["slug"] for a in achievements))
