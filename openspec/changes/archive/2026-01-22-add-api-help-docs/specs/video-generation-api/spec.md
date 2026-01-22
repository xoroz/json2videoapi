## MODIFIED Requirements

### Requirement: API Help Documentation
The API SHALL provide comprehensive help documentation at the `/help` endpoint that explains how to create videos with detailed examples and field documentation.

#### Scenario: User requests help documentation
- **WHEN** a GET request is made to `/help`
- **THEN** the API returns a JSON response containing:
  - API title, description, and version
  - "How It Works" section explaining the async video generation flow
  - Comprehensive examples demonstrating various capabilities (text, images, subtitles, transitions, overlays)
  - Field documentation for key properties
  - Links to `/docs` for full schema reference
  - Support and contact information

#### Scenario: User views help in browser
- **WHEN** a user navigates to `/help` in a web browser
- **THEN** the JSON documentation is displayed in a readable format
- **AND** includes multiple real-world examples from test data
- **AND** provides clear guidance on creating different types of videos
