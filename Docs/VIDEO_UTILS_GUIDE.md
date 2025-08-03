# Video Utils - Single Video Processing Guide

The `video_utils.py` module provides essential utilities for video processing operations including video information extraction, chunking, and audio extraction. This guide focuses on processing single videos with various utilities.

## Overview

The video utilities module offers the following main functions:
- **Video Information**: Extract metadata from video files
- **Time-based Chunking**: Split videos into fixed-duration segments
- **Silence-based Chunking**: Split videos at silence boundaries
- **Audio Extraction**: Extract audio tracks from video files

## Installation Requirements

Ensure you have `ffmpeg` installed on your system:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Command Line Usage

The video utils script provides a command-line interface with multiple subcommands:

```bash
python utils/video_utils.py [command] [options]
```

### Available Commands

1. `info` - Get video information
2. `chunk-time` - Split video into fixed-duration chunks
3. `chunk-silence` - Split video based on silence detection
4. `extract-audio` - Extract audio from video

---

## 1. Video Information Extraction

Get detailed metadata about your video file including duration, codecs, resolution, and audio properties.

### Command Syntax
```bash
python utils/video_utils.py info --input /path/to/video.mp4
```

### Example
```bash
python utils/video_utils.py info --input data/chunk_003.mp4
```

### Sample Output
```
📹 Video Information for: data/chunk_003.mp4
Duration: 5.48 seconds
Video: h264 640x360 @ 25/1 fps
Audio: aac 44100 Hz 2 channels
```

### Use Cases
- **Quality Assessment**: Check video properties before processing
- **Batch Analysis**: Verify video specifications across datasets
- **Preprocessing**: Determine optimal parameters for further processing

---

## 2. Time-based Video Chunking

Split a video into fixed-duration segments with optional overlap between chunks.

### Command Syntax
```bash
python utils/video_utils.py chunk-time --input VIDEO_FILE --output_dir OUTPUT_DIR [options]
```

### Parameters
- `--input`: Input video file path
- `--output_dir`: Directory to save video chunks
- `--duration`: Chunk duration in seconds (default: 30)
- `--overlap`: Overlap between chunks in seconds (default: 0)

### Examples

#### Basic 30-second chunks
```bash
python utils/video_utils.py chunk-time \
  --input data/long_video.mp4 \
  --output_dir chunks/time_based/
```

#### Custom duration with overlap
```bash
python utils/video_utils.py chunk-time \
  --input data/presentation.mp4 \
  --output_dir chunks/presentation/ \
  --duration 60 \
  --overlap 5
```

#### Short chunks for analysis
```bash
python utils/video_utils.py chunk-time \
  --input data/interview.mp4 \
  --output_dir chunks/analysis/ \
  --duration 10 \
  --overlap 2
```

### Output Structure
```
output_dir/
├── chunk_000.mp4
├── chunk_001.mp4
├── chunk_002.mp4
└── ...
```

### Use Cases
- **Training Data Preparation**: Create uniform-length segments for ML training
- **Analysis Windows**: Generate consistent segments for frame-by-frame analysis
- **Memory Management**: Process large videos in smaller, manageable chunks

---

## 3. Silence-based Video Chunking

Automatically split videos at natural silence boundaries, ideal for speech and conversation videos.

### Command Syntax
```bash
python utils/video_utils.py chunk-silence --input VIDEO_FILE --output_dir OUTPUT_DIR [options]
```

### Parameters
- `--input`: Input video file path
- `--output_dir`: Directory to save video chunks
- `--threshold`: Silence threshold in dB (default: -30)
- `--min_silence`: Minimum silence duration to trigger split (default: 1.0s)
- `--min_chunk`: Minimum chunk duration to keep (default: 5.0s)

### Examples

#### Default silence detection
```bash
python utils/video_utils.py chunk-silence \
  --input data/podcast.mp4 \
  --output_dir chunks/podcast_segments/
```

