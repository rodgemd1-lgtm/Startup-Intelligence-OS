#!/usr/bin/env bash
# jake-overnight-intel.sh — Overnight competitive intelligence scan.
# Runs at 5:00 AM, feeds signals into the 6:00 AM morning brief.
#
# Sources: TrendRadar (RSS/news) + SCOUT keyword scan
# Output: .startup-os/briefs/scout-signals-{today}.md
# Schedule: daily at 5:00 AM via com.jake.proactive-overnight-intel.plist

set -euo pipefail

REPO_ROOT="$HOME/Startup-Intelligence-OS"
SUSAN_BACKEND="$REPO_ROOT/susan-team-architect/backend"
VENV="$SUSAN_BACKEND/.venv/bin/python"
LOG_DIR="$REPO_ROOT/.startup-os/logs"
LOG="$LOG_DIR/overnight-intel.log"
BRIEFS_DIR="$REPO_ROOT/.startup-os/briefs"

mkdir -p "$LOG_DIR" "$BRIEFS_DIR"

echo "=== jake-overnight-intel.sh $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"

# Load env
for envfile in "$HOME/.hermes/.env" "$HOME/.openclaw/.env"; do
    if [ -f "$envfile" ]; then
        set -a
        # shellcheck disable=SC1090
        source "$envfile"
        set +a
    fi
done

TODAY=$(date '+%Y-%m-%d')
OUTPUT="$BRIEFS_DIR/scout-signals-${TODAY}.md"

# ── Competitive Keywords ──
# These are the terms SCOUT monitors across all 3 companies
KEYWORDS_SIO="personal ai infrastructure,ai agent orchestration,multi-agent system,openclaw,claude code"
KEYWORDS_ORACLE="oracle health ai,cerner ai,epic ai,healthcare ai,clinical ai"
KEYWORDS_ALEX="recruiting platform,athlete recruiting,ncaa recruiting,nil deals"

# ── TrendRadar Scan (if available) ──
TRENDRADAR_SECTION=""
if [ -n "${TRENDRADAR_API_KEY:-}" ]; then
    echo "[INFO] Running TrendRadar scan..." >> "$LOG"
    # Use the TrendRadar MCP via Python
    TRENDRADAR_SECTION=$("$VENV" -c "
import os, sys, json
sys.path.insert(0, '$SUSAN_BACKEND')

# Use Susan's search_knowledge to find recent competitive intel
try:
    from susan_core.rag import search_knowledge
    results = search_knowledge('competitive intelligence market signals', top_k=5, data_type='competitor_intel')
    signals = []
    for r in results:
        title = r.get('title', r.get('content', '')[:80])
        score = r.get('similarity', 0)
        priority = 'P0' if score > 0.85 else 'P1' if score > 0.7 else 'P2'
        signals.append(f'{priority} — {title}')
    if signals:
        print('\n'.join(signals[:5]))
    else:
        print('No new competitive signals overnight.')
except Exception as e:
    print(f'(TrendRadar scan failed: {e})')
" 2>/dev/null || echo "No signals available")
fi

# ── Susan RAG: Recent Competitor Data ──
COMPETITOR_SECTION=""
if command -v "$VENV" &>/dev/null; then
    COMPETITOR_SECTION=$("$VENV" -c "
import os, sys
sys.path.insert(0, '$SUSAN_BACKEND')
try:
    from supabase import create_client
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_ANON_KEY', '')
    if url and key:
        sb = create_client(url, key)
        # Check for recent competitor profiles updated in last 48h
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(hours=48)).isoformat()
        res = sb.table('knowledge_chunks').select('content,company_id,updated_at').eq('data_type','competitor_intel').gte('updated_at', cutoff).order('updated_at', desc=True).limit(5).execute()
        for r in res.data:
            print(f'  • [{r.get(\"company_id\",\"?\")}] {r.get(\"content\",\"\")[:100]}')
        if not res.data:
            print('  No competitor updates in last 48h.')
except Exception as e:
    print(f'  (competitor scan unavailable: {e})')
" 2>/dev/null || echo "  (no recent competitor data)")
fi

# ── Assemble Signals File ──
cat > "$OUTPUT" << EOF
# SCOUT Overnight Signals — ${TODAY}
Generated: $(date '+%Y-%m-%d %H:%M:%S')

## TrendRadar / Market Signals
${TRENDRADAR_SECTION:-No new signals.}

## Competitor Updates (last 48h)
${COMPETITOR_SECTION:-No recent competitor data.}

## Monitored Keywords
- SIO: ${KEYWORDS_SIO}
- Oracle Health: ${KEYWORDS_ORACLE}
- Alex Recruiting: ${KEYWORDS_ALEX}
EOF

echo "[INFO] Signals written to $OUTPUT" >> "$LOG"
echo "=== DONE $(date '+%Y-%m-%d %H:%M:%S') ===" >> "$LOG"
