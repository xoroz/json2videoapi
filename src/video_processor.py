import subprocess
import json
import os
import tempfile
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
from .schemas import VideoProject, JobStatus
from .config_loader import ROOT_DIR, get_output_dir

class VideoProcessingError(Exception):
    pass

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, dict] = {}

    def create_job(self, project_name: str) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "job_id": job_id,
            "name": project_name,
            "status": JobStatus.QUEUED,
            "progress": 0,
            "created_at": datetime.now(),
            "output_file": None,
            "error": None
        }
        return job_id

    def update_job(self, job_id: str, **kwargs):
        if job_id in self.jobs:
            self.jobs[job_id].update(kwargs)

    def get_job(self, job_id: str) -> Optional[dict]:
        return self.jobs.get(job_id)

job_manager = JobManager()

async def trim_audio_to_duration(audio_src: str, duration: float, project_name: str) -> str:
    """
    Trim audio file to specified duration using FFmpeg.
    Returns path to the trimmed audio file in artifacts directory.
    """
    import logging
    logger = logging.getLogger("src.main")
    
    # Resolve audio path relative to ROOT_DIR
    audio_path = Path(audio_src)
    if not audio_path.is_absolute():
        audio_path = ROOT_DIR / audio_src
    
    # Check if audio file exists
    if not audio_path.exists():
        raise VideoProcessingError(f"Audio file not found: {audio_src}")
    
    # Create trimmed audio in artifacts directory
    artifacts_dir = ROOT_DIR / "tests" / "data" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename based on project name and duration
    safe_name = project_name.replace(" ", "-").replace("/", "-")
    trimmed_filename = f"{safe_name}-audio-{int(duration)}s.mp3"
    trimmed_audio_path = artifacts_dir / trimmed_filename
    
    try:
        # Use FFmpeg to trim audio to specified duration
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-t", str(duration),
            "-acodec", "copy",
            "-y",  # Overwrite output file
            str(trimmed_audio_path)
        ]
        
        logger.info(f"Trimming audio {audio_src} to {duration} seconds -> {trimmed_audio_path}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"FFmpeg audio trim failed: {error_msg}")
            # Clean up file on error
            if trimmed_audio_path.exists():
                trimmed_audio_path.unlink()
            raise VideoProcessingError(f"Audio trimming failed: {error_msg}")
        
        logger.info(f"Audio trimmed successfully to {trimmed_audio_path}")
        return str(trimmed_audio_path)
        
    except Exception as e:
        # Clean up file on error
        if trimmed_audio_path.exists():
            trimmed_audio_path.unlink()
        raise

async def generate_video(project: VideoProject, job_id: str) -> str:

    job_manager.update_job(job_id, status=JobStatus.PROCESSING, progress=10)
    
    # Define paths
    zvid_script = ROOT_DIR / "zvid" / "generate-video.js"
    output_dir = get_output_dir()
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a temporary file for the project JSON
    # Explicitly set width/height if missing, based on resolution, to satisfy zvid validation
    project_dict = project.model_dump(exclude_none=True)
    if "width" not in project_dict or "height" not in project_dict:
        res = project_dict.get("resolution", "hd")
        presets = {
            "sd": (640, 480),
            "hd": (1280, 720),
            "full-hd": (1920, 1080),
            "squared": (1080, 1080),
            "youtube-short": (1080, 1920),
            "instagram-story": (1080, 1920),
            "instagram-post": (1080, 1080),
            "instagram-reel": (1080, 1920),
            "tiktok": (1080, 1920),
            "twitter-landscape": (1200, 675),
            "twitter-portrait": (1080, 1350),
            "twitter-square": (1080, 1080),
            "facebook-video": (1080, 1920),
            "facebook-story": (1080, 1920),
            "facebook-post": (1080, 1080),
            "snapchat": (1080, 1920),
        }
        if res in presets:
            w, h = presets[res]
            project_dict.setdefault("width", w)
            project_dict.setdefault("height", h)

    # Process audio files - trim to video duration for optimization
    trimmed_audio_files = []
    if "audios" in project_dict and project_dict["audios"]:
        import logging
        logger = logging.getLogger("src.main")
        logger.info(f"Processing {len(project_dict['audios'])} audio file(s)")
        
        for i, audio in enumerate(project_dict["audios"]):
            if "src" in audio:
                try:
                    # Trim audio to video duration
                    trimmed_path = await trim_audio_to_duration(
                        audio["src"], 
                        project_dict["duration"],
                        project_dict["name"]
                    )
                    trimmed_audio_files.append(trimmed_path)
                    # Update the audio source to point to trimmed file
                    project_dict["audios"][i]["src"] = trimmed_path
                    logger.info(f"Audio {i+1} trimmed and ready")
                except Exception as e:
                    logger.error(f"Failed to trim audio {audio['src']}: {e}")
                    # Clean up any already trimmed files
                    for temp_file in trimmed_audio_files:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    raise

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        json.dump(project_dict, tmp)
        tmp_path = tmp.name

    try:
        # Construct the command
        cmd = ["node", str(zvid_script), tmp_path, str(output_dir)]
        
        # Run the subprocess asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Log node output for debugging
        stdout_msg = stdout.decode().strip()
        stderr_msg = stderr.decode().strip()
        import logging
        logger = logging.getLogger("src.main")
        if stdout_msg:
            logger.info(f"Node output: {stdout_msg}")
        if stderr_msg:
            logger.warning(f"Node stderr: {stderr_msg}")

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            job_manager.update_job(job_id, status=JobStatus.FAILED, error=error_msg)
            raise VideoProcessingError(f"Video generation failed: {error_msg}")
            
        # Parse stdout to find the success message
        output_lines = stdout.decode().splitlines()
        video_path = None
        
        for line in output_lines:
            if line.startswith("SUCCESS:"):
                video_path = line.split("SUCCESS:", 1)[1].strip()
                
        if not video_path:
             job_manager.update_job(job_id, status=JobStatus.FAILED, error="No path returned")
             raise VideoProcessingError("Video generation completed but returned no path.")
             
        job_manager.update_job(job_id, status=JobStatus.COMPLETED, progress=100, output_file=video_path)
        return video_path

    except Exception as e:
        job_manager.update_job(job_id, status=JobStatus.FAILED, error=str(e))
        raise

    finally:
        # Clean up the temp JSON file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        
        # Note: Trimmed audio files are kept in artifacts directory for reuse