#### Sensitive silence detection
```bash
python utils/video_utils.py chunk-silence \
  --input data/quiet_conversation.mp4 \
  --output_dir chunks/conversation/ \
  --threshold -40 \
  --min_silence 0.5
```

#### Less sensitive (for noisy environments)
```bash
python utils/video_utils.py chunk-silence \
  --input data/conference_call.mp4 \
  --output_dir chunks/conference/ \
  --threshold -20 \
  --min_silence 2.0 \
  --min_chunk 10
```

### Output Structure
```
output_dir/
├── silence_chunk_000_000000.0s.mp4
├── silence_chunk_001_024500.5s.mp4
├── silence_chunk_002_056200.2s.mp4
└── ...
```

### Understanding Silence Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `--threshold` | Audio level considered "silence" | -30dB (normal), -40dB (sensitive), -20dB (noisy) |
| `--min_silence` | How long silence must last to split | 1.0s (conversations), 0.5s (precise), 2.0s (robust) |
| `--min_chunk` | Minimum segment length to keep | 5.0s (analysis), 3.0s (short clips), 10.0s (substantial) |

### Use Cases
- **Podcast Processing**: Split episodes into individual topics/segments
- **Interview Analysis**: Separate questions and answers
- **Meeting Transcription**: Create segments for individual speakers
- **Content Editing**: Identify natural break points for editing

---

## 4. Audio Extraction

Extract audio tracks from video files with customizable format and quality settings.

### Command Syntax
```bash
python utils/video_utils.py extract-audio --input VIDEO_FILE [options]
```

### Parameters
- `--input`: Input video file path
- `--output`: Output audio file path (auto-generated if not specified)
- `--sample_rate`: Audio sample rate in Hz (default: 16000)
- `--channels`: Number of audio channels (default: 1 for mono)

### Examples

#### Basic audio extraction (16kHz mono for speech processing)
```bash
python utils/video_utils.py extract-audio --input data/interview.mp4
```

#### High-quality stereo extraction
```bash
python utils/video_utils.py extract-audio \
  --input data/music_video.mp4 \
  --output audio/music_track.wav \
  --sample_rate 44100 \
  --channels 2
```

#### Speech analysis format
```bash
python utils/video_utils.py extract-audio \
  --input data/presentation.mp4 \
  --output audio/speech.wav \
  --sample_rate 16000 \
  --channels 1
```

### Sample Rate Guidelines

| Use Case | Sample Rate | Channels | Reasoning |
|----------|-------------|----------|-----------|
| Speech Analysis | 16000 Hz | 1 (mono) | Sufficient for speech, smaller files |
| SyncNet Processing | 16000 Hz | 1 (mono) | Required by SyncNet model |
| Music Analysis | 44100 Hz | 2 (stereo) | CD quality, preserves stereo information |
| General Purpose | 22050 Hz | 1 (mono) | Good balance of quality and size |

### Use Cases
- **SyncNet Preprocessing**: Extract audio for sync analysis
- **Transcription**: Prepare audio for speech-to-text
- **Audio Analysis**: Isolate audio track for processing
- **Backup/Archival**: Save audio separately from video

---

## Programmatic Usage

You can also use the video utils functions directly in Python scripts:

### Import and Basic Usage
```python
from utils.video_utils import get_video_info, cut_video_by_time, extract_audio_from_video

# Get video information
info = get_video_info("data/video.mp4")
print(f"Duration: {info['duration']} seconds")

# Extract 30-second clip starting at 60 seconds
cut_video_by_time("data/video.mp4", "output/", start_time=60, duration=30, chunk_name="excerpt.mp4")

# Extract audio for SyncNet processing
extract_audio_from_video("data/video.mp4", "audio/extracted.wav", sample_rate=16000, channels=1)
```

