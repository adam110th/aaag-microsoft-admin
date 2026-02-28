---
description: Work on a JIRA/Linear ticket end-to-end
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git:*), Bash(gh:*), Bash(pip:*), Bash(pytest:*), Bash(ruff:*), Bash(pyright:*), mcp__jira__*, mcp__github__*, mcp__linear__*
---

# Ticket Workflow

Work on ticket: $ARGUMENTS

## Instructions

### 1. Read the Ticket

First, fetch and understand the ticket:

```
Use the JIRA/Linear MCP tools to:
- Get ticket details (title, description, acceptance criteria)
- Check linked tickets or epics
- Review any comments or attachments
```

Summarize:
- What needs to be done
- Acceptance criteria
- Any blockers or dependencies

### 2. Explore the Codebase

Before coding:
- Search for related code
- Understand the current implementation
- Identify files that need changes
- Check for existing tests

### 3. Create a Branch

```bash
git checkout -b {initials}/{ticket-id}-{brief-description}
```

### 4. Implement the Changes

- Follow project patterns (check relevant skills)
- Write tests first (TDD) with pytest
- Run `ruff check` and `pyright` after changes
- Make incremental commits

### 5. Update the Ticket

As you work:
- Add comments with progress updates
- Update status (In Progress -> In Review)
- Log any blockers or questions

### 6. Create PR and Link

When ready:
- Run full test suite: `pytest`
- Run linting: `ruff check .`
- Run type checks: `pyright`
- Create PR with `gh pr create`
- Link the PR to the ticket
- Add ticket ID to PR title: `feat(PROJ-123): description`

### 7. If You Find a Bug

If you discover an unrelated bug while working:
1. Create a new ticket with details
2. Link it to the current ticket if related
3. Note it in the PR description
4. Continue with original task

## Example Workflow

```
You: /ticket PROJ-123

Claude:
1. Fetching PROJ-123 from JIRA...
   Title: Add user profile CSV export
   Acceptance Criteria:
   - [ ] Export button on profile page
   - [ ] CSV includes name, email, join date
   - [ ] Handle large datasets with streaming

2. Searching codebase for related code...
   Found: src/views/profile.py
   Found: src/utils/export.py
   Found: tests/test_export.py

3. Creating branch: aw/PROJ-123-profile-csv-export

4. Writing failing test first (TDD)...
   Running pytest... 1 failed

5. Implementing export feature...
   Running pytest... 1 passed
   Running ruff check... clean
   Running pyright... no errors

6. Updating JIRA status to "In Review"
   Adding comment: "Implementation complete, PR ready"

7. Creating PR linked to PROJ-123...
   PR #456: feat(PROJ-123): add CSV export to user profile
```
