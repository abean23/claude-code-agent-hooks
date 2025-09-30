# Advanced Claude Code Agents & Hooks: Self-Correcting Validation Pipelines

## Overview
[What problem this solves, when to use this pattern]

## Architecture Patterns

### Pattern 1: Agent-Driven Generation
[EdgeCaseAgent example, when to use subagents, how to structure prompts]

### Pattern 2: Hook-Based Validation
[Stop vs PostToolUse, why Stop is reliable, state management]

### Pattern 3: Bounded Auto-Correction
[Why bounded repair matters, correction_attempted flag pattern]

## Implementation Guide

### Step 1: Create Custom Agent
[Show .claude/agents/edge_case_agent.md structure]
[Explain instruction design, output format requirements]

### Step 2: Implement Validation Hook
[Show post_code_gen.sh structure]
[Explain execution flow, error handling]

### Step 3: Build Validation Logic
[IRProcessor architecture, why 3 validation layers]

### Step 4: Add Observability
[Manifest + summary generation, why both formats]

## Best Practices

### Context Management
- How agent discovers files to analyze
- Prompt design for structured output
- Handling special values (NaN, Infinity)

### Hook Orchestration
- When to use Stop vs PostToolUse
- State management across hook invocations
- Preventing infinite loops

### Determinism & Reproducibility
- Checksums for traceability
- Pinned dependencies
- Sorted test execution

## Common Pitfalls

### Pitfall 1: Unbounded Correction Loops
**Problem**: Agent corrects IR, tests fail, agent corrects again...
**Solution**: correction_attempted flag, max 1 attempt
[Show code example]

### Pitfall 2: Masking Real Bugs
**Problem**: Auto-correction makes tests pass when code is wrong
**Solution**: Semantic validation, clear failure taxonomy
[Show failure classification logic]

### Pitfall 3: PostToolUse Hook Reliability
**Problem**: Edit tool doesn't always trigger hooks
**Solution**: Use Stop hook as guaranteed validation point
[Show workaround pattern]

## Measuring Success
- All tests pass: Code meets specifications
- IR_MISMATCH → correction → pass: Agent learned
- CODE_BUG after correction: Real issue surfaced
- Zero infinite loops: Bounds working

## Extending the Pattern
- Adapting to other languages (Jest, JUnit)
- Multi-file validation
- Integration with CI/CD