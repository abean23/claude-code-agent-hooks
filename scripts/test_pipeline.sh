#!/usr/bin/env bash
set -euo pipefail

# always run relative to repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

PROMPT_FILE="${1:-examples/sample_prompt.txt}"
LOG_DIR="logs"; OUT_DIR="outputs"; REPORTS_DIR="reports"
mkdir -p "$LOG_DIR" "$OUT_DIR" "$REPORTS_DIR"

echo "[demo] Running Claude non-interactively…"
RAW_OUT="$LOG_DIR/claude.raw.out"
timeout 120s claude -p "$(cat "$PROMPT_FILE")" >"$RAW_OUT" 2>"$LOG_DIR/claude.stderr"
echo "[debug] Saved raw Claude output to $RAW_OUT"

echo "[demo] Extracting JSON IR → outputs/ir.json"
python3 - "$RAW_OUT" <<'PY'
import sys, json, pathlib

raw_path = pathlib.Path(sys.argv[1])
raw = raw_path.read_text()

# 1) Strip Markdown code fences (common Claude habit)
raw = raw.replace("```json", "").replace("```", "").strip()

# 2) Collect ALL JSON objects from the stream (brace-balance scan)
objs = []
stack = 0
start = None
for i, ch in enumerate(raw):
    if ch == '{':
        if stack == 0:
            start = i
        stack += 1
    elif ch == '}':
        if stack:
            stack -= 1
            if stack == 0 and start is not None:
                segment = raw[start:i+1]
                try:
                    obj = json.loads(segment)
                except Exception:
                    pass
                else:
                    if isinstance(obj, dict):
                        objs.append(obj)
                start = None

if not objs:
    raise SystemExit("No JSON object found in Claude output. Open logs/claude.raw.out to inspect.")

# 3) Prefer an object that looks like IR
candidates = [o for o in objs if "cases" in o and isinstance(o["cases"], list)]
obj = (next((o for o in candidates if "target" in o), None)
       or (candidates[0] if candidates else None))

if obj is None:
    # Help the user debug by showing keys of what we *did* see
    summary = [sorted(o.keys()) for o in objs[:3]]
    raise SystemExit(f"Found JSON but none had the expected IR shape. "
                     f"First object keys: {summary[0] if summary else '[]'}")

# 4) Final sanity checks (fail fast with a helpful message)
missing = [k for k in ("cases",) if k not in obj]
if missing:
    raise SystemExit(f"Selected JSON missing {missing}. Keys present: {sorted(obj.keys())}. "
                     f"Fix the prompt or inspect logs/claude.raw.out.")

# 5) Write IR
out = pathlib.Path("outputs/ir.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(obj, indent=2))
print("ir.json written → outputs/ir.json")
PY


# OPTIONAL: quick mutation demo (flip the first return expr) — remove if you don’t want it
if [[ "${MUTATE:-0}" == "1" && -f division.py ]]; then
  echo "[mutate] Seeding demo bug in division.py"
  cp division.py division.py.bak
  python3 - <<'PY'
import re
from pathlib import Path
p = Path("division.py"); s = p.read_text()
m = re.search(r'^\s*return\s+(.+)$', s, re.M)
if m:
    expr = m.group(1).strip()
    s = re.sub(r'^\s*return\s+(.+)$', f"    return -({expr})", s, count=1, flags=re.M)
    p.write_text(s); print("[mutate] Applied: return X -> return -(X)")
else:
    print("[mutate] No return statement found; skipped")
PY
  trap 'echo "[mutate] Restoring original division.py"; mv -f division.py.bak division.py' EXIT
fi

echo "[demo] Validate IR, generate tests, run pytest…"
python3 pipeline/IRProcessor.py outputs/ir.json division.py
python3 pipeline/validation_orchestrator.py --format --report-json "$REPORTS_DIR/pytest.json"

echo "[demo] Generate manifest & summary…"
python3 pipeline/manifest_generator.py
python3 pipeline/summary_generator.py || true

echo; echo "===== summary (head) ====="
[[ -f "$REPORTS_DIR/summary.md" ]] && sed -n '1,25p' "$REPORTS_DIR/summary.md" || echo "no summary"
