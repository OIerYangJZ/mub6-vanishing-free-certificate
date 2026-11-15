#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Jinze Yang.
# This file is a modified version of the verifier printed in Appendix A of OpenAI, "Exact Fourier certificates for
# complex Hadamard matrices of order six" (2026), distributed at https://github.com/openai/math under the Apache
# License 2.0. Changes made: the alpha-vanishing input is removed; the single-matrix identity (10) and Prop. 5.2 are
# not used; no priority lists; new certificate data are read from a JSON file; exact positive definiteness test p > 0;
# unknown keys are kept as free symbols; refusal to run under -O and an explicit final check; code reorganised with a
# dimension parameter D (fixed to 6 here). See the docstring below and the accompanying note.
"""Exact verification: no seven mutually unbiased bases in C^6, hence N(6) <= 5,
WITHOUT the Fourier-vanishing input (27) and without the cubic (Tao) exclusion.

Framework: OpenAI, "Exact Fourier certificates for complex Hadamard matrices of order six" (2026), Secs. 3, 5, 6, 7.
Relative to that paper's verifier, this program
  * never sets a moment to zero because a charge is a permutation of alpha = (1,1,1,-1,-1,-1)
    (only order-one charges vanish, by orthogonality, Lemma 6.2(ii) first half);
  * does not use the single-matrix identity (10) nor Proposition 5.2;
  * uses the same six test-function lists ws, with new positive definite integer matrices Z.
All arithmetic that certifies anything is integer or rational.  Standard library only.
Run:  python3 verify_d6.py cert_d6_data.json
"""
import sys, json, itertools, hashlib
from functools import lru_cache
from fractions import Fraction as Q
from math import gcd
from collections import Counter

D = 6
VANISH = False
ALPHA = (1, 1, 1, -1, -1, -1)
_CACHED = []


def memo(f):
    g = lru_cache(None)(f)
    _CACHED.append(g)
    return g


def memo1(f):
    g = lru_cache(200000)(f)
    _CACHED.append(g)
    return g


Epair = None
rows0 = {}
MISSES = Counter()

# ---------------------------------------------------------------- basic vector ops
def tr(A):
    return tuple(zip(*A))


def neg(a):
    return tuple(-x for x in a)


def opposite(A):
    return tuple(map(neg, A))


def plus(a, b):
    return tuple(x + y for x, y in zip(a, b))


def order(a):
    return sum(x for x in a if x > 0)


def wt(L):
    return sum(map(order, L))


def basic(A):
    return tuple(sorted(a for a in A if any(a)))


@memo
def perms(m):
    return tuple(itertools.permutations(range(m)))


def perm(a, p):
    return tuple(a[i] for i in p)


@memo
def pp(c):
    s = tuple(sorted(c))
    return tuple(p for p in perms(len(c)) if perm(c, p) == s)


def canon1(A):
    B = tr(A)
    c = tuple(map(order, B))
    C = tuple(sorted(c))
    return C, min(tuple(sorted(tr(perm(B, p)))) for p in pp(c))


@memo1
def canonpair(A):
    A = basic(tr(basic(tr(A))))
    if not A:
        return ()
    B = tr(A)
    L = []
    for C in (A, opposite(A), B, opposite(B)):
        if len(C) >= len(C[0]):
            L.append(canon1(C))
    return min(L)[1]


