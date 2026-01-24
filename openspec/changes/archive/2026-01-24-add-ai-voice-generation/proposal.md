# Proposal: Add AI Voice Generation with ElevenLabs

## Summary
Implement AI-powered voice generation using ElevenLabs API to create high-quality voiceovers for motivational and inspirational videos. This feature adds a middleware/processor layer for handling various media processing tasks.

## Motivation
To create truly engaging YouTube Shorts and TikTok videos that inspire people to do great things, we need natural-sounding AI voices. ElevenLabs provides state-of-the-art text-to-speech that sounds human and emotional, perfect for motivational content.

## Scope
This change will:
- Create a middleware/processor layer (`src/processors/`) for media processing tasks
- Implement `VoiceGenerator` class with ElevenLabs API integration
- Implement `AudioProcessor` class for audio manipulation tasks
- Add ElevenLabs configuration to `config.ini`
- Use environment variable `ELEVENLABS_API_KEY` for API authentication
- Configure voice_id `Qggl4b0xRMiqOwhPtVWT` as default voice
- Create test script to validate API key and voice generation
- Generate test audio from `test-audio.json`

## Architecture
The implementation will follow a 4-step workflow:

1.  **Voice & Timing Extraction**:
    *   Call ElevenLabs API to get audio and alignment data (timestamps for words/characters).
    *   Output: `speech.mp3` and timestamp JSON.

2.  **Asset Standardization (Pillow)**:
    *   Pre-process all input images using Python (Pillow).
    *   Resize and center-crop images to exactly 1080x1920 (9:16 aspect ratio).
    *   Save processed images to a temporary directory.

3.  **Sync Map Generation**:
    *   **Image Map (`inputs.txt`)**: Calculate duration for each image based on word timestamps or even distribution. Generate a file compatible with FFmpeg's `concat` demuxer.
    *   **Subtitle Map (`subs.ass`)**: Generate Advanced Substation Alpha subtitles with karaoke effects based on timestamps.

4.  **Final Assembly (FFmpeg)**:
    *   Use FFmpeg with the concat demuxer to stitch images.
    *   Overlay audio.
    *   Burn subtitles using the `ass` filter.
    *   Apply Ken Burns effect (zoompan) if feasible.

## Out of Scope
*   Voice cloning (custom voice training)
*   Real-time voice synthesis
*   Complex transition effects beyond simple cuts/fades (unless handled by concat)

## Success Criteria
- use example-idea.md
- ElevenLabs API key can be validated
- Voice generation works with test text
- Generated audio files are saved in artifacts
- Audio quality is high and natural-sounding
- Processor layer is extensible for future features
- we do a test using 5 imgs and text to create a full video with TTS img, bg audio and play it on the web browser.

## Dependencies
- ElevenLabs API account and API key
- `aiohttp` library for async HTTP requests
- FFmpeg/FFprobe for audio validation

## Risks & Mitigations
- **Risk**: API rate limits or costs
  - **Mitigation**: Cache generated voices, implement rate limiting
- **Risk**: API key exposure
  - **Mitigation**: Use environment variables, never commit keys
- **Risk**: Network failures
  - **Mitigation**: Proper error handling and retries

## Timeline
- Estimated effort: 2-3 hours
- Testing: 30 minutes
