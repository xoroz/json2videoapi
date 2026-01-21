#!/bin/bash

# Check Uvicorn
UVICORN_PIDS=$(pgrep -f "uvicorn src.main:app" || true)

# Check Caddy
# When caddy starts in background, it usually appears as 'caddy run'
CADDY_PIDS=$(pgrep -f "caddy.*Caddyfile" || true)

echo "--- Process Status ---"

if [ -n "$UVICORN_PIDS" ]; then
    echo "✅ Uvicorn is RUNNING (PIDs: $UVICORN_PIDS)"
else
    echo "❌ Uvicorn is STOPPED"
fi

if [ -n "$CADDY_PIDS" ]; then
    echo "✅ Caddy is RUNNING (PIDs: $CADDY_PIDS)"
else
    echo "❌ Caddy is STOPPED"
fi

echo "----------------------"

# Provide health check info if possible
if [ -n "$UVICORN_PIDS" ]; then
    HEALTH=$(curl -s http://localhost:8000/health || echo '{"status":"offline"}')
    echo "Uvicorn Health: $HEALTH"
fi

if [ -n "$CADDY_PIDS" ]; then
    CADDY_HEALTH=$(curl -s http://localhost:8080/health || echo '{"status":"offline"}')
    echo "Caddy Proxy Health: $CADDY_HEALTH"
fi
