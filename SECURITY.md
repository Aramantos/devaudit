# Security Policy

DevAudit is a small, solo-maintained open-source project. Thank you for taking the time to report a vulnerability responsibly.

## Reporting a Vulnerability

Please do **not** open a public GitHub issue for security problems.

Preferred: use [GitHub Security Advisories](https://github.com/Aramantos/devaudit/security/advisories/new) (private vulnerability reporting) on this repo. This lets us discuss and fix the issue before it's public.

Fallback: email **aramantosdigital@gmail.com** if you can't use GitHub Advisories for any reason.

Include what you can:
- What you found and why it's a security issue
- Steps to reproduce, or a proof of concept
- Affected version / commit
- Your assessment of impact (optional, but helpful)

## Response Targets

This is a solo-maintained project, so responses are best-effort, not guaranteed:
- **Acknowledgement:** within 7 days of your report
- **Fix or mitigation:** no fixed SLA, but you'll be kept informed of progress
- **Credit:** you'll be credited in the advisory/release notes unless you ask not to be

## Supported Versions

Only the latest release line gets security fixes. Older versions are not patched, please upgrade.

| Version       | Supported |
| ------------- | --------- |
| Current source tree (0.3.x, unreleased) and the upcoming v0.4.0 release | Yes |
| v0.1.0 (the only PyPI release to date) and anything older | No, please upgrade |

## Scope Notes Specific to DevAudit

A few things about how this tool works that matter for what counts as a vulnerability here:

- **Local-only server, no auth by design.** `devaudit serve` binds to localhost and has no authentication, because it's meant to run on your own machine for your own eyes only. If you find a way for the server to bind to a non-localhost interface, accept remote connections, or otherwise break that "local machine only" assumption, that's a real bug, please report it.
- **Scan history is local.** Results are stored under `~/.devaudit/` on your own machine. There is no cloud sync of scan data by default.
- **AI features are opt-in and disabled by default.** If you explicitly enable the `[ai]` extra and configure it, scan summaries are sent to **your own** Google Cloud project, using your own credentials, not to any Aramantos-run service. If you find a path where AI features activate without explicit opt-in, or send data anywhere other than the user's own configured GCP project, that's a serious issue, please report it.
- **No telemetry.** DevAudit does not phone home. If you find evidence it does, that's a bug worth reporting.

## Out of Scope

- Vulnerabilities that require local admin/root access you already have (this tool audits your own machine, by design)
- Social engineering
- Issues in third-party dependencies (please report those upstream; we'll still take a report so we can track and update)
