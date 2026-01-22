# Change: Add Comprehensive API Help Documentation

## Why
Users need clear, comprehensive documentation on how to create videos using the JSON API. The current `/help` endpoint exists but lacks detailed explanations and real-world examples. We have excellent test data in `tests/data/` that demonstrates various capabilities, but this isn't exposed to users.

## What Changes
- Enhance the `/help` endpoint with comprehensive documentation including:
  - Detailed explanation of how video generation works
  - Multiple real-world examples from `tests/data/` (text, images, subtitles, transitions, overlays, etc.)
  - Field-by-field documentation for key properties
  - Links to `/docs` (Swagger UI) for full schema reference
- Update `README.md` to mention `/docs` endpoint
- Add instructions to `AGENTS.md` to remember updating help/docs when JSON capabilities expand

## Impact
- Affected specs: `video-generation-api`
- Affected code: `src/main.py`, `README.md`, `AGENTS.md`
- Better user experience and self-service documentation
