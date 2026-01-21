#!/bin/bash
set -e

# Ensure logs directory exists
mkdir -p logs

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Starting Uvicorn..."
uvicorn src.main:app --port 8000 > logs/uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "Uvicorn started with PID $UVICORN_PID"

echo "Starting Caddy..."
./caddy start --config Caddyfile --adapter caddyfile > logs/caddy_start.log 2>&1
echo "Caddy started"

# Trap exit signals to kill background processes
trap "kill $UVICORN_PID; ./caddy stop" EXIT

echo "Services are running. Press Ctrl+C to stop."
sleep 2
./status.sh
wait $UVICORN_PID
