# Video Filtering by SyncNet Quality - Complete Guide

## Overview
The `filter_videos_by_sync_score.py` script processes multiple videos to assess their audio-visual synchronization quality using SyncNet, then filters them based on configurable quality thresholds.

## Quick Start

### Basic Usage
```bash
# Filter videos with default settings (confidence≥5.0, |offset|≤3)
python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results
```

### Using Quality Presets
```bash
# High quality filtering (training data grade)
python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --preset high

# Strict filtering (publication ready)
python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --preset strict
```

## Quality Presets

| Preset   | Min Confidence | Max Offset | Use Case |
|----------|-----------------|------------|----------|
| `strict` | 8.0            | 2 frames   | Publication-ready, highest quality |
| `high`   | 6.0            | 3 frames   | Training data, research quality |
| `medium` | 4.0            | 5 frames   | General purpose, balanced filtering |
| `relaxed`| 2.0            | 8 frames   | Keep most usable content |

## Custom Parameters

```bash
python filter_videos_by_sync_score.py \
  --input_dir /path/to/videos \
  --output_dir /path/to/results \
  --min_confidence 6.5 \
  --max_abs_offset 2 \
  --min_face_size 40 \
  --min_track 30 \
  --max_workers 4
```

### Parameter Descriptions

- `--min_confidence`: Minimum SyncNet confidence score (higher = better sync quality)
- `--max_abs_offset`: Maximum absolute frame offset allowed (lower = better sync)
- `--min_face_size`: Minimum face size in pixels for detection (adjust for video resolution)
- `--min_track`: Minimum number of frames a face must be tracked
- `--max_workers`: Number of parallel processing threads

## Output Structure

```
output_dir/
├── good_quality/              # Videos passing quality thresholds
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
├── poor_quality/              # Videos filtered out
│   ├── low_sync_video1.mp4
│   ├── low_sync_video2.mp4
│   └── ...
└── sync_filter_results.json   # Detailed analysis results
```

## Understanding Results

### sync_filter_results.json Contains:
- **Filter settings**: Thresholds used
- **Statistics**: Count of good/poor/failed videos
- **Individual results**: Per-video metrics including:
  - Confidence score
  - Frame offset
  - Processing time
  - Quality assessment

### Example Results Analysis:
```json
{
  "filter_settings": {
    "min_confidence": 6.0,
    "max_abs_offset": 3
  },
  "total_videos": 100,
  "good_quality": 75,
  "poor_quality": 20,
  "no_faces_detected": 3,
  "processing_failed": 2
}
```

## Troubleshooting

### Common Issues:

1. **"No faces detected"**
   - Reduce `--min_face_size` (try 30-40 for low resolution videos)
   - Check that videos actually contain visible faces

2. **High processing time**
   - Reduce `--max_workers` if system becomes unresponsive
   - Consider processing smaller batches

3. **Most videos filtered out**
   - Use `--preset relaxed` or lower thresholds
   - Check sample videos manually to understand quality distribution

### Analysis-Only Mode:
```bash
# Analyze quality without copying files to separate folders
python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --keep_all
```

## Best Practices

### 1. Start with Analysis
Run with `--keep_all` first to understand your data's quality distribution.

### 2. Choose Appropriate Presets
- **Research/Training**: Use `--preset high`
- **Production/Publication**: Use `--preset strict`
- **Content Curation**: Use `--preset medium`

### 3. Adjust for Video Characteristics
- **Low resolution videos**: Reduce `--min_face_size`
- **Short clips**: Reduce `--min_track`
- **Noisy environments**: Consider `--preset relaxed`

### 4. Monitor Processing
- Start with small batches to verify settings
- Monitor CPU/memory usage with multiple workers
- Check sample results before processing large datasets

## Example Workflows

### Workflow 1: Research Dataset Curation
```bash
# Step 1: Analyze all videos
python filter_videos_by_sync_score.py --input_dir raw_videos --output_dir analysis --keep_all --preset medium

# Step 2: Review results and adjust thresholds
# Check analysis/sync_filter_results.json

# Step 3: Apply final filtering
python filter_videos_by_sync_score.py --input_dir raw_videos --output_dir final_dataset --preset high
```

### Workflow 2: Quick Quality Check
```bash
# Fast assessment with relaxed settings for small faces
python filter_videos_by_sync_score.py \
  --input_dir videos \
  --output_dir filtered \
  --min_confidence 3.0 \
  --max_abs_offset 8 \
  --min_face_size 30 \
  --max_workers 8
```
