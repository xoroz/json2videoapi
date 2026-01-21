# Change: Scaffold Backend API

## Why
We need to establish the core backend infrastructure to allow users to generate videos from JSON via an HTTP API. This integrates `zvid` with a FastAPI server.

## What Changes
- Create a FastAPI application (`src/main.py`)
- Integrate `zvid` (running via Node.js subprocess or binding) to process requests
- Define JSON schema for video requests
- Implement video generation endpoint

## Impact
- Affected specs: `video-generation-api`
- Affected code: New `src/` directory, `requirements.txt`
