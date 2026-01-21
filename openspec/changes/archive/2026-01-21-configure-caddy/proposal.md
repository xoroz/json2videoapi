# Change: Configure Caddy

## Why
We need a production-ready web server to handle incoming requests, manage SSL (future), and proxy to the FastAPI backend. We also need a unified start script. And we should organize our test scripts.

## What Changes
- Configure Caddy as a reverse proxy
- Create `start.sh` to launch both Caddy and Uvicorn
- Move `test.sh` to `tests/` directory

## Impact
- Affected specs: `infrastructure`
- Affected code: `Caddyfile`, `start.sh`, `tests/`
