# Voice Video Workflow Specification

## Overview
 This specification defines the standardized input and workflow for generating AI-narrated vertical videos with synchronized images and karaoke subtitles.

## Input Format ('complete-voice-example.json')

The system accepts a JSON configuration defining the script, visual assets, and timing markers.

```json
{
  "script": "Full narration text...",
  "images": [
    "/path/to/image1.png",
    "/path/to/image2.png"
  ],
  "markers": [
    "word1", 
    "word2"
  ],
  "settings": {
    "voice_id": "optional-voice-id",
    "resolution": [1080, 1920]
  }
}
```

### Fields
- **script**: The text to be synthesized into speech.
- **images**: Ordered list of image paths.
- **markers**: A list of words from the script. 
    - The Nth marker corresponds to the start of the (N+1)th image.
    - Image 1 starts at 0.0s.
    - Image 2 starts when `markers[0]` is spoken.
    - Image 3 starts when `markers[1]` is spoken, etc.

## Workflow Status

### Validated Features
1. **TTS Integration**: Generates audio using ElevenLabs with word-level timestamps.
2. **Image Processing**: Automatically crops and resizes images to 1080x1920 (9:16).
3. **Synchronization**:
    - **Karaoke Subtitles**: 
        - Words are grouped into lines of ~4.
        - Text highlights in real-time (`{\k}` tags).
        - Non-highlighted text remains visible in secondary color.
    - **Image Transitions**:
        - Images switch precisely at the start time of the specified marker words.
        - Logic handles case-insensitivity and punctuation stripping.

### Technical Implementation Details
- **FFmpeg Filter**: Uses `fps=30` before the `ass` subtitle filter to ensure smooth subtitle animation even with static image inputs.
- **Chunking**: Subtitles are generated in chunks to prevent rapid single-word flashing and improve readability.

## Example
See `tests/data/complete-voice-example.json` for the canonical test case used to validate this workflow.
