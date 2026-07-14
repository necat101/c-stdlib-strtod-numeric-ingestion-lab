# c-stdlib-strtod-numeric-ingestion-lab

A tiny deterministic C standard-library correctness lab about `strtod()`, endptr handling, locale-sensitive decimal parsing, and the narrow relationship between textual numeric ingestion and machine-learning-adjacent threshold decisions.

**No model training. No dataset. No throughput benchmark. No external parser.**

- 20 deterministic cases
- 5 methods: `inspect_api`, `parse_value`, `inspect_status`, `compare_contract`, `ml_context_observation`
- 100 result rows
- One C helper (`strtod_lab.c`), one Python runner (`run_lab.py`), one unittest suite (`test_lab.py`)
- Compiler: Zig cc (portable)
- C standard: C11
- Python: stdlib only

## What this lab actually does

The C helper (`strtod_lab.c`) calls the real libc `strtod()` on a fixed set of tokens and records parsed values, endptr offsets, errno, signbit, isnan/isinf, etc. It also includes a deliberately restricted two-decimal parser (-9.99 … +9.99) that is exhaustively tested over all 1999 canonical tokens, comparing against `strtod`.

`run_lab.py` compiles the helper once with zig cc, runs it once, parses the JSON output, and builds 100 result rows (20 cases × 5 methods). Classifications are assigned by five independent handler functions that do **not** read the expected classification map – however, several classification branches return a fixed result based on case ID rather than fully validating the underlying observation (e.g. the infinity case does not inspect the parsed infinity values).

`cases.json` contains a full expectation map for every case/method pair – expectations are **not** copied from runtime results.

Result fields are partially populated from helper observations (parsed values, endptr offsets, errno, signbit, finite/isnan/isinf state, domain counts for the bounded parser). Several fields are hard-coded or left null, including: `exact_equality`, `comparison_target` (hard-coded constants), `errno_before` (always 0), `restricted_parser_hundredths`, per-token threshold labels/validity/rejection reasons/policy differences, `DBL_MAX`/`DBL_MIN`, and rejection counts. The tiny-threshold case does not record per-token naive/strict labels in the result rows – those exist only in the C helper's stdout, not in `results_rows.json`.

`RESULTS.md` is generated from the same in-memory row collection used for JSON/CSV output.

The test suite (`test_lab.py`, 17 tests) independently verifies: case/method counts, no duplicate pairs, classification vocabulary, zig driver identification, decimal parsing (-12.5, 42.125), overflow state, bounded-parser domain size (1999), threshold policy decisions (via C helper), JSON/CSV agreement, and that required artifact files exist with non-zero size. It does **NOT** include: an expectation-mutation independence test, a no-Zig isolated-environment test, a missing-handler-result test, independent stale-errno / midpoint-rounding tests, exhaustive regeneration of all 1,999 bounded-parser tokens with independent scaled-integer recovery, independent checking of every rejection token, or complete threshold-label recomputation. The overflow test can pass based on row classification rather than requiring actual overflow evidence.

The artifact scanner (`test_artifact_scanner`) checks that 11 required files exist and are nonempty, that README contains "Hacker News" and "41501625", that `hn_thread_evidence.md` excludes responsive-design / Firefox / Ctrl+ discussion, and that `.gitignore` covers the `strtod_lab` executable. It does **not** scan every file's complete contents, nor does it check for credentials, tokens, private keys, session IDs, email addresses, full tracebacks with local paths, or environment dumps.

## Results (local)

Compiler: Zig 0.14.0, target x86_64-unknown-linux-musl
FP: FLT_RADIX=2, DBL_MANT_DIG=53, sizeof(double)=8
Locale: C

Classification totals: pass 56, expected_error 7, local_observation 7, locale_skip 2, context_only 3, not_applicable 25, fail 0

Key local observations (from the C helper, not all fields are recorded in `results_rows.json`):

- decimal_full: `"42.125"` → 42.125, fully consumed, errno 0
- leading_space: `" \t-12.5"` → -12.5, signbit set
- trailing_junk: `"3.25xyz"` → endptr offset 4, suffix `"xyz"`; strict whole-token policy rejects
- no_conversion: `"xyz"` → endptr == input start, conversion 0
- overflow: `"1e5000"` → +inf, ERANGE (errno 34)
- underflow: `"1e-5000"` → 0.0, ERANGE
- signed_zero: `"-0"` → value == 0.0, signbit 1
- nan_token: `"nan"` → isnan true
- infinity: `"inf"` / `"-infinity"` → isinf true
- hex_float: `"0x1.8p+1"` → 3.0
- c_locale: `"1.5"` fully consumed as 1.5; `"1,5"` only `"1"` consumed
- comma_locale: no candidate from (`de_DE.UTF-8`, `de_DE.utf8`, `fr_FR.UTF-8`, `fr_FR.utf8`) available → locale_skip
- halfway_rounding: FE_TONEAREST available, ties-to-even observed
- long_zero: 256 leading zeros + `"1.25"` → 1.25, fully consumed
- bounded_two_decimal_parser: domain -9.99 … +9.99 (1999 tokens), restricted parser 1999/1999 success, strtod 1999/1999 full consumption, scaled integer recovery 1999/1999 match; rejection tokens (`""`, `"1"`, `"1.2"`, `"10.00"`, `"1e2"`, `"nan"`, `"inf"`, `"1.00x"`, `" 1.00"`, `"+1.000"`) all rejected
- tiny_threshold: threshold 0.5, tokens `0.49999999999999994`, `0.5`, `0.50000000000000006`, `0.5score`, `nan`, `1e5000`; naive vs strict policies differ – see `strtod_lab.c` threshold output for per-token details (not all fields are recorded in `results_rows.json`)

