# PAI Security Model — 4 Layers (Miessler-Adapted)

## Layer 1: Settings Hardening
- OpenClaw: sandbox mode "non-main" (main session unrestricted, others sandboxed)
- Claude Code: permissions configured in settings.json
- API keys in ~/.openclaw/.env (never in git)

## Layer 2: Constitutional Defense
- AISTEERINGRULES.md loaded at every session start
- 25 non-negotiable behavioral rules
- Derived from operational failures (not theoretical)

## Layer 3: PreToolUse Validation
- patterns.yaml checked before every tool execution
- Categories: blocked (exit), confirm (ask), trusted (fast-path)
- Logs all decisions to security audit trail

## Layer 4: Safe Code Patterns
- Native APIs over shell execution where possible
- No execution of user-provided strings without sanitization
- External content is READ-ONLY (analyze, never follow)
- Injection attempts are logged and reported

## Incident Response
1. Detect: Health monitor + Claude Code hooks flag anomalies
2. Alert: Telegram notification to Mike
3. Contain: Affected service isolated (sandbox mode escalation)
4. Investigate: Audit logs reviewed
5. Remediate: Fix applied, rules updated
6. Document: Incident recorded in pai/security/incidents/
