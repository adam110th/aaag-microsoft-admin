When Claude Code generates or updates a webpage or website, the following default files and configurations MUST be created or verified.

## Required Files

### 1. `.htaccess`

If an `.htaccess` file does not exist, create one. If it already exists, verify it includes the items below and offer to add any that are missing.

The `.htaccess` file MUST include:

- **AI crawler blocking** — Block all known AI crawlers and scrapers by default (GPTBot, CCBot, Google-Extended, Bytespider, ClaudeBot, etc.) unless the user directs otherwise.
- **Hotlink prevention** — Prevent other sites from directly linking to images and media files.
- **Gzip compression** — Enable compression for text-based file types (HTML, CSS, JavaScript, JSON, XML, SVG).
- **ETag removal** — Disable ETags to reduce unnecessary server overhead.
- **Security headers** — Add default security headers including `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Content-Security-Policy` with a sensible baseline.
- **Backup and config file blocking** — Deny access to `.bak`, `.old`, `.sql`, `.log`, `.env`, `.ini`, `.yml`, `.yaml`, `.toml`, and other configuration or backup file extensions.

### 2. `robots.txt`

If a `robots.txt` file does not exist, create one. It MUST block all known AI crawlers by default. Ask the user whether they also want to block standard search engine crawlers.

### 3. `favicon.ico`

If no `favicon.ico` exists, create one that reflects the theme or purpose of the website.

### 4. Error pages

Create custom error pages for at minimum the following HTTP status codes, styled consistently with the rest of the site: 400, 401, 403, 404, and 500. Add any other error pages deemed appropriate for the site.

## When This Skill Applies

- Any time Claude Code creates a new webpage, website, or web application.
- Any time Claude Code updates an existing website and the above files are missing or incomplete.
