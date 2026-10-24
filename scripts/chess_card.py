#!/usr/bin/env python3
# y2k chess card for arcxl0 (chess.com) -> img/y2k-chess.svg (win95 window style)
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
fav = esc(opp_counter.most_common(1)[0][0]) if opp_counter else "-"

# win95 window: 1px #FFFFFF top/left, 1px #404040 bottom/right, #000080 titlebar
SANS = "MS Sans Serif,Verdana,sans-serif"
MONO = "'Courier New',Courier,monospace"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="140" viewBox="0 0 900 140" role="img" aria-label="CHESS.EXE - arcxl0 on chess.com, Win95 style">
  <rect width="900" height="140" fill="#C0C0C0"/>
  <rect x="0" y="0" width="900" height="1" fill="#FFFFFF"/>
  <rect x="0" y="0" width="1" height="140" fill="#FFFFFF"/>
  <rect x="0" y="139" width="900" height="1" fill="#404040"/>
  <rect x="899" y="0" width="1" height="140" fill="#404040"/>
  <rect x="1" y="1" width="898" height="18" fill="#000080"/>
  <text x="5" y="13" font-family="{SANS}" font-weight="bold" font-size="11" fill="#FFFFFF">CHESS.EXE</text>
  <rect x="846" y="3" width="16" height="14" fill="#C0C0C0"/>
  <rect x="846" y="3" width="16" height="1" fill="#FFFFFF"/>
  <rect x="846" y="3" width="1" height="14" fill="#FFFFFF"/>
  <rect x="846" y="16" width="16" height="1" fill="#404040"/>
  <rect x="861" y="3" width="1" height="14" fill="#404040"/>
  <rect x="850" y="12" width="6" height="2" fill="#000000"/>
  <rect x="864" y="3" width="16" height="14" fill="#C0C0C0"/>
  <rect x="864" y="3" width="16" height="1" fill="#FFFFFF"/>
  <rect x="864" y="3" width="1" height="14" fill="#FFFFFF"/>
  <rect x="864" y="16" width="16" height="1" fill="#404040"/>
  <rect x="879" y="3" width="1" height="14" fill="#404040"/>
  <rect x="869" y="7" width="7" height="6" fill="none" stroke="#000000" stroke-width="1"/>
  <rect x="869" y="7" width="7" height="2" fill="#000000"/>
  <rect x="882" y="3" width="16" height="14" fill="#C0C0C0"/>
  <rect x="882" y="3" width="16" height="1" fill="#FFFFFF"/>
  <rect x="882" y="3" width="1" height="14" fill="#FFFFFF"/>
  <rect x="882" y="16" width="16" height="1" fill="#404040"/>
  <rect x="897" y="3" width="1" height="14" fill="#404040"/>
  <path d="M886.5,6.5 L893.5,13.5 M893.5,6.5 L886.5,13.5" stroke="#000000" stroke-width="2"/>
  <g>
'''
# 8x8 board in a sunken panel
sq = 9
bx, by = 16, 31
for row in range(8):
    for col in range(8):
        fill = "#FFFFFF" if (row + col) % 2 == 0 else "#A8A8B0"
        svg += f'  <rect x="{bx + col * sq}" y="{by + row * sq}" width="{sq}" height="{sq}" fill="{fill}"/>\n'
# decorative opening position pieces
pieces = {(7, 4): ("♙", "#FFFFFF", "#404040"), (6, 4): ("♟", "#101010", "none"),
          (5, 4): ("♘", "#FFFFFF", "#404040"), (1, 3): ("♞", "#101010", "none")}
for (row, col), (glyph, fill, stroke) in pieces.items():
    extra = f' stroke="{stroke}" stroke-width="0.4"' if stroke != "none" else ""
    svg += f'  <text x="{bx + col * sq + 1}" y="{by + row * sq + 8}" font-size="8.5"{extra} fill="{fill}">{glyph}</text>\n'
svg += f'''  <rect x="{bx}" y="{by}" width="{8 * sq}" height="{8 * sq}" fill="none" stroke="#404040" stroke-width="1"/>
  <rect x="8" y="23" width="88" height="88" fill="none" stroke="#FFFFFF" stroke-width="1" transform="translate(1,1)"/>
  </g>
  <rect x="104" y="23" width="788" height="88" fill="#FFFFFF"/>
  <rect x="104" y="23" width="788" height="1" fill="#808080"/>
  <rect x="104" y="23" width="1" height="88" fill="#808080"/>
  <rect x="104" y="110" width="788" height="1" fill="#DFDFDF"/>
  <rect x="891" y="23" width="1" height="88" fill="#DFDFDF"/>
  <text x="118" y="46" font-family="{SANS}" font-weight="bold" font-size="13" fill="#000000">arcxl0 <tspan fill="#000080">· chess.com</tspan></text>
  <text x="118" y="68" xml:space="preserve" font-family="{SANS}" font-weight="bold" font-size="13" fill="#000000"><tspan fill="#008000">W {w}</tspan><tspan fill="#808080"> · </tspan><tspan fill="#800000">L {l}</tspan><tspan fill="#808080"> · </tspan><tspan fill="#000080">D {d}</tspan><tspan fill="#404040">   streak {streak}</tspan></text>
  <text x="118" y="88" font-family="{MONO}" font-size="9" fill="#404040">daily games · mostly vs {fav} · puzzles {puzzle if puzzle is not None else "-"} · last online {ago_txt}</text>
  <text x="118" y="102" font-family="{MONO}" font-size="9" fill="#808080">{len(games)} games tracked · data from the chess.com public api</text>
  <rect x="8" y="119" width="190" height="15" fill="#C0C0C0"/>
  <rect x="8" y="119" width="190" height="1" fill="#808080"/>
  <rect x="8" y="119" width="1" height="15" fill="#808080"/>
  <rect x="8" y="133" width="190" height="1" fill="#FFFFFF"/>
  <rect x="197" y="119" width="1" height="15" fill="#FFFFFF"/>
  <text x="14" y="130" font-family="{SANS}" font-size="10" fill="#000000">chess.com public api</text>
  <rect x="202" y="119" width="110" height="15" fill="#C0C0C0"/>
  <rect x="202" y="119" width="110" height="1" fill="#808080"/>
  <rect x="202" y="119" width="1" height="15" fill="#808080"/>
  <rect x="202" y="133" width="110" height="1" fill="#FFFFFF"/>
  <rect x="311" y="119" width="1" height="15" fill="#FFFFFF"/>
  <text x="208" y="130" font-family="{SANS}" font-size="10" fill="#000000">player: arcxl0</text>
  <rect x="316" y="119" width="540" height="15" fill="#C0C0C0"/>
  <rect x="316" y="119" width="540" height="1" fill="#808080"/>
  <rect x="316" y="119" width="1" height="15" fill="#808080"/>
  <rect x="316" y="133" width="540" height="1" fill="#FFFFFF"/>
  <rect x="855" y="119" width="1" height="15" fill="#FFFFFF"/>
  <text x="322" y="130" font-family="{SANS}" font-size="10" fill="#000000">games tracked: {len(games)} · updated daily</text>
  <path d="M880 132 l7 -7 M884 132 l7 -7 M888 132 l7 -7 M892 132 l7 -7" stroke="#808080" stroke-width="1"/>
  <path d="M880 133 l7 -7 M884 133 l7 -7 M888 133 l7 -7 M892 133 l7 -7" stroke="#FFFFFF" stroke-width="1"/>
</svg>
'''
open(OUT, "w").write(svg)
print(f"chess card written: W{w} L{l} D{d}, streak {streak}, puzzles {puzzle}, {len(games)} games")
