When Claude Code receives a coding task that involves multiple independent components, files, or functions, use the Task tool to split the work across parallel sub-agents. This accelerates larger tasks and ensures thorough implementation.

## MANDATORY — This Skill Applies To

- Any coding task that involves creating or modifying 3 or more independent files, functions, or components
- Feature implementations that span multiple layers (e.g. model, API, UI, tests)
- Refactoring or migration tasks affecting multiple files
- Any task where the user explicitly requests parallel or concurrent work

## When This Skill Does Not Apply

- Simple single-file edits, bug fixes, or small changes
- Tasks where all changes are tightly interdependent and must be sequential
- Research, exploration, or information-gathering tasks

## Head Agent Pattern

For larger tasks (5+ files, multi-step implementations, or complex features), operate as a **head agent** that orchestrates the work:

### 1. Analyse and decompose the task

Before writing any code, break the user's request into discrete, independent work units. Identify:

- Which units can run in parallel (no shared dependencies)
- Which units must run sequentially (output of one feeds into another)
- The acceptance criteria for each unit

### 2. Dispatch parallel sub-agents

Use the Task tool to launch sub-agents for independent work units simultaneously. Each sub-agent should receive:

- A clear, self-contained description of its specific task
- All context it needs (file paths, function signatures, patterns to follow)
- The expected output or deliverable

Launch as many parallel agents as there are independent units — do not serialise work that can be parallelised.

### 3. Monitor and verify completeness

After all sub-agents complete:

- Review each sub-agent's output against the original user request
- Check that every function, endpoint, component, or feature the user asked for has been fully implemented — not partially, not stubbed, not skipped
- Verify that the outputs are consistent with each other (e.g. shared interfaces match, imports are correct, naming conventions align)

### 4. Deploy additional agents for gaps

If the review reveals incomplete work — missing functions, unimplemented features, TODO stubs, or integration gaps:

- Launch additional sub-agents to complete the missing pieces
- Continue this review-and-deploy cycle until every requirement from the user's original request is fully satisfied
- Do not report the task as complete until all functions are implemented in full

### 5. Final integration check

Once all units are complete:

- Verify cross-file consistency (imports, type signatures, shared constants)
- Ensure no duplicate or conflicting implementations were produced by different agents
- Run any available tests or linters if configured

## Example Dispatch Pattern

```
User request: "Create a REST API with user authentication, database models, and tests"

Head agent decomposes into:
  +-- Agent 1: Database models and migrations (independent)
  +-- Agent 2: Authentication middleware and helpers (independent)
  +-- Agent 3: API route handlers (depends on 1 & 2 -- run after)
  +-- Agent 4: Test suite (depends on 1, 2 & 3 -- run after)

Parallel phase:   Agents 1 & 2 run simultaneously
Sequential phase: Agent 3 runs after 1 & 2 complete
Sequential phase: Agent 4 runs after 3 completes
Head agent:       Reviews all output, deploys Agent 5 if any gaps found
```

## Guidelines

- **Prefer parallel over sequential** — Default to running agents in parallel unless there is a clear data dependency
- **Provide full context** — Sub-agents do not share memory; give each one all the information it needs
- **Use appropriate agent types** — Match the subagent_type to the work (e.g. `general-purpose` for coding, `Explore` for research, `Bash` for command execution)
- **Keep the user informed** — Report progress as agents complete and flag any issues immediately
- **Do not over-split** — If a task is simple enough to complete directly (1-2 files, straightforward logic), just do it without dispatching agents
- **Never declare done prematurely** — The head agent must verify every requirement from the user's original request is fully implemented before reporting completion. If anything is missing, deploy more agents until all work is done
