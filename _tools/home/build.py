#!/usr/bin/env python3
"""Builds iogames.us index.html with inline pixel-art SVGs (no external requests)."""
import sys, os

OUT = sys.argv[1]

G = {
'A':[".###.","#...#","#...#","#####","#...#","#...#","#...#"],
'B':["####.","#...#","#...#","####.","#...#","#...#","####."],
'C':[".####","#....","#....","#....","#....","#....",".####"],
'E':["#####","#....","#....","####.","#....","#....","#####"],
'F':["#####","#....","#....","####.","#....","#....","#...."],
'G':[".####","#....","#....","#.###","#...#","#...#",".###."],
'H':["#...#","#...#","#...#","#####","#...#","#...#","#...#"],
'I':["#####","..#..","..#..","..#..","..#..","..#..","#####"],
'K':["#...#","#..#.","#.#..","##...","#.#..","#..#.","#...#"],
'M':["#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#"],
'N':["#...#","##..#","#.#.#","#..##","#...#","#...#","#...#"],
'O':[".###.","#...#","#...#","#...#","#...#","#...#",".###."],
'P':["####.","#...#","#...#","####.","#....","#....","#...."],
'R':["####.","#...#","#...#","####.","#.#..","#..#.","#...#"],
'S':[".####","#....","#....",".###.","....#","....#","####."],
'T':["#####","..#..","..#..","..#..","..#..","..#..","..#.."],
'U':["#...#","#...#","#...#","#...#","#...#","#...#",".###."],
'Y':["#...#","#...#",".#.#.","..#..","..#..","..#..","..#.."],
'D':["####.","#...#","#...#","#...#","#...#","#...#","####."],
'L':["#....","#....","#....","#....","#....","#....","#####"],
'Z':["#####","....#","...#.","..#..",".#...","#....","#####"],
'W':["#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"],
' ':[".....",".....",".....",".....",".....",".....","....."],
}

def runs(rows, ox=0, oy=0):
    """Yield (x,y,w) horizontal runs of '#'."""
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x] == '#':
                s = x
                while x < len(row) and row[x] == '#':
                    x += 1
                yield (ox + s, oy + y, x - s)
            else:
                x += 1

def rects(rows, ox, oy, fill):
    return "".join(f'<rect x="{x}" y="{y}" width="{w}" height="1" fill="{fill}"/>' for x, y, w in runs(rows, ox, oy))

def word_svg(text, cls, fg, shadow, label):
    adv = 6
    width = len(text) * adv - 1 + 1
    parts = []
    for i, ch in enumerate(text):
        parts.append(rects(G[ch], i * adv + 1, 1, shadow))
    for i, ch in enumerate(text):
        parts.append(rects(G[ch], i * adv, 0, fg))
    return (f'<svg class="{cls}" viewBox="0 0 {width} 8" role="img" aria-label="{label}" '
            f'shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')

SUITS = {
 'heart':  ([".##.##.","#######","#######",".#####.","..###..","...#...","......."], "#e8604c"),
 'spade':  (["...#...","..###..",".#####.","#######","#######","..#.#..",".#####."], "#ece6d6"),
 'diamond':(["...#...","..###..",".#####.","#######",".#####.","..###..","...#..."], "#f2c14e"),
 'club':   (["..###..","..###..","##.#.##","#######","##.#.##","...#...","..###.."], "#5fbfb2"),
}
def suit_svg(name, cls="suit"):
    rows, col = SUITS[name]
    return (f'<svg class="{cls}" viewBox="0 0 7 7" aria-hidden="true" shape-rendering="crispEdges" '
            f'xmlns="http://www.w3.org/2000/svg">{rects(rows, 0, 0, col)}</svg>')

