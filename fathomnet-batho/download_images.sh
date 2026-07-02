#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASET_JSON="${1:-${SCRIPT_DIR}/batho-inner-dataset.json}"
OUT_DIR="${2:-${SCRIPT_DIR}/image_data}"

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required to parse COCO JSON. Install jq and retry." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

jq -r '.images[] | select(.coco_url != null and .file_name != null) | [.coco_url, .file_name] | @tsv' "$DATASET_JSON" | while IFS=$'\t' read -r url filename; do
  if [ -z "$url" ] || [ -z "$filename" ]; then
    continue
  fi

  dest="$OUT_DIR/$filename"

  if [ -f "$dest" ]; then
    echo "Skipping existing file: $dest"
    continue
  fi

  echo "Downloading: $url -> $dest"
  curl -L -f -o "$dest" "$url"
  echo "Saved: $dest"
done
