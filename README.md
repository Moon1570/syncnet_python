# SyncNet

This repository contains the demo for the audio-to-video synchronisation network (SyncNet). This network can be used for audio-visual synchronisation tasks including: 
1. Removing temporal lags between the audio and visual streams in a video;
2. Determining who is speaking amongst multiple faces in a video. 

Please cite the paper below if you make use of the software. 

## Dependencies
```
pip install -r requirements.txt
```

In addition, `ffmpeg` is required.


## Demo

SyncNet demo:
```
python demo_syncnet.py --videofile data/example.avi --tmp_dir /path/to/temp/directory
```

Check that this script returns:
```
AV offset:      3 
Min dist:       5.353
Confidence:     10.021
```

Full pipeline:
```
sh download_model.sh
python run_pipeline.py --videofile /path/to/video.mp4 --reference name_of_video --data_dir /path/to/output
python run_syncnet.py --videofile /path/to/video.mp4 --reference name_of_video --data_dir /path/to/output
python run_visualise.py --videofile /path/to/video.mp4 --reference name_of_video --data_dir /path/to/output
```

## Parameters

### run_pipeline.py parameters:
- `--min_face_size`: Minimum face size in pixels (default: 100). Reduce this value for videos with smaller faces.
- `--facedet_scale`: Scale factor for face detection (default: 0.25)
- `--crop_scale`: Scale bounding box (default: 0.40)
- `--min_track`: Minimum facetrack duration (default: 100 frames)

Example with smaller faces:
```
python run_pipeline.py --videofile /path/to/video.mp4 --reference name_of_video --data_dir /path/to/output --min_face_size 50
```

## Video Processing Utilities

For video preprocessing, chunking, and analysis, use the video utilities:

```bash
# Get video information
python utils/video_utils.py info --input data/video.mp4

# Split video into 30-second chunks
python utils/video_utils.py chunk-time --input data/video.mp4 --output_dir chunks/ --duration 30

# Split video at silence boundaries (ideal for speech)
python utils/video_utils.py chunk-silence --input data/conversation.mp4 --output_dir chunks/

# Extract audio for processing
python utils/video_utils.py extract-audio --input data/video.mp4 --output audio/extracted.wav
```

**📖 See [VIDEO_UTILS_GUIDE.md](VIDEO_UTILS_GUIDE.md) for comprehensive usage examples and best practices.**

## Troubleshooting

### Issue: Empty pycrop directory / No bounding boxes in output video

**Symptoms:**
- `$DATA_DIR/pycrop/$REFERENCE/` directory is empty
- No bounding boxes appear in the output video
- Face detection appears to work (faces are detected in console output)

**Cause:** The detected faces are smaller than the minimum face size threshold.

**Solution:** 
1. Check your detected face sizes by examining the face detection output
2. Reduce the `--min_face_size` parameter in `run_pipeline.py`
3. For videos with small faces (< 100 pixels), try `--min_face_size 50` or lower

**Example fix:**
```bash
# Instead of default parameters
python run_pipeline.py --videofile data/chunk_003.mp4 --reference chunk_003 --data_dir data/test/

# Use lower minimum face size
python run_pipeline.py --videofile data/chunk_003.mp4 --reference chunk_003 --data_dir data/test/ --min_face_size 50
```

## Batch Processing and Quality Filtering

### Filter Videos by SyncNet Quality Scores

Process multiple videos and automatically filter them based on audio-visual synchronization quality:

```bash
# Basic filtering with default thresholds
python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/filtered_results

# Using quality presets
python filter_videos_by_sync_score.py --input_dir /path/to/videos --output_dir /path/to/results --preset high

# Custom quality thresholds
python filter_videos_by_sync_score.py \
  --input_dir /path/to/videos \
  --output_dir /path/to/results \
  --min_confidence 6.0 \
  --max_abs_offset 3 \
  --min_face_size 40 \
  --max_workers 4
```

