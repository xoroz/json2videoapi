# background-audio Specification

## Purpose
TBD - created by archiving change add-background-audio. Update Purpose after archive.
## Requirements
### Requirement: Audio Trimming
The system MUST trim background audio files to match the video duration before FFmpeg processing to optimize CPU usage.

#### Scenario: Audio Longer Than Video
**Given** a video project with duration of 25 seconds  
**And** a background audio file with duration of 180 seconds  
**When** the video generation process starts  
**Then** the audio file MUST be trimmed to 25 seconds  
**And** the trimmed audio MUST be used in the final video  
**And** the original audio file MUST remain unchanged

#### Scenario: Audio Shorter Than Video
**Given** a video project with duration of 60 seconds  
**And** a background audio file with duration of 30 seconds  
**When** the video generation process starts  
**Then** the audio file SHOULD be used as-is  
**And** the audio MAY loop or fade out based on zvid's default behavior

### Requirement: Audio Processing
The system MUST support background audio in video generation through the `audios` field.

#### Scenario: Single Background Audio Track
**Given** a video project JSON with an `audios` array containing one audio file  
**When** the video is generated  
**Then** the audio MUST be included in the final video output  
**And** the audio volume MUST respect the `volume` parameter (default: 1.0)

#### Scenario: No Audio Specified
**Given** a video project JSON with an empty `audios` array  
**When** the video is generated  
**Then** the video MUST be generated without audio  
**And** no audio processing MUST occur

### Requirement: Temporary File Management
The system MUST clean up temporary audio files after video generation completes or fails.

#### Scenario: Successful Video Generation
**Given** audio trimming creates a temporary file  
**When** video generation completes successfully  
**Then** the temporary audio file MUST be deleted  
**And** only the final video output MUST remain

#### Scenario: Failed Video Generation
**Given** audio trimming creates a temporary file  
**When** video generation fails  
**Then** the temporary audio file MUST still be deleted  
**And** no orphaned files MUST remain in the system

### Requirement: Error Handling
The system MUST handle audio processing errors gracefully.

#### Scenario: Invalid Audio File
**Given** a video project with an audio file that doesn't exist  
**When** the video generation process starts  
**Then** the system MUST return an error  
**And** the error message MUST indicate the audio file is invalid  
**And** the job status MUST be set to FAILED

#### Scenario: Unsupported Audio Format
**Given** a video project with an unsupported audio format  
**When** FFmpeg attempts to process the audio  
**Then** the system MUST capture the FFmpeg error  
**And** the job status MUST be set to FAILED  
**And** the error message MUST be logged

