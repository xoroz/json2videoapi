## ADDED Requirements
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
