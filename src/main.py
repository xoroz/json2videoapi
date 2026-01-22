from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
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

# Setup Jinja2 templates
templates = Jinja2Templates(directory="src/templates")

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

@app.get("/help", response_class=HTMLResponse, tags=["Utilities"])
async def api_help(request: Request):
    """Get comprehensive API usage information and help."""
    help_data = {
        "title": "JSON to Video API",
        "description": "Generate high-quality MP4 videos from JSON specifications",
        "version": "0.3.0",
        
        "how_it_works": {
            "overview": "This API uses an asynchronous workflow for video generation",
            "steps": [
                "1. POST your video specification to /generate - receive a job_id",
                "2. Poll /status/{job_id} to check progress (queued → processing → completed/failed)",
                "3. Download the video from /download/{job_id} when status is 'completed'"
            ],
            "typical_generation_time": "5-30 seconds depending on complexity and duration"
        },
        
        "endpoints": {
            "POST /generate": {
                "description": "Submit a video generation request",
                "body": "JSON video project specification (see examples below)",
                "response": {"job_id": "string", "status": "queued", "message": "string"}
            },
            "GET /status/{job_id}": {
                "description": "Check job status",
                "response": {"job_id": "string", "status": "queued|processing|completed|failed", "message": "string", "output_file": "string (when completed)"}
            },
            "GET /download/{job_id}": {
                "description": "Download completed video",
                "response": "MP4 video file stream"
            },
            "GET /health": {
                "description": "Health check",
                "response": {"status": "ok"}
            },
            "GET /help": {
                "description": "This help documentation",
                "response": "API documentation JSON"
            },
            "GET /docs": {
                "description": "Interactive Swagger UI with full schema documentation",
                "response": "HTML page with interactive API documentation"
            }
        },
        
        "examples": {
            "1_basic_text": {
                "description": "Simple text video with styling",
                "spec": {
                    "name": "hello-world",
                    "duration": 5,
                    "resolution": "720p",
                    "visuals": [
                        {
                            "type": "TEXT",
                            "text": "Hello World",
                            "position": "center",
                            "style": {
                                "fontSize": "80px",
                                "color": "#ffffff"
                            }
                        }
                    ]
                }
            },
            "2_text_with_image": {
                "description": "Text with fade animations and background image",
                "spec": {
                    "name": "text-and-image",
                    "resolution": "720p",
                    "duration": 5,
                    "visuals": [
                        {
                            "type": "TEXT",
                            "text": "Hello World",
                            "style": {"fontSize": "80px", "color": "#ffffff"},
                            "position": "center",
                            "enterBegin": 0,
                            "enterEnd": 1,
                            "exitBegin": 4,
                            "exitEnd": 5
                        },
                        {
                            "type": "IMAGE",
                            "src": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800",
                            "position": "center",
                            "width": 400,
                            "height": 300,
                            "enterBegin": 1,
                            "enterEnd": 2,
                            "exitBegin": 4,
                            "exitEnd": 5
                        }
                    ]
                }
            },
            "3_subtitles": {
                "description": "Video with timed subtitles/captions",
                "spec": {
                    "name": "with-subtitles",
                    "resolution": "720p",
                    "duration": 5,
                    "visuals": [
                        {
                            "type": "TEXT",
                            "text": "Background Content",
                            "style": {"fontSize": "40px"},
                            "position": "center",
                            "enterBegin": 0,
                            "exitEnd": 5
                        }
                    ],
                    "subtitle": {
                        "styles": {
                            "fontSize": 60,
                            "color": "#ffff00",
                            "fontFamily": "Arial"
                        },
                        "captions": [
                            {"start": 0.5, "end": 2.5, "text": "This is the first caption"},
                            {"start": 3.0, "end": 4.5, "text": "And the second one"}
                        ]
                    }
                }
            },
            "4_background_transitions": {
                "description": "Background color transitions with fade effects",
                "spec": {
                    "name": "bg-transitions",
                    "resolution": "720p",
                    "duration": 6,
                    "backgroundColor": "#000000",
                    "visuals": [
                        {
                            "type": "SVG",
                            "svg": "<svg width=\"1280\" height=\"720\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"100%\" height=\"100%\" fill=\"#ff0000\"/></svg>",
                            "position": "center",
                            "enterBegin": 0,
                            "enterEnd": 2,
                            "exitBegin": 2,
                            "exitEnd": 4,
                            "enterAnimation": "fade",
                            "exitAnimation": "fade"
                        },
                        {
                            "type": "SVG",
                            "svg": "<svg width=\"1280\" height=\"720\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"100%\" height=\"100%\" fill=\"#0000ff\"/></svg>",
                            "position": "center",
                            "enterBegin": 4,
                            "enterEnd": 6,
                            "enterAnimation": "fade"
                        }
                    ]
                }
            },
            "5_complex_overlay_grid": {
                "description": "Multiple overlapping elements with precise positioning",
                "spec": {
                    "name": "overlay-grid",
                    "resolution": "full-hd",
                    "duration": 5,
                    "backgroundColor": "#000000",
                    "visuals": [
                        {
                            "type": "IMAGE",
                            "src": "https://picsum.photos/seed/g1/400/400",
                            "x": 100,
                            "y": 100,
                            "width": 400,
                            "height": 400,
                            "enterBegin": 0,
                            "enterEnd": 1,
                            "exitBegin": 4,
                            "exitEnd": 5,
                            "enterAnimation": "fade"
                        },
                        {
                            "type": "TEXT",
                            "text": "GRID LAYOUT",
                            "x": 600,
                            "y": 700,
                            "style": {"fontSize": "80px", "color": "#00ff00"},
                            "enterBegin": 2,
                            "exitEnd": 5
                        }
                    ]
                }
            }
        },
        
        "field_documentation": {
            "project_level": {
                "name": "String - Project name (used for output filename)",
                "duration": "Number - Video duration in seconds",
                "resolution": "String - '720p', 'hd', 'full-hd', '4k', or custom 'WIDTHxHEIGHT'",
                "backgroundColor": "String - Hex color code (e.g., '#000000')",
                "visuals": "Array - List of visual elements (text, images, videos, SVGs, GIFs)",
                "subtitle": "Object - Subtitle configuration with styles and captions",
                "audio": "Object - Background audio configuration"
            },
            "visual_element": {
                "type": "String - 'TEXT', 'IMAGE', 'VIDEO', 'SVG', 'GIF'",
                "position": "String - 'center', 'top-left', 'bottom-right', etc. OR use x/y for precise positioning",
                "x": "Number - Horizontal position in pixels (from left)",
                "y": "Number - Vertical position in pixels (from top)",
                "width": "Number - Width in pixels",
                "height": "Number - Height in pixels",
                "enterBegin": "Number - Start time for enter animation (seconds)",
                "enterEnd": "Number - End time for enter animation (seconds)",
                "exitBegin": "Number - Start time for exit animation (seconds)",
                "exitEnd": "Number - End time for exit animation (seconds)",
                "enterAnimation": "String - 'fade', 'slide', etc.",
                "exitAnimation": "String - 'fade', 'slide', etc."
            },
            "text_specific": {
                "text": "String - The text content to display",
                "style": "Object - CSS-like styling (fontSize, color, fontFamily, fontWeight, etc.)"
            },
            "image_video_specific": {
                "src": "String - URL or local path to the media file"
            },
            "svg_specific": {
                "svg": "String - Raw SVG markup"
            }
        },
        
        "tips": [
            "Use enterBegin/enterEnd and exitBegin/exitEnd to control when elements appear and disappear",
            "Animations like 'fade' create smooth transitions between states",
            "Position can be a preset string ('center', 'top-left') or precise x/y coordinates",
            "Resolution '720p' = 1280x720, 'full-hd' = 1920x1080, '4k' = 3840x2160",
            "For complex layouts, use x/y positioning instead of preset positions",
            "Subtitles are overlaid on top of all visuals automatically"
        ],
        
        "support": {
            "swagger_ui": "Visit /docs for interactive API documentation with full schemas",
            "contact": "https://github.com/felix/json2videoapi",
            "documentation": "See README.md for setup and deployment instructions"
        }
    }
    
    return templates.TemplateResponse("help.html", {"request": request, **help_data})

@app.get("/", response_class=HTMLResponse, tags=["Utilities"])
async def root_redirect(request: Request):
    """Redirect root requests to API help."""
    return await api_help(request)

@app.get("/health", tags=["Utilities"])
async def health_check():
    """Basic health check to verify service availability."""
    return {"status": "ok"}
