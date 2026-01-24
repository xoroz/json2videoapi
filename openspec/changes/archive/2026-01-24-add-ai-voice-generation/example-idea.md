To sync images with ElevenLabs audio based on specific text timestamps, the best approach is to use a Concat Demuxer file.

This method allows you to tell FFmpeg exactly how long each image should stay on screen (e.g., Image 1 until the word "Hello", Image 2 until the word "World").
1. The Strategy

Instead of guessing durations, we use the ElevenLabs character_start_times_seconds or word_timestamps to calculate the duration for each image.
2. Python Script to Generate the Sync File

This script calculates the durations between your chosen "transition words" and creates an inputs.txt file for FFmpeg.
Python

import json

# Your ElevenLabs timestamp data
# Typically looks like: {"words": ["Welcome", "to", "my", "video", ...], "start_times": [0.0, 0.4, 0.8, 1.2, ...]}
elevenlabs_data = {
    "words": ["Welcome", "to", "this", "automated", "TikTok", "video", "tutorial"],
    "start_times": [0.0, 0.5, 0.8, 1.2, 1.8, 2.3, 2.9]
}

# Define which words trigger an image change
# Or just divide the total audio duration by number of images
images = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"]
total_duration = 10.5 # Get this from the audio file length

def generate_ffmpeg_concat(images, timestamps, total_duration):
    # Calculate duration per image (e.g., change every 2 seconds or based on specific words)
    # For this example, we'll just divide duration evenly, but you can use 
    # timestamps['start_times'][index] to trigger on specific words.
    duration_per_image = total_duration / len(images)
    
    with open("inputs.txt", "w") as f:
        for i, img in enumerate(images):
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration_per_image}\n")
        
        # FFmpeg quirk: The last image must be repeated without a duration
        f.write(f"file '{images[-1]}'\n")

generate_ffmpeg_concat(images, elevenlabs_data, total_duration)

3. The FFmpeg Command

Now, run FFmpeg using the inputs.txt we just created. This command will:

    Read the images and their specific durations.

    Add the ElevenLabs audio.

    Burn the .ass subtitles on top.

Bash

ffmpeg -f concat -safe 0 -i inputs.txt \
-i speech.mp3 \
-vf "ass=subs.ass,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
-c:v libx264 -pix_fmt yuv420p \
-c:a copy -shortest \
final_video.mp4

Key Workflow Steps for n8n:

    Step 1: Use an HTTP Request node to get the ElevenLabs audio + timestamps.

    Step 2: Use a Code Node (Python) to:

        Parse the timestamps.

        Write the inputs.txt file (image timing).

        Write the subs.ass file (karaoke text).

    Step 3: Use the Execute Command node to run the FFmpeg command above.

Pro-Tip: Vertical Cropping

Since your images might not be 9:16 (TikTok size), I added scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920 to the filter. This ensures your images fill the entire TikTok screen without black bars.

Would you like me to show you how to map specific words from the ElevenLabs JSON to trigger the image changes?

yes show me!

To make the images change exactly when a specific word is spoken, we need to find the timestamp of that word in the ElevenLabs JSON and use it to calculate the duration of each image for FFmpeg's concat file.
1. The Strategy: "The Word-to-Image Map"

We define an array of "Marker Words." Whenever the script sees one of these words in the ElevenLabs transcript, it marks that time as the point to switch to the next image.
2. Python Logic (n8n Code Node)

This script processes the ElevenLabs alignment data and generates the inputs.txt file for FFmpeg.
Python

import json

# Example Data from ElevenLabs API response
elevenlabs_response = {
    "words": ["Welcome", "to", "this", "amazing", "journey", "through", "space", "and", "time"],
    "start_times": [0.0, 0.4, 0.7, 1.1, 1.8, 2.4, 2.9, 3.2, 3.8],
    "end_times": [0.3, 0.6, 1.0, 1.7, 2.3, 2.8, 3.1, 3.7, 4.5]
}

# The images you want to use
images = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"]

# The words where you want the image to CHANGE
# Note: Ensure these words actually exist in your script!
marker_words = ["amazing", "journey", "space", "time"]

def generate_sync_file(data, image_list, markers):
    sync_points = [0.0] # Always start at 0
    
    # Find the start time for each marker word
    for word in markers:
        if word in data['words']:
            idx = data['words'].index(word)
            sync_points.append(data['start_times'][idx])
    
    # Add the final end time
    sync_points.append(data['end_times'][-1])
    
    # Calculate durations (Difference between sync points)
    durations = []
    for i in range(len(sync_points) - 1):
        durations.append(sync_points[i+1] - sync_points[i])

    # Create the FFmpeg concat file
    with open("inputs.txt", "w") as f:
        for i, img in enumerate(image_list):
            # If we have more images than durations, use the last duration
            d = durations[i] if i < len(durations) else 1.0
            f.write(f"file '{img}'\n")
            f.write(f"duration {round(d, 3)}\n")
        
        # FFmpeg requires the last file to be repeated
        f.write(f"file '{image_list[-1]}'\n")

generate_sync_file(elevenlabs_response, images, marker_words)

3. Handling the "Missing Words" Edge Case

