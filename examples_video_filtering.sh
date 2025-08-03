#!/bin/bash
# Example usage script for video filtering by SyncNet scores

echo "🎬 SyncNet Video Quality Filter - Usage Examples"
echo "================================================"

# Basic usage - filter videos with default thresholds
echo "📝 Basic filtering (confidence≥5.0, |offset|≤3):"
echo "python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/filtered_results"
echo ""

# Using quality presets
echo "📝 Using quality presets:"
echo "# Strict filtering (high quality only)"
echo "python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --preset strict"
echo ""
echo "# Medium quality filtering"
echo "python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --preset medium"
echo ""

# Custom thresholds
echo "📝 Custom quality thresholds:"
echo "python filter_videos_by_sync_score.py \\"
echo "  --input_dir /path/to/videos \\"
echo "  --output_dir /path/to/results \\"
echo "  --min_confidence 4.5 \\"
echo "  --max_abs_offset 5 \\"
echo "  --min_face_size 40 \\"
echo "  --max_workers 4"
echo ""

# Analysis only (don't copy files)
echo "📝 Analysis only (don't copy files to separate folders):"
echo "python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --keep_all"
echo ""

echo "📊 Quality Presets Available:"
echo "  --preset strict   : confidence≥8.0, |offset|≤2 (publication ready)"
echo "  --preset high     : confidence≥6.0, |offset|≤3 (training data)"
echo "  --preset medium   : confidence≥4.0, |offset|≤5 (balanced)"
echo "  --preset relaxed  : confidence≥2.0, |offset|≤8 (keep most usable)"
echo ""

echo "📁 Output Structure:"
echo "  output_dir/"
echo "  ├── good_quality/     # Videos that pass quality thresholds"
echo "  ├── poor_quality/     # Videos that fail quality thresholds"
echo "  └── sync_filter_results.json  # Detailed analysis results"
echo ""

echo "🔧 For videos with small faces, reduce --min_face_size (default: 50)"
echo "⚡ Increase --max_workers for faster processing (but higher CPU usage)"
