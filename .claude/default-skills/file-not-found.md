When Claude Code creates or updates scripts that access local files, the script MUST handle the case where a required file is not found.

## Required Behaviour

1. **Detect the missing file** — Catch `FileNotFoundError` (Python), `ENOENT` (Node.js), or the equivalent exception for the language being used.

2. **Notify the user** — Display a clear message stating which file was not found. Include the full file path so the user can verify the expected location.

3. **Prompt for an alternative** — Ask the user to either:
   - Input an alternate file path, or
   - Type `q` or `quit` to exit the script.

   Example:
   ```
   File not found: C:\Users\data\input.xlsx
   Enter an alternate file path (or 'q' to quit):
   ```

4. **Validate the new path** — If the user provides an alternate path, check whether that file exists. If it does not, loop back to the prompt and ask again.

5. **Sanitize input** — Strip leading and trailing whitespace and quotation marks from the user's input path, as users often paste paths wrapped in quotes.

## When This Skill Applies

- Any script that reads from or writes to local files where the file path is configurable, user-supplied, or could reasonably not exist.
