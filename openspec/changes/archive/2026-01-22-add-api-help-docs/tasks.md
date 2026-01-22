# Implementation Tasks

## 1. Enhance `/help` Endpoint
- [x] 1.1 Add detailed "How It Works" section explaining the async video generation flow
- [x] 1.2 Include comprehensive examples from `tests/data/`:
  - [x] Basic text video
  - [x] Text with image
  - [x] Subtitles example
  - [x] Background transitions with fade
  - [x] Complex overlay grid
- [x] 1.3 Add field documentation for key properties (visuals, animations, positioning, etc.)
- [x] 1.4 Add links to `/docs` for full schema reference
- [x] 1.5 Create beautiful HTML template with modern gradient design
- [x] 1.6 Add Jinja2 templating support to FastAPI
- [x] 1.7 Update endpoint to serve HTML instead of JSON

## 2. Update Documentation
- [x] 2.1 Update `README.md` to mention `/docs` (Swagger UI)
- [x] 2.2 Add instructions to `AGENTS.md` about updating help/docs when JSON capabilities expand
- [x] 2.3 Add `jinja2` to `requirements.txt`

## 3. Testing
- [x] 3.1 Verify `/help` endpoint returns comprehensive documentation
- [x] 3.2 Test in browser to ensure readability and beautiful design
- [x] 3.3 Verify all examples are valid and match test data
