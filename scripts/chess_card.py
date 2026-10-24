#!/usr/bin/env python3
# y2k chess card for arcxl0 (chess.com) -> img/y2k-chess.svg
import json, sys, urllib.request
from collections import Counter
from datetime import datetime, timezone

USER = "arcxl0"
OUT = "img/y2k-chess.svg"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def esc(s):
    return s.replace("&", "&").replace("<", "<").replace(">", ">")

try:
    profile = get(f"https://api.chess.com/pub/player/{USER}")
    stats = get(f"https://api.chess.com/pub/player/{USER}/stats")
    months = get(f"https://api.chess.com/pub/player/{USER}/games/archives")["archives"][-2:]
    games = []
    for m in months:
        games += get(m)["games"]
    games.sort(key=lambda g: g["end_time"])
except Exception as e:
    print(f"chess fetch failed, keeping old card: {e}", file=sys.stderr)
    sys.exit(0)

DRAW = {"agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient"}
w = l = d = 0
opp_counter = Counter()
results = []  # chronological 'W'/'L'/'D'
for g in games:
    side = "white" if g.get("white", {}).get("username", "").lower() == USER else "black"
    me, opp = g[side], g["black" if side == "white" else "white"]
    r = me.get("result")
    if r == "win":
        w += 1; results.append("W")
    elif r in DRAW:
        d += 1; results.append("D")
    else:
        l += 1; results.append("L")
    opp_counter[opp.get("username", "?")] += 1

streak = ""
for ch in reversed(results):
    if not streak or ch == streak[-1]:
        streak = ch + streak
    else:
        break
streak = streak.lower() if streak else "-"

puzzle = stats.get("tactics", {}).get("highest", {}).get("rating")
last_online = datetime.fromtimestamp(profile["last_online"], tz=timezone.utc)
ago = (datetime.now(timezone.utc) - last_online).days
ago_txt = "today" if ago < 1 else f"{ago}d ago"
fav = opp_counter.most_common(1)[0][0] if opp_counter else "-"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="140" viewBox="0 0 900 140" role="img" aria-label="chess card for {esc(USER)} on chess.com">
  <defs>
    <linearGradient id="tb" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000080"/><stop offset="1" stop-color="#1084d0"/>
    </linearGradient>
  </defs>
  <rect width="900" height="140" fill="#0A0A12"/>
  <rect x="1.5" y="1.5" width="897" height="137" fill="none" stroke="#3A3A4A" stroke-width="3"/>
  <rect x="4" y="4" width="892" height="22" fill="url(#tb)"/>
  <text x="14" y="20" font-family="Tahoma,Verdana,sans-serif" font-weight="bold" font-size="12" fill="#FFFFFF">CHESS.EXE</text>
  <rect x="858" y="8" width="14" height="13" fill="#C0C0C0" stroke="#000" stroke-width="1"/>
  <text x="861" y="18" font-family="Tahoma,Verdana,sans-serif" font-size="10" fill="#000">x</text>
  <rect x="838" y="8" width="14" height="13" fill="#C0C0C0" stroke="#000" stroke-width="1"/>
  <rect x="841" y="11" width="8" height="7" fill="none" stroke="#000" stroke-width="1"/>
  <g>
'''
# 8x8 board
sq = 11
bx, by = 24, 40
for row in range(8):
    for col in range(8):
        fill = "#9A9AA8" if (row + col) % 2 == 0 else "#2A2A38"
        svg += f'  <rect x="{bx + col * sq}" y="{by + row * sq}" width="{sq}" height="{sq}" fill="{fill}"/>\n'
# opening position pieces (glyphs)
pieces = {(7, 4): ("♙", "#E8E8F0"), (6, 4): ("♟", "#101018"), (5, 5): ("♘", "#E8E8F0"), (1, 2): ("♞", "#F0F0FF")}
for (row, col), (glyph, fill) in pieces.items():
    svg += f'  <text x="{bx + col * sq + 1}" y="{by + row * sq + 10}" font-size="10" fill="{fill}">{glyph}</text>\n'
svg += f'''  <rect x="{bx}" y="{by}" width="{8 * sq}" height="{8 * sq}" fill="none" stroke="#5A5A6A" stroke-width="1"/>
  </g>
  <text x="140" y="52" font-family="'Courier New',Courier,monospace" font-weight="bold" font-size="15" fill="#FFFFFF">arcxl0 <tspan fill="#5A5A6A">·</tspan> <tspan fill="#00F0FF">chess.com</tspan></text>
  <text x="140" y="70" font-family="'Courier New',Courier,monospace" font-size="9" fill="#8A8A9A">daily games · mostly vs {esc(fav)}</text>
  <text x="140" y="92" xml:space="preserve" font-family="'Courier New',Courier,monospace" font-weight="bold" font-size="13"><tspan fill="#39FF14">W {w}</tspan><tspan fill="#8A8A9A"> · </tspan><tspan fill="#FF4040">L {l}</tspan><tspan fill="#8A8A9A"> · </tspan><tspan fill="#C0C0C0">D {d}</tspan><tspan fill="#8A8A9A">   streak </tspan><tspan fill="#FFD319">{streak}</tspan></text>
  <text x="140" y="110" font-family="'Courier New',Courier,monospace" font-size="9" fill="#8A8A9A">puzzles {puzzle if puzzle is not None else "-"} · last online {ago_txt} · {len(games)} game{'s' if len(games) != 1 else ''} tracked</text>
  <text x="836" y="118" font-size="56" fill="#F0F0FF">♞</text>
  <rect x="4" y="131" width="892" height="5" fill="#00F0FF" opacity="0.35"/>
</svg>
'''
open(OUT, "w").write(svg)
print(f"chess card written: W{w} L{l} D{d}, streak {streak}, puzzles {puzzle}, {len(games)} games")