def scene_svg():
    W, H = 96, 54
    p = []
    R = lambda x, y, w, h, c: p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>')
    R(0, 0, W, H, "#14111f")
    # dungeon wall bricks
    for row in range(0, 30, 4):
        off = 0 if (row // 4) % 2 == 0 else 6
        for bx in range(-6 + off, W, 12):
            R(bx, row, 11, 3, "#1e1a2e")
    R(0, 30, W, 24, "#0f0d18")
    for fx in range(0, W, 8):
        R(fx, 30, 7, 1, "#231e35")
    # torches
    for tx in (12, 80):
        R(tx, 12, 2, 6, "#6b4a2b")
        R(tx - 1, 9, 4, 3, "#e8604c")
        R(tx, 8, 2, 2, "#f2c14e")
        R(tx, 7, 1, 1, "#fff1b8")
    # slime monster
    slime = [
        "......######......",
        "....##########....",
        "...############...",
        "..##############..",
        ".################.",
        ".################.",
        "##################",
        "##################",
        "##################",
        ".################.",
    ]
    sx, sy = 39, 14
    for x, y, w in runs(slime, sx, sy):
        R(x, y, w, 1, "#5fbfb2")
    R(sx + 3, sy + 2, 3, 1, "#a6eadf")
    R(sx + 4, sy + 4, 3, 3, "#ece6d6"); R(sx + 5, sy + 5, 2, 2, "#14111f")
    R(sx + 11, sy + 4, 3, 3, "#ece6d6"); R(sx + 11, sy + 5, 2, 2, "#14111f")
    R(sx + 7, sy + 7, 4, 1, "#2a6b63")
    R(sx, sy + 10, 18, 1, "#0a0812")
    # HP bar
    R(sx - 1, sy - 4, 20, 3, "#0a0812")
    R(sx, sy - 3, 13, 1, "#e8604c")
    R(sx + 13, sy - 3, 5, 1, "#3a2230")
    # hand of cards
    cards = [("heart", 22), ("heart", 33), ("heart", 44), ("spade", 55), ("diamond", 66)]
    for i, (suit, cx) in enumerate(cards):
        cy = 34 + (2 if i in (0, 4) else 0) - (2 if i in (1, 2, 3) and i < 3 else 0)
        lift = i < 3
        cy = 33 if lift else 36
        R(cx + 1, cy + 1, 9, 13, "#0a0812")
        R(cx, cy, 9, 13, "#ece6d6")
        R(cx, cy, 9, 1, "#fff8e6")
        rows, col = SUITS[suit]
        for x, y, w in runs(rows, cx + 1, cy + 3):
            R(x, y, w, 1, col if suit != "spade" else "#2a2540")
        if lift:
            R(cx, cy - 2, 9, 1, "#f2c14e")
    # meld label pixels (gold underline under the run)
    R(22, 48, 31, 1, "#f2c14e")
    return (f'<svg class="scene" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Rummycraft: a hand of cards with a three card meld raised, facing a slime in a torchlit dungeon" '
            f'shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">{"".join(p)}</svg>')

def favicon():
    rows, col = SUITS['diamond']
    body = rects(rows, 0.5, 0.5, col)
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8' shape-rendering='crispEdges'><rect width='8' height='8' fill='%2314111f'/>{body.replace(chr(34), chr(39)).replace('#', '%23')}</svg>"
    return "data:image/svg+xml," + svg

wordmark = word_svg("IO GAMES", "wordmark", "#f2c14e", "#7a4a1c", "IO Games")
h_rummy = word_svg("RUMMYCRAFT", "ph", "#ece6d6", "#3a3352", "Rummycraft")
h_hyper = word_svg("HYPERBREAKS", "ph", "#ece6d6", "#3a3352", "HyperBreaks")
h_daily = word_svg("DAILY PUZZLES", "ph", "#ece6d6", "#3a3352", "Daily puzzles")
h_contact = word_svg("CONTACT", "ph", "#ece6d6", "#3a3352", "Contact")
suits_row = "".join(suit_svg(s) for s in ("spade", "heart", "club", "diamond"))

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>IO Games</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="IO Games is an indie studio making card games. Play Rummycraft, a rummy roguelite, free in your browser.">
<meta name="theme-color" content="#14111f">
<meta property="og:title" content="IO Games">
<meta property="og:description" content="An indie studio making card games. Play Rummycraft, a rummy roguelite.">
<meta property="og:url" content="https://iogames.us/">
<meta property="og:type" content="website">
<link rel="icon" href="{favicon()}">
<style>
/* Layout: one narrow column, each section a framed dungeon panel, stacked top to bottom. */
:root {{
  --bg: #14111f;
  --panel: #1d1930;
  --edge: #3a3352;
  --ink: #ece6d6;
  --muted: #a59fb8;
  --gold: #f2c14e;
  --ember: #e8604c;
  --teal: #5fbfb2;
  --shadow: #0a0812;
  --body: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  color-scheme: dark;
}}
*, *::before, *::after {{ box-sizing: border-box; }}
html {{ background: var(--bg); }}
body {{
  margin: 0;
  background-color: var(--bg);
  background-image:
    linear-gradient(45deg, rgba(255,255,255,.018) 25%, transparent 25%, transparent 75%, rgba(255,255,255,.018) 75%),
    linear-gradient(45deg, rgba(255,255,255,.018) 25%, transparent 25%, transparent 75%, rgba(255,255,255,.018) 75%);
  background-size: 8px 8px;
  background-position: 0 0, 4px 4px;
  color: var(--ink);
  font: 16px/1.6 var(--body);
  -webkit-text-size-adjust: 100%;
}}
.wrap {{
  max-width: 640px;
  margin: 0 auto;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 40px 32px;
  display: grid;
  gap: 28px;
}}
svg {{ display: block; image-rendering: pixelated; }}
a {{ color: var(--gold); text-underline-offset: 3px; }}
a:focus-visible, .btn:focus-visible {{ outline: 3px solid var(--teal); outline-offset: 3px; }}

/* hero */
.hero {{ display: grid; gap: 14px; padding-block: 8px 4px; }}
.wordmark {{ width: min(100%, 360px); height: auto; }}
.tagline {{ margin: 0; font-size: 1.125rem; color: var(--ink); max-width: 34ch; }}
.suits {{ display: flex; gap: 10px; }}
.suit {{ width: 21px; height: 21px; }}

/* panels */
.panel {{
  background: var(--panel);
  border: 3px solid var(--edge);
  box-shadow: 6px 6px 0 var(--shadow);
  padding: 22px 18px;
  display: grid;
  gap: 16px;
  min-width: 0;
}}
.ph {{ height: 22px; width: auto; max-width: 100%; }}
.kicker {{
  margin: -6px 0 0;
  font: 600 .75rem/1.4 var(--mono);
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--teal);
}}
.panel p {{ margin: 0; max-width: 60ch; }}
.muted {{ color: var(--muted); font-size: .9375rem; }}

