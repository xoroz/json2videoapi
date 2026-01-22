# JSON2Video API

A FastAPI-based backend that leverages `zvid` (Node.js) to generate videos from JSON specifications.

## Features

- **FastAPI Backend**: High-performance Python API.
- **zvid Integration**: Uses the powerful `zvid` library for video rendering.
- **Caddy Proxy**: Reverse proxy for production readiness.
- **Rich Visuals**: Supports Text, Images, Videos, GIFs, and SVGs.
- **Logging**: Comprehensive logging in `logs/` directory.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/)
- [FFmpeg](https://ffmpeg.org/)

## Setup

1. **Install Python dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies**:
   ```bash
   cd zvid
   npm install
   ```

3. **Binary Dependencies**:
   The project uses a local `caddy` binary for reverse proxying.

## Running the Project

To start both the API and the Caddy proxy:
```bash
./start.sh
```

To stop all services:
```bash
./stop.sh
```

## Testing

Run the end-to-end test script:
```bash
./tests/test_e2e.sh
```

## API Usage

The API provides multiple ways to explore and understand the endpoints:

- **`GET /help`** - Comprehensive JSON documentation with examples and field descriptions
- **`GET /docs`** - Interactive Swagger UI with full schema documentation and "Try it out" functionality
- **`GET /`** - Root URL redirects to `/help`

For quick reference and copy-paste examples, use `/help`. For interactive testing and detailed schema exploration, use `/docs`.

### POST `/generate`

Generates a video based on the provided JSON body.

Example payload:
```json
{
  "name": "test-video",
  "duration": 5,
  "resolution": "hd",
  "visuals": [
    {
      "type": "TEXT",
      "text": "Hello World",
      "position": "center-center",
      "style": {
        "fontSize": "80px",
        "color": "#ff0000"
      }
    }
  ]
}
```

### Other Endpoints

- `GET /help` - API documentation and usage examples
- `GET /status/{job_id}` - Check video generation status
- `GET /download/{job_id}` - Download completed video
- `GET /health` - Service health check

For full API documentation, start the server and visit `http://localhost:8000/help` or use `curl http://localhost:8000/help`.

## Credits

This project leverages the excellent [zvid](https://github.com/Zvid-io/zvid) package for video generation. Special thanks to the original authors of `zvid` for their work in providing a fully-featured Node.js package for generating videos from JSON configurations using FFmpeg.

## License

ISC
