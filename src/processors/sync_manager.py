import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SyncManager:
    """
    Handles synchronization of audio, images, and subtitles.
    Generates FFmpeg input files (inputs.txt) and subtitle files (subs.ass).
    """
    
    def __init__(self):
        pass

    def generate_sync_map(
        self, 
        processed_images: List[str], 
        alignment_data: Dict[str, Any], 
        marker_words: Optional[List[str]] = None,
        output_dir: str = "/tmp"
    ) -> str:
        """
        Generates the inputs.txt file for FFmpeg concat demuxer.
        
        Args:
            processed_images: List of paths to processed (resized) images.
            alignment_data: Dictionary containing 'words', 'start_times', 'end_times'.
            marker_words: Optional list of words to trigger image changes.
            output_dir: Directory to save inputs.txt.
            
        Returns:
            Path to the generated inputs.txt file.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        inputs_txt_path = output_path / "inputs.txt"
        
        words = alignment_data.get('words', [])
        start_times = alignment_data.get('start_times', [])
        end_times = alignment_data.get('end_times', [])
        
        if not words or not start_times:
            logger.warning("No alignment data provided, using equal duration fallback")
            # TODO: Implement fallback or error
            # For now, let's assume we have data or raise
            pass

        # Calculate sync points
        sync_points = [0.0]
        
        if marker_words:
            # Normalize alignment words for matching
            # Remove punctuation and lowercase
            normalized_words = []
            for w in words:
                 # Simple strip of common punctuation
                 clean_w = w.lower().strip(".,!?;:\"'")
                 normalized_words.append(clean_w)
            
            # Use specific marker words
            for marker in marker_words:
                clean_marker = marker.lower().strip()
                
                # Find first occurrence in normalized list
                if clean_marker in normalized_words:
                    idx = normalized_words.index(clean_marker)
                    start_t = start_times[idx]
                    
                    # Avoid duplicates or out-of-order if user provided bad markers
                    if start_t not in sync_points:
                        sync_points.append(start_t)
                else:
                    logger.warning(f"Marker word '{marker}' not found in transcript.")
            
            # Sort sync points just in case markers were out of order
            sync_points.sort()

        else:
            # Fallback: Distribute evenly based on word count/image count
            # Logic from "generate_even_sync" in user example
            total_words = len(words)
            if len(processed_images) > 0:
                step = total_words // len(processed_images)
                last_time = 0.0
                # We need to recalculate sync points based on even distribution
                sync_points = [0.0]
                for i in range(len(processed_images) - 1): # -1 because last one goes to end
                    word_idx = min((i + 1) * step, total_words - 1)
                    if word_idx < len(end_times):
                        sync_points.append(end_times[word_idx])
                
        # Ensure we have end time
        if end_times:
            final_end = end_times[-1]
            if sync_points[-1] != final_end:
                 sync_points.append(final_end)
        
        # Write inputs.txt
        with open(inputs_txt_path, "w") as f:
            for i, img in enumerate(processed_images):
                # Calculate duration
                if i < len(sync_points) - 1:
                    duration = sync_points[i+1] - sync_points[i]
                else:
                    # Fallback if we run out of sync points
                    duration = 2.0 # Default fallback
                
                # Round to 3 decimal places
                duration = round(duration, 3)
                
                f.write(f"file '{img}'\n")
                f.write(f"duration {duration}\n")
            
            # FFmpeg quirk: The last image must be repeated without a duration (or just file entry)
            # The logic in user example:
            # f.write(f"file '{image_list[-1]}'\n")
            if processed_images:
                f.write(f"file '{processed_images[-1]}'\n")
                
        logger.info(f"Sync map generated at {inputs_txt_path}")
        return str(inputs_txt_path)

    def generate_subtitles(
        self,
        alignment_data: Dict[str, Any],
        output_dir: str = "/tmp"
    ) -> str:
        """
        Generates subs.ass file with karaoke timing.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        subs_path = output_path / "subs.ass"
        
        # Updated ASS Header for better visibility and karaoke style
        ass_content = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # Fontsize 125 (was 60), MarginV 850 (was 50), Outline 3
            # Colors: Primary=Yellow(&H0000FFFF), Secondary=DarkGray(&H00808080) for karaoke effect? 
            # Or Primary=White, Secondary=Blue?
            # Let's try Primary=White, Secondary=Blue(&H00FF0000). 
            # Note: ASS Color is AABBGGRR. White = &H00FFFFFF. Blue = &H00FF0000.
            "Style: Default,Arial,125,&H00FFFFFF,&H00FF0000,&H00000000,&H00000000,1,0,1,3,0,2,10,10,850,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]
        
        words = alignment_data.get('words', [])
        start_times = alignment_data.get('start_times', [])
        end_times = alignment_data.get('end_times', [])
        
        WORDS_PER_LINE = 4
        
        # Iterate in chunks
        for i in range(0, len(words), WORDS_PER_LINE):
            chunk_words = words[i:i + WORDS_PER_LINE]
            chunk_starts = start_times[i:i + WORDS_PER_LINE]
            chunk_ends = end_times[i:i + WORDS_PER_LINE]
            
            if not chunk_words:
                continue
                
            # Line timing
            line_start_time = chunk_starts[0]
            line_end_time = chunk_ends[-1]
            
            ass_line_parts = []
            
            for j in range(len(chunk_words)):
                word = chunk_words[j]
                w_start = chunk_starts[j]
                w_end = chunk_ends[j]
                
                # Determine "karaoke duration" for this word
                # If it's not the last word in this chunk, stretch to next word's start
                # This covers small gaps smoothly
                if j < len(chunk_words) - 1:
                    next_start = chunk_starts[j + 1]
                    duration_seconds = next_start - w_start
                else:
                    # Last word in chunk, just use its own duration
                    duration_seconds = w_end - w_start
                
                # Minimum duration safeguard (ASS doesn't like 0)
                if duration_seconds < 0.01:
                    duration_seconds = 0.01
                    
                dur_cs = int(duration_seconds * 100)
                
                # Add space after word if it's not the absolutely last word of the script?
                # Or just space between words in the line.
                # ASS: {\kXX}Word becomes a highlighted block.
                # structure: {\kXX}Word{\kYY} next
                # We put the space INSIDE the styling of the current word or next?
                # Usually: {\kXX}Word 
                
                # Add trailing space for all but the last word in the *displayed line*
                text_part = word
                if j < len(chunk_words) - 1:
                    text_part += " "
                
                ass_line_parts.append(f"{{\\k{dur_cs}}}{text_part}")
            
            full_line_text = "".join(ass_line_parts)
            
            start_str = self._format_ass_time(line_start_time)
            end_str = self._format_ass_time(line_end_time)
            
            ass_content.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{full_line_text}")
        
        with open(subs_path, "w") as f:
            f.write("\n".join(ass_content))
            
        logger.info(f"Subtitles generated at {subs_path}")
        return str(subs_path)
        
    def _format_ass_time(self, seconds: float) -> str:
        """Converts seconds to H:MM:SS.cs format for ASS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:05.2f}"

