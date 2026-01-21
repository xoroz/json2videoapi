## MODIFIED Requirements
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
