# Module 03: Chained Workflow - Advanced Agent and Hook Integration for Code Validation

This module demonstrates a streamlined, AI-assisted development workflow using Claude Code: generating code, analyzing edge cases with a custom agent, saving an intermediate representation (IR) as JSON, and validating through automated test generation and execution. Designed for Scenario C of an Anthropic interview, it showcases custom agents, hooks for event-driven workflows, and modular patterns, all optimized for clarity, pedagogy, and public consumption.

This README explains each component, its value, setup, and how they connect to form a cohesive pipeline. Aimed at experienced developers, it assumes familiarity with Claude Code basics (e.g., from Modules 01 and 02). The focus is on creating reusable, automated, and production-quality code that’s easy to understand and extend, suitable for showcasing to Anthropic or the public.

## Learning Objectives
- Master custom agents for specialized tasks like edge-case analysis.
- Understand hooks for chaining workflows (e.g., post-agent validation).
- Learn IR-based patterns for modularity and decoupling.
- Explore hybrid AI-deterministic workflows for reliability.
- Debug and extend the pipeline for enterprise use (e.g., CI/CD integration).

## Prerequisites
- **Claude Code**: Install via `npm install -g @anthropic-ai/claude-code`.
- **Python 3.12+**: With `pytest` and `pytest-cov` (`sudo apt install python3-pytest python3-pytest-cov` on WSL/Ubuntu).
- **jq**: For JSON parsing in hooks (`sudo apt install jq`).
- **Project Structure**: `.claude/agents/` with `edge_case_agent.md` and `output_edge_ir.md` (from Module 02).
- **Module Setup**: `__init__.py` in the project directory (`touch guided-path/03-chained-pipeline/__init__.py`).

## Setup Steps
1. **Copy Files**:
   - Place `post_stop.sh`, `validation_orchestrator.py`, and `demo_prompt.txt` in `guided-path/03-chained-pipeline/`.
2. **Configure Hooks**:
   Update `.claude/settings.json` to include a Stop hook:
   ```json
   {
     "hooks": {
       "Stop": [
         {
           "matcher": "*",
           "hooks": [
             {
               "type": "command",
               "command": "\"$CLAUDE_PROJECT_DIR\"/guided-path/03-chained-pipeline/post_stop.sh",
               "timeout": 30
             }
           ]
         }
       ]
     }
   }
   ```
3. **Make Script Executable**:
   ```bash
   chmod +x guided-path/03-chained-pipeline/post_stop.sh
   ```
4. **Set Permissions**:
   ```bash
   chmod -R u+w /home/austin/claude-code-agent-hooks
   ```
5. **Verify Hooks**:
   In Claude Code REPL, run `/hooks` to confirm hook registration.

## Running the Demo
1. Start Claude Code: `claude`.
2. Paste the prompt from `demo_prompt.txt`:
   ```
   Generate a division function in division.py, use EdgeCaseAgent to analyze and generate IR, saving to ir.json.
   ```
3. Outputs:
   - `division.py`: Generated division function (e.g., `def divide(a, b): return a / b`).
   - `ir.json`: IR with edge cases (e.g., `{"target": "division:divide", "cases": [...]}`).
   - `generated_tests.py`: Pytest file with ~12 test cases.
   - `report.json`: Metrics (e.g., 12/12 tests passed, 80%+ coverage).
   - `hook_log.txt`: Logs pipeline execution.
4. Check Results: Verify `report.json` for test outcomes and coverage.

## Pipeline Components
The workflow chains components to automate code generation, analysis, and validation. Below, each component is explained with its role, value, and why it’s exemplary for learning and public consumption.

### 1. Prompt (demo_prompt.txt)
- **Role**: Initiates the workflow by instructing Claude to generate code and invoke EdgeCaseAgent.
- **Example**: 
  ```
  Generate a division function in division.py, use EdgeCaseAgent to analyze and generate IR, saving to ir.json.
  ```
- **Value**: Acts as the user-friendly entry point, leveraging Claude’s natural language understanding to trigger complex workflows. It’s flexible, allowing users to modify for different functions or agents.
- **Why Pedagogical**: Simple, intuitive—developers can learn prompt engineering for AI-driven automation. Public-ready due to its clarity and reusability.
- **How It Connects**: Triggers Claude to write `division.py` and call EdgeCaseAgent, which outputs `ir.json`.

