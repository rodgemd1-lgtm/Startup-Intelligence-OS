-- Migration: Jake Cost Tracking + Business Pipeline
-- Date: 2026-03-22
-- Purpose: Add tables for smart model cost tracking and deal pipeline management

-- =============================================================================
-- Cost Tracking Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jake_cost_tracking (
    id                  uuid            DEFAULT gen_random_uuid() PRIMARY KEY,
    recorded_at         timestamptz     DEFAULT now(),
    task_type           text,
    employee_name       text,
    task_id             text,
    model               text            NOT NULL,
    input_tokens        integer         DEFAULT 0,
    output_tokens       integer         DEFAULT 0,
    estimated_cost_usd  numeric(10,6)   DEFAULT 0,
    metadata            jsonb           DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_date
    ON jake_cost_tracking(recorded_at);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_employee
    ON jake_cost_tracking(employee_name);

CREATE INDEX IF NOT EXISTS idx_cost_tracking_model
    ON jake_cost_tracking(model);

COMMENT ON TABLE jake_cost_tracking IS
    'Jake model usage and cost tracking — every LLM call logged here for spend visibility.';

-- =============================================================================
-- Business Pipeline — Deals Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jake_deals (
    id          uuid            DEFAULT gen_random_uuid() PRIMARY KEY,
    name        text            NOT NULL,
    company     text            NOT NULL,
    stage       text            NOT NULL DEFAULT 'DISCOVERY',
    value_usd   numeric(12,2)   DEFAULT 0,
    probability numeric(3,2)    DEFAULT 0.1,
    owner       text            DEFAULT 'mike',
    source      text            DEFAULT 'oracle_health',
    next_action text,
    notes       text,
    metadata    jsonb           DEFAULT '{}',
    created_at  timestamptz     DEFAULT now(),
    updated_at  timestamptz     DEFAULT now(),

    CONSTRAINT jake_deals_stage_check
        CHECK (stage IN ('DISCOVERY', 'DEMO', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST')),
    CONSTRAINT jake_deals_probability_check
        CHECK (probability >= 0 AND probability <= 1)
);

CREATE INDEX IF NOT EXISTS idx_deals_stage
    ON jake_deals(stage);

CREATE INDEX IF NOT EXISTS idx_deals_source
    ON jake_deals(source);

CREATE INDEX IF NOT EXISTS idx_deals_company
    ON jake_deals(company);

CREATE INDEX IF NOT EXISTS idx_deals_updated
    ON jake_deals(updated_at);

COMMENT ON TABLE jake_deals IS
    'Business pipeline deals — Oracle Health opportunities, Susan commercial, and recruiting.';

-- =============================================================================
-- Business Pipeline — Deal Events Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS jake_deal_events (
    id          uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
    deal_id     uuid        REFERENCES jake_deals(id) ON DELETE CASCADE,
    event_type  text        NOT NULL,   -- stage_change | note_added | action_taken | activity | created
    from_stage  text,
    to_stage    text,
    description text,
    occurred_at timestamptz DEFAULT now(),
    metadata    jsonb       DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_deal_events_deal
    ON jake_deal_events(deal_id);

CREATE INDEX IF NOT EXISTS idx_deal_events_type
    ON jake_deal_events(event_type);

CREATE INDEX IF NOT EXISTS idx_deal_events_occurred
    ON jake_deal_events(occurred_at);

COMMENT ON TABLE jake_deal_events IS
    'Audit log for all deal state changes, notes, and activities.';

-- =============================================================================
-- Helper function: update jake_deals.updated_at on any row change
-- =============================================================================

CREATE OR REPLACE FUNCTION update_jake_deals_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_jake_deals_updated_at ON jake_deals;
CREATE TRIGGER trg_jake_deals_updated_at
    BEFORE UPDATE ON jake_deals
    FOR EACH ROW
    EXECUTE FUNCTION update_jake_deals_updated_at();
