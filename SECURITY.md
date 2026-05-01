# Security Policy

## Project Security Scope

11Writer is a local-first OSINT and spatial intelligence platform for development, research, source evaluation, and evidence-aware data visualization.

The project may include integrations with public, no-auth, no-signup data sources, including government feeds, environmental alerts, aviation and weather sources, marine context sources, public camera inventories, RSS feeds, and other machine-readable public datasets.

Security matters because this project handles:

- Source URLs and feed configuration
- Local development data
- Public-source records and metadata
- Optional user-provided RSS/feed URLs
- Fixture and replay datasets
- Export/snapshot metadata
- API connectors and local backend routes

This repository should not contain private credentials, private API keys, personal feed tokens, private databases, local logs, or local-only artifacts.

## Supported Versions

This project is under active development. Security review and fixes apply to the current `main` branch only.

| Version / Branch | Supported |
| --- | --- |
| `main` | Yes |
| Older commits / abandoned branches | No |

## Reporting a Vulnerability

If you find a security issue, please report it privately.

Preferred method:

- Open a private security advisory through GitHub Security Advisories, if available.

If GitHub Security Advisories are not available, open a minimal public issue that does **not** include exploit details, secrets, private URLs, or sensitive data. State that you have a security concern and provide a safe way to coordinate.

Please include:

- A short description of the issue
- Affected file(s), route(s), connector(s), or workflow(s)
- Steps to reproduce, if safe to share
- Expected vs. actual behavior
- Whether secrets, tokens, private feed URLs, local files, or user data could be exposed
- Any suggested fix, if available

Please do **not** include:

- Real API keys
- Private RSS/feed URLs
- Google Alerts tokenized feed URLs
- Passwords
- Private database files
- Private logs
- Personal data
- Exploit code that enables abuse against real third-party services

## Sensitive Data Rules

Do not commit sensitive or local-only data to this repository.

Never commit:

- `.env` files
- API keys
- Access tokens
- Private RSS feed URLs
- Tokenized Google Alerts feed URLs
- Private database files
- SQLite runtime databases
- Local logs
- Browser traces
- Playwright reports
- `node_modules`
- Frontend build output
- Local caches
- Private certificates or keys

Allowed:

- `.env.example` files with placeholder values only
- Small deterministic fixtures used for tests
- Synthetic or redacted sample data
- Public documentation links
- Source definitions that do not contain credentials or private tokens

If a private URL or token is accidentally committed, rotate or invalidate it immediately and remove it from repository history if needed.

## RSS and Feed URL Safety

11Writer may support RSS/Atom feeds, including user-created feeds such as Google Alerts.

Tokenized feed URLs must be treated as private secrets.

Do not commit real feed URLs like:

```text
https://www.google.com/alerts/feeds/...
```

Use local environment variables or local private config instead.

Safe example:

```text
CYBERSECURITY_GOOGLE_ALERTS_RSS_URL=
```

Unsafe example:

```text
CYBERSECURITY_GOOGLE_ALERTS_RSS_URL=https://www.google.com/alerts/feeds/private-token-here
```

Google Alerts and similar search-alert feeds should be treated as discovery/media context, not authoritative intelligence.

## Source Integration Rules

New source integrations should follow these rules:

- Prefer official, machine-readable, no-auth sources.
- Do not scrape interactive web apps unless explicitly allowed by source terms and project policy.
- Do not bypass CAPTCHA, login walls, rate limits, tokens, or access controls.
- Do not commit credentials or private endpoint URLs.
- Use fixture-first tests.
- Do not make tests depend on live network availability.
- Preserve provenance and source health.
- Clearly distinguish between:
  - Observed data
  - Inferred data
  - Derived data
  - Scored data
  - Advisory/contextual data
  - Fixture/local data
- Do not overclaim source coverage, freshness, precision, or authority.
- Do not present source context as proof of intent, wrongdoing, causation, damage, or impact unless the source explicitly supports that claim.

## Camera and Webcam Source Rules

Camera and webcam integrations require extra caution.

Allowed:

- Official APIs
- Direct image URLs from verified machine-readable public endpoints
- Fixture-first connector development
- Candidate inventory records
- Endpoint verification metadata
- Sandbox/validation-only connectors

Not allowed:

- CAPTCHA bypass
- Scraping viewer-only interactive web apps
- Pretending a viewer page is a direct image source
- Activating candidate sources without verification
- Claiming orientation, coordinates, or direct-image capability without evidence
- Committing private camera URLs or credentials

Candidate sources must remain inactive until reviewed and validated.

## Export and Snapshot Metadata

Exports and snapshots may contain source summaries, selected entity details, context summaries, source health, and caveats.

Export metadata should be compact and safe.

Do not include:

- Raw secret-bearing URLs
- Private feed URLs
- Credentials
- Large raw source payloads
- Private local paths
- Unnecessary personal data
- Hidden tokens

Export metadata should include caveats where relevant, especially for:

- Fixture/local mode
- Stale or unavailable sources
- Approximate locations
- Representative geometries
- Advisory-only alerts
- Community/volunteer data
- Non-authoritative feeds

## Local Development Security

This project is currently local/development-oriented and is not production-hardened.

Recommended local practices:

- Use a Python virtual environment.
- Use `.env` for private local config.
- Keep `.env` out of Git.
- Run validation before committing.
- Review changed files before staging.
- Avoid `git add .` on mixed worktrees.
- Do not expose the local backend to the public internet without additional hardening.
- Do not run untrusted fixtures or source payloads as code.

## Dependency and Supply Chain Notes

The project uses Python and Node.js dependencies.

Before major releases:

- Review dependency changes.
- Avoid unnecessary packages.
- Prefer maintained libraries.
- Keep package lock files if used by the project workflow.
- Do not commit vendored dependency folders such as `node_modules`.
- Do not commit local virtual environments.

## Security Expectations for Contributors and Agents

Contributors and AI coding agents should:

- Keep changes scoped.
- Avoid broad rewrites unless assigned.
- Preserve source caveats.
- Preserve fixture-first tests.
- Avoid live-network tests.
- Avoid committing secrets or private feed URLs.
- Report suspicious files before staging.
- Use source ownership docs when adding connectors.
- Treat build, lint, and import failures as integration blockers, not excuses to weaken semantics.
- Never remove caveats just to make UI or tests easier.

## Out of Scope

The following are generally out of scope unless explicitly assigned:

- Production deployment hardening
- Authentication and user management
- Enterprise secrets management
- Advanced intrusion detection
- Public internet hosting configuration
- Cloud infrastructure security
- Legal review of every public source license or terms document

Even if out of scope, please report obvious risks.

## Known Development Caveats

Some smoke tests may be affected by local browser or Playwright launch issues on Windows.

Some source integrations operate in fixture mode by default.

Some public sources are rate-limited, delayed, approximate, or incomplete.

Some UI surfaces are operational/minimal during Phase 2 and are not final security-reviewed product UX.

These caveats are not excuses to commit secrets, bypass access controls, or overclaim data meaning. Annoying, yes. Optional, no.

## Response Expectations

Security reports will be reviewed when project maintainers are available.

Expected response process:

1. Acknowledge the report.
2. Reproduce or assess the issue.
3. Classify severity.
4. Fix or document mitigation.
5. Add or update tests when practical.
6. Update docs if the issue affects source handling, exports, config, or contributor workflow.