If you don't want to manually pick words, a safer way is to just split the total word count by the number of images:
Python

def generate_even_sync(data, image_list):
    total_words = len(data['words'])
    step = total_words // len(image_list)
    
    with open("inputs.txt", "w") as f:
        last_time = 0.0
        for i in range(len(image_list)):
            word_idx = min((i + 1) * step, total_words - 1)
            end_time = data['end_times'][word_idx]
            duration = end_time - last_time
            
            f.write(f"file '{image_list[i]}'\n")
            f.write(f"duration {round(duration, 3)}\n")
            last_time = end_time
        f.write(f"file '{image_list[-1]}'\n")

4. The Final FFmpeg Polish

To make it look like a real TikTok, we’ll add a slight zoom effect (Ken Burns) so the images aren't static while the text glows.
Bash

ffmpeg -f concat -safe 0 -i inputs.txt \
-i speech.mp3 \
-vf "zoompan=z='min(zoom+0.0015,1.5)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,ass=subs.ass" \
-c:v libx264 -pix_fmt yuv420p -r 30 \
-c:a copy -shortest \
final_video.mp4

Summary of the n8n Workflow

    ElevenLabs Node: Get audio and the alignment JSON.

    Code Node: Run the Python script to create inputs.txt (using the logic above) and subs.ass.

    Wait/Write Node: Ensure the images and files are in a local directory n8n can access.

    Execute Command Node: Run the FFmpeg command.

One important catch:

FFmpeg's concat demuxer is very picky about image resolution. All 5 images must be the same size before running the concat, or it will error out.

Would you like me to add a quick pre-processing step to the Python script that resizes all your images to 1080x1920 automatically?

yes

To ensure your automation doesn't crash, we need to make sure all images are exactly 1080x1920 before FFmpeg tries to stitch them together. If one image is even a pixel different from the others, the concat demuxer will fail.

We can use the Pillow (PIL) library in Python to handle the resizing and cropping, then generate the inputs.txt file.
1. Python Pre-processing & Sync Script

This script does three things:

    Resizes/Crops images to TikTok's 9:16 aspect ratio.

    Maps markers to timestamps.

    Creates the inputs.txt file for FFmpeg.

Python

import json
from PIL import Image
import os

# --- INPUT DATA ---
elevenlabs_response = {
    "words": ["Welcome", "to", "this", "amazing", "journey", "through", "space", "and", "time"],
    "start_times": [0.0, 0.4, 0.7, 1.1, 1.8, 2.4, 2.9, 3.2, 3.8],
    "end_times": [0.3, 0.6, 1.0, 1.7, 2.3, 2.8, 3.1, 3.7, 4.5]
}

images = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"]
marker_words = ["amazing", "journey", "space", "time"]
output_size = (1080, 1920)

def prepare_assets(image_list, data, markers):
    # 1. Resize and Crop Images to 1080x1920
    processed_images = []
    for i, img_path in enumerate(image_list):
        with Image.open(img_path) as img:
            # Calculate aspect ratio and resize/crop to fill 1080x1920
            img_ratio = img.width / img.height
            target_ratio = output_size[0] / output_size[1]
            
            if img_ratio > target_ratio: # Image is too wide
                new_width = int(target_ratio * img.height)
                offset = (img.width - new_width) // 2
                img = img.crop((offset, 0, offset + new_width, img.height))
            else: # Image is too tall
                new_height = int(img.width / target_ratio)
                offset = (img.height - new_height) // 2
                img = img.crop((0, offset, img.width, offset + new_height))
            
            final_img = img.resize(output_size, Image.LANCZOS)
            out_name = f"proc_{i}.jpg"
            final_img.save(out_name)
            processed_images.append(out_name)

    # 2. Calculate Timestamps
    sync_points = [0.0]
    for word in markers:
        if word in data['words']:
            idx = data['words'].index(word)
            sync_points.append(data['start_times'][idx])
    sync_points.append(data['end_times'][-1])

    # 3. Write inputs.txt
    with open("inputs.txt", "w") as f:
        for i, img in enumerate(processed_images):
            # Calculate duration between sync points
            if i < len(sync_points) - 1:
                duration = sync_points[i+1] - sync_points[i]
                f.write(f"file '{img}'\n")
                f.write(f"duration {round(duration, 3)}\n")
        
        # Last image repeat (FFmpeg requirement)
        f.write(f"file '{processed_images[-1]}'\n")

prepare_assets(images, elevenlabs_response, marker_words)

2. The Updated FFmpeg Command

Since we already resized the images in Python, the FFmpeg command becomes much lighter and faster.
Bash

ffmpeg -f concat -safe 0 -i inputs.txt \
-i speech.mp3 \
-vf "ass=subs.ass" \
-c:v libx264 -pix_fmt yuv420p -r 30 \
-c:a copy -shortest \
final_video.mp4

Why this is the "Pro" way:

    Performance: Resizing images in Python is faster than doing complex filters in FFmpeg for every single frame.

    Reliability: By forcing the 1080x1920 crop in Python, you avoid the "Non-matching resolution" error that kills most FFmpeg automation scripts.

    Precision: Your image transitions will happen exactly on the millisecond ElevenLabs starts saying your marker word.