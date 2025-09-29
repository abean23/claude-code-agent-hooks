#!/bin/bash

# Stop hook: Runs orchestrator if ir.json exists.
# Features: Minimal, clear, robust.
# Explanation: After Claude response, runs orchestrator to generate/run tests.

LOG_FILE="$CLAUDE_PROJECT_DIR/hook_log.txt"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

PROJECT_ROOT="/home/austin/claude-code-agent-hooks/guided-path/03-chained-pipeline/"
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PROJECT_ROOT}"
log "Stop Hook Triggered: $CLAUDE_PROJECT_DIR"

ir_file="$CLAUDE_PROJECT_DIR/ir.json"
if [ ! -s "$ir_file" ]; then
  log "No IR—skipping"
  exit 0
fi
log "IR found: $ir_file"

export PYTHONPATH="$CLAUDE_PROJECT_DIR:$PYTHONPATH"
log "PYTHONPATH: $PYTHONPATH"

orch_path="$CLAUDE_PROJECT_DIR/validation_orchestrator.py"
out_file="$CLAUDE_PROJECT_DIR/generated_tests.py"
report_file="$CLAUDE_PROJECT_DIR/report.json"
log "Running orchestrator: $orch_path"
python3 "$orch_path" --in "$ir_file" --out "$out_file" --report "$report_file" --run 2>> "$LOG_FILE" || {
  log "Orchestrator failed"
  exit 1
}
log "Pipeline complete"
exit 0