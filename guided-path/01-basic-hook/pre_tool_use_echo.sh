#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Parse tool_name using jq
tool_name=$(echo "$input" | jq -r '.tool_name')

# Output JSON with systemMessage for main CLI visibility
echo "{\"systemMessage\": \"PreToolUse Hook Triggered: Starting tool '$tool_name'...\"}"

# Exit 0 to continue (non-blocking success)
exit 0