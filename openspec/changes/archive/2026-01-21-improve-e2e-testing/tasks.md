## 1. Implementation
- [x] 1.1 Update `src/schemas.py` with `Subtitle` and `VideoProject.subtitle`
- [x] 1.2 Create `tests/data/` directory
- [x] 1.3 Create `tests/data/default.json`
- [x] 1.4 Create `tests/data/subtitles.json`
- [x] 1.5 Create `tests/data/bg_transition.json`
- [x] 1.6 Update `tests/test_e2e.sh` to handle arguments and use `ffprobe`
- [x] 1.7 Verify all test cases pass

## 2. Advanced Testing (Images & HD Features)
- [x] 2.1 Create `tests/data/image_segments.json` (3 images, matching subtitles)
- [x] 2.2 Create `tests/data/portrait_tik_tok.json` (HD Portrait)
- [x] 2.3 Create `tests/data/video_sample.json` (Video element test)
- [x] 2.4 Create `tests/data/overlay_grid.json` (Complex multi-visual layout)
- [x] 2.5 Verify all new test cases pass

## 3. Robustness & Original Examples
- [x] 3.1 Fix `start.sh` to automatically activate `.venv`
- [x] 3.2 Update `src/schemas.py` to support full `zvid` spec (track, anchor, opacity, angle, transitions, etc.)
- [x] 3.3 Verify original `zvid` examples (`text.json`, `gif.json`, `svg.json`, etc.)
- [x] 3.4 Ensure `test_e2e.sh` provides clear error messages if server is down
