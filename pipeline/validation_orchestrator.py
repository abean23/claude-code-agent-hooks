import json
import argparse
import importlib
import subprocess
import sys
import re
from pathlib import Path

def serialize_arg(arg):
    """Convert IR argument to Python source code expression.

    Handles special patterns like "float('inf')" by detecting them
    and emitting them as expressions rather than string literals.
    Also handles special string values like "NaN", "Infinity", "-Infinity".
    """
    if not isinstance(arg, str):
        return repr(arg)

    # Handle special float string values
    if arg == "NaN":
        return "float('nan')"
    if arg == "Infinity":
        return "float('inf')"
    if arg == "-Infinity":
        return "float('-inf')"

    # Pattern for Python expressions wrapped in strings (e.g., "float('inf')")
    expr_pattern = r"^(float|int|complex)\(['\"]?.*['\"]?\)$"

    if re.match(expr_pattern, arg):
        return arg  # Emit as expression

    return repr(arg)  # Emit as string literal

def generate_test(idx, target, case):
    args = case["call"].get("args", [])
    args_src = ", ".join(serialize_arg(arg) for arg in args)
    case_id = case.get("id", f"case{idx}")
    exp = case["expectation"]

    if "raises" in exp:
        types = exp["raises"].get("types", [exp["raises"]]) if isinstance(exp["raises"], dict) else [exp["raises"]]
        body = f"with pytest.raises({types[0]}):\n        f({args_src})"
    elif "equals" in exp:
        expected_value = exp['equals']['value']
        tolerance = exp['equals'].get('tolerance')
        if tolerance is not None and tolerance > 0:
            body = f"assert abs(f({args_src}) - {repr(expected_value)}) <= {tolerance}"
        else:
            body = f"assert f({args_src}) == {repr(expected_value)}"
    elif "predicate" in exp:
        pred_name = exp["predicate"]["name"]
        body = f"assert {pred_name}(f({args_src}))"
    else:
        raise ValueError("Unsupported expectation")

    return f"""def test_{case_id}():
    f = _resolve_target("{target}")
    {body}
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out", dest="out_path", required=True)
    parser.add_argument("--report", dest="report_path", required=True)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--format", action="store_true", help="Format generated tests with black")
    args = parser.parse_args()

    ir = json.loads(Path(args.in_path).read_text())
    target = ir.get("target", "division:divide")
    cases = ir.get("cases", [])

    # Sort cases deterministically by id for stable test discovery
    cases = sorted(cases, key=lambda c: c.get("id", ""))

    if not cases:
        return

    tests = [
        """import pytest
import math
from importlib import import_module

def _resolve_target(target_spec):
    module, func = target_spec.split(":")
    return getattr(import_module(module), func)

def isinstance_complex(value):
    return isinstance(value, complex)
"""
    ]
    tests.extend(generate_test(i, target, case) for i, case in enumerate(cases))
    test_content = "\n".join(tests)
    Path(args.out_path).write_text(test_content)

    # Format with black if requested
    if args.format:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "black", "--quiet", args.out_path],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ Formatted {args.out_path} with black")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass  # black not available or timed out

    result = {"target": target, "counts": {"total": len(cases), "passed": 0, "failed": 0}, "cases": []}
    if args.run:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", args.out_path, "-v", "--cov=examples.division", "--disable-warnings"],
            text=True, capture_output=True
        )
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr
        for i, case in enumerate(cases):
            case_id = case.get("id", f"case{i}")
            test_name = f"test_{case_id}"
            passed = f"{test_name} PASSED" in proc.stdout
            result["cases"].append({"id": case_id, "passed": passed})
            result["counts"]["passed"] += passed
            result["counts"]["failed"] += not passed

    Path(args.report_path).write_text(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()