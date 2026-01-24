import os
from pathlib import Path
from typing import List, Tuple
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Handles image processing tasks like resizing and cropping using Pillow.
    """
    
    def __init__(self):
        self.output_size = (1080, 1920) # 9:16 aspect ratio
        
    def process_images(self, image_paths: List[str], output_dir: str) -> List[str]:
        """
        Resize and center-crop a list of images to 1080x1920.
        
        Args:
            image_paths: List of absolute paths to source images
            output_dir: Directory to save processed images
            
        Returns:
            List of absolute paths to processed images
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        processed_images = []
        
        for i, img_path in enumerate(image_paths):
            try:
                processed_path = self._process_single_image(img_path, output_path, i)
                processed_images.append(processed_path)
            except Exception as e:
                logger.error(f"Failed to process image {img_path}: {e}")
                # If processing fails, we might want to skip or raise. 
                # For now, let's raise to fail fast as sync depends on all images.
                raise
                
        return processed_images

    def _process_single_image(self, img_path: str, output_dir: Path, index: int) -> str:
        """
        Process a single image: resize, crop, and save.
        """
        try:
            with Image.open(img_path) as img:
                # Calculate aspect ratio and resize/crop to fill 1080x1920
                img_ratio = img.width / img.height
                target_ratio = self.output_size[0] / self.output_size[1]
                
                # Copy image logic from user example
                if img_ratio > target_ratio: # Image is too wide
                    new_width = int(target_ratio * img.height)
                    offset = (img.width - new_width) // 2
                    # crop((left, top, right, bottom))
                    img = img.crop((offset, 0, offset + new_width, img.height))
                else: # Image is too tall
                    new_height = int(img.width / target_ratio)
                    offset = (img.height - new_height) // 2
                    img = img.crop((0, offset, img.width, offset + new_height))
                
                final_img = img.resize(self.output_size, Image.LANCZOS)
                
                # Save
                # Use a consistent naming scheme for sync manager
                out_name = f"proc_{index}.jpg"
                out_full_path = output_dir / out_name
                
                # Convert to RGB to handle PNGs with transparency if needed, 
                # though user example didn't explicitely say, usually safest for JPEG output
                if final_img.mode in ('RGBA', 'P'): 
                    final_img = final_img.convert('RGB')
                
                final_img.save(out_full_path, quality=95)
                logger.debug(f"Processed image saved to {out_full_path}")
                
                return str(out_full_path)
        except Exception as e:
             logger.error(f"Error processing {img_path}: {e}")
             raise

