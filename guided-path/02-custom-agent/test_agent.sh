#!/bin/bash

# Run in project root with .claude/agents/edge_case_agent.yaml set up
echo "Testing EdgeCaseAgent..."

# Simulate: Generate code, then pipe to agent (in real: integrate via hook)
generated_code=$(cat PATH_GUIDED/02-custom-agent/demo_code.py)
python PATH_GUIDED/02-custom-agent/edge_case_agent.py --code "$generated_code"

# Full workflow: claude < sample_prompt.txt | grep "edge_cases" (placeholder for integration)
echo "Check output for JSON with edge_cases."