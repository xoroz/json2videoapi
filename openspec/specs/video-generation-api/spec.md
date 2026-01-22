# video-generation-api Specification

## Purpose
TBD - created by archiving change scaffold-backend-api. Update Purpose after archive.
## Requirements
### Requirement: Video Generation API
The API SHALL accept a JSON project definition and generate an MP4 video file asynchronously.

#### Scenario: Successful job submission
- **WHEN** a valid JSON project is POSTed to `/generate`
- **THEN** the API SHALL return a status code 202 (Accepted) with a `job_id`.

#### Scenario: Polling for status
- **WHEN** a client calls `GET /status/{job_id}` for an active job
- **THEN** the API SHALL return the current status (e.g., `queued`, `processing`, `completed`) and progress.

#### Scenario: Downloading result
- **WHEN** a client calls `GET /download/{job_id}` for a completed job
- **THEN** the API SHALL return the MP4 file as a stream.

#### Scenario: Metadata Support
- **WHEN** a visual item has `track`, `opacity`, or `angle` properties
- **THEN** the system SHALL reflect these transformations in the rendered output (verified via end-to-end processing).

### Requirement: API Help Documentation
The API SHALL provide comprehensive help documentation at the `/help` endpoint that explains how to create videos with detailed examples and field documentation.

#### Scenario: User requests help documentation
- **WHEN** a GET request is made to `/help`
- **THEN** the API returns an HTML page containing:
  - API title, description, and version
  - "How It Works" section explaining the async video generation flow
  - Comprehensive examples demonstrating various capabilities (text, images, subtitles, transitions, overlays)
  - Field documentation for key properties
  - Links to `/docs` for full schema reference
  - Support and contact information

#### Scenario: User views help in browser
- **WHEN** a user navigates to `/help` in a web browser
- **THEN** the HTML documentation is displayed with modern, professional styling
- **AND** includes multiple real-world examples from test data
- **AND** provides clear guidance on creating different types of videos

