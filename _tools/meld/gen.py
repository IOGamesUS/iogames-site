#!/usr/bin/env python3
"""Meld puzzle generator.
A hand of cards from one deck must be split into rummy melds using every card:
  set = 3 or 4 cards of the same rank (all different suits)
  run = 3 or more cards of one suit in a row (ace is high or low: A 2 3 or Q K A, no wrapping)
Keeps hands with exactly one way to split them and enough decoy melds to make it a puzzle."""
import random, json, sys
from itertools import combinations

SUITS = "SHDC"

def legal_melds(cards):
    """All legal melds (as frozensets of card indices) in the hand."""
    out = set()
    byrank, bysuit = {}, {}
    for i, (r, s) in enumerate(cards):
        byrank.setdefault(r, []).append(i)
        bysuit.setdefault(s, {})[r] = i
    for r, idx in byrank.items():
        for k in (3, 4):
            for combo in combinations(idx, k):
                out.add(frozenset(combo))
    for s, ranks in bysuit.items():
        hi = dict(ranks)
        if 1 in ranks:
            hi[14] = ranks[1]  # ace can also sit above the king (Q K A), but runs never wrap (K A 2)
        for start in range(1, 15):
            run = []
            r = start
            while r in hi and not (r == 14 and start == 1):
                run.append(hi[r])
                if len(run) >= 3:
                    out.add(frozenset(run))
                r += 1
    return out

def solutions(cards, limit=2):
    melds = legal_melds(cards)
    by_card = {}
    for m in melds:
        for c in m:
            by_card.setdefault(c, []).append(m)
    n = len(cards)
    found = []
    def go(used, chosen):
        if len(found) >= limit:
            return
        free = next((i for i in range(n) if i not in used), None)
        if free is None:
            found.append(list(chosen)); return
        for m in by_card.get(free, []):
            if m & used:
                continue
            chosen.append(m); go(used | m, chosen); chosen.pop()
    go(frozenset(), [])
    return found, len(melds)

def make(rng, n_melds, min_decoys):
    for _ in range(20000):
        deck = [(r, s) for r in range(1, 14) for s in SUITS]
        used = set(); hand = []; plan = []
        ok = True
        for _ in range(n_melds):
            if rng.random() < 0.5:
                # run
                s = rng.choice(SUITS); L = rng.choice([3, 3, 4, 4, 5]); start = rng.randint(1, 15 - L)
                m = [((r - 1) % 13 + 1, s) for r in range(start, start + L)]
            else:
                r = rng.randint(1, 13); k = rng.choice([3, 3, 4])
                m = [(r, s) for s in rng.sample(SUITS, k)]
            if any(c in used for c in m):
                ok = False; break
            used.update(m); hand.extend(m); plan.append(m)
        if not ok:
            continue
        rng.shuffle(hand)
        sols, nm = solutions(hand)
        if len(sols) == 1 and nm - n_melds >= min_decoys:
            sol = [sorted(m) for m in sols[0]]
            return {"cards": [r_s[0] * 10 + "SHDC".index(r_s[1]) for r_s in hand], "melds": len(sol), "sol": [[hand.index(hand[i]) for i in sorted(m)] for m in sols[0]], "decoys": nm - n_melds}
    return None

if __name__ == "__main__":
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    for nm, dec in [(4, 2), (4, 4), (5, 4), (5, 6)]:
        print(json.dumps(make(rng, nm, dec)))
