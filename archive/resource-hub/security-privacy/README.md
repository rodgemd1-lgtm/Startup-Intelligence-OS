# Security & Privacy — SOC 2, GDPR, OWASP & Cloud Security

> Security best practices, compliance automation, and privacy frameworks for AI startups.

---

## 1. Security Roadmap by Stage

### Day 1 (Non-Negotiable)
- [ ] MFA on all accounts (GitHub, AWS, Google, etc.)
- [ ] Secrets management (never commit secrets to git)
- [ ] HTTPS everywhere
- [ ] Password hashing (bcrypt/argon2)
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection
- [ ] Rate limiting on auth endpoints
- [ ] Dependency vulnerability scanning (Dependabot)

### Pre-$500K ARR
- [ ] SOC 2 Type I preparation
- [ ] Security policy documentation
- [ ] Incident response plan
- [ ] Employee security training
- [ ] Access control reviews (quarterly)
- [ ] Penetration testing (annual)

### Pre-$2M ARR
- [ ] SOC 2 Type II certification
- [ ] GDPR compliance (if EU users)
- [ ] Bug bounty program
- [ ] Security team or contractor
- [ ] Advanced monitoring and alerting
- [ ] Data classification policy

---

## 2. SOC 2 Compliance

### SOC 2 Trust Service Criteria
| Criteria | What It Covers |
|----------|---------------|
| **Security** (required) | Protection against unauthorized access |
| **Availability** | System uptime and performance |
| **Processing Integrity** | Accurate, complete data processing |
| **Confidentiality** | Protection of confidential information |
| **Privacy** | Personal information handling |

### SOC 2 Automation Tools (2026)
| Tool | Pricing | Key Feature |
|------|---------|-------------|
| **Vanta** | $10K+/yr | Market leader, 300+ integrations |
| **Drata** | $8K+/yr | Strong automation, good UX |
| **TryComp AI** | $3K+/yr | AI-powered, budget-friendly |
| **EasyAudit** | Custom | AI agents for compliance |
| **Secureframe** | $8K+/yr | Fast onboarding |
| **Tugboat Logic** (OneTrust) | Custom | Enterprise-grade |

### SOC 2 Timeline
1. **Month 1-2**: Choose tool, implement controls
2. **Month 3**: Internal readiness assessment
3. **Month 4-5**: SOC 2 Type I audit
4. **Month 5-11**: Observation period
5. **Month 12**: SOC 2 Type II audit

---

## 3. OWASP Top 10 (2025) Checklist

| # | Risk | Prevention |
|---|------|-----------|
| 1 | **Broken Access Control** | RBAC, deny by default, test authorization |
| 2 | **Cryptographic Failures** | TLS everywhere, strong hashing, key management |
| 3 | **Injection** | Parameterized queries, input validation, ORM |
| 4 | **Insecure Design** | Threat modeling, secure design patterns |
| 5 | **Security Misconfiguration** | Hardened defaults, remove unused features |
| 6 | **Vulnerable Components** | Dependency scanning, automated updates |
| 7 | **Auth & Session Failures** | MFA, session timeouts, secure cookies |
| 8 | **Software Integrity Failures** | CI/CD security, signed builds, SBOMs |
| 9 | **Logging & Monitoring Failures** | Centralized logging, alerting, audit trails |
| 10 | **SSRF** | Allowlist URLs, validate redirects |

---

## 4. GDPR Compliance

### GDPR Checklist for Startups
- [ ] Privacy policy (clear, accessible)
- [ ] Cookie consent banner (CookieYes, Osano)
- [ ] Data processing records (Article 30)
- [ ] Data subject rights (access, deletion, portability)
- [ ] Data Processing Agreements with vendors
- [ ] Privacy by design in product development
- [ ] Data breach notification process (72-hour rule)
- [ ] International data transfer safeguards (SCCs)

### GDPR Tools
| Tool | Purpose |
|------|---------|
| **CookieYes** | Cookie consent management |
| **OneTrust** | Privacy management platform |
| **Osano** | Consent management |
| **Transcend** | Data subject request automation |
| **DataGrail** | Privacy management |

---

## 5. AI-Specific Security

### AI Security Risks
| Risk | Mitigation |
|------|-----------|
| **Prompt injection** | Input validation, output filtering, sandboxing |
| **Data poisoning** | Training data validation, anomaly detection |
| **Model extraction** | Rate limiting, watermarking, access controls |
| **PII in training data** | Data anonymization, PII detection, filtering |
| **Hallucination risks** | Output validation, human-in-the-loop, guardrails |
| **Supply chain** | Model provenance, signed artifacts |

### AI Governance Framework
1. **Model cards**: Document model capabilities, limitations, biases
2. **Data lineage**: Track all training data sources and licenses
3. **Evaluation**: Regular bias and fairness testing
4. **Access control**: Role-based access to models and data
5. **Audit logging**: Track all model inputs/outputs
6. **Incident response**: Plan for AI-specific incidents

---

## 6. Cloud Security

### AWS Security Essentials
- [ ] Root account MFA + no daily use
- [ ] IAM roles (not access keys) for services
- [ ] VPC with private subnets for databases
- [ ] S3 bucket policies (no public by default)
- [ ] CloudTrail enabled for audit logging
- [ ] GuardDuty for threat detection
- [ ] AWS Config for compliance rules

### Secrets Management
| Tool | Purpose |
|------|---------|
| **1Password** | Team password management |
| **AWS Secrets Manager** | Application secrets |
| **Doppler** | Secrets orchestration |
| **Infisical** | Open-source secrets management |
| **Vault (HashiCorp)** | Enterprise secrets |

### Security Monitoring
| Tool | Purpose |
|------|---------|
| **Sentry** | Error tracking (reveals security issues) |
| **Datadog Security** | SIEM, threat detection |
| **Snyk** | Dependency vulnerability scanning |
| **Socket** | Supply chain security |
| **GitGuardian** | Secret detection in code |

---

## Sources

| Source | URL |
|--------|-----|
| Vanta — SOC 2 Compliance Software 2026 | [vanta.com](https://www.vanta.com/resources/best-soc-2-compliance-software) |
| Vanta vs Drata Comparison | [trycomp.ai](https://trycomp.ai/vanta-vs-drata) |
| EasyAudit — AI for Compliance | [easyaudit.ai](https://www.easyaudit.ai/) |
| HackerNoon — SOC 2 Platforms 2025 | [hackernoon.com](https://hackernoon.com/7-of-the-best-soc-2-compliance-software-platforms-in-2025) |
| Vanta — New in Vanta Jan 2026 | [vanta.com](https://www.vanta.com/resources/new-in-vanta-january-2026) |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
