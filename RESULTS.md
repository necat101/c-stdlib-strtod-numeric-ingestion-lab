# RESULTS – c-stdlib-strtod-numeric-ingestion-lab

zig: /portable-zig/.local/zig/zig 0.14.0
zig_cc: clang version 19.1.7 (https://github.com/ziglang/zig-bootstrap 1c3c59435891bc9caf8cd1d3783773369d191c5f)
target: x86_64-unknown-linux-musl
compile_flags: -std=c11 -O2 -Wall -Wextra -Wpedantic
link_flags: -lm
python: 3.12.3 Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
FLT_RADIX=2 DBL_MANT_DIG=53 sizeof(double)=8
locale_init=C

cases: 20, methods: 5, rows: 100

classification totals:
- pass: 56
- expected_error: 7
- local_observation: 7
- locale_skip: 2
- format_skip: 0
- toolchain_skip: 0
- context_only: 3
- not_applicable: 25
- fail: 0

elapsed: 0.292s

## observations
- zig_compiler_marker: token=None parsed=None full=None errno=None
- strtod_api_marker: token='strtod api probe' parsed=None full=None errno=None
- decimal_full_consumption_marker: token='42.125' parsed=42.125 full=True errno=0
- leading_space_sign_marker: token=' \\t-12.5' parsed=-12.5 full=True errno=None
- trailing_junk_endptr_marker: token='3.25xyz' parsed=3.25 full=False errno=None
- no_conversion_endptr_marker: token='xyz' parsed=None full=False errno=None
- stale_errno_marker: token='1.25' parsed=None full=True errno=0
- overflow_erange_marker: token='1e5000' parsed=None full=True errno=34
- underflow_erange_marker: token='1e-5000' parsed=None full=True errno=34
- signed_zero_marker: token='-0' parsed=0 full=True errno=None
- nan_token_marker: token='nan' parsed=None full=True errno=None
- infinity_token_marker: token='inf / -infinity' parsed=None full=True errno=None
- hexadecimal_float_marker: token='0x1.8p+1' parsed=3 full=True errno=None
- c_locale_decimal_marker: token='1.5 / 1,5' parsed=None full=None errno=None
- optional_comma_locale_marker: token='1,5 / 1.5' parsed=None full=None errno=None
- halfway_rounding_local_marker: token='midpoint test' parsed=None full=None errno=None
- long_leading_zero_marker: token=None parsed=1.25 full=True errno=None
- bounded_two_decimal_parser_marker: token='-9.99 … +9.99' parsed=None full=None errno=None
- tiny_feature_threshold_marker: token='0.499… / 0.5 / 0.500… / 0.5score / nan / 1e5000' parsed=None full=None errno=None
- no_global_float_parser_or_ml_validity_claim_marker: token=None parsed=None full=None errno=None
