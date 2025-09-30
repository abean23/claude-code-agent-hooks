"""Generate human-readable summary from test results."""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_summary(report_path: Path, ir_path: Path, output_path: Path):
    """Generate concise human-readable summary."""

    # Load report
    try:
        with open(report_path) as f:
            report = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error: Could not read report: {e}"

    # Load IR for diagnosis
    try:
        with open(ir_path) as f:
            ir = json.load(f)
    except:
        ir = None

    counts = report.get("counts", {})
    total = counts.get("total", 0)
    passed = counts.get("passed", 0)
    failed = counts.get("failed", 0)

    # Determine diagnosis
    if failed == 0:
        diagnosis = "✓ All tests passed - code meets IR specifications"
        status = "PASS"
    else:
        # Check if failures look like IR issues or code bugs
        failing_cases = [c for c in report.get("cases", []) if not c.get("passed", False)]
        failing_ids = [c["id"] for c in failing_cases[:5]]  # Top 5

        # Simple heuristic: if all tests fail, likely IR issue
        if failed == total:
            diagnosis = "⚠ All tests failed - likely IR specification issue"
            status = "IR_INVALID"
        elif failed > total * 0.7:
            diagnosis = "⚠ Most tests failed - likely IR specification issue"
            status = "IR_MISMATCH"
        else:
            diagnosis = "✗ Some tests failed - code under test may have bugs"
            status = "CODE_BUG"

    # Extract top traceback if available
    stdout = report.get("stdout", "")
    traceback_lines = []
    if "FAILED" in stdout:
        lines = stdout.split("\n")
        for i, line in enumerate(lines):
            if "FAILED" in line and i + 1 < len(lines):
                # Get next few lines after FAILED
                traceback_lines = lines[i:min(i+5, len(lines))]
                break

    # Build summary
    summary = f"""# Test Summary Report

**Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status**: {status}

## Results
- **Total**: {total} tests
- **Passed**: {passed} ✓
- **Failed**: {failed} ✗
- **Pass Rate**: {(passed/total*100) if total > 0 else 0:.1f}%

## Diagnosis
{diagnosis}
"""

    if failed > 0:
        failing_cases = [c for c in report.get("cases", []) if not c.get("passed", False)]
        failing_ids = [c["id"] for c in failing_cases[:5]]
        summary += f"\n## Failing Tests (top 5)\n"
        for fid in failing_ids:
            summary += f"- `{fid}`\n"

        if traceback_lines:
            summary += f"\n## Sample Failure\n```\n"
            summary += "\n".join(traceback_lines[:3])
            summary += "\n```\n"

    summary += f"\n---\n*Full details in pytest.json*\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary)
    print(f"✓ Generated summary: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python summary_generator.py <report.json> <ir.json> [output.md]")
        sys.exit(1)

    report_path = Path(sys.argv[1])
    ir_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("reports/summary.md")

    generate_summary(report_path, ir_path, output_path)