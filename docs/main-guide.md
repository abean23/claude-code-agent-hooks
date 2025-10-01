# Advanced Claude Code Agents & Hooks: Self-Correcting Validation Pipelines

## Overview
This guide shows how to build a robust pipeline that combines Claude Code agents with hooks to automatically generate, validate, and correct test specifications. The pattern is designed for those who want LLM-assisted test generation with guardrails: reliable outputs, clear error handling, and reproducibility across runs.

When to use this pattern:
- You want to extract structured test cases (IRs) from natural language prompts or code.
- You need hooks to enforce validation, not just rely on raw model output.
- You want bounded correction so the system never loops indefinitely.

---

## Architecture Patterns

### Pattern 1: Agent-Driven Generation
Agents are used for tasks requiring reasoning, such as analyzing a function for edge cases.  
Example: **EdgeCaseAgent** scans a Python function and emits JSON IRs with test cases.  
Best practices:
- Constrain outputs with JSON-only instructions (no Markdown, no prose).
- Represent special values with explicit strings (`"NaN"`, `"Infinity"`) for JSON compatibility.
- Keep prompts narrowly scoped: “analyze this function” rather than “understand the entire repo.”

### Pattern 2: Hook-Based Validation
Hooks guarantee that every IR produced goes through validation.  
- **PostToolUse hooks** can catch some file events, but are unreliable with `Edit` tool calls.  
- **Stop hooks** always fire at the end of a Claude Code run, making them the best place for deterministic validation.  

State management tip: treat hooks as *validators only*, not reasoning layers. Let the agent generate, and let the hook enforce rules.

### Pattern 3: Bounded Auto-Correction
If the IR doesn’t match actual code behavior, the pipeline can attempt one correction pass.  
- A `correction_attempted` flag prevents infinite loops.  
- If the corrected IR still fails, the system classifies the failure as a real bug in the code.  
- This preserves trust: green tests mean the code is actually correct, not endlessly patched IR.

---

## Implementation Guide

### Step 1: Create a Custom Agent
Define the agent in `.claude/agents/edge_case_agent.md`.  
Key elements:
- **Purpose**: identify edge cases and generate test IRs.  
- **Instruction design**: insist on raw JSON only.  
- **Output schema**: include `target`, `cases`, and one of three expectation types (`raises`, `equals`, `predicate`).  

### Step 2: Implement a Validation Hook
Use a stop hook (e.g. `post_code_gen.sh`) to orchestrate validation.  
Flow:  
1. Detect `ir.json`.  
2. Run pre-validation and syntax fixing.  
3. Call the orchestrator to generate tests.  
4. Produce both machine-readable reports and human summaries.  

### Step 3: Build Validation Logic
Core logic lives in **IRProcessor**. It runs in three layers:  
1. **Syntax validation** — fixes malformed JSON (`float('nan')` → `"NaN"`).  
2. **Schema validation** — checks required fields, types, and predicates.  
3. **Semantic validation** — runs actual code with test inputs and compares results.  

### Step 4: Add Observability
Two key outputs:  
- **Run manifest (`run.meta.json`)**: captures environment, versions, file checksums, and traceability metadata.  
- **Summary report (`summary.md`)**: concise human-readable pass/fail overview with sample failures.  

---

## Best Practices

### Context Management
- Scope prompts narrowly to the file under test.  
- Always serialize special values (`"NaN"`, `"Infinity"`, `"-Infinity"`).  
- Keep IR outputs flat and minimal for portability.  

### Hook Orchestration
- Prefer **Stop hooks** for reliability.  
- Track state with flags to prevent loops.  
- Keep hooks idempotent — rerunning the same hook should not corrupt state.  

### Determinism & Reproducibility
The pipeline can’t guarantee identical IRs each run (LLM variance), but it guarantees *traceability*.  
- File checksums show exactly which inputs produced which reports.  
- Pinned dependencies and sorted test execution reduce noise.  
- Manifests allow you to compare runs to see if changes came from code, schema, or IR.  

---

## Common Pitfalls

### Pitfall 1: Unbounded Correction Loops
**Problem**: agent keeps rewriting IR after each failure.  
**Solution**: add `correction_attempted` flag to limit to one retry.  

### Pitfall 2: Masking Real Bugs
**Problem**: over-correcting IR makes broken code appear to pass.  
**Solution**: semantic validation that distinguishes “IR mismatch” from “real code bug.”  

### Pitfall 3: PostToolUse Reliability
**Problem**: Edit tool calls don’t consistently trigger validation.  
**Solution**: rely on Stop hook, which always executes at the end of the run.  

---

## Measuring Success
- All tests pass: code meets IR specifications.  
- IR mismatch → correction → pass: agent improved IR to reflect reality.  
- Code bug persists after correction: surfaced a genuine defect.  
- No infinite loops: correction bounded.  

---

## Extending the Pattern
This pipeline is language-agnostic. Potential extensions include:  
- Swap pytest for Jest (JavaScript) or JUnit (Java).  
- Add multi-file analysis and validation.  
- Integrate with CI/CD to block merges when tests fail.  
