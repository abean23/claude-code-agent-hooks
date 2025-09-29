#!/bin/bash

# Assume Claude Code is in PATH; run in project dir with .claude/settings.json set up

echo "Testing basic hook..."

# Start Claude Code (simulate prompt submission; in real use, run 'claude' and paste prompt)
# For demo, echo expected output (full automation requires piping, but keep simple)
echo "Expected: PreToolUse Hook Triggered: Starting tool 'Read'..."

# Placeholder for full test: Run 'claude < example_prompt.txt' and grep output
# If you have Claude Code, uncomment:
# claude < example_prompt.txt | grep "PreToolUse Hook Triggered"

echo "Test complete. Check terminal for echo message."