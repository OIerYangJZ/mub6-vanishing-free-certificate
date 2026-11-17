# No seven mutually unbiased bases in C^6 without Fourier vanishing: exact certificate

Release package, 15 November 2026. Author: Jinze Yang, School of Physics, Xidian University.
Archived at Zenodo: version 1.0.0, DOI [10.5281/zenodo.24296807](https://doi.org/10.5281/zenodo.24296807) (all versions: [10.5281/zenodo.24296806](https://doi.org/10.5281/zenodo.24296806)).
Paper: [arXiv:2611.19809](https://arxiv.org/abs/2611.19809).
License: `verify_d6.py` — Apache License 2.0 (adapted from OpenAI's Apache-2.0 verifier; see `LICENSE`, `NOTICE`); `cert_d6_data.json` and logs — CC BY 4.0 (see `LICENSE-data.txt`).

## What this proves

**Theorem.** There do not exist seven mutually unbiased orthonormal bases of C^6. Equivalently, there are no seven
orthonormal bases B_1, ..., B_7 of C^6 with |<b_{r,i}, b_{s,j}>|^2 = 1/6 for all r ≠ s and all i, j.
By Weiner's gap theorem (M. Weiner, Proc. Amer. Math. Soc. 141 (2013) 1963–1969), the maximum number of mutually
unbiased bases in C^6 therefore satisfies **N(6) ≤ 5**.

The same statement was proved by OpenAI in *Exact Fourier certificates for complex Hadamard matrices of order six*
(OpenAI Math Release preprint, 24 September 2026). That proof has two parts:
- **Part A** (Sections 3–5) proves the Fourier-vanishing conjecture of Matolcsi, Ruzsa and Weiner,
  g_H(πα) = 0 with α = (1,1,1,−1,−1,−1), for every complex Hadamard matrix of order six except Tao's cubic matrix. It
  then excludes the cubic matrix from a complete family (Prop. 5.2).
- **Part B** (Section 6) is a mixed-moment positivity certificate that takes this vanishing, their eq. (27), as input.

The certificate here **does not use Part A**. It uses the same six test-function lists (λ, ws) as OpenAI's Section 6,
and the same valid linear identities:
- the contraction relations of their Lemma 3.2, including the formal seven-row version, up to total order 11;
- vanishing of moments with an order-one charge (orthogonality);
- the symmetries of Lemma 6.2(i), the singleton reduction (iii) / eq. (34), which comes from the second-moment
  (2-design) identity (12), and the single-label expansion (iv);
- the mixed identities (36), (37) up to total order 11.

**No moment is ever set to zero because a charge is a permutation of α.** With new positive definite integer Gram
matrices Z_λ, the averaged positive form satisfies the following, where every X_ρ is an actual moment with
|X_ρ| ≤ 1:

    5 · Σ_λ E[Y_λ^* Z_λ Y_λ]  =  f + Σ_ρ β_ρ X_ρ ,
    f        = −821605927536823/38880          ≈ −2.113184e10
    Σ_ρ|β_ρ| =   5531688869329/12960           ≈  4.268278e8
    f + Σ|β| = −201252715232209/9720           ≈ −2.070501e10  < 0

The left side is ≥ 0 and the right side is ≤ f + Σ|β| < 0, a contradiction. The inputs are orthonormality,
unbiasedness, the 2-design identity of a complete family, and the trivial bounds |moment| ≤ 1.

## Files

| file | content |
|---|---|
| `verify_d6.py` | standalone verifier: Python standard library only; every certifying step is integer/rational arithmetic; it regenerates all relations itself |
| `cert_d6_data.json` | certificate data: the six records (λ, ws, e, a) in the format of OpenAI's Appendix A. The (λ, ws) are OpenAI's, unchanged; `a` is the lower triangle of the new integer matrix Z_λ in row order; e = 0 for all blocks; `limit` = 11 |
| `SHA256SUMS` | checksums of the two files above |
| `verification_logs/` | logs of the reference run of this verifier and the script that produced them (see below); `superseded_old_verifier/` holds the logs of an earlier revision |
| `CITATION.cff`, `.zenodo.json` | citation metadata and Zenodo deposit metadata |

SHA-256:

    8149c17e766767712fa6a1724a9d9f22154ce2f473df8b38a652aad19d86df19  verify_d6.py
    2f7b602b28799008f78a28744ae6c0e0ee02633038b0f21bf8707a4c7080f3e7  cert_d6_data.json

Check with `sha256sum -c SHA256SUMS` (Linux) or `shasum -a 256 -c SHA256SUMS` (macOS). The checksums are those of the files as distributed, with LF line endings; a copy whose line endings were
converted to CRLF (for example by a Git checkout on Windows with `core.autocrlf`) has a different checksum. This
repository's `.gitattributes` turns that conversion off.

## How to run

Requirements: Python ≥ 3.8 (the verifier uses `pow(x, -1, p)`), standard library only. No third-party
packages, no network access. This verifier was run with CPython 3.10.12 on Linux (see Runtime); an earlier revision
(see below) was run with CPython 3.9.18 and 3.12.4.

    python3 verify_d6.py cert_d6_data.json

We recommend isolated mode, which also ignores `PYTHON*` environment variables:

    python3 -I verify_d6.py cert_d6_data.json

**Assertions must be enabled.** The internal checks (exact substitution check, positive definiteness pivots, input
format) are `assert` statements, so the verifier refuses to run under `-O`, `-OO` or `PYTHONOPTIMIZE`: it prints
`Refusing to run with -O / PYTHONOPTIMIZE: ...` and exits with status 1 (logged in
`verification_logs/refuse_optimize.log`). OpenAI's wrapper `run.py` has the same guard. The final sign test
f + Σ|β| < 0 is an explicit check: if it fails, the program prints `NOT VERIFIED` and exits with status 1.

### Expected output (complete)

    certificate cert_d6_data.json sha256 2f7b602b28799008f78a28744ae6c0e0ee02633038b0f21bf8707a4c7080f3e7
    rank table: 8871 909 897
    rank table: 40618 3583 2842
    constant f       = -821605927536823/38880 ~ -2.113184e+10
    sum |beta|       = 5531688869329/12960 ~ 4.268278e+08
    f + sum|beta|    ~ -2.070501e+10
    VERIFIED: the averaged positive form is <= f + sum|beta| < 0, a contradiction; no 7 MUBs in C^6.

Each `rank table` line gives the number of nonzero integer equations, the number of moment coordinates, and the
number of independent witness rows used for exact substitution. The first line is the pair table and the second the
mixed table. The pair table is identical to OpenAI's. Their mixed table, built with vanishing, is
46041 3429 2767.

### Runtime

| interpreter | machine | wall time | peak memory |
|---|---|---|---|
| `/usr/bin/python3 -I` (CPython 3.10.12, system Python) | Linux workstation, Intel Core i7-13700KF, one core | 45 s | 0.38 GB |

Reference run of this verifier (sha256 8149c17e…df19) on 2026-11-15: `bash run_verify.sh` in a fresh directory that
contained only `verify_d6.py`, `cert_d6_data.json` and the script (a copy is in `verification_logs/run_verify.sh`). It produced exactly the output above, with exit status 0; the three `-O` variants were refused with exit
status 1. Logs: `verification_logs/run_env.txt` (machine, interpreter, sha256 of both files),
`verification_logs/verify_system_python3.log`, `verification_logs/refuse_optimize.log`.

An earlier revision of the verifier (sha256 f6cfab32…a55b), without the `-O` guard and with `assert f + v < 0`
instead of the explicit final check, produced the same output on a Linux cluster node on 2026-11-14 with CPython
3.9.18 (82 s) and 3.12.4 (69 s). Those logs are kept in `verification_logs/superseded_old_verifier/`; they are not
evidence for the current file.

## What the verifier checks

1. **Pair relations.** It generates the formal seven-row contraction relations (OpenAI Lemma 3.2, eq. (6)) of total
   order 7–11 with 2–4 columns, reduces them by the order-one contraction (5), and computes exact substitution rules.
   This is modular echelon form, CRT and rational reconstruction, followed by the **exact** integer check `W P = 0`
   of OpenAI's Lemma 7.1. The modular steps only propose; the exact check proves.
2. **Mixed relations.** It generates the identities (36), (37) for all charge triples of total order ≤ 11, with the
   reductions of Lemma 6.2 (i), (iii), (iv) and the order-one zero rule only. It then computes exact substitution
   rules in the same way.
3. **Positive definiteness.** For each block it rebuilds the symmetric integer matrix Z_λ and checks positive
   definiteness by exact rational Schur complements. Every pivot must be > 0; all 98 pivots are positive.
4. **Gram expansion and bound.** It expands Σ_λ E[Y_λ^* Z_λ Y_λ] through the Gram formulas of Lemma 6.1, applies the
   reductions and substitutions, and checks f + Σ|β| < 0 in exact rational arithmetic (an explicit test, not an
   `assert`).

## Relation to OpenAI's verifier

`verify_d6.py` is a line-by-line adaptation of the verifier printed in OpenAI's Appendix A (`verification/verify.py`,
sha256 `104a7306…0eb0e2aa9`). After normalising formatting, 34 of their functions are unchanged, among them the
canonical forms, the contraction, the modular elimination, rational reconstruction, the Young-symmetrised test
functions and the Gram tagging. The mathematical differences are:

1. `special()` always returns `False`, so no moment is set to zero for a permuted-α charge. Only order-one charges
   vanish.
2. There is no single-matrix identity (10) (`check_pair`, their Prop. 3.4). Nothing depends on their Cor. 3.1, Prop. 4.1
   or Prop. 5.2.
3. The coordinate order is the default sort, without the priority lists `I`. This changes which coordinates are free,
   not which relations are used.
4. The Z matrices are new, and the pivot test is `p > 0`, the exact criterion, instead of their margin `p > 40000`. The
   minimum pivots of the new Z are about 1–12, so the new data would not pass that margin.

Other differences: the code is written for a general dimension parameter `D = 6`; the data are read from JSON; and
f and Σ|β| are printed rather than asserted against hard-coded values. Unknown keys would be kept as free symbols
rather than raising `KeyError`, which is sound because such a symbol is still an actual moment bounded by 1. A
diagnostic run confirms that this fallback is never used with these data.

**Cross-check.** An independent C++ re-implementation of the relation generation and exact elimination is not part of
this release. It reproduces, exactly, the pair table (8871/909/897), OpenAI's mixed table with vanishing
(46041/3429/2767) together with their published f and Σ|β|, and the no-vanishing mixed table (40618/3583/2842) used
here. It has not been run on the Z data of this release. The certificate itself rests on `verify_d6.py` alone.

## How the data were produced (informational; not needed for verification)

An SDP was solved for pseudo-moments with OpenAI's six test-function blocks and all relations above, with no
vanishing. Its floating-point dual matrices were symmetrised, projected to the PSD cone, scaled and rounded to
integers (about 10^9 scale), and the smallest diagonal shift (1 or 10) making each rounded matrix positive definite
was added. Nothing about this process needs to be trusted: the verifier checks the resulting integers exactly.