### 2. EdgeCaseAgent (edge_case_agent.md)
- **Role**: A custom agent that analyzes `division.py` for edge cases (e.g., division by zero, type errors) and generates structured IR JSON.
- **Structure**:
  - Defined in Markdown with YAML frontmatter specifying `name`, `tools`, and `model`.
  - Uses `output_edge_ir` tool to enforce IR format: `{"target": "division:divide", "cases": [...]}`.
- **Value**: Extends Claude Code for specialized analysis, catching edge cases humans might miss (e.g., `float('inf')`, `None`). Structured output ensures downstream compatibility.
- **Why Pedagogical**: Teaches agent creation with clear constraints (no text, strict JSON). Easy to extend for new analyses (e.g., security checks).
- **How It Connects**: Saves `ir.json`, which the hook picks up for validation.

### 3. OutputEdgeIR Tool (output_edge_ir.md)
- **Role**: Enforces structured IR output from EdgeCaseAgent, ensuring consistent JSON format.
- **Schema**: 
  ```json
  {
    "target": "string",
    "cases": [
      {
        "id": "string",
        "call": {"args": ["any"]},
        "expectation": {
          "raises": {"types": ["string"]},
          "equals": {"value": "any"},
          "predicate": {"name": "string"}
        }
      }
    ]
  }
  ```
- **Value**: Guarantees machine-readable output, enabling modular workflows (e.g., IR to tests). Prevents LLM verbosity, adding production quality.
- **Why Pedagogical**: Shows how tools enforce structure, a key pattern for reliable AI pipelines. Public-ready due to clear schema.
- **How It Connects**: Used by EdgeCaseAgent to write `ir.json`, consumed by the orchestrator.

### 4. Stop Hook (post_stop.sh)
- **Role**: Bash script triggered on Claude’s Stop event, checks for `ir.json`, sets PYTHONPATH, and runs the orchestrator.
- **Key Logic**:
  ```bash
  if [ ! -s "$ir_file" ]; then
    log "No IR—skipping"
    exit 0
  fi
  python3 "$orch_path" --in "$ir_file" --out "$out_file" --report "$report_file" --run
  ```
- **Value**: Automates the workflow by reacting to Claude’s completion, enabling event-driven chaining (e.g., post-agent validation). Minimal logging aids debugging.
- **Why Pedagogical**: Teaches hooks for automation, a core Claude Code feature. Simple, clear script is public-ready and easy to modify (e.g., add notifications).
- **How It Connects**: Triggers `validation_orchestrator.py` to process `ir.json`.

### 5. Orchestrator (validation_orchestrator.py)
- **Role**: Python script that parses `ir.json`, generates pytest code (`generated_tests.py`), runs tests with coverage, and saves metrics to `report.json`.
- **Key Logic**:
  ```python
  ir = json.loads(Path(args.in_path).read_text())
  tests = [HEADER] + [generate_test(i, target, case) for i, case in enumerate(cases)]
  Path(args.out_path).write_text("\n".join(tests))
  proc = subprocess.run([...], text=True, capture_output=True)
  ```
- **Value**: Bridges AI (IR from agent) with deterministic tools (pytest), ensuring reliable validation. Generates tests for edge cases, measures coverage (80%+), and reports results.
- **Why Pedagogical**: Shows hybrid AI-deterministic workflows, modular test generation, and error handling. Clean, minimal code is public-ready.
- **How It Connects**: Consumes `ir.json`, produces `generated_tests.py` and `report.json`.

### 6. Generated Tests (generated_tests.py)
- **Role**: Pytest file with test cases generated from `ir.json` (e.g., `test_divide_by_zero`, `test_divide_none_numerator`).
- **Example**:
  ```python
  def test_divide_by_zero():
      f = _resolve_target("division:divide")
      with pytest.raises(ZeroDivisionError):
          f(10, 0)
  ```
- **Value**: Executes edge-case tests, catching bugs in `division.py` (e.g., TypeError for strings). Ensures high coverage (80%+).
- **Why Pedagogical**: Teaches test generation from IR, a reusable pattern. Clear, standard pytest format is public-ready.
- **How It Connects**: Run by orchestrator, results saved to `report.json`.

### 7. Report (report.json)
- **Role**: JSON file with test results and metrics (e.g., passed/failed, coverage).
- **Example**:
  ```json
  {
    "target": "division:divide",
    "counts": {"total": 12, "passed": 12, "failed": 0},
    "cases": [{"id": "divide_by_zero", "passed": true}, ...]
  }
  ```
