# Incident Response Playbook

Runbook for responding to security incidents.

## Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P1 — Critical | Active data breach, RLS bypass, secret leak | < 1 hour |
| P2 — High | Vulnerability with known exploit, DoS | < 4 hours |
| P3 — Medium | Misconfiguration, failed auth spikes | < 1 business day |
| P4 — Low | Dependency vulnerability without exploit | Next sprint |

## Response Steps

1. **Detect** — Alert from monitoring, GitHub Advisory, or reporter.
2. **Triage** — Assign severity, identify affected systems.
3. **Contain** — Rotate secrets, disable affected routes, rollback deploy.
4. **Remediate** — Patch, test, deploy fix.
5. **Communicate** — Update `SECURITY.md` if needed, notify reporters per policy.
6. **Post-mortem** — Document in `audit-log.md`, update `hardening.md`.

## Contacts

- **Security lead**: security@stridealytics.com (PGP key on request)
- **On-call**: See `docs/operations/on-call.md` (if exists)
