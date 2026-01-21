# infrastructure Specification

## Purpose
TBD - created by archiving change configure-caddy. Update Purpose after archive.
## Requirements
### Requirement: Web Server
The system SHALL use Caddy as the entry point for HTTP requests.

#### Scenario: Proxy requests
- **WHEN** a request is sent to the public port (8080)
- **THEN** Caddy proxies it to the backend service (8000)

### Requirement: Service Management
The system SHALL provide a single script to start all necessary services.

#### Scenario: Start services
- **WHEN** `start.sh` is executed
- **THEN** both the API backend and Web Server are started

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

