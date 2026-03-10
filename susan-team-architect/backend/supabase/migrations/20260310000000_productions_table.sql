-- Film & Image Studio: Productions persistence layer
-- Stores production lifecycle state across sessions

CREATE TABLE IF NOT EXISTS productions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    production_id text NOT NULL UNIQUE,
    company_id text NOT NULL,
    brief text NOT NULL,
    title text,
    format text NOT NULL,
    status text NOT NULL DEFAULT 'design',
    agents_assigned text[] DEFAULT '{}',
    outputs jsonb DEFAULT '[]',
    quality_results jsonb DEFAULT '[]',
    legal_clearances jsonb DEFAULT '[]',
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_productions_company ON productions(company_id);
CREATE INDEX IF NOT EXISTS idx_productions_status ON productions(status);
CREATE INDEX IF NOT EXISTS idx_productions_format ON productions(format);
CREATE INDEX IF NOT EXISTS idx_productions_created ON productions(created_at DESC);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_productions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER productions_updated_at_trigger
    BEFORE UPDATE ON productions
    FOR EACH ROW
    EXECUTE FUNCTION update_productions_updated_at();

-- Enable RLS
ALTER TABLE productions ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role full access" ON productions
    FOR ALL
    USING (true)
    WITH CHECK (true);
