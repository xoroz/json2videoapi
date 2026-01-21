#!/bin/bash

echo "Stopping Caddy..."
if [ -f "./caddy" ]; then
    ./caddy stop || pkill -f "caddy.*Caddyfile"
else
    caddy stop || pkill -f "caddy.*Caddyfile"
fi

echo "Stopping Uvicorn..."
pkill -f "uvicorn src.main:app" || true

echo "All services stopped."
