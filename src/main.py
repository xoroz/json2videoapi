from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging
import os
from .schemas import VideoProject, JobResponse, JobStatus
from .video_processor import generate_video, VideoProcessingError, job_manager
from .config_loader import settings, get_log_dir

# Initialize logging based on config
log_dir = get_log_dir()
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

description = """
JSON to Video API helps you generate high-quality MP4 videos from JSON specifications.

## Features
* **Asynchronous Rendering**: Submit jobs and poll for status.
* **Text Overlays**: support for HTML and CSS-styled text.
* **Media Support**: Images (PNG/JPG), GIFs, and Videos (MP4).
* **SVG Support**: Pass raw SVG content to render as visuals.
* **Subtitles**: Project-wide subtitle support with multiple display modes.
* **Transitions**: Professional transitions between clips.
"""

app = FastAPI(
    title="JSON to Video API",
    description=description,
    version="0.3.0",
    contact={
        "name": "JSON2Video Support",
        "url": "https://github.com/felix/json2videoapi",
    }
)

@app.post("/generate", response_model=JobResponse, status_code=202, tags=["Video Generation"])
async def generate_video_endpoint(project: VideoProject, background_tasks: BackgroundTasks):
    """
    Submit a video generation request.
    
    Returns a `job_id` which can be used to poll `/status/{job_id}`.
    """
    job_id = job_manager.create_job(project.name)
    logger.info(f"Queued video generation job: {job_id} for project: {project.name}")
    background_tasks.add_task(generate_video, project, job_id)
    
    return {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "message": "Video generation job has been queued."
    }

@app.get("/status/{job_id}", response_model=JobResponse, tags=["Video Generation"])
async def get_job_status(job_id: str):
    """Check the status of a video generation job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/download/{job_id}", tags=["Video Generation"])
async def download_video(job_id: str):
    """Download the completed video file."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job["status"] == JobStatus.FAILED:
        raise HTTPException(status_code=400, detail=f"Video generation failed: {job.get('error')}")
        
    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Video is not ready. Status: {job['status']}")
    
    video_path = job["output_file"]
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Generated video file not found on disk")
        
    return FileResponse(video_path, media_type="video/mp4", filename=f"{job['name']}.mp4")

@app.get("/health", tags=["Utilities"])
async def health_check():
    """Basic health check to verify service availability."""
    return {"status": "ok"}
