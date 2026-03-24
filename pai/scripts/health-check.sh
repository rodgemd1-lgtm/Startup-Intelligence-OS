#!/bin/bash
# pai/scripts/health-check.sh
# Checks all PAI services and alerts via Telegram if anything is down.

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-8716281531:AAF67DEFcw_tJTJ6wHO5D6n1k2Qpfwm66ig}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-8634072195}"
export PATH="$HOME/.npm-global/bin:$HOME/go/bin:/opt/homebrew/bin:$PATH"

check_service() {
    local name="$1"
    local check_cmd="$2"
    if ! eval "$check_cmd" > /dev/null 2>&1; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=PAI Health Alert: ${name} is DOWN" \
            -d "parse_mode=Markdown" > /dev/null
        return 1
    fi
    return 0
}

# Check OpenClaw gateway
check_service "OpenClaw Gateway" "curl -s --max-time 5 http://127.0.0.1:18789/health"

# Check Fabric API
check_service "Fabric API" "curl -s --max-time 5 http://127.0.0.1:8080/patterns/names"

# Check Claude Code CLI is available
check_service "Claude Code CLI" "which claude"

# Check OpenClaw gateway launchd service
check_service "OpenClaw LaunchAgent" "launchctl list | grep -q ai.openclaw.gateway"

# Check LosslessClaw DB
check_service "LosslessClaw DB" "test -f ~/.openclaw/lcm.db"

echo "[$(date)] Health check complete"
