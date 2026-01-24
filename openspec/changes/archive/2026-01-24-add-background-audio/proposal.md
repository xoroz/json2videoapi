# Proposal: Add Background Audio Support

## Summary
Add support for background audio/music in video generation. This feature will allow users to specify an audio file that plays throughout the video, with automatic trimming to match the video duration to optimize FFmpeg processing performance.

## Motivation
Currently, the API supports video generation with visuals and subtitles, but lacks background audio support. Adding background music is essential for creating engaging videos, especially for social media content like YouTube Shorts, TikTok videos, and Instagram Reels.

## Scope
This change will:
- Enable users to specify background audio via the `audios` field in the JSON payload
- Automatically trim audio files to match video duration before processing
- Optimize CPU usage by preprocessing audio instead of letting FFmpeg handle full-length files
- Provide a test case demonstrating background audio functionality

## Out of Scope
- Audio mixing/effects (fade in/out, volume automation)
- Multiple audio tracks with different timing
- Audio format conversion (will rely on FFmpeg's built-in support)

## Success Criteria
- Users can add background audio by specifying an audio file in the `audios` array
- Audio is automatically trimmed to video duration before FFmpeg processing
- Test case with background music passes successfully
- Browser-based testing confirms audio plays correctly in generated video

## Dependencies
- Existing `Audio` schema in `src/schemas.py`
- FFmpeg for audio processing
- Test audio file: `tests/data/artifacts/default.mp3`

## Risks & Mitigations
- **Risk**: Audio trimming might fail for certain formats
  - **Mitigation**: Use FFmpeg's robust format support and add error handling
- **Risk**: Performance impact from audio preprocessing
  - **Mitigation**: Trimming audio upfront is faster than processing full-length files

## Timeline
- Estimated effort: 1-2 hours
- Testing: 30 minutes
