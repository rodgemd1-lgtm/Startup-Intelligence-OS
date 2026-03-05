# Foundation & Legal — AI Startup Playbook

> Intelligence for taking a startup from 0 → $10M: Legal formation, IP, equity, compliance.

---

## 1. Entity Formation

### Delaware C-Corp (The Default for VC-Backed Startups)

**Why Delaware:**
- Business-friendly corporate law, predictable governance
- Investors trust Delaware courts (Court of Chancery)
- Standard for institutional fundraising — avoids restructuring later

**Key Steps:**
1. Incorporate Delaware C-Corp via Stripe Atlas, Clerky, or lawyer
2. Apply for EIN (federal tax ID)
3. Register as foreign entity in your operating state
4. Open business bank account (Mercury, Brex, or SVB)
5. File 83(b) elections within 30 days of stock grants

### Alternative: LLC → C-Corp Conversion
- OK for bootstrapping initially, but conversion is messy after equity distribution
- If VC is in your future, start as C-Corp

### Sources
| Source | URL |
|--------|-----|
| Beancount — Startup Incorporation Guide (Jan 2026) | [beancount.io](https://beancount.io/blog/2026/01/26/startup-incorporation-guide-delaware-c-corp-llc) |
| Legal Nodes — Delaware Incorporation for Founders | [legalnodes.com](https://www.legalnodes.com/article/delaware-incorporation-founders-guide) |
| Terms.Law — Delaware for AI, SaaS & Tech | [terms.law](https://terms.law/2025/11/23/delaware-incorporation-for-ai-saas-tech-companies/) |
| Inkle — Delaware C-Corp Ultimate Guide | [inkle.ai](https://www.inkle.ai/blog/delaware-c-corp-the-ultimate-guide-for-success) |

---

## 2. Equity & Vesting

### Standard Structure
- **4-year vesting, 1-year cliff** — industry standard
- Founder equity should be subject to vesting (protects against early departures)
- Reserve 10-20% option pool for employees

### SAFE Notes (Simple Agreement for Future Equity)
- Standard for pre-seed/seed (Y Combinator SAFE template)
- Post-money SAFEs are now standard (clearer dilution math)
- Typical caps: $5-15M for pre-seed, $10-25M for seed

### 83(b) Election
- **CRITICAL**: File within 30 days of receiving restricted stock
- Failure = potentially massive tax liability on vesting
- No extensions, no exceptions

### Cap Table Management
- Use Carta, Pulley, or AngelList for cap table
- Keep it clean from day 1 — messy cap tables kill deals

---

## 3. IP Protection for AI Startups

### The IP Checklist (from Traverse Legal)

**Before You Build:**
- [ ] Ensure all founders assign IP to the company (IP Assignment Agreement)
- [ ] Verify no university IP claims (if research-origin)
- [ ] Get tech transfer license if applicable
- [ ] Document all pre-existing IP vs. new IP

**During Development:**
- [ ] All contractors sign IP assignment + NDA
- [ ] Track open-source licenses (GPL, Apache, MIT implications)
- [ ] Document model training data provenance
- [ ] Maintain invention disclosure logs

**Before Fundraising:**
- [ ] Clean IP audit (no orphan code, no unlicensed data)
- [ ] Patent strategy (provisional patents for core innovations)
- [ ] Trademark your brand name and logo
- [ ] Terms of Service and Privacy Policy for product

### AI-Specific IP Considerations
- **Training data licensing** — verify rights for all training data
- **Model output ownership** — clarify in ToS who owns AI-generated content
- **Open-source model licenses** — Llama, Mistral have specific restrictions
- **Employee invention assignment** — ensure all employees assign AI innovations

### Sources
| Source | URL |
|--------|-----|
| Traverse Legal — Ultimate Legal Checklist for AI Startups | [traverselegal.com](https://www.traverselegal.com/blog/legal-checklist-for-ai-startups/) |
| Delaware Tax Expert — Legal Checklist for AI Startups in Delaware | [delawaretaxexpert.com](https://delawaretaxexpert.com/tax/legal-checklist-for-ai-startups-in-delaware/) |
| Herzog Law — PBC vs C-Corp for Generative AI Startups | [herzoglaw.co.il](https://herzoglaw.co.il/en/news-and-insights/white-paper-choosing-between-a-delaware-public-benefit-corporation-and-a-traditional-c-corporation-structure-for-generative-ai-start-ups/) |

---

## 4. Compliance & Regulatory

### SOC 2 Compliance
- Start SOC 2 Type I early (investors increasingly require it)
- **Vanta** — market leader, automated evidence collection ($10K+/yr)
- **Drata** — strong alternative, good for startups
- **TryComp AI** — budget-friendly, AI-powered compliance
- **EasyAudit** — AI agents for SOC 2, ISO 27001, HIPAA

### GDPR / Privacy
- Required if you have ANY EU users
- Appoint DPO if processing significant personal data
- Implement data deletion/export capabilities
- Cookie consent + privacy policy

### AI-Specific Regulations (2026)
- **EU AI Act** — risk-based framework, high-risk AI systems need conformity assessment
- **US Executive Order on AI** — reporting requirements for large models
- **State laws** — Colorado, Illinois have AI-specific regulations emerging

### Sources
| Source | URL |
|--------|-----|
| Vanta — Best SOC 2 Compliance Software 2026 | [vanta.com](https://www.vanta.com/resources/best-soc-2-compliance-software) |
| TryComp AI — Vanta vs Drata Comparison | [trycomp.ai](https://trycomp.ai/vanta-vs-drata) |
| EasyAudit — AI Agents for Compliance | [easyaudit.ai](https://www.easyaudit.ai/) |
| HackerNoon — 7 Best SOC 2 Platforms in 2025 | [hackernoon.com](https://hackernoon.com/7-of-the-best-soc-2-compliance-software-platforms-in-2025) |

---

## 5. Founder Agreements

### Essential Documents
1. **Founder Agreement** — roles, equity splits, IP assignment, departure terms
2. **Bylaws** — corporate governance, board structure, voting rights
3. **Stock Purchase Agreement** — with vesting schedules
4. **Confidentiality & Invention Assignment (CIIA)** — for all team members
5. **Advisor Agreement** — standard 0.25-1% equity, 2-year vesting

### Key Clauses
- **Non-compete** (where enforceable) and **non-solicitation**
- **Drag-along / Tag-along** rights
- **Right of first refusal** on secondary sales
- **Accelerated vesting** triggers (single vs. double trigger)

---

## 6. Banking & Financial Infrastructure

### Recommended Stack
| Tool | Purpose |
|------|---------|
| **Mercury** | Primary business banking (startup-friendly, integrations) |
| **Brex** | Corporate credit card (no personal guarantee) |
| **Stripe Atlas** | Incorporation + Stripe payments |
| **Gusto** or **Rippling** | Payroll & HR |
| **Bench** or **Pilot** | Bookkeeping |
| **Carta** or **Pulley** | Cap table management |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
