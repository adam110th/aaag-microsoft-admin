# Verification Before Completion

Before claiming any task is complete, follow this evidence-based
verification protocol. Never declare a task done based on belief or
expectation alone.

## Verification Steps

1. **Run the test suite** — Execute `pytest` and confirm all tests pass.
   If no tests exist for the new functionality, write them first. A task
   is not complete without passing tests.

2. **Run linting and type checks** — Execute `ruff check .` and
   `pyright` (or the project's configured tools). Fix any new warnings
   or errors introduced by your changes.

3. **Verify the specific acceptance criteria** — Re-read the original
   request or ticket. Check off each requirement individually. If
   something was requested but not implemented, it is not done.

4. **Test edge cases** — Consider and test boundary conditions, empty
   inputs, error states, and large inputs where relevant.

5. **Check for regressions** — Run the full test suite, not just the
   tests related to your changes. Confirm existing functionality still
   works.

6. **Review your own diff** — Run `git diff` and read every changed line.
   Look for:
   - Debug `print()` statements left behind
   - Commented-out code
   - TODO comments that should have been resolved
   - Hardcoded test values or paths
   - Missing `encoding="utf-8"` on `open()` calls

7. **Verify cross-platform** — If the code touches file paths, subprocess
   calls, or system-specific features, confirm it works on both Windows
   and Linux (or note the limitation).

## What "Done" Means

A task is complete ONLY when ALL of the following are true:

- [ ] All requested features are implemented (not stubbed)
- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checks pass (`pyright`)
- [ ] No debug artifacts remain in the code
- [ ] `requirements.txt` updated if dependencies changed
- [ ] README or documentation updated if behavior changed

## Anti-Patterns

- **"It should work"** — Run it and prove it works.
- **"I'll fix that later"** — Fix it now or flag it explicitly.
- **Declaring done without running tests** — Always run the tests.
- **Skipping the diff review** — Your diff is the truth of what changed.
