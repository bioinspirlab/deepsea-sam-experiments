#!/bin/bash

set -e

# Download PANGAEA dataset file to obsea directory, removing 34 lines of header metadata
URL="https://doi.pangaea.de/10.1594/PANGAEA.946149?format=textfile"
OUTPUT_DIR="${1:-.}/obsea"
FILENAME="${2:-PANGAEA.946149.csv}"
LIST_FILE="${1:-.}/obsea/image_list.txt"
IMAGE_URL_PREFIX="https://download.pangaea.de/dataset/946149/files/"
IMAGE_DIR="$OUTPUT_DIR/image_data"
MAX_RETRIES=360
RETRY_DELAY=10

mkdir -p "$OUTPUT_DIR"
mkdir -p "$IMAGE_DIR"

echo "Downloading metadata from $URL..."
curl -L "$URL" | tail -n +34 > "$OUTPUT_DIR/$FILENAME"

echo "Saved to $OUTPUT_DIR/$FILENAME"

# Download JPG files with LTO tape retry logic
if [ -f "$LIST_FILE" ]; then
    echo "Downloading images from $LIST_FILE..."
    while IFS= read -r filename; do
        # Skip empty lines
        [ -z "$filename" ] && continue
        
        image_url="${IMAGE_URL_PREFIX}${filename}"
        echo "Requesting $filename..."
        
        retry_count=0
        while [ $retry_count -lt $MAX_RETRIES ]; do
            http_code=$(curl -s -o "$IMAGE_DIR/$filename" -w "%{http_code}" -L "$image_url")
            
            if [ "$http_code" = "200" ]; then
                echo "✓ Downloaded $filename"
                break
            elif [ "$http_code" = "202" ]; then
                # 202 Accepted - tape request queued, wait for retrieval
                echo "  Tape retrieval in progress (attempt $((retry_count + 1))/$MAX_RETRIES)..."
                sleep $RETRY_DELAY
                retry_count=$((retry_count + 1))
            elif [ "$http_code" = "503" ]; then
                # 503 Service Unavailable - server overloaded, wait and retry
                echo "  Server unavailable (attempt $((retry_count + 1))/$MAX_RETRIES)..."
                sleep $RETRY_DELAY
                retry_count=$((retry_count + 1))
            else
                echo "✗ Error: HTTP $http_code for $filename"
                break
            fi
        done
        
        if [ $retry_count -ge $MAX_RETRIES ]; then
            echo "✗ Timeout waiting for $filename after $((MAX_RETRIES * RETRY_DELAY)) seconds"
        fi
    done < "$LIST_FILE"
    echo "Images saved to $IMAGE_DIR"
else
    echo "Warning: $LIST_FILE not found. Skipping image downloads."
fi