# Engineering — Startup Technical Playbook

> Best practices for CI/CD, infrastructure, testing, architecture, and DevOps from 0 → $10M.

---

## 1. Architecture Decision Framework

### Stage-Appropriate Architecture

| Stage | Revenue | Architecture | Why |
|-------|---------|-------------|-----|
| Pre-PMF ($0-100K) | Monolith | Single Next.js/Rails app, managed DB | Speed > everything |
| Early Growth ($100K-1M) | Modular Monolith | Separate concerns internally, API layers | Maintainability without complexity |
| Scaling ($1M-5M) | Service-Oriented | Extract critical paths (auth, billing, AI) | Isolate scaling bottlenecks |
| Growth ($5M-10M) | Microservices (targeted) | Only decompose what needs independent scaling | Don't over-engineer |

### Key Principle
> "Premature microservices kill more startups than monoliths ever will."

---

## 2. Recommended Tech Stack (2026)

### Frontend
| Tool | Purpose | Why |
|------|---------|-----|
| **Next.js 15** | Full-stack React framework | SSR, API routes, edge runtime |
| **shadcn/ui** | Component library | Copy-paste, customizable, Tailwind-native |
| **Tailwind CSS v4** | Styling | Utility-first, AI-friendly, fast iteration |
| **Zustand** or **Jotai** | State management | Lightweight, no boilerplate |
| **TanStack Query** | Server state | Caching, optimistic updates, real-time |

### Backend
| Tool | Purpose | Why |
|------|---------|-----|
| **Node.js + Hono** | API framework | Ultra-fast, edge-compatible, TypeScript-native |
| **Python + FastAPI** | AI/ML services | Best ML ecosystem, async, type-safe |
| **Supabase** | Database + Auth + Storage | Postgres, real-time, row-level security |
| **Drizzle ORM** | TypeScript ORM | Type-safe, fast, SQL-like |

### Infrastructure
| Tool | Purpose | Why |
|------|---------|-----|
| **Vercel** | Frontend hosting | Zero-config deploys, edge functions |
| **Railway** or **Render** | Backend hosting | Simple container deploys, autoscaling |
| **Cloudflare** | CDN, Workers, R2 storage | Global edge network, cheap at scale |
| **AWS** (targeted) | S3, SQS, Lambda for specific needs | When you need specific AWS services |

### AI/ML Infrastructure
| Tool | Purpose | Why |
|------|---------|-----|
| **Anthropic Claude API** | Primary LLM | Best reasoning, tool use, coding |
| **OpenAI API** | Secondary LLM | GPT-4o for vision, embeddings |
| **Pinecone** or **Qdrant** | Vector database | Semantic search, RAG |
| **LangChain** or **LlamaIndex** | LLM orchestration | Agent pipelines, RAG chains |
| **Modal** or **Replicate** | GPU compute | Serverless GPU, model hosting |

---

## 3. CI/CD Pipeline

### Minimum Viable CI/CD
```yaml
# GitHub Actions — every PR
name: CI
on: [pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test
      - run: npm run build
```

### Production Pipeline
1. **PR Created** → lint + typecheck + unit tests
2. **PR Approved** → integration tests + preview deploy
3. **Merged to main** → staging deploy + smoke tests
4. **Staging validated** → production deploy (blue-green)
5. **Post-deploy** → health checks + error monitoring

### Tools
| Tool | Purpose |
|------|---------|
| **GitHub Actions** | CI/CD (free for public repos, generous limits) |
| **Turborepo** | Monorepo build orchestration, caching |
| **Changesets** | Version management, changelogs |
| **Sentry** | Error tracking, performance monitoring |
| **Datadog** or **Grafana** | Infrastructure monitoring |

---

## 4. Testing Strategy

### Testing Pyramid for Startups

```
         /  E2E  \        ← Playwright: critical user flows only
        / Integr.  \      ← API tests, database tests
       /   Unit      \    ← Vitest: business logic, utilities
      /______________\
```

### Pragmatic Approach
- **Unit tests**: Business logic, utility functions, data transformations
- **Integration tests**: API endpoints, database queries, auth flows
- **E2E tests**: Only critical paths (signup, payment, core feature)
- **Skip**: Snapshot tests, CSS tests, trivial getters/setters

### Tools
| Tool | Purpose |
|------|---------|
| **Vitest** | Unit + integration testing (fast, ESM-native) |
| **Playwright** | E2E testing (cross-browser, reliable) |
| **MSW** | API mocking (service worker-based) |
| **Faker.js** | Test data generation |

---

## 5. Code Quality

### Essential Tooling
| Tool | Purpose |
|------|---------|
| **ESLint v9** | Linting (flat config) |
| **Prettier** | Code formatting |
| **TypeScript** (strict mode) | Type safety |
| **Husky** + **lint-staged** | Pre-commit hooks |
| **Conventional Commits** | Commit message standards |

### Code Review Process
1. All PRs require 1 review (2 for critical paths)
2. Use Claude Code for automated review suggestions
3. Max PR size: ~400 lines (break larger changes up)
4. Require passing CI before merge

---

## 6. Security Engineering

### OWASP Top 10 Essentials
- [ ] Input validation on all user inputs
- [ ] Parameterized queries (no raw SQL)
- [ ] CSRF protection on all state-changing endpoints
- [ ] Rate limiting on auth endpoints
- [ ] Content Security Policy headers
- [ ] Dependency vulnerability scanning (Snyk, Dependabot)
- [ ] Secrets management (never commit secrets)

### Auth Stack
| Tool | Purpose |
|------|---------|
| **Clerk** or **Auth0** | Managed auth (fastest to implement) |
| **Supabase Auth** | If already using Supabase |
| **NextAuth.js** | Self-hosted, flexible |

---

## 7. Observability

### Three Pillars
1. **Logs** — Structured JSON logging (Pino, Winston) → Datadog/Loki
2. **Metrics** — Response times, error rates, queue depths → Grafana/Datadog
3. **Traces** — Distributed tracing for AI pipelines → OpenTelemetry

### Error Tracking
- **Sentry** — Error tracking + performance monitoring (free tier is generous)
- Set up alerts for: error rate spikes, p99 latency, 5xx responses

---

## Sources

| Source | URL |
|--------|-----|
| Dev.to — CI/CD Pipeline Best Practices 2025 | [dev.to](https://dev.to/buildkite/ci-cd-pipeline-best-practices-5alo) |
| Dev.to — Docker Security for Startups | [dev.to](https://dev.to/codemaker2015/docker-security-best-practices-1g99) |
| Builder.io — React Component Libraries 2026 | [builder.io](https://www.builder.io/blog/react-component-libraries-2026) |
| UntitledUI — 14 Best React UI Libraries 2026 | [untitledui.com](https://www.untitledui.com/blog/react-component-libraries) |

---

*Compiled from live Exa AI + Firecrawl research, March 2026*
