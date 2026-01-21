# Change: Add Asynchronous Video Generation

## Why
Generating videos can take a significant amount of time, often exceeding standard HTTP timeout limits for synchronous requests. An asynchronous architecture improves user experience and system reliability by allowing the client to poll for status.

## What Changes
- **MODIFIED** `/generate` endpoint: Now returns a `job_id` and `status: "queued/processing"` immediately instead of waiting for rendering.
- **ADDED** `GET /status/{job_id}` endpoint: Returns current status, and results (if done).
- **ADDED** `GET /download/{job_id}` endpoint: Allows downloading the finished video.
- **ADDED** Background task management: A simple in-memory queue/manager for tracking rendering jobs.

## Impact
- Affected specs: `video-generation-api`
- Affected code: `src/main.py`, `src/video_processor.py`
