# Claude Code Hooks Learning Journey

This repo demonstrates how Claude Code **hooks** and **agents** work in practice.  
Unlike a notebook, these are lifecycle events in a terminal/filesystem context — so this repo is intentionally **CLI-first**.

---

## Structure

```text
claude-code-hooks-guide/
├── 01-hello-world/
│   ├── README.md
│   ├── hook.sh
│   └── test.sh
├── 02-validation-agent/
│   ├── README.md
│   ├── validation_agent.py
│   ├── .claude/
│   │   ├── hooks/
│   │   │   └── pre_tool_use.sh
│   │   └── settings.json
│   └── run_demo.sh
├── 03-advanced-patterns/
│   └── README.md
└── docs/
    ├── conceptual-guide.md
    ├── troubleshooting.md
    └── PLANNING.md
```

---

## Rubric Mapping

- **Scenario selection + justification** → see root README (this section).
- **Planning document** → [`docs/PLANNING.md`](docs/PLANNING.md).
- **Comprehensive guide** → [`docs/conceptual-guide.md`](docs/conceptual-guide.md) + [`docs/troubleshooting.md`](docs/troubleshooting.md).
- **Working implementation** → [`02-validation-agent/`](02-validation-agent/).
- **Transcript of Claude usage** → [`docs/transcripts/`](docs/transcripts).

---

## Why not a Jupyter notebook?

Hooks run as **shell executables** around tool use. They intercept requests, validate/transform them, and exit with a status code.  
A notebook can only *invoke* these (via `!bash run_demo.sh`), but the source of truth is the CLI.

---

## Quickstart

```bash
cd 02-validation-agent
./run_demo.sh
