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
from .processors.voice_generator import VoiceGenerator, VoiceGenerationError
from .processors.audio_processor import AudioProcessor

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
    
    # Generate filename based on project name, source filename, and duration
    safe_name = project_name.replace(" ", "-").replace("/", "-")
    source_name = audio_path.stem
    trimmed_filename = f"{safe_name}-{source_name}-{int(duration)}s.mp3"
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

from .processors.video_engine import VideoEngine

# ... (keep existing imports)

async def generate_video(project: VideoProject, job_id: str) -> str:

    job_manager.update_job(job_id, status=JobStatus.PROCESSING, progress=10)
    
    # Define paths
    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Project conversion to dict for easier access
    project_dict = project.model_dump(exclude_none=True)
    
    try:
        # Collect assets for VideoEngine
        script_parts = []
        image_paths = []
        
        # 1. Extract Script from Voices
        if "voices" in project_dict and project_dict["voices"]:
            for voice in project_dict["voices"]:
                if "text" in voice:
                    script_parts.append(voice["text"])
        
        full_script = " ".join(script_parts)
        
        # 2. Extract Images from Visuals
        if "visuals" in project_dict and project_dict["visuals"]:
            for visual in project_dict["visuals"]:
                if "src" in visual:
                    src = visual["src"]
                    # Resolve to absolute path
                    path_obj = Path(src)
                    if not path_obj.is_absolute():
                         path_obj = ROOT_DIR / src
                    
                    if path_obj.exists():
                        image_paths.append(str(path_obj))
                    else:
                         import logging
                         logging.getLogger("src.main").warning(f"Image not found: {path_obj}")
        
        if not full_script and not image_paths:
            # Fallback to legacy zvid or error?
            # User wants to replace JSON2Video, so let's try VideoEngine even with empty script?
            # VideoEngine needs script for voice.
            # If no script, maybe we can't use VideoEngine for voice syncing.
            # But the requirement is "add-ai-voice-generation".
            pass

        # 3. Use VideoEngine
        import logging
        logger = logging.getLogger("src.main")
        logger.info(f"Starting Python VideoEngine for job {job_id}")
        
        engine = VideoEngine()
        
        # We need to handle the case where there is no script (maybe just images?)
        # VideoEngine.create_video currently REQUIRES script_text for voice generation.
        # If full_script is empty, we should define behavior. 
        # For now, we assume this flow is for Voice+Images.
        
        output_filename = f"video_{job_id}.mp4"
        
        video_path = await engine.create_video(
            script_text=full_script if full_script else " ", # Avoid empty string error if any
            image_paths=image_paths,
            output_filename=output_filename
        )
        
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

