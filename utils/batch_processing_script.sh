#!/bin/bash
VIDEO_DIR="/Users/darklord/Research/Audio Visual/Code/bengali-speech-audio-visual-dataset/poc/outputs/aRHpoSebPPI/chunks/video"
OUTPUT_DIR="batch_analysis"

for video in "$VIDEO_DIR"/*.mp4; do
  video_name=$(basename "$video" .mp4)
  echo "Processing: $video_name"
  
  python process_long_video.py \
    --input_video "$video" \
    --output_dir "$OUTPUT_DIR/${video_name}_analysis" \
    --chunk_duration 30 \
    --overlap 5
  
  echo "Analyzing results for: $video_name"
  python analyze_results.py "$OUTPUT_DIR/${video_name}_analysis/processing_summary.json" --detailed
done