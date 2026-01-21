# Change: Expand API Features

## Why
Users need to generate videos with more than just text. We also need to simplify testing and improve logging for better observability.

## What Changes
- Add support for `IMAGE`, `VIDEO`, `GIF`, and `SVG` visual types in `src/schemas.py`.
- Create a `test.sh` script for end-to-end verification.
- Add a `logs/` directory and implement file-based logging in `src/`.

## Impact
- Affected specs: `video-generation-api`
- Affected code: `src/schemas.py`, `src/video_processor.py`, new `test.sh`
