# Department Ten-State Benchmark Packet

## Research Question

What exact data-source and capability conditions must exist before a Startup Intelligence OS section or department can honestly claim `10/10` maturity?

## Definitions

- `10/10`: best in the world, not merely functional
- `data-source maturity`: the department has the right source classes, refresh paths, and proof of access
- `capability maturity`: the department has the right operating behaviors, protocols, visibility, and feedback loops
- `verification`: a file-backed proof path exists for the claimed source or capability

## Methods

1. Start from the existing department registry under `.startup-os/departments`.
2. Normalize all departments and core sections onto one shared category system for data and capabilities.
3. Map proof paths to files already present in the repo: department YAML, artifacts, protocols, manifests, runner scripts, and studio assets.
4. Add missing live-web manifests for the departments that still lacked a declared source stack.
5. Render the result into a visual dashboard so the operator can review the score surface directly.

## Source Stack

- `.startup-os/departments/*.yaml`
- `.startup-os/capabilities/*.yaml`
- `.startup-os/artifacts/startup-intelligence-os-full-maturity-roadmap-2026-03-12.md`
- `.startup-os/artifacts/startup-intelligence-os-zero-to-ten-maturity-system-2026-03-12.md`
- `susan-team-architect/backend/data/scrape_manifests/*.yaml`
- `susan-team-architect/backend/data/studio_assets/**/*`
- `susan-team-architect/backend/scripts/run_department_gap_closure_wave.py`

## Benchmark Targets

For a section or department to claim `10/10`, it must have:

- an explicit source stack
- a refresh or automation path
- visible proof paths
- reusable output artifacts
- a scorecard
- writeback behavior
- operator visibility
- a review or evaluation loop

## Synthesis

The current system is strongest on `structured contracts`, `intake/diagnosis`, `reusable artifacts`, and `handoff rules`. It is weakest on `evaluation loops`, `automation refresh`, and `operator-visible proof` for several departments. Data maturity is uneven for the core departments that did not yet have declared live-web source manifests. This packet closes that definition gap and moves the OS toward a verifiable maturity model.

## Unknowns

- Which departments should count certain live metrics as required versus optional?
- Which proof paths should only count after a live crawl or refresh has completed successfully?
- How much of the dashboard should move into the operator app versus stay as an artifact-first verification surface?

## Next Research Steps

1. Execute the expanded gap-closure manifests and refresh proof paths with run summaries.
2. Add benchmark datasets and case libraries for the weakest departments.
3. Bring the verification matrix into the operator console.