- **Value**: Provides measurable outcomes, enabling iterative improvement (e.g., fix failing tests). Coverage metrics validate code quality.
- **Why Pedagogical**: Shows how to capture and report test results, a key dev practice. JSON format is machine-readable for CI/CD.
- **How It Connects**: Generated by orchestrator, summarizes pipeline output.

## Pipeline Value
This workflow automates code validation, combining AI’s creativity with deterministic rigor:
- **Efficiency**: Single prompt generates code, analyzes edges, runs tests (~12 tests, <15 mins).
- **Reliability**: Catches bugs (e.g., `ZeroDivisionError`, `TypeError`) with 80%+ coverage.
- **Modularity**: IR decouples agent analysis from test execution, reusable for new functions or agents.
- **Automation**: Hook eliminates manual steps, ideal for CI/CD.
- **Pedagogy**: Teaches agent creation, hooks, IR patterns, and hybrid workflows.

**Comparison Table**:
| Approach | Pros | Cons |
|----------|------|------|
| Prompt-Only | Quick, no setup | Non-reusable, no automation |
| This Pipeline | Automated, reusable, measurable | Prompt-driven start |
| SDK (Future) | Headless, CI/CD-ready | Requires dev |

## Troubleshooting
- **No IR Saved**: Claude Code may fail to write `ir.json` (known quirk). Reprompt or use Write tool explicitly:
  ```
  Generate division.py, use EdgeCaseAgent to analyze and write IR to ir.json using Write tool.
  ```
- **Hook Not Triggering**: Check `/hooks` in REPL; restart Claude session.
- **Import Errors**: Ensure `__init__.py` exists; verify PYTHONPATH:
  ```bash
  export PYTHONPATH=$CLAUDE_PROJECT_DIR/guided-path/03-chained-pipeline:$PYTHONPATH
  ```
- **Orchestrator Failure**: Check `hook_log.txt` for errors; ensure `pytest`, `pytest-cov` installed (`sudo apt install python3-pytest python3-pytest-cov`).
- **Permissions**: Ensure write access:
  ```bash
  chmod -R u+w /home/austin/claude-code-agent-hooks
  ```

## Gaps and Improvements
- **Gap**: Prompt-driven agent invocation (Claude Code limitation).
- **Improvement**: Develop SDK for headless chaining (50% CI/CD speedup).
- **Extension**: Add hook to email `report.json` or integrate with CI tools (e.g., Jenkins).

## Alternative Use-Cases
For even cleaner, more exemplary pipelines:
1. **PostToolUse Hook**:
   - Trigger on Write tool when EdgeCaseAgent saves `ir.json`.
   - **Pros**: Precise, automated, public-ready (shows tool-driven automation).
   - **Cons**: Requires explicit Write tool call.
   - **Setup**:
     ```json
     {
       "hooks": {
         "PostToolUse": [
           {
             "matcher": "Write",
             "hooks": [
               {
                 "type": "command",
                 "command": "\"$CLAUDE_PROJECT_DIR\"/guided-path/03-chained-pipeline/post_write.sh",
                 "timeout": 30
               }
             ]
           }
         ]
       }
     }
     ```
     Prompt: "Generate division.py, use EdgeCaseAgent to analyze and write IR to ir.json using Write tool."
2. **Manual Trigger**:
   - Run orchestrator manually after Claude generates `ir.json`.
   - **Pros**: Simplest, no hook quirks, ideal for demos.
   - **Cons**: Less automated.
   - Script (`run_tests.sh`):
     ```bash
     #!/bin/bash
     export PYTHONPATH="${CLAUDE_PROJECT_DIR:-/home/austin/claude-code-agent-hooks}/guided-path/03-chained-pipeline:$PYTHONPATH"
     python3 guided-path/03-chained-pipeline/validation_orchestrator.py \
       --in ir.json \
       --out generated_tests.py \
       --report report.json --run
     ```

## Next Steps
- Experiment with new functions (e.g., `sqrt`) by modifying the prompt.
- Extend EdgeCaseAgent for new analyses (e.g., performance, security).
- Integrate with CI/CD by piping `report.json` to monitoring tools.

This pipeline is a reusable, pedagogical blueprint for AI-assisted development, ready for Anthropic’s high bar and public consumption. Dive in, tweak, and showcase!