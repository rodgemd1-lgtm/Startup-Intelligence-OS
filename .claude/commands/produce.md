---
description: Start and manage film/image productions — create, orchestrate, advance, and deliver content across 6 formats
argument-hint: '"brief" [--company company_id] [--format film|reel|photo|carousel|image|documentary] [--auto]'
---

Use the `film-production` skill to handle the following production request:

$ARGUMENTS

## Parse the Request

Extract from the arguments above:

1. **Brief** — The production description or creative brief (required, quoted string)
2. **Company** — `--company` value, defaults to `founder-intelligence-os`
3. **Format** — `--format` value, one of: `film`, `reel`, `photo`, `carousel`, `image`, `documentary`. If not specified, infer from the brief (e.g., "Instagram reel" = reel, "product photos" = photo, "brand anthem" = film). Default to `image` if ambiguous.
4. **Auto flag** — If `--auto` is present, run fully autonomous production through refinement phase

## Execute the Production

### Step 1: Start the production

Call `mcp__susan-intelligence__start_production` with:
- `brief`: the extracted brief text
- `company_id`: the company namespace
- `format`: the selected format

This returns a `production_id`. Store it for all subsequent calls.

### Step 2: Choose execution mode

**If `--auto` flag is present:**
- Call `mcp__susan-intelligence__auto_run_production` with the `production_id`
- This runs the full pipeline autonomously: design → storyboard → generation → refinement
- Monitor progress and report final status when complete

**If no `--auto` flag:**
- Call `mcp__susan-intelligence__orchestrate_production` with the `production_id`
- This auto-assigns design-phase agents and advances to the first phase
- Show the user what agents were assigned and what the next steps are

### Step 3: Report status

After execution, call `mcp__susan-intelligence__get_production_status` with the `production_id` and present:

```
Production started: "{brief}"

  ID:       {production_id}
  Format:   {format}
  Company:  {company_id}
  Phase:    {current_phase}
  Status:   {status}

Assigned agents:
  - {agent_name} ({role})
  - ...

Next steps:
  - {what the user should do next or what will happen next}
```

If the production reached refinement or delivered phase, also show quality gate results and any deliverables.

## Error Handling

- If `start_production` fails, report the error and suggest checking company_id or format
- If `orchestrate_production` fails, check whether agents are available for the chosen format
- If `auto_run_production` stalls, call `get_production_status` to diagnose which phase is blocked
- Always surface actionable next steps, never leave the user without a clear path forward
