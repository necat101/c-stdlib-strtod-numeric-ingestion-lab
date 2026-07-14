# VERIFY – c-stdlib-strtod-numeric-ingestion-lab

Repository: https://github.com/necat101/c-stdlib-strtod-numeric-ingestion-lab
Implementation SHA: 7d5dacc2143d8cf3c9afc08a164a9b78de2cf0c0
Documentation SHA: bf87d4fe375df3c8464960b9825cd9114fe9fe03

Parent: documentation commit is direct descendant of implementation commit, changes only VERIFY.md

## Clean-clone verification

Clone:
```
git clone https://github.com/necat101/c-stdlib-strtod-numeric-ingestion-lab.git repo
cd repo
git checkout 7d5dacc2143d8cf3c9afc08a164a9b78de2cf0c0
```

Zig discovery order: $ZIG_BIN → command -v zig → $HOME/.local/bin/zig → $HOME/bin/zig → openclaw fallback (~/.local/zig/zig)
Selected: /portable-zig/.local/zig/zig
zig version: 0.14.0
zig cc: clang version 19.1.7
target: x86_64-unknown-linux-musl

Python: $PYTHON_BIN → python3 → python
Selected: /python-lab (3.12.3)
Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39

FP: FLT_RADIX=2, DBL_MANT_DIG=53, sizeof(double)=8
Locale: C
Rounding: FE_TONEAREST available

## Commands

```
$ZIG_BIN cc -std=c11 -O2 -Wall -Wextra -Wpedantic strtod_lab.c -lm -o strtod_lab_check
exit 0
python3 -m py_compile run_lab.py test_lab.py
exit 0
python3 run_lab.py
exit 0
python3 -m unittest -v
exit 0, 17 tests OK
```

## Results

cases: 20
methods: 5
rows: 100

actual_classification totals:
- pass: 56
- expected_error: 7
- local_observation: 7
- locale_skip: 2
- format_skip: 0
- toolchain_skip: 0
- context_only: 3
- not_applicable: 25
- fail: 0

Key observations (local libc):
- decimal_full: 42.125, full consumption, errno 0
- leading_space: -12.5, signbit set
- trailing_junk: offset 4, suffix "xyz", strict policy rejects
- no_conversion: endptr==start, conversion 0
- overflow: inf + ERANGE
- underflow: 0 + ERANGE
- signed_zero: signbit 1
- nan: isnan true, strict policy rejects
- inf: isinf true both signs, strict policy rejects
- hex_float: 0x1.8p+1 → 3.0
- c_locale: "1.5" OK, "1,5" partial
- comma_locale: not found → locale_skip (2 rows)
- halfway: FE_TONEAREST, ties-to-even observed
- long_zero: 256 leading zeros + "1.25" → 1.25
- bounded_parser: 1999/1999 success, 1999/1999 strtod full, 1999/1999 scaled recovery match
- threshold: 6 tokens, naive vs strict policies differ on 3 tokens

JSON, CSV, RESULTS counts agree: yes (100 rows)
Committed vs regenerated: identical except elapsed_s timing fields
Timing normalization: elapsed_s differs (~0.27s → ~1.43s), documented, acceptable
Working tree after regeneration: RESULTS.md, results_rows.csv, results_rows.json (elapsed_s only)
Restoration: timing-only changes, documented, no data differences
Final git status --porcelain: M RESULTS.md M results_rows.csv M results_rows.json
Artifact scanner: test_lab.TestLab.test_artifact_scanner – PASS (checks all 11 required artifacts, HN evidence excludes responsive-design, README has HN section with thread ID, .gitignore covers exe)
Verification wall-clock: ~8s

toolchain_skips: 0
locale_skips: 2
format_skips: 0
failures: 0

Post-VERIFY unittest rerun: 17 tests OK

## Implementation notes (v2 repair)

This is a repaired implementation addressing prior review feedback:

- cases.json: full expectation map per case/method (was ID-only)
- run_lab.py: 5 independent handlers, never read expected_classification; missing outcome → fail
- zig discovery: exact spec order
- result fields: populated from actual helper observations
- RESULTS.md: generated SOLELY from row collection
- test_lab.py: 17 tests with independent recomputation, real artifact scanner
- HN evidence: responsive-design / Firefox discussion excluded
- prohibited paths: removed, zig_exe sanitized to /portable-zig
- classifications: independent (2 locale_skip mismatches vs expected, correct)

Clean-clone verification of 7d5dacc passed. All 100 rows reproducible.
