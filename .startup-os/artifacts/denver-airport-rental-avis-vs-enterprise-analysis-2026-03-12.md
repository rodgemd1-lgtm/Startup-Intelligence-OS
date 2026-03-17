# Denver Airport Rental Competitive Analysis: Avis vs Enterprise (2026-03-12)

## Objective
Define what Avis should do in the Denver airport rental segment to win share against Enterprise, using available local scrape artifacts and a pragmatic operating plan.

## Framing
Current scrape artifacts exist under:
- `susan-team-architect/backend/data/domains/enterprise_rental_intelligence/datasets/customer_review_training_seed/runs/`

Latest run:
- `enterprise_multitool_20260312T204814Z`

Observed hard facts from run metadata:
- Exa/Brave/Firecrawl/Apify are key-gated in this environment and were skipped.
- Jina attempted but returned 403 for target review URLs.
- Therefore, present conclusions are directional and should be upgraded once provider-backed payloads are collected.

## Options
1. **Price-first war**
   - compete via lower headline rates and coupons
   - risk: race-to-bottom margin compression

2. **Speed + certainty play (recommended)**
   - promise shortest checkout/pickup time, guaranteed class availability, and transparent total price at booking
   - combine with frictionless rebook/extend flows

3. **Premium trust play**
   - focus on fleet quality guarantees, cleanliness confidence, and service recovery SLAs
   - risk: may miss value-sensitive travelers unless bundled with selective offers

## Recommendation
Avis should run a **Speed + certainty play** for Denver airport with surgical price support:
- guarantee pickup SLA windows (e.g., "in-car in <12 minutes")
- show total out-the-door price pre-arrival (base + fees + expected add-ons)
- provide category reliability guardrails (or automatic upgrade credits)
- implement aggressive service recovery on queue failures and vehicle mismatch events
- support all of this with weekly competitor price and review-theme monitoring

## Assumptions
- Airport renters over-index on reliability and time certainty vs broad market leisure renters.
- Enterprise advantage likely includes operational consistency and trust familiarity.
- Avis can change branch-level operations and messaging faster than it can sustainably underprice all competitors.

## Risks
- If operational SLA promises are not consistently met, trust damage can exceed gains.
- If Enterprise counters with rapid queue/process improvements, differentiation narrows.
- Without actual provider-ingested review payloads, some hypotheses remain weakly evidenced.

## What Avis should do next in DEN airport section (specific actions)
1. Publish a **DEN airport guarantee** page and in-flow badge:
   - "Pickup time guarantee"
   - "Vehicle class guarantee"
   - "Transparent total price"
2. Add **arrival-intent segmentation**:
   - business traveler fast-lane experience
   - family/ski traveler baggage + vehicle fit recommendations
3. Run **service recovery automation**:
   - if pickup SLA breached, auto-credit + priority counter routing
4. Weekly **competitor watchtower** (Enterprise + others):
   - price ladder snapshots
   - review-theme shifts
   - queue-time social proof collection
5. Build a **Denver holdout experiment**:
   - control: current flow
   - treatment: guarantee-first flow
   - KPIs: booking conversion, no-show, cancellation, review sentiment, repeat rate

## Artifacts created or updated
- `.startup-os/artifacts/team-assembly-james-denver-airport-rental.yaml`
- `.startup-os/artifacts/enterprise-rental-researcher-connection.yaml`
- `.susan/project-context.yaml`

## Next actions
- Load provider keys into one of:
  - `susan-team-architect/backend/.env`
  - repo root `.env`
  - `.startup-os/.env`
- Re-run `scripts/run_enterprise_rental_multitool_scrape.py` until non-empty Exa/Brave/Firecrawl/Apify payloads are captured.
- Recompute this analysis from actual review text and contradiction scan outputs.
