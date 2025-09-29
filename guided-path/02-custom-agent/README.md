# Module 02: Custom Agent - Edge Case Identification

Builds on Module 01 by creating a reusable agent for analyzing code. This sets up for chaining in Module 03 (e.g., trigger via post-code-gen hook).

## Objectives
- Create and configure a custom agent.
- Use Python for analysis logic.
- Output structured results for orchestration.

## Setup
1. Copy `edge_case_agent.yaml` to project-root `.claude/agents/`.
2. Install no deps (uses stdlib ast).
3. Update `.claude/settings.json` if integrating with hooks (see Module 03).

## Running
1. Run `./test_agent.sh` for standalone test.
2. In Claude REPL: Paste prompt from `sample_prompt.txt`—agent should output JSON edges.
> Note: Agent results may appear in transcript (CTRL-O); use explicit 'Return just the JSON' in prompts for main CLI display.

## Explanation
- **edge_case_agent.py**: Parses AST to find issues like div-by-zero. Rationale: Static analysis is efficient for edges without execution risks.
- Extends to parallelism: Multiple agents can run async in orchestration.

## Pitfalls
- YAML syntax errors: Validate with `yaml lint` if available.
- Input escaping: Ensure code passed via --code is quoted in commands.
- See REF_HUB/troubleshooting.md#agent-failures.

## Next: Chain with validation in Module 03.
Link: [REF_HUB/agents-catalog.md#custom-creation](./../../REF_HUB/agents-catalog.md#custom-creation)