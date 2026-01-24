"""
Audio Processor for handling audio-related tasks.
"""

import subprocess
import asyncio
import os
from pathlib import Path
from typing import Optional
import logging

from ..config_loader import ROOT_DIR

logger = logging.getLogger(__name__)


class AudioProcessingError(Exception):
    """Raised when audio processing fails."""
    pass


class AudioProcessor:
    """
    Handles audio processing tasks like trimming, downloading, and validation.
    """
    
    @staticmethod
    async def trim_audio(
        input_path: str,
        duration: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Trim audio file to specified duration using FFmpeg.
        
        Args:
            input_path: Path to input audio file
            duration: Duration in seconds to trim to
            output_path: Optional output path. If not provided, generates one.
        
        Returns:
            Path to trimmed audio file
        
        Raises:
            AudioProcessingError: If trimming fails
        """
        # Resolve input path
        audio_path = Path(input_path)
        if not audio_path.is_absolute():
            audio_path = ROOT_DIR / input_path
        
        if not audio_path.exists():
            raise AudioProcessingError(f"Audio file not found: {input_path}")
        
        # Generate output path if not provided
        if output_path is None:
            artifacts_dir = ROOT_DIR / "tests" / "data" / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            output_path = artifacts_dir / f"trimmed-{int(duration)}s-{audio_path.name}"
        else:
            output_path = Path(output_path)
        
        # FFmpeg command to trim audio
        cmd = [
            "ffmpeg",
            "-i", str(audio_path),
            "-t", str(duration),
            "-acodec", "copy",
            "-y",
            str(output_path)
        ]
        
        logger.info(f"Trimming audio: {input_path} -> {duration}s")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"FFmpeg trim failed: {error_msg}")
                if output_path.exists():
                    output_path.unlink()
                raise AudioProcessingError(f"Audio trimming failed: {error_msg}")
            
            logger.info(f"Audio trimmed successfully: {output_path}")
            return str(output_path)
        
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise AudioProcessingError(f"Error trimming audio: {e}")
    
    @staticmethod
    async def get_audio_duration(audio_path: str) -> float:
        """
        Get duration of audio file in seconds using FFprobe.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Duration in seconds
        
        Raises:
            AudioProcessingError: If unable to get duration
        """
        path = Path(audio_path)
        if not path.is_absolute():
            path = ROOT_DIR / audio_path
        
        if not path.exists():
            raise AudioProcessingError(f"Audio file not found: {audio_path}")
        
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise AudioProcessingError(f"FFprobe failed: {stderr.decode()}")
            
            duration = float(stdout.decode().strip())
            return duration
        
        except ValueError as e:
            raise AudioProcessingError(f"Invalid duration value: {e}")
        except Exception as e:
            raise AudioProcessingError(f"Error getting audio duration: {e}")
    
    @staticmethod
    def validate_audio_file(audio_path: str) -> bool:
        """
        Validate that a file is a valid audio file.
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            True if valid, False otherwise
        """
        path = Path(audio_path)
        if not path.is_absolute():
            path = ROOT_DIR / audio_path
        
        if not path.exists():
            return False
        
        # Check file extension
        valid_extensions = {'.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac'}
        if path.suffix.lower() not in valid_extensions:
            return False
        
        return True

    @staticmethod
    async def mix_audios(
        audio_configs: list,
        output_duration: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Mix multiple audio files into a single track with offsets and volumes using FFmpeg.
        
        Args:
            audio_configs: List of dicts with keys:
                          - src: path to audio file
                          - volume: volume multiplier (0.0 to 1.0)
                          - videoBegin: start time in video (seconds)
            output_duration: Total duration of the resulting mixed track
            output_path: Optional output path
            
        Returns:
            Path to the mixed audio file
        """
        if not audio_configs:
            raise AudioProcessingError("No audio configurations provided for mixing")

        # Resolve output path
        if output_path is None:
            artifacts_dir = ROOT_DIR / "tests" / "data" / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            output_path = artifacts_dir / f"mixed-audio-{int(output_duration)}s.mp3"
        else:
            output_path = Path(output_path)

        # Build FFmpeg command
        inputs = []
        filter_parts = []
        
        for i, config in enumerate(audio_configs):
            src = config['src']
            path = Path(src)
            if not path.is_absolute():
                path = ROOT_DIR / src
            
            if not path.exists():
                logger.warning(f"Audio file not found during mixing: {src}")
                continue
                
            inputs.extend(["-i", str(path)])
            
            # Apply volume and delay
            # adelay expects milliseconds
            delay_ms = int(config.get('videoBegin', 0) * 1000)
            volume = config.get('volume', 1.0)
            
            # Note: adelay syntax for Stereo is delay|delay
            filter_parts.append(f"[{i}:a]adelay={delay_ms}|{delay_ms},volume={volume}[a{i}]")

        # Combine all tracks using amix
        mix_inputs = "".join([f"[a{i}]" for i in range(len(filter_parts))])
        amix_filter = f"{mix_inputs}amix=inputs={len(filter_parts)}:duration=first:dropout_transition=3[out]"
        
        full_filter = ";".join(filter_parts + [amix_filter])

        cmd = [
            "ffmpeg",
            *inputs,
            "-filter_complex", full_filter,
            "-map", "[out]",
            "-t", str(output_duration),
            "-y",
            str(output_path)
        ]

        logger.info(f"Mixing {len(audio_configs)} audio tracks into {output_path}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"FFmpeg mix failed: {error_msg}")
                raise AudioProcessingError(f"Audio mixing failed: {error_msg}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error mixing audios: {e}")
            raise AudioProcessingError(f"Unexpected error during audio mixing: {e}")
