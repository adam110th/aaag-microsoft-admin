---
description: Check if documentation is in sync with code
allowed-tools: Read, Glob, Grep, Bash(git:*)
---

# Documentation Sync

Check if documentation matches the current code state.

## Instructions

1. **Find recent code changes**:
   ```bash
   git log --since="30 days ago" --name-only --pretty=format: -- "*.py" | sort -u
   ```

2. **Find related documentation**:
   - Search `/docs/` for files mentioning changed code
   - Check README files near changed code
   - Look for docstrings in changed files

3. **Verify documentation accuracy**:
   - Do code examples still work?
   - Are function signatures correct?
   - Are type hints up to date?
   - Does `requirements.txt` match actual imports?

4. **Report only actual problems**:
   - Documentation is a living document
   - Only flag things that are WRONG, not missing
   - Don't suggest documentation for documentation's sake

5. **Output a checklist** of documentation that needs updating.
