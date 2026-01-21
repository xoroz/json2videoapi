# Change: Improve Web 01 (Status, Config, and Docs)

## Why
We need better operational tools to monitor the service, a centralized configuration system, and documentation for users. Additionally, generated videos need to be served via HTTP for web access.

## What Changes
- Create `status.sh` to monitor Uvicorn and Caddy processes.
- Configure Caddy to serve the `output/` directory as static files.
- Introduce `config.ini` to manage variables like `output_dir` and `log_dir`.
- Update Python code to read from `config.ini`.
- Add Swagger/ReDoc documentation and a dedicated `API_GUIDE.md`.

## Impact
- Affected specs: `infrastructure`, `video-generation-api`
- Affected code: `start.sh`, `src/main.py`, `src/video_processor.py`, `Caddyfile`
