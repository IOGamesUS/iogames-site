#!/usr/bin/env python3
"""Find WordTangle candidates.
Usage: gen.py W H dirs seed count
dirs: 4 chars for top,right,bottom,left; f = forward (L->R or T->B), r = reversed.
Geometric strings: top/bottom read L->R, left/right read T->B.
Corners: top[0]=left[0], top[-1]=right[0], bottom[0]=left[-1], bottom[-1]=right[-1].
"""
import sys, random, re
from collections import defaultdict
from wordfreq import top_n_list

W, H, dirs, seed, count = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
N = int(sys.argv[6]) if len(sys.argv) > 6 else 7000
BAD = set("""""".split())
words = [w for w in top_n_list('en', N) if re.fullmatch(r'[a-z]+', w) and w not in BAD]
bylen = defaultdict(list)
for w in words:
    bylen[len(w)].append(w)

def geo(w, d):
    return w if d == 'f' else w[::-1]

# index geometric strings by (first,last)
def index(L, d):
    idx = defaultdict(list)
    for w in bylen[L]:
        g = geo(w, d)
        idx[(g[0], g[-1])].append((w, g))
    return idx

dt, dr, db, dl = dirs
I_top = bylen[W]
I_right = index(H, dr)
I_bottom = index(W, db)
I_left = index(H, dl)
rng = random.Random(seed)
out = set()
tops = I_top[:]
rng.shuffle(tops)
for t in tops:
    gt = geo(t, dt)
    lefts = [x for k, v in I_left.items() if k[0] == gt[0] for x in v]
    rights = [x for k, v in I_right.items() if k[0] == gt[-1] for x in v]
    rng.shuffle(lefts); rng.shuffle(rights)
    for lw, lg in lefts[:40]:
        for rw, rg in rights[:40]:
            if len({t, lw, rw}) < 3:
                continue
            bs = I_bottom.get((lg[-1], rg[-1]), [])
            bs = [b for b in bs if b[0] not in (t, lw, rw)]
            if bs:
                bw = rng.choice(bs)[0]
                out.add((t, rw, bw, lw))
                break
        if len(out) >= count:
            break
    if len(out) >= count:
        break
for q in sorted(out):
    print(f"top={q[0]} right={q[1]} bottom={q[2]} left={q[3]}")
