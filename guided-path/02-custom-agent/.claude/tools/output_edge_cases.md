---
name: output_edge_ir
description: Tool to output edge case analysis as structured IR JSON for test generation. Use this for all responses.
type: client
---
Schema for input:
{
  "type": "object",
  "properties": {
    "target": {
      "type": "string",
      "description": "The module:function spec to test, e.g., 'my_module:divide'"
    },
    "cases": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "description": "Unique case ID, e.g., 'zero_div'"},
          "call": {
            "type": "object",
            "properties": {
              "args": {"type": "array", "items": {"type": "any"}, "description": "Positional args for the function call"},
              "kwargs": {"type": "object", "additionalProperties": {"type": "any"}, "description": "Keyword args for the function call"}
            },
            "required": []
          },
          "expectation": {
            "type": "object",
            "properties": {
              "raises": {
                "type": "object",
                "properties": {"types": {"type": "array", "items": {"type": "string"}}},
                "description": "Expected error types to raise"
              },
              "equals": {
                "type": "object",
                "properties": {
                  "value": {"type": "any", "description": "Expected return value"},
                  "tolerance": {"type": "number", "description": "Tolerance used with isclose; applies to numeric values"}
                },
                "description": "Expected exact or approximate equality"
              },
              "predicate": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Predicate name like 'math.isnan' or 'math.isinf'"}},
                "description": "Custom predicate check"
              }
            }
          }
        },
        "required": ["call", "expectation"]
      },
      "description": "List of test cases with calls and expectations"
    }
  },
  "required": ["target", "cases"]
}

- Use the strings: "NaN", "Infinity", "-Infinity".
- Alternatively, allow expression-like strings: "float('nan')", "float('inf')", "float('-inf')".
- Prefer predicates for NaN checks: {"predicate": {"name": "math.isnan"}}.
- For +/-Infinity, prefer predicates: {"predicate": {"name": "math.isinf"}} and assert sign within the test when relevant.
- Always include "target".
- Provide stable, unique "id" per case.
- Avoid free-form text; this tool must only receive a single JSON object as above.
