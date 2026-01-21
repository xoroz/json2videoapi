# video-generation-api Specification

## Purpose
TBD - created by archiving change scaffold-backend-api. Update Purpose after archive.
## Requirements
### Requirement: Video Generation API
The API SHALL accept a JSON project definition and generate an MP4 video file based on the provided visuals, audios, and subtitles.

#### Scenario: Successful generation with subtitles
- **WHEN** a valid JSON project with a `subtitle` property and multiple `visuals` is POSTed to `/generate`
- **THEN** the API SHALL return a status code 200 and the path to the generated MP4 file.

#### Scenario: Metadata Support
- **WHEN** a visual item has `track`, `opacity`, or `angle` properties
- **THEN** the system SHALL reflect these transformations in the rendered output.

