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

## API Specification

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

## License

ISC
