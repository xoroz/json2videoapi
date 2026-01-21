# Change: Improve E2E Testing

## Why
We need to verify more complex scenarios (subtitles, transitions) and ensure the generated video is actually valid. Better test automation simplifies development.

## What Changes
- Update `src/schemas.py` to support `subtitle` field.
- Create a directory `tests/data/` for JSON test cases.
- Create JSON test cases: `default.json`, `subtitles.json`, `bg_transition.json`.
- Modernize `tests/test_e2e.sh` to support arguments and `ffprobe` validation.

## Impact
- Affected specs: `testing`
- Affected code: `src/schemas.py`, `tests/`
