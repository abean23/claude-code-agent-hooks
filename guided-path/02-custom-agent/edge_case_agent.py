import sys
import ast
import json
import argparse

def analyze_code(code):
    """Basic static analysis for edge cases."""
    edge_cases = []
    
    # Parse AST
    tree = ast.parse(code)
    
    # Look for potential issues (e.g., divisions, loops)
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            edge_cases.append("Potential division by zero if denominator is 0.")
        elif isinstance(node, ast.For) or isinstance(node, ast.While):
            edge_cases.append("Infinite loop risk if condition never falsifies.")
        # Add more heuristics as needed (e.g., input bounds)
    
    # Fallback if no specifics found
    if not edge_cases:
        edge_cases.append("General: Test with empty inputs or max values.")
    
    return {"edge_cases": edge_cases}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", required=True, help="Code to analyze")
    args = parser.parse_args()
    
    result = analyze_code(args.code)
    print(json.dumps(result))  # Output JSON for Claude to parse