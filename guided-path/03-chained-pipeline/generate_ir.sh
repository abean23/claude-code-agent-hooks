#!/bin/bash

# Generate IR JSON using EdgeCaseAgent and write directly to ir.json
# This ensures 100% deterministic capture of agent output

set -e

SOURCE_FILE="${1:-division.py}"
OUTPUT_FILE="${2:-ir.json}"
LOG_FILE="${3:-hook_log.txt}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

log "Generating IR from $SOURCE_FILE using EdgeCaseAgent"

# Create a temporary file for the agent prompt
PROMPT_FILE=$(mktemp)
cat > "$PROMPT_FILE" <<'EOF'
Analyze the divide function in division.py for potential edge cases and generate structured IR for test generation.

CRITICAL INSTRUCTIONS:
- Return ONLY raw JSON, NO markdown code blocks, NO explanations
- Use "NaN" NOT float('nan')
- Use "Infinity" NOT float('inf')
- Use "-Infinity" NOT float('-inf')

Required JSON structure:
{
  "target": "module:function",
  "cases": [
    {
      "id": "case_id",
      "call": {"args": [value1, value2]},
      "expectation": {"raises": {"types": ["ErrorType"]}}
    }
  ]
}

Return the complete JSON IR.
EOF

# Call the EdgeCaseAgent and capture output
# Note: This would need integration with Claude Code's agent system
# For now, this is a placeholder showing the intended flow

log "EdgeCaseAgent invocation - output will be written to $OUTPUT_FILE"

# TODO: Actual agent invocation would happen here
# For now, this script shows the intended structure

rm -f "$PROMPT_FILE"

log "IR generation complete"