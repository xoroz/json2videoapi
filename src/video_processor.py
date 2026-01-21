import subprocess
import json
import os
import tempfile
import asyncio
from pathlib import Path
from .schemas import VideoProject
from .config_loader import ROOT_DIR, get_output_dir

class VideoProcessingError(Exception):
    pass

async def generate_video(project: VideoProject) -> str:
    """
    Generates a video from the project definition using the zvid Node.js script.
    Returns the path to the generated video file.
    """
    
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
            stdout_msg = stdout.decode().strip()
            raise VideoProcessingError(f"Video generation failed: {error_msg}\nSTDOUT: {stdout_msg}")
            
        # Parse stdout to find the success message
        output_lines = stdout.decode().splitlines()
        video_path = None
        
        for line in output_lines:
            if line.startswith("SUCCESS:"):
                video_path = line.split("SUCCESS:", 1)[1].strip()
                
        if not video_path:
             raise VideoProcessingError("Video generation completed but returned no path.")
             
        return video_path

    finally:
        # Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
