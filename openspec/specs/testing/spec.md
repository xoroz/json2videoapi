# testing Specification

## Purpose
TBD - created by archiving change improve-e2e-testing. Update Purpose after archive.
## Requirements
### Requirement: Enhanced E2E Testing
The system SHALL provide a suite of E2E tests covering subtitles and image segments.

#### Scenario: Subtitle rendering
- **WHEN** a project with subtitles is submitted
- **THEN** the output video contains rendered subtitles

### Requirement: Media Validation
The test suite SHALL validate output video integrity using ffprobe.

#### Scenario: Duration check
- **WHEN** test_e2e.sh runs
- **THEN** it verifies output duration matches project duration

### Requirement: Web Test Interface
The system SHALL provide an HTML page to facilitate manual testing of the API.

#### Scenario: Submitting project via web
- **WHEN** a user enters JSON in the web form and clicks "Generate"
- **THEN** it sends a request to the API and displays the result link.

