# Planning Document: Claude Code Agents and Hooks

### Scenario Choice Justification
I chose Scenario C (Agents + Hooks) because it best reflects my previous hands-on experience with Claude Code; as the sole developer working on my SaaS platform, DocuBot, I've extensively used agentic workflows and hooks. Most recently, I implemented an agent/hook combo that lends LLM validation to my git commits. This experience specifically indicated the value of using hooks to verify the work of your subagents-- subagents are remarkably powerful, but non-deterministic, so it is necessary to have solid visibility/logging/idempotency/etc. where possible.

The single-module pipeline I’ve built is representative of how agents and hooks can be composed into deterministic, contract-driven, and observable systems—patterns that matter for real-world reliability.

## Documentation Strategy Outline

### 1. Success Criteria
This package succeeds if:
* A developer can run a single command and see the full pipeline execute: agent → IR → tests → pytest → reports.
* They leave with a clear mental model of how agents and hooks complement each other.
* They can reuse the IR contract + hook structure as a template for their own projects.

### 2. Developer Needs Analysis
In order to make intelligent decisions about implementing this scenario, a developer will need to understand a few main concepts:
* Subagents
* Hooks and hook commands

### 3. Content Structure
Two main deliverables:
1. GitHub repo with pipeline and documentation
2. External documentation deliverable

### 4. Implementation Approach
The implementation will focus on one robust agent-hook pipeline. The main blocks will be:
* EdgeCaseAgent: An agent that will emit IR JSON after an edge-case analysis of generated code
* Stop Hook + Command: A hook command that will validate the IR, attempt corrections to the IR, generate pyest tests, and execute them
* Pytest: Arbiter role; results will be logged with human-readable exports

### 5. Workflow Optimization
A dedicated “Future Work” section will sketch how this pipeline could grow into a more robust workflow. To give a few examples of places of improvement around the edges of this workflow:
* Better 'matcher' configuration in settings.json to prevent unnecessary hook runs
* IR cache, so we can reuse the last canonical IR when the target code + agent config haven't changed
* Single orchestrator entry-point

### 6. Technical Depth Assessment
Aside from a multi-step agent-hook workflow, the depth of this submission is further shown in:
* Defense-in-depth validation (syntax, schema, semantic)
* Deterministic guarantees (sorting, pinned deps, black formatting)
* Observability (run manifests, checksums, human + machine reports)
* Bounded repair (1 attempt, then fail-fast)

### 7. Code Architecture Rationale
The repo will be intentionally simple:
* One agent (`EdgeCaseAgent`) and one hook (`post_code_gen.sh`) demonstrate the pattern
* All observability artifacts (`reports/`) are written deterministically
* Code is modularized within a single self-contained directory so learners can copy the pattern directly