“Duplicates still appearing” → normalize before hashing; ensure single-writer.

“Malformed JSON in edge_cases.jsonl” → atomic writes; validate before append.

“Validator nondeterministic” → seed; freeze locales/timezones; avoid wall-clock deps.

## Issue: PreToolUse (or Other) Hook Triggers Multiple Times

If your hook executes repeatedly (e.g., 2x or more per tool call) without errors, this is a known bug in Claude Code where hook configurations duplicate progressively during a session. It can escalate with prolonged use, leading to redundant triggers before outputs like summaries appear.

**Common Causes**:
- Session state buildup, especially in interactive REPL flows with tools like Read/Write.

**Solutions**:
- Restart the Claude Code session: Exit with CTRL+C or `/exit`, then relaunch with `claude`.
- Check for updates: Run `npm update -g @anthropic-ai/claude-code` and test again.