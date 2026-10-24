#!/usr/bin/env python3
# dynamic github stats + achievements cards -> img/y2k-win-stats.svg, img/y2k-win-achievements.svg (win95 style)
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

USER = "ARCANGEL0"
STATS_OUT = "img/y2k-win-stats.svg"
ACHIEVEMENTS_OUT = "img/y2k-win-achievements.svg"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"}
TOKEN = os.environ.get("GITHUB_TOKEN")
if TOKEN:
    UA["Authorization"] = f"token {TOKEN}"


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def graphql(query):
    if not TOKEN:
        return None
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        headers={**UA, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception:
        return None


try:
    profile = get(f"https://api.github.com/users/{USER}")
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated")
except Exception as e:
    print(f"stats fetch failed, keeping old cards: {e}", file=sys.stderr)
    sys.exit(0)

total_stars = sum(r.get("stargazers_count", 0) for r in repos)
total_forks = sum(r.get("forks_count", 0) for r in repos)
repo_count = len([r for r in repos if not r.get("fork")])
langs = {}
for r in repos:
    l = r.get("language") or "Unknown"
    langs[l] = langs.get(l, 0) + 1
top_langs = [l for l, _ in sorted(langs.items(), key=lambda x: -x[1])[:5]]

created_naive = datetime.strptime(profile["created_at"], "%Y-%m-%dT%H:%M:%SZ")
created = created_naive.replace(tzinfo=timezone.utc)
ago_years = (datetime.now(timezone.utc) - created).days // 365
member_since = created.strftime("%b %d, %Y")

# achievements via graphql (optional, degrades gracefully)
achievements = []
gql = graphql(f'{{user(login:"{USER}"){{profileAchievements{{achievements{{name title description assetUrl publishedAt}}}}}}}}')
if gql and not gql.get("errors"):
    achievements = gql["data"]["user"]["profileAchievements"]["achievements"]

# win95 window chrome
SANS = "MS Sans Serif,Verdana,sans-serif"
MONO = "'Courier New',Courier,monospace"

WINDOW_TOP = '''  <rect x="1" y="1" width="{w}" height="18" fill="#000080"/>
  <text x="5" y="13" font-family="{SANS}" font-weight="bold" font-size="11" fill="#FFFFFF">{title}</text>
  {buttons}
  <path d="M{rx1},6.5 L{ry1},13.5 M{ry1},6.5 L{rx1},13.5" stroke="#000000" stroke-width="2"/>
'''
WINDOW_BUTTONS = '''  <rect x="{x}" y="3" width="16" height="14" fill="#C0C0C0"/>
  <rect x="{x}" y="3" width="16" height="1" fill="#FFFFFF"/>
  <rect x="{x}" y="3" width="1" height="14" fill="#FFFFFF"/>
  <rect x="{x}" y="16" width="16" height="1" fill="#404040"/>
  <rect x="{dx}" y="3" width="1" height="14" fill="#404040"/>
'''


def titlebar(title, w, h, text=None):
    rx1 = w - 113
    ry1 = w - 95
    bx1 = w - 129
    bx2 = w - 113
    bx3 = w - 97
    buttons = ""
    for x, dx in ((w - 135, w - 119), (w - 117, w - 101), (w - 99, w - 83)):
        buttons += WINDOW_BUTTONS.format(x=x, dx=dx)
    # minimize dash
    buttons += f'  <rect x="{w-123}" y="12" width="6" height="2" fill="#000000"/>\n'
    # maximize inner square
    buttons += f'  <rect x="{w-105}" y="7" width="7" height="7" fill="none" stroke="#000000" stroke-width="0.8"/>\n'
    # close X
    buttons += f'  <rect x="{w-87}" y="7" width="7" height="6" fill="none" stroke="#000000" stroke-width="1"/>\n'
    buttons += f'  <rect x="{w-87}" y="7" width="7" height="2" fill="#000000"/>\n'
    return WINDOW_TOP.format(w=w, h=h, title=title, SANS=SANS, buttons=buttons, rx1=rx1, ry1=ry1)


def pane(w, h, y=23):
    return f'''  <rect x="8" y="{y}" width="{w-16}" height="{h-y-9}" fill="#FFFFFF"/>
  <rect x="8" y="{y}" width="{w-16}" height="1" fill="#808080"/>
  <rect x="8" y="{y}" width="1" height="{h-y-9}" fill="#808080"/>
  <rect x="8" y="{h-9}" width="{w-16}" height="1" fill="#DFDFDF"/>
  <rect x="{w-8}" y="{y}" width="1" height="{h-y-9}" fill="#DFDFDF"/>
'''


# ---------- stats.svg ----------
w, h = 900, 160
stats = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="stats.exe — GitHub stats for {USER}, Win95 style">
  <rect width="{w}" height="{h}" fill="#C0C0C0"/>
  <rect x="0" y="0" width="{w}" height="1" fill="#FFFFFF"/>
  <rect x="0" y="0" width="1" height="{h}" fill="#FFFFFF"/>
  <rect x="0" y="{h-1}" width="{w}" height="1" fill="#404040"/>
  <rect x="{w-1}" y="0" width="1" height="{h}" fill="#404040"/>
{titlebar(f"STATS.exe — {USER}", w, h)}
{pane(w, h)}

  <text x="18" y="44" font-family="{SANS}" font-weight="bold" font-size="11" fill="#000080">GitHub statistics</text>

  <g font-family="{SANS}">
    <!-- repos -->
    <rect x="18" y="60" width="210" height="50" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
    <rect x="18" y="60" width="210" height="1" fill="#FFFFFF"/>
    <rect x="18" y="60" width="1" height="50" fill="#FFFFFF"/>
    <rect x="18" y="109" width="210" height="1" fill="#404040"/>
    <rect x="227" y="60" width="1" height="50" fill="#404040"/>
    <text x="28" y="80" font-size="13" fill="#000000">{repo_count}</text>
    <text x="28" y="99" font-size="9" fill="#404040">public repos</text>

    <!-- stars -->
    <rect x="240" y="60" width="210" height="50" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
    <rect x="240" y="60" width="210" height="1" fill="#FFFFFF"/>
    <rect x="240" y="60" width="1" height="50" fill="#FFFFFF"/>
    <rect x="240" y="109" width="210" height="1" fill="#404040"/>
    <rect x="449" y="60" width="1" height="50" fill="#404040"/>
    <text x="250" y="80" font-size="13" fill="#000000">{total_stars}</text>
    <text x="250" y="99" font-size="9" fill="#404040">stars</text>

    <!-- forks -->
    <rect x="462" y="60" width="210" height="50" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
    <rect x="462" y="60" width="210" height="1" fill="#FFFFFF"/>
    <rect x="462" y="60" width="1" height="50" fill="#FFFFFF"/>
    <rect x="462" y="109" width="210" height="1" fill="#404040"/>
    <rect x="671" y="60" width="1" height="50" fill="#404040"/>
    <text x="472" y="80" font-size="13" fill="#000000">{total_forks}</text>
    <text x="472" y="99" font-size="9" fill="#404040">forks</text>

    <!-- followers -->
    <rect x="684" y="60" width="208" height="50" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
    <rect x="684" y="60" width="208" height="1" fill="#FFFFFF"/>
    <rect x="684" y="60" width="1" height="50" fill="#FFFFFF"/>
    <rect x="684" y="109" width="208" height="1" fill="#404040"/>
    <rect x="{w-8}" y="60" width="1" height="50" fill="#404040"/>
    <text x="694" y="80" font-size="13" fill="#000000">{profile.get('followers', 0)}</text>
    <text x="694" y="99" font-size="9" fill="#404040">followers</text>
  </g>

  <rect x="18" y="120" width="264" height="22" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
  <rect x="18" y="120" width="264" height="1" fill="#FFFFFF"/>
  <rect x="18" y="120" width="1" height="22" fill="#FFFFFF"/>
  <rect x="18" y="141" width="264" height="1" fill="#404040"/>
  <rect x="281" y="120" width="1" height="22" fill="#404040"/>
  <text x="28" y="134" font-size="10" fill="#000000">member since {member_since} · {profile.get('followers', 0)} followers · {profile.get('following', 0)} following</text>

  <rect x="284" y="120" width="{w-292}" height="22" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
  <rect x="284" y="120" width="{w-292}" height="1" fill="#FFFFFF"/>
  <rect x="284" y="120" width="1" height="22" fill="#FFFFFF"/>
  <rect x="284" y="141" width="{w-292}" height="1" fill="#404040"/>
  <rect x="{w-8}" y="120" width="1" height="22" fill="#404040"/>
  <text x="294" y="134" font-size="10" fill="#000000">top languages: {" · ".join(top_langs) if top_langs else "none"}</text>
</svg>
'''

# ---------- achievements.svg ----------
w, h = 900, 200
ach_rows = ""
if achievements:
    x, y = 18, 134
    for i, a in enumerate(achievements[:6]):
        col = x + (i % 3) * 292
        row = y + (i // 3) * 52
        avatar = a.get("assetUrl", "")
        title = a.get("title", "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ach_rows += f'''
  <rect x="{col}" y="{row}" width="64" height="48" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
  <rect x="{col}" y="{row}" width="64" height="1" fill="#FFFFFF"/>
  <rect x="{col}" y="{row}" width="1" height="48" fill="#FFFFFF"/>
  <rect x="{col}" y="{row+47}" width="64" height="1" fill="#404040"/>
  <rect x="{col+64}" y="{row}" width="1" height="48" fill="#404040"/>
'''
else:
    ach_rows = '''
  <rect x="18" y="168" width="48" height="48" fill="#C0C0C0" stroke="#808080" stroke-width="1"/>
  <rect x="18" y="168" width="48" height="1" fill="#FFFFFF"/>
  <rect x="18" y="168" width="1" height="48" fill="#FFFFFF"/>
  <rect x="18" y="215" width="48" height="1" fill="#404040"/>
  <rect x="65" y="168" width="1" height="48" fill="#404040"/>
  <text x="42" y="192" text-anchor="middle" font-family="MS Sans Serif,Verdana,sans-serif" font-size="8" fill="#000000">none</text>
  <text x="78" y="188" font-family="MS Sans Serif,Verdana,sans-serif" font-size="10" fill="#000000">· no data ·</text>
'''

achievements_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="achievements.exe — GitHub profile achievements for {USER}, Win95 style">
  <rect width="{w}" height="{h}" fill="#C0C0C0"/>
  <rect x="0" y="0" width="{w}" height="1" fill="#FFFFFF"/>
  <rect x="0" y="0" width="1" height="{h}" fill="#FFFFFF"/>
  <rect x="0" y="{h-1}" width="{w}" height="1" fill="#404040"/>
  <rect x="{w-1}" y="0" width="1" height="{h}" fill="#404040"/>
{titlebar(f"ACHIEVEMENTS.exe — {USER}", w, h)}
{pane(w, h)}

  <text x="18" y="46" font-family="{SANS}" font-weight="bold" font-size="11" fill="#000080">Profile achievements</text>
  <text x="18" y="64" font-family="{MONO}" font-size="10" fill="#404040">account · created {member_since}</text>
  <text x="18" y="82" font-family="{MONO}" font-size="10" fill="#404040">public repositories · {repo_count}</text>
  <text x="18" y="100" font-family="{MONO}" font-size="10" fill="#404040">stars · {total_stars} · forks · {total_forks}</text>
  <text x="18" y="118" font-family="{MONO}" font-size="10" fill="#404040">followers · {profile.get('followers', 0)} · following · {profile.get('following', 0)}</text>
  <rect x="18" y="130" width="{w-36}" height="1" fill="#C0C0C0"/>
  <text x="18" y="150" font-family="{SANS}" font-size="10" fill="#000080">badge icons: {len(achievements)} unlocked · 0 pending</text>
{ach_rows}
</svg>
'''

open(STATS_OUT, "w").write(stats)
open(ACHIEVEMENTS_OUT, "w").write(achievements_svg)
print(f"stats written: repos={repo_count} stars={total_stars} forks={total_forks} achievements={len(achievements)}")
