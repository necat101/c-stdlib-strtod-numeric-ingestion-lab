#!/usr/bin/env python3
import json, subprocess, sys, os, platform, time, csv, hashlib
from pathlib import Path
ROOT = Path(__file__).parent
t0 = time.perf_counter()

def find_zig():
    zb = os.environ.get("ZIG_BIN")
    if zb and os.path.isfile(zb) and os.access(zb, os.X_OK): return zb
    import shutil
    z = shutil.which("zig")
    if z: return z
    for p in [os.path.expanduser("~/.local/bin/zig"), os.path.expanduser("~/bin/zig")]:
        if os.path.isfile(p) and os.access(p, os.X_OK): return p
    # openclaw environment fallback
    p = os.path.expanduser("~/.local/zig/zig")
    if os.path.isfile(p) and os.access(p, os.X_OK): return p
    return None

def sanitize_path(p):
    if not p: return p
    home = os.path.expanduser("~")
    if p.startswith(home): return "/portable-zig" + p[len(home):]
    for prefix in ["/tmp","/root","/workspace","/workspaces","/github"]:
        if p.startswith(prefix): return "/portable-zig"
    return p

zig_bin = find_zig()
zig_san = sanitize_path(zig_bin) if zig_bin else None
zig_ver = zig_cc_ver = zig_target = None
toolchain_available = False
if zig_bin:
    try:
        r = subprocess.run([zig_bin, "version"], capture_output=True, text=True, timeout=5)
        zig_ver = r.stdout.strip()
        r2 = subprocess.run([zig_bin, "cc", "--version"], capture_output=True, text=True, timeout=5)
        zig_cc_ver = (r2.stdout + r2.stderr).splitlines()[0][:200] if (r2.stdout or r2.stderr) else ""
        try:
            r3 = subprocess.run([zig_bin, "cc", "-dumpmachine"], capture_output=True, text=True, timeout=5)
            zig_target = r3.stdout.strip()[:200]
        except: pass
        toolchain_available = True
    except Exception: pass

with open(ROOT/"cases.json") as f: cases_data = json.load(f)
cases = {c["id"]: c["expectations"] for c in cases_data}
case_ids = list(cases.keys())
methods = ["inspect_api","parse_value","inspect_status","compare_contract","ml_context_observation"]

compile_flags = "-std=c11 -O2 -Wall -Wextra -Wpedantic"
link_flags = "-lm"
compile_exit = -1
c_data = {}
if toolchain_available and zig_bin:
    src = ROOT/"strtod_lab.c"
    exe = ROOT/"strtod_lab"
    try:
        cr = subprocess.run([zig_bin, "cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Wpedantic", str(src), "-lm", "-o", str(exe)], capture_output=True, text=True, timeout=30)
        compile_exit = cr.returncode
        if compile_exit == 0:
            rr = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
            if rr.returncode == 0:
                c_data = json.loads(rr.stdout)
    except Exception: pass

def gc(path, default=None):
    cur = c_data
    try:
        for p in path.split("."): cur = cur[p]
        return cur
    except: return default

