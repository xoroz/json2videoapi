## 1. Preparation
- [x] 1.1 Update `src/schemas.py` to include Job-related models (JobStatus, JobResponse, etc.)

## 2. Implementation
- [x] 2.1 Implement `JobManager` in `src/video_processor.py` to track job state and file paths.
- [x] 2.2 Update `/generate` in `src/main.py` to use FastAPI's `BackgroundTasks` and return a `job_id`.
- [x] 2.3 Implement `/status/{job_id}` endpoint.
- [x] 2.4 Implement `/download/{job_id}` endpoint.
- [x] 2.5 Ensure the output video is mapped to the `job_id` correctly.

## 3. Testing
- [x] 3.1 Verify async flow with `curl`.
- [x] 3.2 Update `tests/test_e2e.sh` to handle polling for status.
