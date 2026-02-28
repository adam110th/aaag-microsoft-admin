# Systematic Debugging

When debugging issues, bugs, errors, or unexpected behavior, follow this
structured four-phase methodology. Do not jump to conclusions or make
random changes hoping to fix the problem.

## Phase 1: Gather Evidence

Before forming any hypothesis:

1. **Reproduce the issue** — Confirm you can trigger the exact problem.
   Get the precise error message, traceback, and conditions.
2. **Read the error carefully** — Parse the full traceback. Note the
   exception type, message, and the exact line where it originates.
3. **Check recent changes** — Run `git diff` and `git log --oneline -10`
   to see what changed recently. The bug likely lives in recent changes.
4. **Collect context** — Note the Python version, OS, relevant package
   versions, input data, and environment state.

## Phase 2: Form Hypotheses

Based on the evidence, form 2-3 ranked hypotheses:

1. State each hypothesis clearly: "The error occurs because X when Y."
2. For each hypothesis, identify what evidence would confirm or refute it.
3. Rank by likelihood based on the evidence gathered.
4. Do NOT start fixing anything yet.

## Phase 3: Test Hypotheses

For each hypothesis, starting with the most likely:

1. **Design a minimal test** — Write the smallest code or check that
   proves or disproves the hypothesis.
2. **Test one variable at a time** — Do not change multiple things
   simultaneously.
3. **Use print/logging strategically** — Add targeted `logging.debug()`
   calls at decision points, not everywhere.
4. **Check assumptions** — Verify types with `type()`, values with
   `repr()`, and state with breakpoints or assertions.
5. **If refuted**, move to the next hypothesis. If all are refuted,
   return to Phase 1 with new information.

## Phase 4: Fix and Verify

Once the root cause is confirmed:

1. **Write a failing test first** — Create a test that reproduces the
   bug. Confirm it fails.
2. **Make the minimal fix** — Change only what is necessary to fix the
   root cause. Do not refactor unrelated code.
3. **Run the failing test** — Confirm it now passes.
4. **Run the full test suite** — Ensure no regressions.
5. **Remove debug artifacts** — Remove any temporary print/logging
   statements added during investigation.
6. **Document the fix** — In the commit message, explain what caused the
   bug and why the fix resolves it.

## Anti-Patterns to Avoid

- **Shotgun debugging** — Making random changes and hoping the problem
  goes away.
- **Fixing symptoms** — Wrapping errors in try/except without
  understanding the cause.
- **Assuming the cause** — "It must be X" without evidence.
- **Changing multiple things** — Making several changes at once so you
  cannot tell which one fixed it.
- **Ignoring the traceback** — The traceback almost always points to the
  problem; read it carefully.
