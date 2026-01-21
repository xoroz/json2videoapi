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
echo "📤 Submitting job..."
RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d @"$JSON_FILE")

JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')

if [ "$JOB_ID" == "null" ] || [ -z "$JOB_ID" ]; then
    echo "❌ Error: Failed to get job_id from API. Response:"
    echo "$RESPONSE"
    exit 1
fi

echo "🆔 Job ID: $JOB_ID"

# Polling
echo "⏳ Polling for completion..."
while true; do
    STATUS_RESP=$(curl -s "${API_URL%/generate}/status/$JOB_ID")
    STATUS=$(echo "$STATUS_RESP" | jq -r '.status')
    PROGRESS=$(echo "$STATUS_RESP" | jq -r '.progress')
    
    echo "   Status: $STATUS ($PROGRESS%)"
    
    if [ "$STATUS" == "completed" ]; then
        echo "✅ Job completed!"
        break
    elif [ "$STATUS" == "failed" ]; then
        ERROR=$(echo "$STATUS_RESP" | jq -r '.error // .message')
        echo "❌ Job failed: $ERROR"
        exit 1
    fi
    sleep 2
done

# Download
echo "📥 Downloading video to $OUTPUT_FILE..."
RESPONSE_CODE=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" "${API_URL%/generate}/download/$JOB_ID")

if [ "$RESPONSE_CODE" -ne 200 ]; then
    echo "❌ Error: Download failed with HTTP $RESPONSE_CODE"
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
