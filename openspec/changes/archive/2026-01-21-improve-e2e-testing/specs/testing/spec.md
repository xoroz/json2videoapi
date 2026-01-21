# Spec Delta: Enhanced Testing and Subtitles

## ADDED Requirements

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
