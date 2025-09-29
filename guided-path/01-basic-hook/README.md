# Module 01: Basic Hook - Intro to PreToolUse Echo

This module introduces Claude Code hooks with a simple, non-blocking `PreToolUse` echo hook. It demonstrates setup, execution, and basic stdin parsing—bridging basic usage to advanced workflows like chaining in later modules.

## Learning Objectives
- Understand hook configuration and events.
- Set up a testable hook script.
- Handle common pitfalls like missing dependencies.

## Prerequisites
- Node.js >=18 installed (download from nodejs.org).
- Claude Code CLI globally installed: `npm install -g @anthropic-ai/claude-code` (see official docs at https://docs.anthropic.com for setup).
- Bash-compatible shell: Native on macOS/Linux; WSL (Ubuntu recommended) or Git Bash on Windows.
- `jq` for JSON parsing: Install via package manager (e.g., `brew install jq` on macOS, `sudo apt install jq` in WSL).
- Anthropic API key set: Export `ANTHROPIC_API_KEY=sk-...` or configure via Claude Code login.
**Windows Note**: If using WSL, run all commands from a WSL terminal for best compatibility. For setup help, refer to Microsoft's WSL guide: https://learn.microsoft.com/en-us/windows/wsl/install.

## Setup Steps
1. **Configure the Hook**: Copy the contents of `sample_settings.json` into your project's `.claude/settings.json` (create if needed). This registers the hook for all tools on `PreToolUse`.
   
   **Cross-Platform Note**: If using WSL on Windows, you may need to prefix the `command` in settings.json with `wsl bash -lc` (e.g., `"command": "wsl bash -lc '\"$CLAUDE_PROJECT_DIR\"/PATH_GUIDED/01-basic-hook/pre_tool_use_echo.sh'"`). Test on macOS/Linux first to avoid breakage—customize per OS. For native Windows, use Git Bash and adapt paths (e.g., replace '/' with '\').

2. **Make Scripts Executable**: Run `chmod +x pre_tool_use_echo.sh test.sh` (on Unix-like; on Windows, skip or use Git Bash).

## Running the Demo
1. Navigate to your project root.
2. Start Claude Code: Run `claude` in terminal (logs in if needed).
3. Submit the prompt from `example_prompt.txt`: Paste "Read the contents of README.md and summarize it." and hit Enter.
4. Observe the echo: You should see "PreToolUse Hook Triggered: Starting tool 'Read'..." in the output.
5. Test automatically: Run `./test.sh` for a quick check.

## Code Explanation
- **pre_tool_use_echo.sh**: Parses stdin JSON with `jq`, echoes tool details, exits 0 (non-blocking). Rationale: Shows event data access without complexity.
- **Why PreToolUse?**: Runs before tools, ideal for logging/prep—escalates to post-hooks/agents later.

## Common Pitfalls and Troubleshooting
- **jq Not Found**: Install `jq`; error on stderr if missing. Solution: Check with `jq --version`.
- **Hook Not Triggering**: Verify `.claude/settings.json` path and matcher ("*"). Run `/hooks` in Claude REPL to inspect config.
- **Cross-Platform Issues**: On macOS, no prefix needed; on WSL, test prefix but remove for portability. If paths fail, use absolute paths instead of `$CLAUDE_PROJECT_DIR`.
- **Timeout/Blocking**: If hook hangs, reduce `timeout` or debug script.

## Success Patterns
- Use inline `jq` for quick parsing.
- Keep hooks non-blocking (exit 0) for starters.

## Next Steps
Build on this in Module 02 (Custom Agent). See REF_HUB/hooks-patterns.md for recipes or troubleshooting.md for more issues.

(Placeholder: With more time, add a diagram of hook lifecycle via Mermaid.)