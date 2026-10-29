#!/usr/bin/env python3
"""Pemdaze puzzle generator.
A puzzle is a row of numbers plus an unordered pool of signs (+ - * / and exactly one =).
Rules: normal precedence, = anywhere (one), any true placement counts, division must be exact
and no step may go negative (the generator also requires this of every solution it counts).
Keeps puzzles with exactly one valid placement."""
import random, json, sys
from fractions import Fraction
from itertools import permutations

OPS = "+-*/"

def eval_side(nums, ops):
    """Evaluate with precedence; return int or None if a step is fractional or negative."""
    # first pass: * and /
    vals = [nums[0]]
    pend = []
    for o, n in zip(ops, nums[1:]):
        if o == '*':
            vals[-1] = vals[-1] * n
        elif o == '/':
            if n == 0 or vals[-1] % n:
                return None
            vals[-1] = vals[-1] // n
        else:
            pend.append(o); vals.append(n)
    acc = vals[0]
    for o, v in zip(pend, vals[1:]):
        acc = acc + v if o == '+' else acc - v
        if acc < 0:
            return None
    return acc

def true_eq(nums, ops):
    if ops.count('=') != 1:
        return False
    i = ops.index('=')
    l = eval_side(nums[:i + 1], ops[:i])
    r = eval_side(nums[i + 1:], ops[i + 1:])
    return l is not None and r is not None and l == r

def solutions(nums, pool):
    return {p for p in set(permutations(pool)) if true_eq(nums, p)}

def make(rng, n_nums, maxn):
    for _ in range(4000):
        k = n_nums - 1
        eq = rng.randrange(k)  # slot index of =
        ops = [rng.choice(OPS) for _ in range(k)]
        ops[eq] = '='
        # build left side numbers, then set the last number on the right so it balances
        nums = [rng.randint(1, maxn) for _ in range(n_nums)]
        # make divisions exact: choose divisor first, adjust dividend
        for j, o in enumerate(ops):
            if o == '/':
                nums[j + 1] = rng.randint(2, 9)
                nums[j] = nums[j + 1] * rng.randint(1, max(1, maxn // nums[j + 1]))
        l = eval_side(nums[:eq + 1], ops[:eq])
        if l is None:
            continue
        # right side: try every value for its last number in range to balance
        right_nums = nums[eq + 1:]
        right_ops = ops[eq + 1:]
        ok = False
        for v in list(range(1, 100)):
            right_nums[-1] = v
            r = eval_side(right_nums, right_ops)
            if r == l:
                ok = True; break
        if not ok:
            continue
        nums = nums[:eq + 1] + right_nums
        if any(x > 99 for x in nums):
            continue
        pool = sorted(ops)
        sols = solutions(nums, pool)
        if len(sols) == 1 and tuple(ops) in sols:
            return {'nums': nums, 'pool': pool, 'sol': ops}
    return None

if __name__ == '__main__':
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    plan = [(3, 12), (4, 12), (4, 15), (5, 12), (5, 20), (6, 15), (6, 20), (7, 20), (8, 20)]
    out = []
    for n, mx in plan:
        p = make(rng, n, mx)
        if p:
            out.append(p)
    for p in out:
        print(json.dumps(p))
