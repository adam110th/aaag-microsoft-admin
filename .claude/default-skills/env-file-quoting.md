When Claude Code creates or updates `.env` or `.env.example` files, all variable values MUST be wrapped in single quotes.

## Why

Many environment variable values — particularly API keys, tokens, passwords, and connection strings — contain `#` characters. In `.env` files, `#` marks the start of an inline comment. Without quoting, everything after the `#` is silently stripped, resulting in truncated values that cause authentication failures, cryptic API errors, or broken connections that are extremely difficult to diagnose.

Single quotes are used instead of double quotes because double quotes allow variable interpolation (`$VAR`), which can cause unexpected substitutions if a value happens to contain `$`.

## Required Behaviour

1. **Always single-quote values** — Every variable assignment in a `.env` or `.env.example` file must use single quotes around the value:
   ```
   # Correct
   API_KEY='sk-abc123#def456'
   DATABASE_URL='postgresql://user:p@ss#word@localhost:5432/db'
   SECRET_KEY='my-secret-with-#-and-$-chars'

   # Wrong — value will be truncated at the #
   API_KEY=sk-abc123#def456
   DATABASE_URL=postgresql://user:p@ss#word@localhost:5432/db
   ```

2. **Apply to both `.env` and `.env.example`** — Check and fix quoting in both files whenever either is created or updated.

3. **Empty values** — Use empty single quotes for placeholder or empty values:
   ```
   API_KEY=''
   ```

4. **Placeholder values** — When using placeholder text, still wrap in single quotes:
   ```
   API_KEY='YOUR_API_KEY_HERE'
   ```

5. **Comments** — Comments on their own line (starting with `#`) are unaffected and should remain unquoted:
   ```
   # This is a comment — no quoting needed
   API_KEY='value-here'
   ```

6. **Existing `.env` files** — When updating an existing `.env` file that has unquoted values, fix the quoting on all values, not just the ones being changed.

7. **Scripts that generate `.env` files** — When Claude Code writes a script that programmatically generates or modifies `.env` files, the script must wrap all values in single quotes when writing them.

## When This Skill Applies

- Every time Claude Code creates, updates, or generates a `.env`, `.env.example`, `.env.local`, `.env.production`, `.env.development`, `.env.test`, or any other dotenv-format file.
- Every time Claude Code writes a script that programmatically creates or modifies dotenv files.
