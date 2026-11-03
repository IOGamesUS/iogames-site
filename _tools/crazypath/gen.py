#!/usr/bin/env python3
"""Crazy Path puzzle generator.
A grid of face-up cards. Draw one path through every card, stepping up, down, left or right,
where each step matches the previous card's suit or rank (the Crazy Eights rule).
Keeps grids with exactly one such path (a path and its reverse count as the same path)."""
import random, json, sys

SUITS = "SHDC"

def neighbors(R, C, i):
    r, c = divmod(i, C)
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < R and 0 <= cc < C:
            yield rr * C + cc

def match(a, b):
    return a[0] == b[0] or a[1] == b[1]

def count_paths(R, C, cards, limit=3):
    """Number of directed Hamiltonian paths through the match graph, stopping at limit."""
    n = R * C
    adj = [[j for j in neighbors(R, C, i) if match(cards[i], cards[j])] for i in range(n)]
    if any(not a for a in adj):
        return 0
    found = [0]
    seen = [False] * n
    def go(i, depth):
        if found[0] >= limit:
            return
        if depth == n:
            found[0] += 1
            return
        for j in adj[i]:
            if not seen[j]:
                seen[j] = True
                go(j, depth + 1)
                seen[j] = False
    for s in range(n):
        seen[s] = True
        go(s, 1)
        seen[s] = False
        if found[0] >= limit:
            break
    return found[0]

def random_ham_path(R, C, rng):
    n = R * C
    for _ in range(2000):
        start = rng.randrange(n)
        path = [start]; seen = {start}
        while len(path) < n:
            opts = [j for j in neighbors(R, C, path[-1]) if j not in seen]
            if not opts:
                break
            # Warnsdorff: prefer cells with fewer onward options, random tie-break
            opts.sort(key=lambda j: (sum(1 for k in neighbors(R, C, j) if k not in seen), rng.random()))
            nxt = opts[0] if rng.random() < 0.85 else rng.choice(opts)
            path.append(nxt); seen.add(nxt)
        if len(path) == n:
            return path
    return None

def make(rng, R, C, min_decoys):
    n = R * C
    for _ in range(6000):
        path = random_ham_path(R, C, rng)
        if not path:
            continue
        deck = [(r, s) for r in range(1, 14) for s in SUITS]
        used = set()
        cur = rng.choice(deck)
        seq = [cur]; used.add(cur)
        ok = True
        for _ in range(n - 1):
            opts = [c for c in deck if c not in used and match(c, cur)]
            if not opts:
                ok = False; break
            # favour suit changes through shared ranks now and then so paths cross suits
            cur = rng.choice(opts)
            seq.append(cur); used.add(cur)
        if not ok:
            continue
        cards = [None] * n
        for i, cell in enumerate(path):
            cards[cell] = seq[i]
        # decoys: matching neighbours that are not consecutive on the path
        pos = {cell: i for i, cell in enumerate(path)}
        decoys = 0
        for i in range(n):
            for j in neighbors(R, C, i):
                if i < j and match(cards[i], cards[j]) and abs(pos[i] - pos[j]) != 1:
                    decoys += 1
        if decoys < min_decoys:
            continue
        if count_paths(R, C, cards) == 2:
            return {"rows": R, "cols": C, "cards": [r * 10 + SUITS.index(s) for r, s in cards], "path": path, "decoys": decoys}
    return None

if __name__ == "__main__":
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    for R, C, d in [(4, 4, 3), (5, 4, 5), (5, 5, 7)]:
        p = make(rng, R, C, d)
        print(json.dumps(p) if p else "none", flush=True)