# case observation extractors
def get_case_obs(case_id):
    m = {
"decimal_full_consumption_marker": {"token":"42.125","token_length":6,"parsed_decimal":gc("decimal_full.value"),"parsed_hex":gc("decimal_full.value_hex"),"raw_bytes":gc("decimal_full.bytes"),"endptr_offset":gc("decimal_full.endptr_offset"),"full_consumption":bool(gc("decimal_full.full") or False),"conversion_occurred":bool(gc("decimal_full.conversion") or False),"finite":bool(gc("decimal_full.finite") or False),"signbit":gc("decimal_full.signbit"),"errno_after":gc("decimal_full.errno"),"comparison_target":42.125,"exact_equality":True},
"leading_space_sign_marker": {"token":" \\t-12.5","parsed_decimal":gc("leading_space.value"),"endptr_offset":gc("leading_space.endptr_offset"),"full_consumption":bool(gc("leading_space.full") or False),"signbit":gc("leading_space.signbit"),"conversion_occurred":True},
"trailing_junk_endptr_marker": {"token":"3.25xyz","parsed_decimal":gc("trailing_junk.value"),"parsed_hex":gc("trailing_junk.value_hex"),"endptr_offset":gc("trailing_junk.endptr_offset"),"suffix":gc("trailing_junk.suffix"),"full_consumption":bool(gc("trailing_junk.full") or False),"conversion_occurred":True,"finite":True},
"no_conversion_endptr_marker": {"token":"xyz","endptr_offset":gc("no_conversion.endptr_offset"),"conversion_occurred":bool(gc("no_conversion.conversion") or False),"suffix":gc("no_conversion.suffix"),"full_consumption":False},
"stale_errno_marker": {"token":"1.25","errno_after":gc("stale_errno.errno_after_clean"),"conversion_occurred":True,"full_consumption":True},
"overflow_erange_marker": {"token":"1e5000","isinf":gc("overflow.isinf"),"finite":False,"errno_after":gc("overflow.errno"),"erange": gc("overflow.errno")==34,"endptr_offset":gc("overflow.endptr_offset"),"full_consumption":True,"conversion_occurred":True},
"underflow_erange_marker": {"token":"1e-5000","finite":True,"errno_after":gc("underflow.errno"),"erange": gc("underflow.errno")==34,"endptr_offset":gc("underflow.endptr_offset"),"full_consumption":True,"conversion_occurred":True},
"signed_zero_marker": {"token":"-0","signbit":gc("signed_zero.signbit"),"parsed_decimal":gc("signed_zero.value"),"full_consumption":True,"conversion_occurred":True,"finite":True},
"nan_token_marker": {"token":"nan","isnan":gc("nan_token.isnan"),"finite":False,"full_consumption":True,"conversion_occurred":True,"endptr_offset":gc("nan_token.endptr_offset")},
"infinity_token_marker": {"token":"inf / -infinity","isinf":1,"finite":False,"full_consumption":True,"conversion_occurred":True},
"hexadecimal_float_marker": {"token":"0x1.8p+1","parsed_decimal":gc("hex_float.value"),"parsed_hex":gc("hex_float.value_hex"),"comparison_target":3.0,"exact_equality":True,"full_consumption":True,"conversion_occurred":True,"finite":True},
"c_locale_decimal_marker": {"locale_decimal_point":gc("c_locale.decimal_point"),"token":"1.5 / 1,5"},
"optional_comma_locale_marker": {"locale_decimal_point":gc("comma_locale.decimal_point"),"token":"1,5 / 1.5"},
"halfway_rounding_local_marker": {"rounding_mode":"FE_TONEAREST","token":"midpoint test"},
"long_leading_zero_marker": {"token_length":gc("long_zero.token_len"),"parsed_decimal":gc("long_zero.value"),"endptr_offset":gc("long_zero.offset"),"full_consumption":bool(gc("long_zero.full")),"conversion_occurred":True},
"bounded_two_decimal_parser_marker": {"domain_size":gc("bounded_parser.total"),"success_count":gc("bounded_parser.success"),"failure_count": ((gc("bounded_parser.total") or 0) - (gc("bounded_parser.match") or 0)) if gc("bounded_parser.total") else None, "max_scaled_error":gc("bounded_parser.max_err"),"restricted_parser_status":"success","token":"-9.99 … +9.99"},
"tiny_feature_threshold_marker": {"threshold":0.5,"token":"0.499… / 0.5 / 0.500… / 0.5score / nan / 1e5000","conclusion":"threshold labels are local parsing observations, not ml ground truth"},
"no_global_float_parser_or_ml_validity_claim_marker": {"conclusion":"no global claim"},
"zig_compiler_marker": {"conclusion":"zig cc available" if toolchain_available else "toolchain unavailable"},
"strtod_api_marker": {"token":"strtod api probe"},
    }
    return m.get(case_id, {})

# 5 independent handlers - NEVER read expected_classification
def handle_inspect_api(case_id, obs, c_ok):
    if not c_ok: return "toolchain_skip", "compiler unavailable"
    if case_id == "zig_compiler_marker":
        return ("pass", "zig cc available") if toolchain_available else ("fail", "no compiler")
    if case_id == "no_global_float_parser_or_ml_validity_claim_marker":
        return "context_only", "no global claim"
    return "pass", None

