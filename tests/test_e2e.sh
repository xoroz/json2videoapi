#!/bin/bash

# Configuration
API_URL="http://localhost:8080/generate"
DATA_DIR="tests/data"
OUTPUT_DIR="tests/output"

mkdir -p "$OUTPUT_DIR"

# Usage function
usage() {
    echo "Usage: $0 [test_name]"
    echo "Tests found in $DATA_DIR/:"
    ls "$DATA_DIR" | sed 's/\.json$//'
    exit 1
}

# Determine which test to run
TEST_CASE=${1:-default}
JSON_FILE="$DATA_DIR/$TEST_CASE.json"

if [ ! -f "$JSON_FILE" ]; then
    echo "❌ Error: Test case '$TEST_CASE' not found in $DATA_DIR"
    usage
fi

# Check if server is up
echo "🔍 Checking API availability at $API_URL..."
if ! curl -s --head --request GET "${API_URL%/generate}/health" | grep "200 OK" > /dev/null; then
    echo "❌ Error: API server is not reachable at $API_URL"
    echo "Please run ./start.sh first."
    exit 1
fi
echo "✅ API is up."

OUTPUT_FILE="$OUTPUT_DIR/${TEST_CASE}_output.mp4"
rm -f "$OUTPUT_FILE"

echo "🚀 Running test: $TEST_CASE"
echo "📂 JSON: $JSON_FILE"
echo "📤 Output: $OUTPUT_FILE"

# Send request
# Note: we use -s for silent and -w to get http code
RESPONSE_CODE=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d @"$JSON_FILE")

if [ "$RESPONSE_CODE" -ne 200 ]; then
    echo "❌ Error: API request failed with HTTP $RESPONSE_CODE"
    if [ -f "$OUTPUT_FILE" ]; then
        echo "Response body:"
        cat "$OUTPUT_FILE"
        rm "$OUTPUT_FILE"
    fi
    exit 1
fi

if [ ! -s "$OUTPUT_FILE" ]; then
    echo "❌ Error: Output file is empty."
    exit 1
fi

echo "✅ Video generated. Validating with ffprobe..."

# FFmpeg validation
FFPROBE_OUT=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_FILE" 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$FFPROBE_OUT" ]; then
    echo "🎞️  Video duration: $FFPROBE_OUT seconds"
    echo "✅ Success! Video is valid."
    ls -lh "$OUTPUT_FILE"
else
    echo "❌ Error: ffprobe failed to validate the video."
    exit 1
fi
