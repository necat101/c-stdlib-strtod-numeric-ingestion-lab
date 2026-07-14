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

## Results (local)

Compiler: Zig 0.14.0, target x86_64-unknown-linux-musl
FP: FLT_RADIX=2, DBL_MANT_DIG=53, sizeof(double)=8
Locale: C

Classification totals: pass 56, expected_error 7, local_observation 7, locale_skip 2, context_only 3, not_applicable 25, fail 0

Key local observations: decimal full consumption OK, leading space/sign OK, trailing junk endptr correct, no-conversion endptr==start, overflow → inf + ERANGE, underflow → 0 + ERANGE, signed zero signbit preserved, NaN/inf recognized and rejected by strict policy, hex float 0x1.8p+1 → 3.0, C locale decimal OK, comma locale not installed → skip, midpoint rounding ties-to-even, 256 leading zeros → 1.25 OK, bounded two-decimal parser: 1999/1999 success, threshold policy differs on 3/6 tokens.

## Hacker News thread access

HN thread: **"Strtod Is Wild"** — https://news.ycombinator.com/item?id=41501625

Tool: `hackernews` CLI — `python3 ./hackernews get-item --id 41501625`

Evidence: `hn_thread_evidence.md` / `hn_comments_sanitized.json`

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