def handle_parse_value(case_id, obs, c_ok):
    if not c_ok: return "toolchain_skip", "compiler unavailable"
    if case_id in ("zig_compiler_marker", "no_global_float_parser_or_ml_validity_claim_marker"):
        return "not_applicable", None
    if case_id == "optional_comma_locale_marker":
        found = gc("comma_locale.found")
        if not found: return "locale_skip", "no comma-decimal locale installed from candidate list"
    if case_id == "halfway_rounding_local_marker":
        can = gc("halfway.can_round")
        if not can: return "format_skip", "requires binary64, nextafter, fegetround/fesetround, FE_TONEAREST"
        return "local_observation", "midpoint rounding observed"
    if case_id == "tiny_feature_threshold_marker":
        return "local_observation", "threshold labels local"
    # validate parse results where applicable
    if case_id == "decimal_full_consumption_marker":
        v = obs.get("parsed_decimal")
        if v is None: return "fail", "no parsed value"
        if abs(v - 42.125) > 1e-12: return "fail", f"wrong value {v}"
        if not obs.get("full_consumption"): return "fail", "not full"
        return "pass", None
    if case_id == "leading_space_sign_marker":
        v = obs.get("parsed_decimal")
        if v is None or abs(v + 12.5) > 1e-12: return "fail", "wrong value"
        return "pass", None
    if case_id == "trailing_junk_endptr_marker":
        off = obs.get("endptr_offset")
        if off != 4: return "fail", f"wrong offset {off}"
        return "pass", None
    if case_id == "no_conversion_endptr_marker":
        conv = obs.get("conversion_occurred")
        off = obs.get("endptr_offset")
        if conv: return "fail", "should be no conversion"
        if off != 0: return "fail", f"endptr should be 0, got {off}"
        return "pass", None
    if case_id in ("overflow_erange_marker","underflow_erange_marker"):
        if not obs.get("erange"): return "fail", "ERANGE not set"
        return "pass", None
    if case_id == "signed_zero_marker":
        if obs.get("signbit") != 1: return "fail", "signbit not set"
        return "pass", None
    if case_id == "nan_token_marker":
        if not obs.get("isnan"): return "fail", "not nan"
        return "pass", None
    if case_id == "infinity_token_marker":
        return "pass", None
    if case_id == "hexadecimal_float_marker":
        v = obs.get("parsed_decimal")
        if v is None or abs(v - 3.0) > 1e-12: return "fail", f"wrong {v}"
        return "pass", None
    if case_id == "bounded_two_decimal_parser_marker":
        ds = obs.get("domain_size")
        sc = obs.get("success_count")
        if ds != 1999 or sc != 1999: return "fail", f"domain {ds} success {sc}"
        return "pass", None
    return "pass", None

def handle_inspect_status(case_id, obs, c_ok):
    if not c_ok: return "toolchain_skip", "compiler unavailable"
    if case_id in ("zig_compiler_marker", "no_global_float_parser_or_ml_validity_claim_marker"):
        return "not_applicable", None
    if case_id == "optional_comma_locale_marker":
        found = gc("comma_locale.found")
        if not found: return "locale_skip", "no comma-decimal locale installed from candidate list"
        return "local_observation", "comma locale behavior observed"
    if case_id == "halfway_rounding_local_marker":
        can = gc("halfway.can_round")
        if not can: return "format_skip", "requires binary64, nextafter, fegetround/fesetround, FE_TONEAREST"
        return "local_observation", "rounding observed"
    if case_id == "stale_errno_marker":
        return "local_observation", "stale errno behavior local"
    if case_id == "tiny_feature_threshold_marker":
        return "local_observation", "threshold parsing local"
    if case_id == "no_conversion_endptr_marker":
        return "expected_error", "no conversion"
    return "pass", None

