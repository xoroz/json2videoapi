# API User Guide

This guide explains how to use the JSON to Video API.

## Base URL
The API is served via Caddy at: `http://localhost:8080`

## Documentation
- **Interactive Swagger UI**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **ReDoc**: [http://localhost:8080/redoc](http://localhost:8080/redoc)

## Core Concepts

### VideoProject
The main wrapper for your video.
- `name`: String, used for output filename.
- `resolution`: One of `sd`, `hd` (default), `full-hd`, `tiktok`, `squared`, etc.
- `duration`: Float, total length in seconds.
- `backgroundColor`: Hex code (e.g., `#000000`).
- `visuals`: List of `Visual` items.
- `audios`: List of `Audio` items.

### Visual Types

#### TEXT
Render text or HTML.
```json
{
  "type": "TEXT",
  "text": "Hello World",
  "style": { "fontSize": "80px", "color": "#ffffff" },
  "position": "center",
  "enterBegin": 0, "exitEnd": 5
}
```

#### IMAGE / GIF / VIDEO
Load media from a URL.
```json
{
  "type": "IMAGE",
  "src": "https://example.com/image.png",
  "resize": "cover",
  "enterBegin": 1, "exitEnd": 4
}
```

#### SVG
Render raw SVG content.
```json
{
  "type": "SVG",
  "svg": "<svg>...</svg>",
  "position": "center",
  "duration": 5
}
```

### Static File Access
Once a video is generated, it is stored in the `output/` folder and can be accessed directly at:
`http://localhost:8080/output/<filename>.mp4`

## Example Request (curl)
```bash
curl -X POST "http://localhost:8080/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "quick-start",
       "duration": 3,
       "visuals": [{"type": "TEXT", "text": "GO!", "position": "center"}]
     }' \
     --output my_video.mp4
```
