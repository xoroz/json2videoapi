# Spec Delta: Infrastructure Monitoring and Configuration

## ADDED Requirements

### Requirement: Service Monitoring
The system SHALL provide a mechanism to check the health and process status of all background services.

#### Scenario: Status check
- **WHEN** running `status.sh`
- **THEN** it displays whether Uvicorn and Caddy are currently active.

### Requirement: Centralized Configuration
The system SHALL use a configuration file to manage operational variables.

#### Scenario: Configurable Output Path
- **WHEN** a custom path is set in `config.ini`
- **THEN** generated videos are saved to that location.

### Requirement: Static Asset Serving
The web server SHALL serve generated video files via HTTP.

#### Scenario: Accessing generated video
- **WHEN** a request is made to `http://localhost:8080/output/<filename>`
- **THEN** it returns the corresponding MP4 file.