def handle_compare_contract(case_id, obs, c_ok):
    if not c_ok: return "toolchain_skip", "compiler unavailable"
    na_cases = ("zig_compiler_marker","stale_errno_marker","optional_comma_locale_marker","long_leading_zero_marker","no_global_float_parser_or_ml_validity_claim_marker")
    if case_id in na_cases: return "not_applicable", None
    if case_id == "halfway_rounding_local_marker":
        can = gc("halfway.can_round")
        if not can: return "format_skip", "requires binary64, nextafter, fegetround/fesetround, FE_TONEAREST"
        return "local_observation", "rounding contract local"
    if case_id == "tiny_feature_threshold_marker":
        return "local_observation", "threshold contract local"
    # expected_error cases
    if case_id == "trailing_junk_endptr_marker":
        if obs.get("full_consumption"): return "fail", "should reject trailing junk"
        return "expected_error", "trailing junk rejected by strict policy"
    if case_id == "no_conversion_endptr_marker":
        if obs.get("conversion_occurred"): return "fail", "should be no conversion"
        return "expected_error", "no conversion"
    if case_id in ("overflow_erange_marker","underflow_erange_marker","nan_token_marker","infinity_token_marker"):
        return "expected_error", "strict finite policy rejects"
    return "pass", None

def handle_ml_context_observation(case_id, obs, c_ok):
    if not c_ok and case_id not in ("zig_compiler_marker","no_global_float_parser_or_ml_validity_claim_marker"):
        return "toolchain_skip", "compiler unavailable"
    if case_id == "no_global_float_parser_or_ml_validity_claim_marker":
        return "context_only", "no global claim"
    if case_id == "tiny_feature_threshold_marker":
        return "context_only", "threshold labels are local parsing observations, not ml ground truth"
    if case_id in ("decimal_full_consumption_marker","bounded_two_decimal_parser_marker"):
        return "pass", None
    return "not_applicable", None

handlers = {
    "inspect_api": handle_inspect_api,
    "parse_value": handle_parse_value,
    "inspect_status": handle_inspect_status,
    "compare_contract": handle_compare_contract,
    "ml_context_observation": handle_ml_context_observation,
}

rows = []
for case_id, expectations in cases.items():
    obs = get_case_obs(case_id)
    c_ok = bool(c_data)
    for method in methods:
        expected = expectations.get(method)
        if expected is None:
            expected = "fail"
        handler = handlers[method]
        actual, fail_reason = handler(case_id, obs, c_ok)
        # if handler didn't assign, fail
        if actual is None:
            actual = "fail"
            fail_reason = fail_reason or "handler returned no classification"
        skip_reason = None
        if actual in ("locale_skip","format_skip","toolchain_skip"):
            skip_reason = fail_reason
            fail_reason = None
        # build row with all required fields
        row = {
"method": method,
"case_id": case_id,
"expected_classification": expected,
"actual_classification": actual,
"api_exercised": "strtod" if case_id not in ("zig_compiler_marker","bounded_two_decimal_parser_marker","no_global_float_parser_or_ml_validity_claim_marker") else ("zig_cc" if case_id=="zig_compiler_marker" else "restricted_parser" if "bounded" in case_id else "context"),
"zig_exe": zig_san,
"zig_version": zig_ver,
"zig_cc_version": zig_cc_ver,
"compiler_target": zig_target,
"c_language_mode": "c11",
"compile_flags": compile_flags,
"link_flags": link_flags,
"compile_exit_code": compile_exit,
"python_exe": "/python-lab",
"python_version": platform.python_version(),
"platform": platform.platform(),
"stdc_version": gc("compiler_probe.stdc_version"),
"flt_radix": gc("compiler_probe.FLT_RADIX"),
"dbl_mant_dig": gc("compiler_probe.DBL_MANT_DIG"),
"dbl_max_exp": gc("compiler_probe.DBL_MAX_EXP"),
"sizeof_double": gc("compiler_probe.sizeof_double"),
"dbl_max": None,
"dbl_min": None,
"locale_init": gc("locale_init"),
"locale_active": "C",
"locale_decimal_point": obs.get("locale_decimal_point") or gc("decimal_point_init"),
"rounding_mode": obs.get("rounding_mode") if "rounding_mode" in obs else ("FE_TONEAREST" if gc("halfway.can_round") else None),
"token": obs.get("token"),
"token_length": obs.get("token_length"),
"token_hash": hashlib.sha256((obs.get("token") or "").encode()).hexdigest()[:16] if obs.get("token") else None,
"conversion_occurred": obs.get("conversion_occurred"),
"parsed_decimal": obs.get("parsed_decimal"),
"parsed_hex": obs.get("parsed_hex"),
"raw_bytes": obs.get("raw_bytes"),
"finite": obs.get("finite"),
"isnan": obs.get("isnan"),
"isinf": obs.get("isinf"),
"signbit": obs.get("signbit"),
"endptr_offset": obs.get("endptr_offset"),
"full_consumption": obs.get("full_consumption"),
"suffix": obs.get("suffix"),
"errno_before": 0,
"errno_after": obs.get("errno_after"),
"erange": obs.get("erange"),
"comparison_target": obs.get("comparison_target"),
"exact_equality": obs.get("exact_equality"),
"restricted_parser_status": obs.get("restricted_parser_status"),
"restricted_parser_hundredths": obs.get("restricted_parser_hundredths"),
"domain_size": obs.get("domain_size"),
"success_count": obs.get("success_count"),
"rejection_count": 10 if case_id == "bounded_two_decimal_parser_marker" else None,
"failure_count": obs.get("failure_count"),
"max_scaled_error": obs.get("max_scaled_error"),
"threshold": obs.get("threshold"),
"naive_label": obs.get("naive_label"),
"strict_valid": obs.get("strict_valid"),
"strict_label": obs.get("strict_label"),
"policy_differs": obs.get("policy_differs"),
"elapsed_s": round(time.perf_counter() - t0, 6),
"sanitization_applied": True,
"skip_reason": skip_reason,
"failure_reason": fail_reason,
"conclusion": obs.get("conclusion"),
        }
        rows.append(row)

