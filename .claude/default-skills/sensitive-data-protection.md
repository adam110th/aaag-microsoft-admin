When Claude Code creates or updates scripts and configuration files, sensitive data MUST NEVER be hardcoded in source code.

## What Counts as Sensitive Data

API keys, tokens, passwords, database connection strings, private keys, OAuth secrets, webhook URLs with embedded tokens, and any other credentials or secrets.

## Required Behaviour

1. **Use environment variables** — Store sensitive values in environment variables and read them at runtime (e.g. `os.environ["API_KEY"]` in Python, `process.env.API_KEY` in Node.js).

2. **Use `.env` files** — For local development, use `.env` files loaded by libraries like `python-dotenv` or `dotenv` for Node.js. The `.env` file MUST be listed in `.gitignore`. If it is not already excluded, add it.

3. **Use placeholders in examples** — When generating example or template code that requires credentials, use clearly marked placeholders (e.g. `YOUR_API_KEY_HERE`) and include a comment explaining how to set the real value via environment variables.

4. **Never commit secrets** — Never commit files that contain real credentials. If a secrets file is accidentally staged, alert the user immediately.

5. **Secret management tools** — For production deployments, recommend appropriate secret management tools (e.g. AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) where applicable.

## When This Skill Applies

- Every script, configuration file, or code sample that Claude Code creates or updates.
