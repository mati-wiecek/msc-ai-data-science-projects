# Security Policy

This repository is a research scaffold. It must not contain real patient-identifiable data, NHS data extracts, credentials, API keys or private access tokens.

## Reporting a security issue

If you discover that sensitive information has been committed, immediately:

1. stop using the repository publicly;
2. rotate any exposed credentials;
3. remove the sensitive content from history using an approved process;
4. follow the relevant university, organisational or NHS information governance process where applicable.

## Local development rules

- Store secrets in `.env`, never in tracked files.
- Store restricted datasets outside this repository.
- Use synthetic or approved public data only.
- Treat all EHR-like data as sensitive during development.