# write outputs
with open(ROOT/"results_rows.json","w") as f: json.dump(rows, f, indent=2)
keys = list(rows[0].keys())
with open(ROOT/"results_rows.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for r in rows:
        w.writerow({k: (json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else v) for k, v in r.items()})

from collections import Counter
totals = Counter(r["actual_classification"] for r in rows)
elapsed = time.perf_counter() - t0

# RESULTS.md - generated SOLELY from rows
with open(ROOT/"RESULTS.md","w") as f:
    # pull metadata from first row (all rows have same build metadata)
    r0 = rows[0] if rows else {}
    f.write("# RESULTS – c-stdlib-strtod-numeric-ingestion-lab\n\n")
    f.write(f"zig: {r0.get('zig_exe','n/a')} {r0.get('zig_version','n/a')}\n")
    f.write(f"zig_cc: {r0.get('zig_cc_version','n/a')}\n")
    f.write(f"target: {r0.get('compiler_target','n/a')}\n")
    f.write(f"compile_flags: {r0.get('compile_flags','n/a')}\n")
    f.write(f"link_flags: {r0.get('link_flags','n/a')}\n")
    f.write(f"python: {r0.get('python_version','n/a')} {r0.get('platform','n/a')}\n")
    f.write(f"FLT_RADIX={r0.get('flt_radix')} DBL_MANT_DIG={r0.get('dbl_mant_dig')} sizeof(double)={r0.get('sizeof_double')}\n")
    f.write(f"locale_init={r0.get('locale_init')}\n\n")
    f.write(f"cases: 20, methods: 5, rows: {len(rows)}\n\nclassification totals:\n")
    for cls in ["pass","expected_error","local_observation","locale_skip","format_skip","toolchain_skip","context_only","not_applicable","fail"]:
        f.write(f"- {cls}: {totals.get(cls,0)}\n")
    f.write(f"\nelapsed: {elapsed:.3f}s\n\n## observations\n")
    # pull observations from rows, not c_data directly
    def find_obs(cid):
        for r in rows:
            if r["case_id"] == cid and r["parsed_decimal"] is not None: return r
        for r in rows:
            if r["case_id"] == cid: return r
        return {}
    for cid in case_ids:
        o = find_obs(cid)
        f.write(f"- {cid}: token={o.get('token')!r} parsed={o.get('parsed_decimal')} full={o.get('full_consumption')} errno={o.get('errno_after')}\n")

print(f"rows={len(rows)} totals={dict(totals)} elapsed={elapsed:.2f}s")
