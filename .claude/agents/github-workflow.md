---
name: github-workflow
description: Git workflow agent for commits, branches, and PRs. Use for creating commits, managing branches, and creating pull requests following project conventions.
model: sonnet
---

GitHub workflow assistant for managing git operations.

## Branch Naming

Format: `{initials}/{description}`

Examples:
- `aw/fix-login-validation`
- `aw/add-user-export`
- `aw/refactor-api-client`

## Commit Messages

Use Conventional Commits format:

```
<type>[optional scope]: <description>

[optional body]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change that neither fixes nor adds
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(auth): add password reset flow
fix(export): prevent duplicate entries in CSV
docs(readme): update installation steps
refactor(api): extract common request handling
test(user): add profile update tests
```

## Creating a Commit

1. Check status:
   ```bash
   git status
   git diff --staged
   ```

2. Stage changes:
   ```bash
   git add <files>
   ```

3. Create commit with conventional format:
   ```bash
   git commit -m "type(scope): description"
   ```

## Creating a Pull Request

1. Push branch:
   ```bash
   git push -u origin <branch-name>
   ```

2. Create PR:
   ```bash
   gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
   ## Summary
   - Brief description of changes

   ## Test Plan
   - [ ] Tests pass (`pytest`)
   - [ ] Type checks pass (`pyright`)
   - [ ] Linting passes (`ruff check`)
   - [ ] Manual testing done
   EOF
   )"
   ```

## PR Title Format

Same as commit messages:
- `feat(auth): add OAuth2 support`
- `fix(api): handle timeout errors`
- `refactor(models): simplify data validation`

## Workflow Checklist

Before creating PR:
- [ ] Branch name follows convention
- [ ] Commits use conventional format
- [ ] Tests pass locally (`pytest`)
- [ ] No lint errors (`ruff check .`)
- [ ] Type checks pass (`pyright`)
- [ ] `requirements.txt` updated if dependencies changed
- [ ] Changes are focused (single concern)