.shot {{
  border: 3px solid var(--shadow);
  background: var(--bg);
  max-width: 100%;
}}
.scene {{ width: 100%; height: auto; aspect-ratio: 16 / 9; }}

.modes {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }}
.modes li {{ display: grid; grid-template-columns: 14px 1fr; gap: 10px; align-items: baseline; }}
.modes li::before {{ content: ""; width: 8px; height: 8px; background: var(--gold); transform: translateY(-1px); }}
.modes b {{ color: var(--ink); }}

.actions {{ display: flex; flex-wrap: wrap; gap: 14px; }}
.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 10px 20px;
  font: 700 .9375rem/1 var(--mono);
  letter-spacing: .08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--shadow);
  background: var(--gold);
  border: 3px solid var(--shadow);
  box-shadow: inset -3px -3px 0 rgba(0,0,0,.25), inset 3px 3px 0 rgba(255,255,255,.35), 4px 4px 0 var(--shadow);
  transition: transform .08s steps(2), box-shadow .08s steps(2);
  flex: 1 1 160px;
}}
.btn:hover {{ transform: translate(-1px, -1px); box-shadow: inset -3px -3px 0 rgba(0,0,0,.25), inset 3px 3px 0 rgba(255,255,255,.35), 5px 5px 0 var(--shadow); }}
.btn:active {{ transform: translate(3px, 3px); box-shadow: inset -3px -3px 0 rgba(0,0,0,.25), inset 3px 3px 0 rgba(255,255,255,.35), 1px 1px 0 var(--shadow); }}
.btn.alt {{ background: var(--ink); }}
.btn.cool {{ background: var(--teal); }}

