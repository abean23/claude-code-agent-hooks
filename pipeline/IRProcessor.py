"""IR processing, validation, and correction for test generation pipeline."""

import json
import math
import importlib
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class IRProcessingError(Exception):
    """Base exception for IR processing errors."""
    pass


class ValidationError(IRProcessingError):
    """Raised when IR validation fails."""
    pass


class CorrectionError(IRProcessingError):
    """Raised when IR correction fails."""
    pass


class IRProcessor:
    """Handles special value conversion in IR JSON."""

    SPECIAL_VALUES = {
        "__nan__": lambda: float("nan"),
        "__inf__": lambda: float("inf"),
        "__-inf__": lambda: float("-inf"),
        "__none__": lambda: None,
        "__true__": lambda: True,
        "__false__": lambda: False
    }

    def process_ir(self, ir_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process IR JSON, converting special values."""
        return self._traverse(ir_data)

    def _traverse(self, obj: Any) -> Any:
        """Recursively traverse and convert special values."""
        if isinstance(obj, str) and obj in self.SPECIAL_VALUES:
            return self.SPECIAL_VALUES[obj]()
        elif isinstance(obj, dict):
            return {k: self._traverse(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._traverse(item) for item in obj]
        return obj


class IRSyntaxFixer:
    """Fixes common JSON syntax errors in IR files."""

    @staticmethod
    def fix_python_float_expressions(content: str) -> tuple[str, bool]:
        """
        Fix Python float expressions to JSON-compatible strings.
        Returns: (fixed_content, was_modified)
        """
        original = content
        content = re.sub(r"float\(['\"]nan['\"]\)", '"NaN"', content)
        content = re.sub(r"float\(['\"]inf['\"]\)", '"Infinity"', content)
        content = re.sub(r"float\(['\"]-inf['\"]\)", '"-Infinity"', content)

        return content, content != original


class IRValidator:
    """Validates IR expectations against actual function execution."""

    def __init__(self, tolerance: float = 1e-10):
        self.tolerance = tolerance

    def validate(self, ir_path: Path, target_module: str) -> List[Dict[str, Any]]:
        """
        Validate IR test cases against actual function behavior.

        Args:
            ir_path: Path to IR JSON file
            target_module: Module path containing the target function

        Returns:
            List of validation results with mismatches

        Raises:
            ValidationError: If IR file is invalid or cannot be processed
        """
        try:
            with open(ir_path) as f:
                content = f.read()
        except FileNotFoundError:
            raise ValidationError(f"IR file not found: {ir_path}")

        # Pre-validate JSON syntax with auto-fix for common issues
        try:
            ir_data = json.loads(content)
        except json.JSONDecodeError as e:
            # Attempt to auto-fix Python float expressions
            fixed_content, was_fixed = IRSyntaxFixer.fix_python_float_expressions(content)

            if was_fixed:
                # Try parsing again after fixes
                try:
                    ir_data = json.loads(fixed_content)
                    # Write the fixed content back to file
                    with open(ir_path, 'w') as f:
                        f.write(fixed_content)
                    print(f"✓ Auto-fixed JSON syntax errors in {ir_path}")
                    print("  Replaced Python float expressions with JSON-compatible strings")
                except json.JSONDecodeError as e2:
                    # Still has errors after auto-fix
                    lines = fixed_content.split('\n')
                    line_num = e2.lineno - 1 if e2.lineno else 0
                    problematic_line = lines[line_num] if 0 <= line_num < len(lines) else ""

                    error_msg = f"JSON syntax errors remain after auto-fix at line {e2.lineno}, column {e2.colno}:\n"
                    error_msg += f"  {problematic_line.strip()}\n"
                    error_msg += f"  {' ' * (e2.colno - 1)}^\n"
                    error_msg += f"Error: {e2.msg}\n"
                    raise ValidationError(error_msg)
            else:
                # No auto-fix available, provide detailed error
                lines = content.split('\n')
                line_num = e.lineno - 1 if e.lineno else 0
                problematic_line = lines[line_num] if 0 <= line_num < len(lines) else ""

                error_msg = f"Invalid JSON syntax in IR file at line {e.lineno}, column {e.colno}:\n"
                error_msg += f"  {problematic_line.strip()}\n"
                error_msg += f"  {' ' * (e.colno - 1)}^\n"
                error_msg += f"Error: {e.msg}\n\n"
                error_msg += "Common issues:\n"
                error_msg += "  - Using Python expressions like float('nan'), float('inf') instead of JSON strings\n"
                error_msg += "  - Use \"NaN\", \"Infinity\", \"-Infinity\" as string values instead\n"
                error_msg += "  - Missing commas, quotes, or brackets\n"

                raise ValidationError(error_msg)

        # Validate against JSON schema if available
        if JSONSCHEMA_AVAILABLE:
            schema_path = Path(ir_path).parent.parent / "schemas" / "ir_schema.json"
            if schema_path.exists():
                try:
                    with open(schema_path) as f:
                        schema = json.load(f)
                    jsonschema.validate(ir_data, schema)
                    print(f"✓ IR structure validated against schema")
                except jsonschema.ValidationError as e:
                    raise ValidationError(f"Schema validation failed: {e.message}\nAt path: {list(e.path)}")
                except json.JSONDecodeError:
                    print("Warning: Invalid schema file, skipping schema validation")

        if "target" not in ir_data or "cases" not in ir_data:
            raise ValidationError("IR file missing required 'target' or 'cases' fields")

        try:
            func = self._resolve_target(ir_data["target"], target_module)
        except (ImportError, AttributeError) as e:
            raise ValidationError(f"Cannot resolve target function: {e}")

        mismatches = []
        for case in ir_data["cases"]:
            if "id" not in case or "call" not in case or "expectation" not in case:
                raise ValidationError(f"Invalid case structure: {case}")

            result = self._validate_case(func, case)
            if not result["valid"]:
                mismatches.append(result)

        return mismatches

    def _resolve_target(self, target: str, module_path: str) -> callable:
        """Resolve target function from module:function specification."""
        module_name, func_name = target.split(":")
        module = importlib.import_module(module_name)
        return getattr(module, func_name)

    def _validate_case(self, func: callable, case: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single test case."""
        case_id = case["id"]
        call = case["call"]
        expectation = case["expectation"]

        args = self._process_args(call.get("args", []))
        kwargs = self._process_args(call.get("kwargs", {}))

        try:
            actual = func(*args, **kwargs)
            valid, reason = self._check_expectation(actual, expectation)

            return {
                "case_id": case_id,
                "valid": valid,
                "actual": actual,
                "expected": expectation,
                "reason": reason
            }
        except Exception as e:
            # Check if exception was expected
            if "raises" in expectation:
                expected_types = expectation["raises"]["types"]
                if type(e).__name__ in expected_types:
                    return {"case_id": case_id, "valid": True}
                return {
                    "case_id": case_id,
                    "valid": False,
                    "actual": {"exception": type(e).__name__},
                    "expected": expectation,
                    "reason": f"Wrong exception: expected {expected_types}, got {type(e).__name__}"
                }

            return {
                "case_id": case_id,
                "valid": False,
                "actual": {"exception": type(e).__name__},
                "expected": expectation,
                "reason": f"Unexpected exception: {e}"
            }

    def _check_expectation(self, actual: Any, expectation: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Check if actual result matches expectation."""
        if "raises" in expectation:
            return False, "Expected exception but function returned normally"

        if "equals" in expectation:
            expected_value = expectation["equals"]["value"]
            tolerance = expectation["equals"].get("tolerance", self.tolerance)

            if isinstance(actual, float) and isinstance(expected_value, (int, float)):
                if math.isclose(actual, expected_value, abs_tol=tolerance):
                    return True, None
                return False, f"Values differ: {actual} != {expected_value}"

            if actual == expected_value:
                return True, None
            return False, f"Values differ: {actual} != {expected_value}"

        if "predicate" in expectation:
            predicate_name = expectation["predicate"]["name"]
            predicate = self._resolve_predicate(predicate_name)

            if predicate(actual):
                return True, None
            return False, f"Predicate {predicate_name} failed for value {actual}"

        return False, "No valid expectation type found"

    def _resolve_predicate(self, name: str) -> callable:
        """Resolve predicate function from name."""
        if "." in name:
            module_name, func_name = name.rsplit(".", 1)
            if module_name == "math":
                return getattr(math, func_name)
        raise ValueError(f"Cannot resolve predicate: {name}")

    def _process_args(self, args: Any) -> Any:
        """Process arguments, evaluating string expressions and special float values."""
        if isinstance(args, str):
            # Handle special float string values (from JSON-compatible format)
            if args == "NaN":
                return float('nan')
            if args == "Infinity":
                return float('inf')
            if args == "-Infinity":
                return float('-inf')

            # Try to evaluate string expressions safely
            if args.startswith(('float(', 'int(', 'str(')):
                try:
                    return eval(args, {"__builtins__": {}}, {"float": float, "int": int, "str": str})
                except:
                    return args
            # Handle quoted strings
            if args.startswith('"') and args.endswith('"'):
                return args[1:-1]
            return args
        elif isinstance(args, list):
            return [self._process_args(arg) for arg in args]
        elif isinstance(args, dict):
            return {k: self._process_args(v) for k, v in args.items()}
        return args


class IRCorrector:
    """Corrects IR expectations based on validation failures."""

    def __init__(self, validator: IRValidator):
        self.validator = validator

    def correct(self, ir_path: Path, target_module: str, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Correct IR file based on validation failures.

        Args:
            ir_path: Path to IR JSON file
            target_module: Module path containing the target function
            output_path: Optional output path (defaults to ir_path)

        Returns:
            Statistics about corrections made

        Raises:
            CorrectionError: If correction fails
        """
        try:
            mismatches = self.validator.validate(ir_path, target_module)
        except ValidationError as e:
            raise CorrectionError(f"Validation failed: {e}")

        if not mismatches:
            return {"corrected": 0, "total": 0}

        try:
            with open(ir_path) as f:
                ir_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise CorrectionError(f"Cannot read IR file: {e}")

        corrections = 0
        for mismatch in mismatches:
            case_id = mismatch["case_id"]
            for case in ir_data["cases"]:
                if case["id"] == case_id:
                    case["expectation"] = self._create_expectation(mismatch["actual"])
                    corrections += 1
                    break

        output = output_path or ir_path
        try:
            with open(output, "w") as f:
                json.dump(ir_data, f, indent=2)
        except IOError as e:
            raise CorrectionError(f"Cannot write corrected IR: {e}")

        return {
            "corrected": corrections,
            "total": len(mismatches),
            "mismatches": [{"id": m["case_id"], "reason": m["reason"]} for m in mismatches]
        }

    def _create_expectation(self, actual: Any) -> Dict[str, Any]:
        """Create expectation dict from actual result.

        Only generates expectations using approved predicates:
        - math.isnan
        - math.isinf
        - math.isfinite
        """
        if isinstance(actual, dict) and "exception" in actual:
            return {"raises": {"types": [actual["exception"]]}}

        if isinstance(actual, complex):
            # Complex numbers indicate the function behavior may be unexpected
            # Flag this by using a predicate that will need to be handled
            if math.isnan(actual.real) or math.isnan(actual.imag):
                return {"predicate": {"name": "math.isnan"}}
            # For complex results, we can't easily express this in IR
            # Best to skip or require manual intervention
            raise CorrectionError(f"Complex number result ({actual}) cannot be auto-corrected. Manual review needed.")

        if isinstance(actual, float):
            # Check for special float values
            if math.isnan(actual):
                return {"predicate": {"name": "math.isnan"}}
            if math.isinf(actual):
                return {"predicate": {"name": "math.isinf"}}

            return {"equals": {"value": actual, "tolerance": 1e-10}}

        return {"equals": {"value": actual, "tolerance": 1e-10}}


def main():
    """CLI entry point for IR correction."""
    if len(sys.argv) < 3:
        print("Usage: python IRProcessor.py <ir_file> <target_module> [output_file]", file=sys.stderr)
        print("\nExample: python IRProcessor.py ir.json division", file=sys.stderr)
        sys.exit(1)

    ir_path = Path(sys.argv[1])
    target_module = sys.argv[2]
    output_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    try:
        validator = IRValidator()
        corrector = IRCorrector(validator)
        result = corrector.correct(ir_path, target_module, output_path)

        if result["corrected"] == 0:
            print("✓ All test cases valid - no corrections needed")
            sys.exit(0)

        print(f"✓ Corrected {result['corrected']} of {result['total']} failing cases\n")
        print("Mismatches found:")
        for mismatch in result["mismatches"]:
            print(f"  • {mismatch['id']}: {mismatch['reason']}")

    except IRProcessingError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()