**Quality Presets:**
- `--preset strict`: confidence≥8.0, |offset|≤2 (publication ready)
- `--preset high`: confidence≥6.0, |offset|≤3 (training data quality)
- `--preset medium`: confidence≥4.0, |offset|≤5 (balanced filtering)
- `--preset relaxed`: confidence≥2.0, |offset|≤8 (keep most usable)

**Output Structure:**
```
output_dir/
├── good_quality/              # Videos that pass quality thresholds
│   ├── video1.mp4             # Original videos
│   ├── video2.mp4
│   └── syncnet_outputs/       # SyncNet processing results (NEW!)
│       ├── video1/
│       │   ├── cropped_faces/     # Cropped face track videos
│       │   ├── video1_with_bboxes.avi  # Video with bounding boxes
│       │   └── analysis/          # Analysis results
│       │       ├── offsets.txt        # Frame offset values
│       │       └── tracks.pkl         # Face tracking data
│       └── video2/
│           └── ...
├── poor_quality/              # Videos filtered out for low quality
│   ├── rejected_video.mp4     # Original videos
│   └── syncnet_outputs/       # SyncNet outputs for poor quality videos
│       └── rejected_video/
│           └── ...
├── syncnet_outputs/           # All SyncNet processing results
│   ├── video1/               # Individual video results
│   └── video2/
└── sync_filter_results.json   # Detailed analysis results
```

**🎯 Enhanced Output Preservation (NEW!):**

The filtering tool now preserves valuable SyncNet processing outputs for further analysis:

- **Cropped Face Videos**: Individual face tracks as separate video files (`cropped_faces/*.avi`)
- **Bounding Box Visualizations**: Original video with face detection overlays (`*_with_bboxes.avi`)
- **Analysis Data**: Frame offsets, confidence scores, and tracking information
- **Quality-Organized**: All outputs copied to `good_quality/` and `poor_quality/` folders

This is especially useful for:
- **Active Speaker Detection**: Use cropped faces and bounding boxes for annotation
- **Training Data Preparation**: Access to pre-processed face tracks and metadata
- **Quality Analysis**: Compare outputs between good and poor quality videos

**Testing the Enhanced Filter:**

Test the enhanced filtering functionality:

```bash
python test_enhanced_filter.py
```

This will verify that:
- All required dependencies are present
- Output preservation works correctly
- Quality directories are created with proper structure
- SyncNet outputs are preserved in organized folders

### Directory Preparation Utility

Organize SyncNet results into structured directories for easy access:

```bash
# Organize filtered results into 4 directories
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized_output
```

This creates:
- **`video_normal/`**: Original chunk videos 
- **`video_bbox/`**: Bounding box visualizations (converted to MP4)
- **`video_cropped/`**: Cropped face videos (converted to MP4)
- **`audio/`**: Extracted audio files (16kHz mono WAV)

See [`utils/DIRECTORY_PREPARE_README.md`](utils/DIRECTORY_PREPARE_README.md) for detailed usage guide.

**Parameters:**
- `--min_confidence`: Minimum SyncNet confidence score to keep video
- `--max_abs_offset`: Maximum absolute frame offset to keep video
- `--keep_all`: Analyze quality but don't copy files to separate folders

Outputs:
```
$DATA_DIR/pycrop/$REFERENCE/*.avi - cropped face tracks
$DATA_DIR/pywork/$REFERENCE/offsets.txt - audio-video offset values
$DATA_DIR/pyavi/$REFERENCE/video_out.avi - output video (as shown below)
```
<p align="center">
  <img src="img/ex1.jpg" width="45%"/>
  <img src="img/ex2.jpg" width="45%"/>
</p>

##Todo
- add duplicate remover

## Publications
 
```
@InProceedings{Chung16a,
  author       = "Chung, J.~S. and Zisserman, A.",
  title        = "Out of time: automated lip sync in the wild",
  booktitle    = "Workshop on Multi-view Lip-reading, ACCV",
  year         = "2016",
}
```