/* daily puzzles */
.daily {{ border-color: var(--gold); }}
.games {{
  display: flex;
  gap: 12px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 0;
  padding-bottom: 6px;
  margin-inline: -4px;
  padding-inline: 4px;
  scrollbar-width: none;
}}
.games::-webkit-scrollbar {{ display: none; }}
.game {{
  flex: 0 0 86%;
  scroll-snap-align: start;
  display: grid;
  grid-template-rows: auto 1fr auto;
  gap: 14px;
  padding: 16px;
  background: var(--bg);
  border: 3px solid var(--edge);
  color: var(--ink);
  text-decoration: none;
  min-width: 0;
}}
.game:hover {{ border-color: var(--teal); }}
.game:hover .btn {{ transform: translate(-1px, -1px); }}
.mini {{ display: grid; grid-template-columns: repeat(5, 14px); grid-auto-rows: 14px; gap: 3px; height: 65px; align-content: center; }}
.mini.row {{ display: flex; align-items: center; gap: 4px; }}
.mini i {{ width: 14px; height: 14px; display: grid; place-items: center; background: var(--cell, #262040); border: 2px solid var(--edge); font: 700 8px/1 var(--mono); font-style: normal; color: var(--ink); }}
.mini i.v {{ background: none; border-color: transparent; }}
.mini i.c {{ background: var(--teal); border-color: var(--teal); }}
.mini i.g {{ color: var(--gold); }}
.mini b {{ font: 700 1.125rem/1 var(--mono); color: var(--ink); padding-inline: 2px; }}
.mini u {{ width: 24px; height: 28px; display: grid; place-items: center; text-decoration: none; background: var(--cell, #262040); border: 2px dashed var(--edge); font: 700 1rem/1 var(--mono); color: var(--gold); }}
.mini u.f {{ border-style: solid; }}
.mini u.c {{ border: 2px solid var(--teal); }}
.gi {{ display: grid; gap: 4px; align-content: start; min-width: 0; }}
.gname {{ font: 700 1.0625rem/1.2 var(--mono); letter-spacing: .04em; color: var(--gold); }}
.gdesc {{ font-size: .9375rem; line-height: 1.45; }}
.gmeta {{ font: .75rem/1.4 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }}
.game .btn {{ flex: none; width: 100%; }}
.game.soon {{ border-style: dashed; place-content: center; text-align: center; font: .875rem/1.5 var(--mono); color: var(--muted); grid-template-rows: none; }}
.dots {{ display: flex; justify-content: center; gap: 8px; }}
.dots button {{ width: 12px; height: 12px; padding: 0; border: 2px solid var(--edge); background: transparent; cursor: pointer; }}
.dots button[aria-current="true"] {{ background: var(--gold); border-color: var(--gold); }}
@media (min-width: 560px) {{
  .game {{ flex-basis: calc(50% - 6px); }}
}}
.links {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }}
.links li {{ display: grid; grid-template-columns: 92px 1fr; gap: 12px; align-items: baseline; min-width: 0; }}
.links .k {{ font: 600 .75rem/1.4 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }}
.links a {{ overflow-wrap: anywhere; }}

footer {{
  font: .8125rem/1.5 var(--mono);
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  padding-top: 4px;
}}

@media (min-width: 640px) {{
  .wrap {{ padding-block: 64px 40px; gap: 32px; }}
  .panel {{ padding: 28px 28px; }}
  .ph {{ height: 26px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  .btn {{ transition: none; }}
}}
</style>
</head>
<body>
<main class="wrap">

  <header class="hero">
    <h1 style="margin:0">{wordmark}</h1>
    <p class="tagline">An indie studio making card games and daily puzzles.</p>
    <a class="btn" style="justify-self:start;flex:none" href="#daily">Play today&#39;s puzzles</a>
    <div class="suits">{suits_row}</div>
  </header>

  <section class="panel daily" aria-labelledby="daily">
    <h2 id="daily" style="margin:0">{h_daily}</h2>
    <p class="kicker">New puzzles every day</p>
    <p>Quick puzzles from IO Games. Everyone gets the same puzzle, it takes a couple of minutes, and you can share your score with friends.</p>
    <div class="games" id="games" aria-label="Daily puzzles, swipe for more">
      <a class="game" href="/wordtangle/">
        <div class="mini" aria-hidden="true"><i class="g">T</i><i class="g">A</i><i class="g">N</i><i class="g">G</i><i class="g">L</i><i></i><i class="v"></i><i class="v"></i><i class="v"></i><i class="c"></i><i></i><i class="v"></i><i class="v"></i><i class="v"></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div class="gi">
          <span class="gname">WordTangle</span>
          <span class="gdesc">Four clues, four words, one rectangle. The words share their corner letters.</span>
          <span class="gmeta">Word puzzle &middot; about 2 minutes</span>
        </div>
        <span class="btn">Play WordTangle</span>
      </a>
      <a class="game" href="/pemdash/">
        <div class="mini row" aria-hidden="true"><b>8</b><u class="f">&divide;</u><b>4</b><u class="c"></u><b>2</b></div>
        <div class="gi">
          <span class="gname">Pemdash</span>
          <span class="gdesc">A row of numbers and a handful of signs. Put the signs in the gaps to make the math true.</span>
          <span class="gmeta">Number puzzle &middot; about 2 minutes</span>
        </div>
        <span class="btn cool">Play Pemdash</span>
      </a>
      <div class="game soon">More daily puzzles<br>are on the way.</div>
    </div>
    <div class="dots" id="dots" role="group" aria-label="Choose a puzzle"></div>
  </section>

  <section class="panel" aria-labelledby="rummycraft">
    <h2 id="rummycraft" style="margin:0">{h_rummy}</h2>
    <p class="kicker">Rummy roguelite</p>
    <div class="shot">{scene_svg()}</div>
    <p>Meld runs, sets and flushes to fight your way through a dungeon full of monsters. Every hand is an attack, so build it well.</p>
    <ul class="modes">
      <li><span><b>Campaign:</b> work through the dungeon floor by floor.</span></li>
      <li><span><b>The Delve:</b> go as deep as your deck can carry you.</span></li>
      <li><span><b>Daily Delve:</b> one shared run each day that everyone plays.</span></li>
    </ul>
    <div class="actions">
      <a class="btn" href="https://play.iogames.us">Play now</a>
      <a class="btn alt" href="https://iogamesus.itch.io/rummycraft">itch.io</a>
    </div>
    <p class="muted">On a phone? Rummycraft plays best right in your browser at <a href="https://play.iogames.us">play.iogames.us</a>.</p>
  </section>

  <section class="panel" aria-labelledby="hyperbreaks">
    <h2 id="hyperbreaks" style="margin:0">{h_hyper}</h2>
    <p class="kicker">Live card breaks</p>
    <p>Live trading card breaks, streamed on Whatnot. Grab a spot and rip packs with us.</p>
    <div class="actions">
      <a class="btn cool" href="https://www.whatnot.com/user/hyperbreaks">Whatnot shop</a>
      <a class="btn alt" href="https://www.instagram.com/hyper.breaks/">Instagram</a>
    </div>
  </section>

  <section class="panel" aria-labelledby="contact">
    <h2 id="contact" style="margin:0">{h_contact}</h2>
    <ul class="links">
      <li><span class="k">Email</span><a href="mailto:ian@iogames.us">ian@iogames.us</a></li>
      <li><span class="k">Instagram</span><a href="https://www.instagram.com/iogames.us/">@iogames.us</a></li>
    </ul>
  </section>

  <footer>
    <span>&copy; 2026 IO Games</span>
    <span>No trackers. No cookies.</span>
  </footer>

</main>
<script>
(function () {{
  var row = document.getElementById("games"), dots = document.getElementById("dots");
  if (!row || !dots) return;
  var cards = row.children;
  for (var i = 0; i < cards.length; i++) {{
    var b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", "Show card " + (i + 1));
    (function (n) {{ b.addEventListener("click", function () {{ row.scrollTo({{ left: cards[n].offsetLeft - row.offsetLeft - 4, behavior: "smooth" }}); }}); }})(i);
    dots.appendChild(b);
  }}
  function mark() {{
    var best = 0, d = Infinity;
    for (var i = 0; i < cards.length; i++) {{
      var x = Math.abs(cards[i].offsetLeft - row.offsetLeft - 4 - row.scrollLeft);
      if (x < d) {{ d = x; best = i; }}
    }}
    if (row.scrollLeft + row.clientWidth >= row.scrollWidth - 4) best = cards.length - 1;
    for (var j = 0; j < dots.children.length; j++) dots.children[j].setAttribute("aria-current", j === best ? "true" : "false");
  }}
  row.addEventListener("scroll", function () {{ window.requestAnimationFrame(mark); }}, {{ passive: true }});
  mark();
}})();
</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("wrote", OUT, len(html), "bytes")
