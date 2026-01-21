from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import logging
import os
from .schemas import VideoProject
from .video_processor import generate_video, VideoProcessingError
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
* **Text Overlays**: support for HTML and CSS-styled text.
* **Media Support**: Images (PNG/JPG), GIFs, and Videos (MP4).
* **SVG Support**: Pass raw SVG content to render as visuals.
* **Subtitles**: Project-wide subtitle support with multiple display modes.
* **Transitions**: Professional transitions between clips.
"""

app = FastAPI(
    title="JSON to Video API",
    description=description,
    version="0.2.0",
    contact={
        "name": "JSON2Video Support",
        "url": "https://github.com/felix/json2videoapi",
    }
)

@app.post("/generate", responses={
    200: {
        "content": {"video/mp4": {}},
        "description": "Returns the generated MP4 file",
    },
    500: {"description": "Video generation failed"}
})
async def generate_video_endpoint(project: VideoProject):
    """
    Generate a video from a JSON project definition.
    
    The request body must follow the VideoProject schema.
    Returns the generated MP4 file directly.
    """
    logger.info(f"Received video generation request: {project.name}")
    try:
        video_path = await generate_video(project)
        logger.info(f"Video generated successfully: {video_path}")
        return FileResponse(video_path, media_type="video/mp4", filename=f"{project.name}.mp4")
    except VideoProcessingError as e:
        logger.error(f"Video processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health", tags=["Utilities"])
async def health_check():
    """Basic health check to verify service availability."""
    return {"status": "ok"}
