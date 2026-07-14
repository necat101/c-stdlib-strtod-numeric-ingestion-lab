# VERIFY – c-stdlib-strtod-numeric-ingestion-lab

Repository: https://github.com/necat101/c-stdlib-strtod-numeric-ingestion-lab
Implementation SHA: 7d5dacc2143d8cf3c9afc08a164a9b78de2cf0c0
Documentation SHA: (see git log – this file was added in a direct descendant of the implementation commit and may be amended to correct the recorded SHA)

Parent: documentation commit is direct descendant of implementation commit, changes only VERIFY.md (plus any subsequent SHA-correction amends).

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

JSON, CSV, RESULTS counts agree: yes (100 rows)

Committed vs regenerated: identical except elapsed_s timing fields

Timing normalization: elapsed_s differs between runs (expected). The committed results_rows.json contains timing from the original run.

Working-tree changes after regeneration: RESULTS.md, results_rows.csv, results_rows.json – **elapsed_s fields only**. No token, offset, errno, classification, or conclusion differences.

Final git status --porcelain after regeneration (before restoration): 
```
 M RESULTS.md
 M results_rows.csv
 M results_rows.json
```

Restoration: timing-only changes were **not** restored before recording the above status. To get a clean tree, run `git checkout HEAD -- RESULTS.md results_rows.csv results_rows.json`.

Normalized comparison command: not performed – a full field-by-field comparison excluding elapsed_s was not run. The diff was inspected manually and showed only elapsed_s changes.

Artifact scanner: `test_lab.TestLab.test_artifact_scanner` – **partial**. Checks that 11 required files exist and are nonempty, that README contains "Hacker News" and "41501625", that `hn_thread_evidence.md` excludes responsive-design / Firefox / Ctrl+ discussion, and that `.gitignore` covers the `strtod_lab` executable. It does **NOT** scan every file's complete contents, nor check for credentials, tokens, private keys, session IDs, email addresses, full tracebacks with local paths, or environment dumps.

## Known limitations (v2)

- Result row fields: partially populated from helper observations; several fields are hard-coded or null (exact_equality, comparison_target, errno_before, restricted_parser_hundredths, per-token threshold labels/validity/rejection reasons/policy differences, DBL_MAX/DBL_MIN, rejection_count). See README "What this lab actually does" for full list.
- Classifications: handlers do not read `expected_classification` (independent), but several branches return fixed results based on case ID without fully validating the underlying observation (e.g. infinity case).
- Test suite: 17 tests with independent recomputation for decimal parsing, trailing junk offsets, overflow state, bounded-parser domain size, threshold policy decisions, JSON/CSV agreement. **Missing**: expectation-mutation independence test, no-Zig isolated-environment test, missing-handler-result test, independent stale-errno / midpoint-rounding tests, exhaustive regeneration of all 1,999 bounded-parser tokens, independent checking of every rejection token, complete threshold-label recomputation. The overflow test can pass based on row classification rather than requiring actual overflow evidence.
- Artifact scanner: partial – see above.
- Threshold-policy per-token results, restricted-parser rejection details, stale-errno both-call observations, infinity both-sign observations, locale decimal-point strings, rounding-mode restoration – emitted by the C helper but not all recorded in `results_rows.json`.
- VERIFY.md documentation SHA self-reference: this file records the implementation SHA accurately (7d5dacc), but the documentation SHA field is a known bootstrapping problem – see git log for the exact commit containing this file version.

## Summary

Clean-clone verification of implementation commit 7d5dacc: the lab compiles, runs, produces 100 deterministic rows with the reported classification distribution, and 17 tests pass. All 100 rows are reproducible (only elapsed_s differs).

However – see "Known limitations" above. In particular: incomplete observation field population, partial classification validation, partial test coverage, partial artifact scanning, no normalized comparison command run, working tree not restored to clean before recording final status, and VERIFY.md documentation SHA bootstrapping issue.

The repository contains a substantive C implementation exercising real `strtod()` behavior, a restricted two-decimal parser with exhaustive 1999-token testing, and well-attributed HN discussion documentation – but the evidence harness is incomplete, and "clean-clone verified" / "real artifact scanner" claims would overstate what is demonstrated. This VERIFY.md attempts to describe the actual state honestly.
