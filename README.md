# Agent-Driven Edge Case Testing
This project demonstrates an agent-hook workflow in Claude Code designed to autonomously generate edge cases, create self-repairing test functions, and run tests using pytest.  
## Prerequisites
To make the most of the agent-hook workflow in this repo, you'll need `Claude Code`, `Python`, and a working bash environment with `jq` installed. This repo is written under the assumption that you are already familiar working in Claude Code.

The code examples are written in Python and Bash, but the concepts remain the same across any programming language.

If you're brand new to agents in Claude Code, I recommend starting with Anthropic's [Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices) to get spun up on basics.
## Repository Table of Contents
### Tool Use and Guides
* [Tool Details](./docs/main-guide.md): Main technical document with feature descriptions and conceptual information
* [Implementation Guide](./docs/implementation-guide.md): Guide on how to adapt this pipeline to your own workflow
* [Best Practices](./docs/best-practices.md): Best practices when working with agent-hook workflows
* [Troubleshooting](./docs/troubleshooting.md): Best practices when working with agent-hook workflows
### Submission Details
* [Planning Document](./docs/PLANNING.md): Includes scenario justification and planning approach
* [Optimizations & Future Work](./docs/optimizations.md): Places where, given more time, improvements can be made to the submission
## Quick Start
1. Clone the Repository:
```shell
git clone https://github.com/abean23/claude-code-agent-hooks
cd claude-code-agent-hooks
```

2. Set up the environment:
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install r- requirements.txt
```

3. Follow along in [Implementation Guide](./docs/implementation-guide.md)
## Peek Inside
* **Highlights**: Multi-layer validation, bounded auto-correction, and automatic code testing
```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Agent -> Hook Validation Flow                    │
└──────────────────────────────────────────────────────────────────────────┘

User prompt
   │
   ▼
[ Claude Code ]
   └─ runs EdgeCaseAgent on target function (e.g., division.py)
      └─ emits test IR (JSON)  ───────────────►  outputs/ir.json

(Stop Hook fires automatically at end of run)
   │
   ▼
[ Validation & Orchestration ]
   ├─ IRProcessor
   │   ├─ JSON syntax / schema checks
   │   ├─ semantic check against function under test
   │   └─ bounded auto-correction (≤1 pass) if IR mismatch
   │
   ├─ Test Orchestrator
   │   ├─ generates tests -> outputs/generated_tests.py
   │   └─ run pytest -> outputs/reports/pytest.json
   │
   └─ Observability
       ├─ manifest -> outputs/reports/run.meta.json
       └─ summary  -> outputs/reports/summary.md

                      ┌────────────────────────────────┐
                      │  Outcomes (classified)         │
                      ├────────────────────────────────┤
                      │  PASS        → code matches IR │
                      │  IR_MISMATCH → fixed (one pass)│
                      │  CODE_BUG    → tests still fail│
                      └────────────────────────────────┘
```

## Additional Resources
Some additional helpful links on Anthropic's Claude Code Agents and Hooks can be found here:
* [Get started with Claude Code hooks](https://docs.claude.com/en/docs/claude-code/hooks-guide)
* [Hooks reference](https://docs.claude.com/en/docs/claude-code/hooks)

