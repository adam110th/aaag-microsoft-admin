When Claude Code creates or updates scripts that make network requests, API calls, database queries, subprocess invocations, or other external I/O operations, reasonable timeout values MUST be included.

## Required Behaviour

1. **No indefinite blocking** — Never allow an external operation to block indefinitely. Every network call, database query, and subprocess invocation must have a timeout.

2. **Use language-appropriate mechanisms:**
   - **Python** — `timeout` parameter in `requests`, `httpx`, `urllib3`; `asyncio.wait_for()` for async code; `subprocess.run(timeout=...)` for subprocesses
   - **JavaScript/TypeScript** — `AbortController` with `fetch`; `setTimeout` for custom timeouts
   - **Go** — `context.WithTimeout()` or `context.WithDeadline()`

3. **Sensible defaults:**
   - HTTP requests: 30 seconds
   - Database queries: 60 seconds
   - Subprocess invocations: 120 seconds
   - File downloads: scale with expected file size, but never unlimited

4. **Make timeouts configurable** — Where appropriate, allow timeout values to be overridden via command-line arguments, environment variables, or configuration files.

5. **Handle timeouts gracefully** — When a timeout occurs, catch the timeout exception, log a clear error message explaining that the operation timed out, and suggest the user check their network connection or try again.

## When This Skill Applies

- Every script that makes network requests, API calls, database queries, subprocess invocations, or any other external I/O operation.
