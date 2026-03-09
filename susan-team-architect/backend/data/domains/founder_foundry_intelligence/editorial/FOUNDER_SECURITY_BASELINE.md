# Founder Security Baseline

The foundry should give every new company a practical security floor from day one.

## Minimum controls

- server-side validation
- least-privilege credentials
- secrets outside the repo
- row-level access controls where user data is stored
- auditability for sensitive actions
- dependency and auth review before launch

## Security operating model

- Sentinel defines the baseline
- Atlas implements the platform shape
- Forge verifies failure modes and regressions
- Susan blocks launches that violate the baseline in high-risk domains