## Limitations

- Several result row fields are hard-coded or null rather than derived from helper observations (see "What this lab actually does" above)
- Classifications are independent of expectations (handlers never read `expected_classification`), but several branches return fixed results based on case ID without fully validating the underlying observation
- The test suite is partial – see the list of missing independent tests above
- The artifact scanner checks file existence and a few specific strings, not full content scanning for credentials/tokens/PII
- Threshold-policy per-token results, restricted-parser rejection details, stale-errno both-call observations, infinity both-sign observations, locale decimal-point strings, and rounding-mode restoration are emitted by the C helper but not all are recorded in `results_rows.json`
- All floating-point behavior (rounding, NaN payload, signed zero, hex float acceptance, ERANGE) is local to the tested libc / FP format / rounding mode / installed locale set – not generalized

## Hacker News thread access

HN thread: **"Strtod Is Wild"** — https://news.ycombinator.com/item?id=41501625

Tool: `hackernews` CLI — `python3 ./hackernews get-item --id 41501625`

Evidence: `hn_thread_evidence.md` / `hn_comments_sanitized.json` — responsive-design / Firefox / browser zoom discussion excluded per lab spec.

### Summary

The linked article presents fully general decimal-to-binary conversion as much deeper than a simple classroom parser. **The current article includes post-discussion references added after HN/Lobsters feedback — do not confuse with pre-thread state.**

- **lifthrasiir** argued David Gay's dtoa lineage should not be treated as the only modern approach, pointing to Google's **double-conversion** (Grisu family) and **Eisel-Lemire**-style approaches (used in Go/Rust), noting conversion only needs bounded bigint (~3 KB). Does NOT establish any library is universally best.

- **jezek2** described a simple algorithm using 128-bit floats, passing full tests for 32-bit floats and sparse tests for doubles, claiming only the testing actually performed.

- **Neywiny** described replacing `strtod` with a narrower parser on an embedded system because of **code-size constraints** — simple `xx.yy` strings, parsing two integers. Narrow input contract, NOT a general parsing claim.

- **nly** warned that simple decimal-to-double logic can return the **wrong bit pattern** for many inputs.

- **Neywiny** replied the actual requirement was only **one or two decimal places**, "worked fine for me" — an **anecdote, not comprehensive validation**.

- **yjftsjthsd-h** suggested **exhaustive testing rather than random fuzzing** for such a tightly bounded input domain. Bounded exhaustive testing and general fuzzing answer different questions.

- **jancsika** asked how many real public datasets actually require extremely long numeric tokens, speculating that even million-digit inputs could be parsed with a 64-character cap. This was a **question and speculation, not measured evidence**. A 64-character cap was **not established as sufficient for all datasets**.

The thread does **not** establish: strtod's exact allocation behavior on local libc; that a fixed token-length cap, hand-written parser, or modern third-party algorithm is universally preferable; that strtod is badly designed; or that general-purpose libc functions are unsuitable for embedded systems.

### Article vs HN vs POSIX vs local

- **Article (current)**: strtod needs arbitrary-precision arithmetic; classic dtoa can allocate unbounded memory; Sun Microsystems lineage exists with less accuracy emphasis, no allocation; **post-discussion update** adds Grisu / double-conversion / Eisel-Lemire / fast_float references — added after HN feedback.
- **HN**: see summary above.
- **Author**: acknowledged modern-algorithm feedback, said references would be added.
- **POSIX strtod**: `double strtod(const char *nptr, char **endptr)`; skips leading white space; endptr points to first unrecognized char, or nptr if no conversion; errno ERANGE on overflow/underflow; locale-sensitive decimal-point via LC_NUMERIC.
- **Local libc (zig cc / musl)**: IEEE binary64; accepts decimal, hex float, NaN, infinity; overflow → inf + ERANGE; underflow → 0 + ERANGE; signed zero preserved.
- **Restricted two-decimal parser (this repo)**: Accepts only optional sign + 1 digit + `.` + 2 digits, range -9.99 … +9.99. Returns integer hundredths. **Repository code, NOT libc.** Exhaustively tested 1999 tokens. NOT a general strtod replacement.
- All FP behavior is local observations only, not generalized.

### ML adjacency

Textual numeric parsing is relevant to CSV-style features, telemetry, configuration values, thresholds, ranking inputs, and other ML-adjacent data preparation.

**This repository does NOT validate:** an ML model, a dataset, a feature pipeline, a numeric file format, or a production ingestion system.

## Building

```
$ZIG_BIN cc -std=c11 -O2 -Wall -Wextra -Wpedantic strtod_lab.c -lm -o strtod_lab
python3 run_lab.py
python3 -m unittest -v
```

## License

MIT