### Batch Processing Example
```python
import os
from pathlib import Path
from utils.video_utils import get_video_info, cut_video_by_time

def process_video_collection(input_dir, output_dir, chunk_duration=30):
    """Process all videos in directory"""
    video_files = list(Path(input_dir).glob("*.mp4"))
    
    for video_file in video_files:
        print(f"Processing: {video_file.name}")
        
        # Get video info
        info = get_video_info(str(video_file))
        if not info:
            continue
            
        # Create chunks
        video_output_dir = os.path.join(output_dir, video_file.stem)
        total_duration = info['duration']
        
        num_chunks = int(total_duration // chunk_duration) + 1
        for i in range(num_chunks):
            start_time = i * chunk_duration
            if start_time >= total_duration:
                break
                
            actual_duration = min(chunk_duration, total_duration - start_time)
            chunk_name = f"chunk_{i:03d}.mp4"
            
            cut_video_by_time(
                str(video_file), 
                video_output_dir, 
                start_time, 
                actual_duration, 
                chunk_name
            )

# Usage
process_video_collection("raw_videos/", "processed_chunks/")
```

---

## Integration with SyncNet Pipeline

The video utils integrate seamlessly with the SyncNet processing pipeline:

### Complete Workflow Example
```bash
# Step 1: Get video information
python utils/video_utils.py info --input raw_video.mp4

# Step 2: Split video into manageable chunks (optional for long videos)
python utils/video_utils.py chunk-time \
  --input raw_video.mp4 \
  --output_dir video_chunks/ \
  --duration 60 \
  --overlap 5

# Step 3: Process each chunk with SyncNet (using adjusted face size)
for chunk in video_chunks/*.mp4; do
  chunk_name=$(basename "$chunk" .mp4)
  python run_pipeline.py \
    --videofile "$chunk" \
    --reference "$chunk_name" \
    --data_dir syncnet_output/ \
    --min_face_size 50
    
  python run_syncnet.py \
    --videofile "$chunk" \
    --reference "$chunk_name" \
    --data_dir syncnet_output/
done

# Step 4: Filter results by quality
python filter_videos_by_sync_score.py \
  --input_dir video_chunks/ \
  --output_dir filtered_results/ \
  --preset high
```

---

## Best Practices

### 1. **Choose Appropriate Chunk Sizes**
- **Short videos (< 2 min)**: Process as single file
- **Medium videos (2-10 min)**: 30-60 second chunks
- **Long videos (> 10 min)**: 60-120 second chunks with overlap

### 2. **Silence Detection Tips**
- **Clean recordings**: Use -30dB threshold
- **Noisy environments**: Use -20dB or higher
- **Whispered speech**: Use -40dB or lower
- **Test different values** on sample data first

### 3. **Audio Extraction Guidelines**
- **SyncNet processing**: Always use 16kHz mono
- **Transcription**: 16kHz mono sufficient
- **Music analysis**: Use original sample rate and channels
- **Storage optimization**: Use lowest acceptable quality

### 4. **File Organization**
```
project/
├── raw_videos/           # Original video files
├── chunks/              # Video segments
│   ├── time_based/      # Fixed-duration chunks
│   └── silence_based/   # Natural break chunks
├── audio/               # Extracted audio files
├── syncnet_data/        # SyncNet processing results
└── filtered_results/    # Quality-filtered videos
```

---

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   ```
   Error: ffmpeg command not found
   Solution: Install ffmpeg or add to PATH
   ```

2. **Permission errors**
   ```
   Error: Permission denied writing to output directory
   Solution: Check directory permissions or use different output path
   ```

3. **No audio track found**
   ```
   Error: Could not extract audio
   Solution: Verify video has audio track using 'info' command
   ```

4. **Very short chunks produced**
   ```
   Issue: Silence detection creates tiny segments
   Solution: Increase --min_chunk parameter
   ```

### Performance Tips

- **Large files**: Use time-based chunking first, then process chunks
- **Slow processing**: Reduce video resolution before chunking
- **Memory issues**: Process smaller chunks or reduce overlap
- **Storage concerns**: Use appropriate audio sample rates

This comprehensive guide should help you effectively use the video utilities for single video processing in your SyncNet workflow!
