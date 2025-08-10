# Enhanced SyncNet Filter - Output Preservation Update

## Summary of Changes

This update enhances the `filter_videos_by_sync_score.py` script to preserve valuable SyncNet processing outputs instead of discarding them after analysis. This addresses the user's need to keep cropped videos and bounding boxes for active speaker annotation.

## Key Enhancements

### 1. Output Preservation System

**New Method: `_preserve_syncnet_outputs(result, video_name, temp_video_dir, output_dir)`**
- Preserves cropped face videos from `pycrop/` directory
- Saves bounding box visualization videos
- Keeps analysis results (offsets.txt, tracks.pkl)
- Organizes outputs in structured directories

**New Method: `_copy_syncnet_outputs_to_quality_dir(result, quality_dir, output_dir)`**
- Copies SyncNet outputs to quality-specific directories
- Enables easy access to processing results by quality level
- Maintains organized structure for further analysis

### 2. Enhanced Processing Pipeline

**Added Visualization Step:**
- Automatically runs `run_visualise.py` after SyncNet analysis
- Generates videos with bounding box overlays
- Creates visual annotations for active speaker detection

**Improved Output Structure:**
```
output_dir/
├── good_quality/
│   ├── video1.mp4                    # Original videos
│   └── syncnet_outputs/              # SyncNet results
│       └── video1/
│           ├── cropped_faces/        # Individual face tracks
│           ├── video1_with_bboxes.avi # Bounding box visualization
│           └── analysis/             # Offsets, tracking data
├── poor_quality/
│   └── syncnet_outputs/              # Results for filtered videos
├── syncnet_outputs/                  # Master results directory
└── sync_filter_results.json         # Analysis summary
```

### 3. New Files Created

**`test_enhanced_filter.py`**
- Comprehensive test suite for the enhanced functionality
- Validates output structure and preservation
- Provides usage examples and verification

**Updated Documentation:**
- Enhanced README.md with new output structure
- Added testing instructions
- Documented use cases for preserved outputs

## Technical Implementation

### Code Changes in `filter_videos_by_sync_score.py`:

1. **Added visualization step** in `process_single_video()`:
   ```python
   # Generate visualization with bounding boxes
   viz_cmd = [
       sys.executable, 'run_visualise.py',
       '--videofile', video_path,
       '--reference', video_name,
       '--data_dir', temp_video_dir
   ]
   subprocess.run(viz_cmd, check=True)
   ```

2. **Added output preservation** after successful processing:
   ```python
   # Preserve SyncNet outputs for further use
   self._preserve_syncnet_outputs(result, video_name, temp_video_dir, output_dir)
   ```

3. **Enhanced quality directory copying**:
   ```python
   # Also copy SyncNet outputs to the quality directory
   self._copy_syncnet_outputs_to_quality_dir(result, dst_dir, output_dir)
   ```

### Benefits for Users:

1. **Active Speaker Annotation**: Direct access to cropped faces and bounding boxes
2. **Training Data Preparation**: Organized face tracks with quality metadata
3. **Analysis Workflow**: All processing artifacts preserved for further research
4. **Quality Comparison**: Easy comparison between good and poor quality results

## Usage

### Basic Usage (with preservation):
```bash
python filter_videos_by_sync_score.py \
    --input_dir /path/to/videos \
    --output_dir /path/to/results \
    --preset medium
```

### Testing:
```bash
python test_enhanced_filter.py
```

## Compatibility

- **Backward Compatible**: All existing functionality preserved
- **No Breaking Changes**: Original API and behavior maintained
- **Optional Features**: Preservation doesn't interfere with filtering logic
- **Error Handling**: Graceful degradation if preservation fails

## Future Enhancements

This update provides a foundation for:
- Custom output format selection
- Metadata-driven organization
- Integration with annotation tools
- Batch processing pipelines

The enhanced filter now serves as both a quality filtering tool and a comprehensive SyncNet output manager, making it more valuable for research and production workflows.
