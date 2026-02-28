When Claude Code creates or updates code that prompts users for input, all user input MUST be sanitized and validated before use.

## Required Behaviour

### Command-line and terminal input

1. **Type validation** — Verify that the user's response matches the expected type (string, integer, float, date, file path, etc.) before processing it. If the input is invalid, display a clear error message and re-prompt.

2. **Length and range checks** — Enforce reasonable limits on input length and numeric ranges to prevent buffer overflows, excessive memory usage, or nonsensical values.

3. **Path sanitization** — If the input is a file path, resolve it to an absolute path and verify it does not traverse outside expected directories (e.g. reject `../../etc/passwd`).

4. **Injection prevention** — If user input is incorporated into shell commands, SQL queries, file names, or HTML output, escape or parameterise it appropriately. Never pass raw user input directly into `os.system()`, `subprocess.run(shell=True)`, string-concatenated SQL, or `innerHTML`.

### Web forms and web applications

5. **Server-side validation** — Always validate and sanitise form input on the server side, even if client-side validation is also present. Client-side validation is for user experience only and can be bypassed.

6. **CSRF protection** — Include CSRF tokens in forms that perform state-changing operations.

7. **XSS prevention** — Escape all user-supplied data before rendering it in HTML. Use template engines' built-in escaping by default.

## When This Skill Applies

- Any code that accepts input from a user, whether via terminal prompts, command-line arguments, web forms, API request bodies, or configuration file values.
