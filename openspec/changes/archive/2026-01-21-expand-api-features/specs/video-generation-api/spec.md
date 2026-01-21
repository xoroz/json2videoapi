## MODIFIED Requirements
### Requirement: Video Generation API
The system SHALL provide an HTTP endpoint to generate videos from JSON specifications with support for rich media.

#### Scenario: Generate video with mixed media
- **WHEN** a POST request is sent to `/generate` with JSON containing TEXT, IMAGE, and VIDEO visuals
- **THEN** the system returns a video file containing all specified elements
- **AND** correct media attributes (src, resize, volume) are respected

#### Scenario: Verify output
- **WHEN** a video is generated
- **THEN** it SHALL be a valid MP4 file readable by standard players
