#!/bin/bash

# Stop hook: Runs orchestrator if ir.json exists, auto-corrects IR on test failures.
# Features: In-memory loop prevention, IR validation/correction, clear logging.
# Explanation: After Claude response, runs orchestrator to generate/run tests.
#              If tests fail, attempts to correct IR once (state tracked in memory).

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

# First, validate and auto-fix JSON syntax
log "Pre-validating IR JSON syntax"
target=$(jq -r '.target' "$ir_file" 2>/dev/null | cut -d':' -f1)
if [ -z "$target" ]; then
  target="division"  # fallback
fi

if python3 "$CLAUDE_PROJECT_DIR/IRProcessor.py" "$ir_file" "$target" >> "$LOG_FILE" 2>&1; then
  log "IR JSON syntax validated successfully"
else
  log "IR JSON syntax validation/correction failed"
  exit 1
fi

orch_path="$CLAUDE_PROJECT_DIR/validation_orchestrator.py"
out_file="$CLAUDE_PROJECT_DIR/generated_tests.py"
report_file="$CLAUDE_PROJECT_DIR/report.json"

# In-memory loop prevention: track correction attempts within this execution
correction_attempted=false
max_correction_attempts=1

log "Running orchestrator: $orch_path"
python3 "$orch_path" --in "$ir_file" --out "$out_file" --report "$report_file" --run 2>> "$LOG_FILE" || {
  log "Orchestrator failed"
  exit 1
}

# Check for test failures in report
if [ -f "$report_file" ]; then
  failed=$(jq -r '.counts.failed // 0' "$report_file")

  if [ "$failed" -gt 0 ] && [ "$correction_attempted" = false ]; then
    log "Tests failed: $failed cases"
    log "Attempting IR correction (attempt 1/$max_correction_attempts)"

    # Extract target module from IR
    target=$(jq -r '.target' "$ir_file" | cut -d':' -f1)

    # Run IRProcessor corrector
    if python3 "$CLAUDE_PROJECT_DIR/IRProcessor.py" "$ir_file" "$target" >> "$LOG_FILE" 2>&1; then
      log "IR corrected successfully"
      correction_attempted=true

      # Re-run tests with corrected IR
      log "Re-running orchestrator with corrected IR"
      python3 "$orch_path" --in "$ir_file" --out "$out_file" --report "$report_file" --run 2>> "$LOG_FILE" || {
        log "Re-run failed"
        exit 1
      }

      # Check if correction fixed the issues
      failed_after=$(jq -r '.counts.failed // 0' "$report_file")
      if [ "$failed_after" -eq 0 ]; then
        log "IR correction successful - all tests passing"
      else
        log "Tests still failing after correction - likely a real bug in the code"
      fi
    else
      log "IR correction failed"
    fi
  elif [ "$failed" -gt 0 ]; then
    log "Tests failing but correction already attempted - likely real bugs in code"
  else
    log "All tests passed"
  fi
fi

log "Pipeline complete"
exit 0