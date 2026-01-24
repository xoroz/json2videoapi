import asyncio
import os
from pathlib import Path
from PIL import Image
from src.processors.video_engine import VideoEngine

# Setup paths
TEST_DIR = Path("tests/data/temp_test")
TEST_DIR.mkdir(parents=True, exist_ok=True)

async def main():
    print("Starting E2E Workflow Test with Real Images...")
    
    # 1. Load Test Config from JSON
    json_path = Path("tests/data/complete-voice-example.json")
    if not json_path.exists():
        print(f"ERROR: Config file not found: {json_path}")
        return

    import json
    with open(json_path) as f:
        config = json.load(f)
        
    print(f"Loaded config from {json_path}")
    
    script = config["script"]
    markers = config["markers"]
    
    # Resolve image paths relative to the repo root/cwd
    # The JSON has relative paths "tests/data/artifacts/X.png"
    images = []
    for img_rel_path in config["images"]:
        img_full_path = Path(img_rel_path).absolute()
        if img_full_path.exists():
            images.append(str(img_full_path))
            print(f"Found image: {img_full_path}")
        else:
            print(f"ERROR: Image not found: {img_full_path}")
            return
    
    # 3. Initialize Engine
    engine = VideoEngine()
    
    # 4. Run Pipeline
    try:
        print("Running VideoEngine pipeline...")
        # Note: ensuring we have API key
        if not os.getenv("ELEVENLABS_API_KEY"):
            print("WARNING: ELEVENLABS_API_KEY not set. Test might fail.")
        
        output_video = await engine.create_video(
            script_text=script,
            image_paths=images,
            output_filename="test_real_images.mp4",
            marker_words=markers
        )
        
        print(f"SUCCESS: Video generated at {output_video}")
        
        # Validate existence
        if os.path.exists(output_video):
            size = os.path.getsize(output_video)
            print(f"File size: {size} bytes")
        else:
            print("ERROR: Output file does not exist!")
            
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
