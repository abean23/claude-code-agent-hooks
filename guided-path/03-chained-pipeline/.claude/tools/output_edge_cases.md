---
name: output_edge_cases
description: Tool to output edge case analysis as JSON. Use this for all responses.
type: client
---
Schema for input:
{
  "type": "object",
  "properties": {
    "edge_cases": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of edge case descriptions"
    }
  },
  "required": ["edge_cases"]
}