---
description: Run code quality checks on a directory
allowed-tools: Read, Glob, Grep, Bash(ruff:*), Bash(pyright:*), Bash(pytest:*), Bash(pip:*)
---

# Code Quality Review

Review code quality in: $ARGUMENTS

## Instructions

1. **Identify files to review**:
   - Find all `.py` files in the target directory
   - Exclude test files and generated files for the main review
   - Note test coverage gaps separately

2. **Run automated checks**:
   ```bash
   ruff check $ARGUMENTS
   ruff format --check $ARGUMENTS
   pyright $ARGUMENTS
   ```

3. **Manual review checklist**:
   - [ ] No bare `except:` blocks
   - [ ] `encoding="utf-8"` on all `open()` calls
   - [ ] Type hints on public functions
   - [ ] Context managers for resource handling
   - [ ] No hardcoded secrets or credentials
   - [ ] Proper error logging with context
   - [ ] No mutable default arguments
   - [ ] Dependencies pinned in requirements.txt

4. **Report findings** organized by severity:
   - Critical (must fix)
   - Warning (should fix)
   - Suggestion (could improve)

5. **Fix issues** where the fix is clear and safe.
