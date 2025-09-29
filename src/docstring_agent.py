#!/usr/bin/env python3
#DocstringAgent: A simple sub-agent that adds placeholder docstrings to Python functions.
import argparse
import ast
import sys
from pathlib import Path


def add_docstring_to_first_function(source_code: str) -> str:
    """
    Add a placeholder docstring to the first function definition in the source code.

    Args:
        source_code: The Python source code as a string

    Returns:
        Modified source code with a docstring added to the first function
    """
    lines = source_code.splitlines(keepends=True)

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Error: Unable to parse Python file: {e}", file=sys.stderr)
        sys.exit(1)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_line = node.lineno - 1

            if ast.get_docstring(node) is not None:
                print(f"Function '{node.name}' already has a docstring. Skipping.")
                return source_code

            indent = len(lines[func_line]) - len(lines[func_line].lstrip())
            docstring_indent = ' ' * (indent + 4)
            docstring = f'{docstring_indent}"""TODO: Add a detailed docstring."""\n'

            insert_position = func_line + 1
            lines.insert(insert_position, docstring)

            return ''.join(lines)

    print("Warning: No function definitions found in the file.", file=sys.stderr)
    return source_code


def main():
    parser = argparse.ArgumentParser(
        description="Add placeholder docstrings to the first function in a Python file."
    )
    parser.add_argument(
        "target_file",
        type=str,
        help="Path to the target Python file"
    )

    args = parser.parse_args()
    target_path = Path(args.target_file)

    if not target_path.exists():
        print(f"Error: File not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    if not target_path.is_file():
        print(f"Error: Path is not a file: {target_path}", file=sys.stderr)
        sys.exit(1)

    try:
        source_code = target_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error: Unable to read file: {e}", file=sys.stderr)
        sys.exit(1)

    modified_code = add_docstring_to_first_function(source_code)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_filename = f"{target_path.stem}_documented{target_path.suffix}"
    output_path = output_dir / output_filename

    try:
        output_path.write_text(modified_code, encoding='utf-8')
        print(f"Success: Modified file written to {output_path}")
    except Exception as e:
        print(f"Error: Unable to write output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()