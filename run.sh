#!/bin/bash
set -e
cd "$(dirname "$0")"

# Find zig
if [ -n "$ZIG_BIN" ] && [ -x "$ZIG_BIN" ]; then
  ZIG="$ZIG_BIN"
elif command -v zig >/dev/null 2>&1; then
  ZIG="$(command -v zig)"
elif [ -x "$HOME/.local/bin/zig" ]; then
  ZIG="$HOME/.local/bin/zig"
elif [ -x "$HOME/bin/zig" ]; then
  ZIG="$HOME/bin/zig"
elif [ -x "$HOME/.local/zig/zig" ]; then
  ZIG="$HOME/.local/zig/zig"
else
  echo "zig not found (tried \$ZIG_BIN, command -v zig, ~/.local/bin/zig, ~/bin/zig, ~/.local/zig/zig)" >&2
  exit 1
fi

# Find python
if [ -n "$PYTHON_BIN" ] && [ -x "$PYTHON_BIN" ]; then
  PY="$PYTHON_BIN"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PY="$(command -v python)"
else
  echo "python not found" >&2
  exit 1
fi

echo "zig: $("$ZIG" version)"
echo "python: $("$PY" --version)"

"$ZIG" cc -std=c11 -O2 -Wall -Wextra -Wpedantic strtod_lab.c -lm -o strtod_lab_check
rm -f strtod_lab_check strtod_lab_check.exe
echo "compile check: ok"

"$PY" -m py_compile run_lab.py test_lab.py
echo "py_compile: ok"

"$PY" run_lab.py
echo ""
"$PY" -m unittest -v
