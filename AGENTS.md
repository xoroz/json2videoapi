<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Local Development Rules
- **Do NOT use the browser tool**: We are developing locally. The browser tool cannot access `localhost`. Use `curl` or ask the user to verify manually.

# Documentation Maintenance
- **When expanding JSON video capabilities**: Always update both `/help` endpoint (`src/main.py`) and Swagger schemas to reflect new features
  - Add new examples to the `examples` section in `/help` 
  - Update `field_documentation` if new fields are added
  - Consider adding test data files in `tests/data/` to demonstrate new capabilities
  - The `/help` endpoint should always showcase real-world examples from our test suite