"""
Voice Generator using ElevenLabs API for text-to-speech conversion.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables from .env file
load_dotenv()

from ..config_loader import ROOT_DIR, settings

logger = logging.getLogger(__name__)


class VoiceGenerationError(Exception):
    """Raised when voice generation fails."""
    pass


class VoiceGenerator:
    """
    Handles AI voice generation using ElevenLabs API.
    """
    
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not found in environment variables")
        
        self.voice_id = settings.get('elevenlabs', 'voice_id', fallback='Qggl4b0xRMiqOwhPtVWT')
        
        # Initialize ElevenLabs client
        if self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
        else:
            self.client = None
        
    async def generate_voice(
        self, 
        text: str, 
        output_path: Optional[str] = None,
        voice_settings: Optional[dict] = None
    ) -> str:
        """
        Generate voice audio from text using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            output_path: Optional path to save the audio file. If not provided,
                        saves to tests/data/artifacts/
            voice_settings: Optional voice settings (stability, similarity_boost, etc.)
        
        Returns:
            Path to the generated audio file
        
        Raises:
            VoiceGenerationError: If API call fails or API key is missing
        """
        if not self.api_key or not self.client:
            raise VoiceGenerationError("ELEVENLABS_API_KEY environment variable not set")
        
        # Prepare output path
        if output_path is None:
            artifacts_dir = ROOT_DIR / "tests" / "data" / "artifacts"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            # Create filename from first few words of text + hash for uniqueness
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            safe_name = "-".join(text.split()[:5]).replace(",", "").replace(".", "").replace(" ", "-")
            output_path = artifacts_dir / f"voice-{safe_name}-{text_hash}.mp3"
        else:
            output_path = Path(output_path)
        
        logger.info(f"Generating voice for text: '{text[:50]}...'")
        logger.info(f"Using voice_id: {self.voice_id}")
        
        try:
            # Generate audio using ElevenLabs SDK
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2"
            )
            
            # The convert method returns a generator of audio chunks
            # We need to collect all chunks and save them
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)
            
            # Combine all chunks
            audio_data = b''.join(audio_chunks)
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"Voice generated successfully: {output_path}")
            logger.info(f"Audio size: {len(audio_data) / 1024:.2f} KB")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error during voice generation: {e}")
            raise VoiceGenerationError(f"Voice generation failed: {e}")
    
    async def validate_api_key(self) -> bool:
        """
        Validate the ElevenLabs API key by making a test request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        if not self.api_key or not self.client:
            logger.error("No API key to validate")
            return False
        
        try:
            # Try to get voices to validate the API key
            voices = self.client.voices.get_all()
            if voices:
                logger.info("ElevenLabs API key validated successfully")
                logger.info(f"Available voices: {len(voices.voices)}")
                return True
            else:
                logger.error("API key validation failed: No voices returned")
                return False
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False


    async def generate_with_timestamps(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate voice audio with timestamps using ElevenLabs API SDK.
        
        Args:
            text: Text to convert
            output_path: Optional path for audio file
            
        Returns:
            Tuple of (audio_file_path, alignment_data)
        """
        if not self.api_key or not self.client:
             raise VoiceGenerationError("ELEVENLABS_API_KEY environment variable not set")
             
        try:
            logger.info(f"Generating voice with timestamps for text: '{text[:50]}...'")
            
            # Use SDK method
            response = self.client.text_to_speech.convert_with_timestamps(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings=None # default
            )
            
            # Extract audio and alignment
            # Check if response is bytes (AudioWithTimestampsResponse usually contains audio)
            # Inspect shows return type AudioWithTimestampsResponse
            
            # Based on SDK types, we might need to access attributes
            # Assuming response has .audio_base64 or .audio and .alignment
            
            # If using convert_with_timestamps (not stream), it returns the whole object.
            
            # Let's handle attributes assuming Pydantic model
            # However, raw inspection showed return type annotation.
            
            # If we don't know exact attribs, we can try to verify with dir() in debug 
            # or try standard access.
            
            # Usually: response.audio (bytes) and response.alignment (Alignment object)
            
            # But wait, inspection output says it returns AudioWithTimestampsResponse.
            # I will trust it has 'alignment' and 'audio' (or audio_base64).
            
            # Let's assume response is a Pydantic model and use .model_dump() or dict() if possible?
            # Or just attribute access.
            
            # Attribute is audio_base_64
            import base64
            
            alignment_obj = response.alignment
            audio_bytes = base64.b64decode(response.audio_base_64) # Decode base64 string
            
            # Save audio
            if output_path is None:
                artifacts_dir = ROOT_DIR / "tests" / "data" / "artifacts"
                artifacts_dir.mkdir(parents=True, exist_ok=True)
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_path = artifacts_dir / f"voice-ts-{text_hash}.mp3"
            else:
                output_path = Path(output_path)
                
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
                
            # Convert alignment object to dict for processing
            # Alignment object has characters, character_start_times_seconds, etc.
            
            alignment_dict = {
                "characters": alignment_obj.characters,
                "character_start_times_seconds": alignment_obj.character_start_times_seconds,
                "character_end_times_seconds": alignment_obj.character_end_times_seconds
            }
            
            words_data = self._convert_alignment_to_words(alignment_dict)
            
            logger.info(f"Generated voice with timestamps: {output_path}")
            return str(output_path), words_data

        except Exception as e:
            logger.error(f"Error in generate_with_timestamps: {e}")
            raise VoiceGenerationError(f"Failed to generate with timestamps: {e}")

    def _convert_alignment_to_words(self, alignment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert character-level alignment to word-level alignment.
        """
        chars = alignment.get("characters", [])
        starts = alignment.get("character_start_times_seconds", [])
        ends = alignment.get("character_end_times_seconds", [])
        
        words = []
        word_starts = []
        word_ends = []
        
        current_word = ""
        current_start = None
        
        for i, char in enumerate(chars):
            if char == " ":
                if current_word:
                    words.append(current_word)
                    word_starts.append(current_start if current_start is not None else starts[i])
                    word_ends.append(ends[i-1] if i > 0 else ends[i])
                    current_word = ""
                    current_start = None
            else:
                if current_start is None:
                    current_start = starts[i]
                current_word += char
                
        # Last word
        if current_word:
            words.append(current_word)
            word_starts.append(current_start)
            word_ends.append(ends[-1])
            
        return {
            "words": words,
            "start_times": word_starts,
            "end_times": word_ends
        }
