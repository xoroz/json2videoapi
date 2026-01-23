# Tasks: Add Background Audio Support

## Task List

### 1. Create Test Case with Background Audio
- [x] Create `tests/data/yt-short-with-audio.json` based on `yt-short-noaudio.json`
- [x] Add `audios` field with reference to `tests/data/artifacts/default.mp3`
- [x] Set appropriate volume level (e.g., 0.7 to not overpower potential voice content)

### 2. Implement Audio Trimming Logic
- [x] Add function to trim audio to video duration using FFmpeg
- [x] Place trimmed audio in temporary file
- [x] Ensure cleanup of temporary audio files after processing

### 3. Update Video Processor
- [x] Modify `src/video_processor.py` to detect audio in project
- [x] Call audio trimming function before invoking zvid
- [x] Update project JSON to reference trimmed audio file
- [x] Add error handling for audio processing failures

### 4. Testing
- [x] Run API with new test case
- [x] Verify audio is trimmed correctly
- [x] Test video playback in browser to confirm audio works
- [x] Verify no temporary files are left behind
- [x] Check FFmpeg performance improvement with trimmed audio

### 5. Documentation
- [x] Update API_GUIDE.md with audio usage examples
- [x] Document audio trimming behavior
- [x] Add notes about supported audio formats

## Validation Criteria
- ✅ Test case generates successfully
- ✅ Audio plays in generated video
- ✅ Audio duration matches video duration
- ✅ No temporary files remain after processing
- ✅ Browser playback confirms audio works correctly
