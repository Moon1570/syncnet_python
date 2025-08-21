# Directory Preparation Utility

This utility organizes SyncNet processing results into a structured format for easy access and analysis.

## Overview

The `directory_prepare.py` script takes a directory containing SyncNet results (such as `results/video1/good_quality`) and reorganizes the content into 4 well-structured directories:

1. **`video_normal/`** - Original chunk videos (all chunks)
2. **`video_bbox/`** - Bounding box visualization videos (converted to MP4)
3. **`video_cropped/`** - Cropped face videos (converted to MP4, renamed to chunk IDs)
4. **`audio/`** - Audio extracted from normal chunk videos

## Features

- **Parallel Processing**: Uses ThreadPoolExecutor for efficient batch conversion
- **Format Conversion**: Automatically converts AVI files to MP4 for better compatibility
- **Audio Extraction**: Extracts mono 16kHz audio optimized for speech processing
- **Progress Tracking**: Real-time progress updates and comprehensive summary
- **Error Handling**: Graceful error handling with detailed logging
- **Validation**: Input structure validation and dependency checks

## Requirements

- **Python 3.6+** with required packages (see main `requirements.txt`)
- **FFmpeg** - For video conversion and audio extraction
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/)

## Usage

### Basic Usage

```bash
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized_output
```

### Advanced Usage

```bash
# Use more workers for faster processing
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized_output \
    --max_workers 8
```

### Command-Line Arguments

- `--input_dir` (required): Input directory containing SyncNet results
- `--output_dir` (required): Output directory where organized folders will be created
- `--max_workers` (optional): Number of parallel workers (default: 4)

## Input Structure

The script expects the following input structure:

```
input_dir/
├── chunk_000.mp4                    # Original chunk videos
├── chunk_001.mp4
├── ...
└── syncnet_outputs/
    ├── chunk_000/
    │   ├── chunk_000_with_bboxes.avi    # Bounding box visualization
    │   ├── cropped_faces/
    │   │   └── 00000.avi                # Cropped face video
    │   └── analysis/
    └── chunk_001/
        └── ...
```

## Output Structure

The script creates the following organized structure:

```
output_dir/
├── video_normal/
│   ├── chunk_000.mp4                # Original videos (copied)
│   ├── chunk_001.mp4
│   └── ...
├── video_bbox/
│   ├── chunk_000_with_bboxes.mp4    # Bounding box videos (AVI→MP4)
│   ├── chunk_001_with_bboxes.mp4
│   └── ...
├── video_cropped/
│   ├── chunk_000.mp4                # Cropped faces (AVI→MP4, renamed)
│   ├── chunk_001.mp4
│   └── ...
└── audio/
    ├── chunk_000.wav                # Extracted audio (16kHz mono)
    ├── chunk_001.wav
    └── ...
```

## Processing Details

### Video Conversion (AVI → MP4)
- **Video Codec**: H.264 (libx264)
- **Audio Codec**: AAC
- **Quality**: CRF 23 (high quality)
- **Optimization**: Fast start enabled for web compatibility

### Audio Extraction
- **Format**: WAV (PCM 16-bit)
- **Sample Rate**: 16kHz (optimized for speech)
- **Channels**: Mono
- **Use Case**: Speech recognition, audio analysis

### Parallel Processing
- **Default Workers**: 4 (adjust based on your system)
- **Processing Order**: Chunks processed in sorted order
- **Progress Tracking**: Real-time status updates
- **Error Resilience**: Individual chunk failures don't stop the process

## Examples

### Process Good Quality Results

```bash
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized/video1_good
```

### Process Poor Quality Results for Analysis

```bash
python utils/directory_prepare.py \
    --input_dir results/video1/poor_quality \
    --output_dir organized/video1_poor
```

### High-Performance Processing

```bash
# Use 8 workers for faster processing (adjust based on CPU cores)
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized/video1_good \
    --max_workers 8
```

## Use Cases

### 1. **Active Speaker Detection**
- Use `video_bbox/` for annotation with pre-drawn bounding boxes
- Use `video_cropped/` for face-only analysis
- Use `audio/` for audio-visual synchronization analysis

### 2. **Training Data Preparation**
- Organized structure makes it easy to create training datasets
- Consistent naming convention for batch processing
- MP4 format ensures compatibility with most ML frameworks

### 3. **Quality Analysis**
- Compare good vs poor quality results side by side
- Analyze correlation between video quality and audio clarity
- Study face detection accuracy across different conditions

### 4. **Annotation Workflows**
- `video_bbox/`: Start with pre-detected faces for faster annotation
- `video_cropped/`: Focus annotation on face regions only
- `audio/`: Synchronized audio for multi-modal annotation

## Performance

### Typical Processing Times
- **47 chunks** (as tested): ~19 seconds with 2 workers
- **Scaling**: Processing time scales roughly with `total_chunks / workers`
- **Bottleneck**: Usually FFmpeg conversion, not I/O

### Resource Usage
- **CPU**: Scales with worker count (FFmpeg is CPU-intensive)
- **Memory**: Low memory usage (~100MB typical)
- **Disk**: Temporary space needed during conversion

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```
   ❌ FFmpeg not found. Please install FFmpeg to use this script.
   ```
   **Solution**: Install FFmpeg using your system package manager

2. **Input directory not found**
   ```
   ❌ Input directory not found: /path/to/input
   ```
   **Solution**: Check the path and ensure it exists

3. **No syncnet_outputs directory**
   ```
   ValueError: syncnet_outputs directory not found in: /path/to/input
   ```
   **Solution**: Ensure you're pointing to a directory that contains SyncNet results

4. **Conversion failures**
   ```
   ❌ FFmpeg conversion failed for input.avi
   ```
   **Solution**: Check that input video files are not corrupted

### Performance Optimization

- **Worker Count**: Set `--max_workers` to your CPU core count for optimal performance
- **Disk Speed**: Use SSD storage for better I/O performance
- **Memory**: Ensure sufficient free disk space (roughly 2x input size)

## Integration

This utility integrates well with:

- **SyncNet Pipeline**: Use after running `filter_videos_by_sync_score.py`
- **Annotation Tools**: Organized structure works with most video annotation software
- **ML Frameworks**: MP4 and WAV formats are widely supported
- **Batch Processing**: Easy to incorporate into larger processing pipelines

## Output Validation

The script provides comprehensive logging and summary statistics:

```
📊 DIRECTORY PREPARATION SUMMARY
================================================================================
Total chunks processed: 47
✅ Normal videos: 47/47
📦 Bbox videos: 47/47  
👤 Cropped videos: 47/47
🔊 Audio files: 47/47

📁 Output directories:
   video_normal: test_organized/video_normal (47 files)
   video_bbox: test_organized/video_bbox (47 files)
   video_cropped: test_organized/video_cropped (47 files)
   audio: test_organized/audio (47 files)
```