@memo
def parts(k, n, lo, hi):
    if not n:
        return ((),) if k == 0 else ()
    return tuple((i,) + L for i in range(lo, min(k // n, hi) + 1) for L in parts(k - i, n - 1, i, hi))


@memo
def comps(k, n, cap):
    if not n:
        return ((),) if k == 0 else ()
    return tuple((i,) + L for i in range(max(0, k - sum(cap[1:])), min(k, cap[0]) + 1)
                 for L in comps(k - i, n - 1, cap[1:]))


def vecs(k, n):
    for u in comps(k, n, (k,) * n):
        for v in comps(k, n, tuple(k * (i == 0) for i in u)):
            yield plus(u, neg(v))


def add(d, g, s=1):
    for a, x in g.items():
        v = x * s + d.get(a, 0)
        if v:
            d[a] = v
        elif a in d:
            del d[a]


def lin(g, F):
    r = {}
    for a, x in g.items():
        add(r, F(a), x)
    return r


# ---------------------------------------------------------------- single-matrix (pair) moments
def expand_degree1(B, i):
    a = B[i]
    C = B[:i] + B[i + 1:]
    v = {}
    for j, b in enumerate(C):
        add(v, evpair(canonpair(C[:j] + (plus(a, b),) + C[j + 1:])))
    return v


@memo
def evpair(A):
    for B in (A, tr(A)):
        assert len(B) <= D and not any(map(sum, B))
    for B in (A, tr(A)):
        for i, a in enumerate(B):
            if order(a) == 1:
                r = {}
                add(r, expand_degree1(B, i), -Q(1, D + 1 - len(B)))
                return r
    return {A: 1}


def allAB(r, c, output):
    """Enumerate (D+1)-row balanced exponent matrices with row orders r, column orders c."""
    m = len(c)
    seen = set()
    R = D + 1

    @lru_cache(200000)
    def steps(i, s, t, key):
        if i == R:
            return ()
        k = r[i]
        rest = sum(r[i + 1:])
        w = []
        for u in comps(k, m, s):
            ss = plus(s, neg(u))
            for v in comps(k, m, tuple(j if h == 0 else 0 for h, j in zip(u, t))):
                a = plus(u, neg(v))
                if a < key:
                    continue
                tt = plus(t, neg(v))
                if max(plus(ss, tt)) > rest:
                    continue
                st = (i + 1, ss, tt, a if i + 1 < R and r[i + 1] == k else ())
                if i == R - 1 or steps(*st):
                    w.append((st, a))
        return w

    def visit(state, A):
        for st, a in steps(*state):
            C = A + (a,)
            if len(C) < R:
                visit(st, C)
            else:
                B = canonpair(C)
                if B not in seen:
                    seen.add(B)
                    output(C)
    visit((0, c, c, ()), ())


def lcm(a, b):
    return a * (b // gcd(a, b))


def intscale(s):
    d = 1
    for a in s.values():
        d = lcm(d, a.denominator)
    return d, {i: (d // a.denominator) * a.numerator for i, a in s.items()}


def inv(a, p):
    return pow(a, -1, p)


def minusmod(s, t, b, p):
    for i, z in t.items():
        h = (s.get(i, 0) - z * b) % p
        if h:
            s[i] = h
        elif i in s:
            del s[i]


def echelon(E, p):
    rel = {}
    wit = []
    for vec in E:
        s = {i: x % p for i, x in vec.items() if x % p}
        while s:
            k = max(s)
            b = s[k]
            if k not in rel:
                b = inv(b, p)
                rel[k] = {i: z * b % p for i, z in s.items()}
                wit.append(vec)
                break
            minusmod(s, rel[k], b, p)
    for k in sorted(rel):
        s = rel[k]
        for i, z in list(s.items()):
            if i != k and i in rel:
                minusmod(s, rel[i], z, p)
    return rel, wit


def rat(z, T):
    M = T
    w = z
    u, v = 0, 1
    while w * w > T // 2:
        M, w, u, v = w, M % w, v, u - M // w * v
    return Q(w, v)


def eliminate(rows, keys=None, verbose=True):
    """Exact substitution rules from linear relations (modular echelon + CRT + rational
    reconstruction, then exact verification of every relation) -- Lemma 7.1."""
    E0 = []
    for row in rows:
        g = intscale(row)[1]
        if g:
            E0.append(g)
    p = 1000000007
    if keys is None:
        keys = sorted(set(k for g in E0 for k in g))
    num = {k: i for i, k in enumerate(keys)}
    assert len(num) == len(keys)
    E = [{num[a]: x for a, x in g.items()} for g in E0]
    R, small = echelon(E, p)
    M = p
    proj = {}
    for q in (1000000009, 998244353, 1000003, 2013265921, 754974721, 32452843, 86028121):
        if proj:
            break
        S, _ = echelon(small, q)
        if R.keys() != S.keys():
            continue
        iq = inv(M, q)

        def combine(x, y):
            return x + ((y - x) * iq % q) * M
        for k, v in list(R.items()):
            u = S[k]
            R[k] = {i: combine(v.get(i, 0), u.get(i, 0)) for i in v.keys() | u.keys()}
        M *= q
        rel = []
        for i, k in enumerate(keys):
            if i in R:
                f = {j: -rat(z, M) for j, z in R[i].items() if j != i}
                if max((max(abs(x.numerator), x.denominator) for x in f.values()), default=0) ** 2 > M // 200:
                    proj = {}
                    break
            else:
                f = {i: 1}
            proj[k] = {keys[j]: x for j, x in f.items()}
            rel.append(intscale(f))
    assert proj and len(proj) == len(keys) and len(R) == len(small)
    for g in small:
        m = 1
        for i in g:
            m = lcm(m, rel[i][0])
        s = {}
        for i, x in g.items():
            d, f = rel[i]
            add(s, f, (m // d) * x)
        assert not s
    if verbose:
        print("rank table:", len(E0), len(keys), len(R), flush=True)
    return proj


def pair_rows(kmin, kmax, ncol_max=4):
    """Relations (6) from formal (D+1)-row exponent matrices, total order kmin..kmax."""
    rows = []

    def out(A):
        assert order(A[0]) == 1 and len(A) == D + 1
        assert not any(map(sum, A)) and not any(map(sum, tr(A)))
        rows.append(expand_degree1(A, 0))
    for k in range(kmin, kmax + 1):
        for n in range(2, min(ncol_max, k // 2) + 1):
            for c in parts(k, n, 2, k // 2):
                for r in parts(k, D + 1, 1, k // 2):
                    allAB(r, c, out)
    return rows


def pairtable(kmax=11, ncol_max=4, I=None):
    global Epair
    rows = pair_rows(D + 1, kmax, ncol_max)
    keys = sorted(set(k for g in rows for k in g), key=lambda A: (wt(A), A))
    if I is not None:
        keys = [keys[i] for i in I] + [k for i, k in enumerate(keys) if i not in I]
    Epair = eliminate(rows, keys)
    return Epair


@memo
def partition(n):
    if not n:
        return ((),)
    return tuple(a + (j,) for a in partition(n - 1) for j in range(max(a, default=-1) + 2))


def fall(n, k):
    return n * fall(n - 1, k - 1) if k else 1


MISSES = Counter()


def _epair_get(A):
    # symbols not touched by any pair relation stay free (counted, so validation can insist on none)
    if A in Epair:
        return Epair[A]
    MISSES['pair'] += 1
    return {A: 1}


@memo
def rep_pair(A):
    if not A:
        return lin(evpair(A), _epair_get)
    n = len(A[0])
    v = {}
    for s in partition(n):
        k = 1 + max(s)
        if k > D:
            continue
        B = tuple(tuple(sum(x for i, x in zip(s, a) if i == j) for j in range(k)) for a in A)
        add(v, evpair(canonpair(B)), Q(fall(D, k), D ** n))
    return lin(v, _epair_get)


def sortleft(A):
    return basic(tr(basic(tr(A))))


def apair(*args):
    return rep_pair(sortleft(tr(args)))


# ---------------------------------------------------------------- mixed moments (complete family)
def normalize(c):
    new = {}
    return tuple(new.setdefault(s, len(new)) for s in c)


@memo1
def cmix(c, A):
    B = tr(A)
    keep = tuple(i for i, b in enumerate(B) if any(b))
    K = []
    for p in itertools.permutations(keep):
        T = tr(perm(B, p))
        K.append((normalize(perm(c, p)), min(basic(T), basic(opposite(T)))))
    return min(K)


def mk(c, *args):
    return cmix(c, basic(tr(args)))


def special(a):
    return VANISH and sorted(a) == sorted(ALPHA)


rows0 = {}


@memo
def evmix(K):
    c, A = K
    assert len(A) <= D and not any(map(sum, A)) and not any(map(sum, tr(A)))
    B = tr(A)
    zero = any(order(b) == 1 or special(b) for b in B)
    types = sorted(set(c))
    if len(types) <= 1:
        v = rep_pair(A)
        v = {((), a): x for a, x in v.items()}
        if zero:
            rows0[K] = v
            return {}
        return v
    if zero:
        return {}
    for i, b in enumerate(B):
        if order(b) == 2 and c.count(c[i]) == 1:
            v = {}
            for t in types:
                if t != c[i]:
                    add(v, evmix(cmix(c[:i] + (t,) + c[i + 1:], A)), -Q(1, D + 1 - len(types)))
            return v
    return {K: 1}


def shift(a, i, j):
    return tuple(x + (t == i) - (t == j) for t, x in enumerate(a))


def mixeq(A, rows, used, limit):
    def val(S, args):
        v = evmix(mk(S, *args))
        used.update(v)
        return v
    for s in partition(3):
        val(s, tr(A))
    for a, b, c in sorted(set(itertools.permutations(tr(A)))):
        if a > b:
            continue
        combs = {(i, j): (shift(a, i, j), shift(b, j, i), c) for i in range(D) for j in range(D)}
        if max(map(wt, combs.values())) <= limit:
            sets = ((0, 1, 2), (0, 1, 0), (0, 1, 1)) if any(c) else ((0, 1, 0),)
            for s in sets:
                v = {}
                for (i, j), q in combs.items():
                    if i != j:
                        add(v, val(s, q))
                if v:
                    rows.append(v)
        for s in (((0, 0, 0), (0, 0, 1)) if any(c) else ((0, 0, 0),)):
            for i in range(D):
                for inv0 in range(2):
                    comb = [combs[(j, i) if inv0 else (i, j)] for j in range(D)]
                    if max(map(wt, comb)) <= limit:
                        v = {}
                        for B in comb:
                            add(v, val(s, B))
                        add(v, val(s[-2:], (neg(c), c)), -1)
                        if v:
                            rows.append(v)


def sortedv(a):
    return min(tuple(sorted(a)), tuple(sorted(neg(a))))


def triples(limit):
    g = [list(vecs(k, D)) for k in range(limit // 2 + 1)]
    for n, ga in enumerate(g):
        for a in sorted(set(map(sortedv, ga))):
            s = set()
            for gb in g[:n + 1]:
                for b in gb:
                    c = neg(plus(a, b))
                    if order(c) <= order(b) and wt((a, b, c)) <= limit:
                        s.add(tuple(sorted(zip(a, b, c))))
            yield from sorted(s)


def mix_rows(limit):
    rows = []
    keys = set()
    for A in triples(limit):
        mixeq(A, rows, keys, limit)
    for g in rows0.values():
        keys.update(g)
        rows.append(g)
    return rows, keys


def mixtable(limit, I=None):
    rows, keys = mix_rows(limit)
    keys = sorted(keys, key=lambda t: (bool(t[0]), wt(t[1]), t))
    if I is not None:
        keys = [keys[i] for i in I] + [k for i, k in enumerate(keys) if i not in I]
    return eliminate(rows, keys)


# ---------------------------------------------------------------- positive forms
def permsign(L):
    pp_ = [itertools.permutations(s) for s in L]
    for ls in itertools.product(*pp_):
        p = list(range(D))
        invn = 0
        for a, b in zip(L, ls):
            for i, z in enumerate(b):
                p[a[i]] = z
                invn += sum(x > z for x in b[:i])
        yield tuple(p), (-1) ** invn


def polynomial(lam, t, v):
    L = []
    h = 1
    for r in lam:
        L.append(tuple(range(h, h + r)))
        h += r
    H = [tuple(s[j] for s in L if len(s) > j) for j in range(max(lam))]
    f = {}
    for q, sgn in permsign(H):
        for p, _ in permsign(L):
            add(f, {(t, perm(perm(v, q), p)): sgn})
    return f


def posdef(B, minpivot=Q(0)):
    B = [list(map(Q, a)) for a in B]
    while B:
        q = B.pop()
        p = q.pop()
        assert p > minpivot
        B = [[x - y * a / p for x, a in zip(b, q)] for b, y in zip(B, q)]


def makeZ(m, a, minpivot=Q(0)):
    assert len(a) * 2 == m * (m + 1)
    itera = iter(a)
    Z = [[0] * m for _ in range(m)]
    for i in range(m):
        for j in range(i + 1):
            Z[i][j] = Z[j][i] = next(itera)
    posdef(Z, minpivot)
    return Z


@memo1
def tagmom(X, Y):
    s, a = X
    t, v = Y
    b = neg(v)
    args = a, b, neg(plus(a, b))
    K = mk((s, t, 0), *args)
    if not s * t:
        return K, None
    return K, mk((1, 2, 0), *args)


def product(h, x, y, z):
    """Adds (D-1) * Re E F_x conj(F_y) * z to h (Lemma 6.1)."""
    for X, p in x.items():
        for Y, q in y.items():
            K, L = tagmom(X, Y)
            s = z * p * q
            if L is None:
                h[K] += (D - 1) * s
            else:
                h[K] += s
                h[L] += (D - 2) * s




def main():
    if sys.flags.optimize:
        raise SystemExit("Refusing to run with -O / PYTHONOPTIMIZE: every check in this verifier is an assertion.")
    path = sys.argv[1] if len(sys.argv) > 1 else "cert_d6_data.json"
    raw = open(path, "rb").read()
    print("certificate", path, "sha256", hashlib.sha256(raw).hexdigest())
    cert = json.loads(raw)
    data = [(tuple(lam), [(t, tuple(v)) for t, v in ws], e, a) for lam, ws, e, a in cert["data"]]
    limit = cert["limit"]
    pairtable(limit, 4)
    Emix = mixtable(limit)
    E = max(e for lam, ws, e, a in data)
    h = Counter()
    for lam, ws, e, a in data:
        assert sum(lam) == D - 1 and all(t in (0, 1) and len(v) == D and sum(v) == 0 for t, v in ws)
        B = [polynomial(lam, t, v) for t, v in ws]
        m = len(B)
        Z = makeZ(m, a, minpivot=Q(0))
        for i in range(m):
            for j in range(i + 1):
                product(h, B[i], B[j], Z[i][j] * (1 + (i != j)) * 10 ** (E - e))
    ans = lin(lin(h, evmix), lambda k: Emix[k] if k in Emix else {k: 1})
    f = ans.pop(((), ()), Q(0))
    v = sum(abs(y) for y in ans.values())
    print("constant f       =", f, "~ %.6e" % float(f))
    print("sum |beta|       =", v, "~ %.6e" % float(v))
    print("f + sum|beta|    ~ %.6e" % float(f + v))
    if not (f + v < 0):
        raise SystemExit("NOT VERIFIED: f + sum|beta| >= 0")
    print("VERIFIED: the averaged positive form is <= f + sum|beta| < 0, a contradiction; no 7 MUBs in C^6.")


if __name__ == "__main__":
    main()
