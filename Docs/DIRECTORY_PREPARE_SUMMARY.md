# Directory Preparation Script - Implementation Summary

## ✅ **Complete Implementation**

I have successfully created the `utils/directory_prepare.py` script that takes a SyncNet results directory as input and organizes it into 4 structured directories as requested.

## 🎯 **Script Features**

### **Input Structure Expected:**
```
results/video1/good_quality/
├── chunk_000.mp4, chunk_001.mp4, ...           # Original chunk videos
└── syncnet_outputs/
    ├── chunk_000/
    │   ├── chunk_000_with_bboxes.avi           # Bounding box video
    │   ├── cropped_faces/
    │   │   └── 00000.avi                       # Cropped face video
    │   └── analysis/                           # Analysis files
    └── chunk_001/, chunk_002/, ...
```

### **Output Structure Created:**
```
organized_output/
├── video_normal/                               # 1. Original chunk videos (copied)
│   ├── chunk_000.mp4, chunk_001.mp4, ...
├── video_bbox/                                 # 2. Bounding box videos (AVI→MP4)
│   ├── chunk_000_with_bboxes.mp4, ...
├── video_cropped/                              # 3. Cropped faces (AVI→MP4, renamed)
│   ├── chunk_000.mp4, chunk_001.mp4, ...
└── audio/                                      # 4. Extracted audio (16kHz mono WAV)
    ├── chunk_000.wav, chunk_001.wav, ...
```

## 🚀 **Usage**

### **Basic Command:**
```bash
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized_output
```

### **Advanced Options:**
```bash
python utils/directory_prepare.py \
    --input_dir results/video1/good_quality \
    --output_dir organized_output \
    --max_workers 8                             # Use 8 parallel workers
```

## ⚡ **Performance Results**

**Test Results with your data (47 chunks):**
- ✅ **Normal videos**: 47/47 (copied)
- 📦 **Bbox videos**: 47/47 (AVI→MP4 converted)  
- 👤 **Cropped videos**: 47/47 (AVI→MP4 converted, renamed)
- 🔊 **Audio files**: 47/47 (extracted to 16kHz mono WAV)
- ⏱️ **Processing time**: ~19 seconds with 2 workers

## 🔧 **Technical Implementation**

### **Video Conversion (AVI → MP4):**
- **Video Codec**: H.264 (libx264)
- **Audio Codec**: AAC
- **Quality**: CRF 23 (high quality)
- **Optimization**: Fast start enabled for web compatibility

### **Audio Extraction:**
- **Format**: WAV (PCM 16-bit)
- **Sample Rate**: 16kHz (optimized for speech)
- **Channels**: Mono
- **Source**: Original chunk videos

### **Processing Features:**
- **Parallel Processing**: ThreadPoolExecutor for efficient batch conversion
- **Progress Tracking**: Real-time status updates and comprehensive summary
- **Error Handling**: Graceful error handling with detailed logging
- **Input Validation**: Structure validation and dependency checks

## 📚 **Documentation Created**

1. **`utils/directory_prepare.py`** - Main script with comprehensive features
2. **`utils/DIRECTORY_PREPARE_README.md`** - Detailed usage guide
3. **Updated main `README.md`** - Added directory preparation section

## 🎯 **Use Cases Enabled**

### **1. Active Speaker Detection**
- `video_bbox/`: Use pre-drawn bounding boxes for annotation
- `video_cropped/`: Analyze face-only regions
- `audio/`: Audio-visual synchronization analysis

### **2. Training Data Preparation**
- Organized structure for ML dataset creation
- Consistent naming convention for batch processing
- MP4 format ensures compatibility with ML frameworks

### **3. Annotation Workflows**
- `video_bbox/`: Start with detected faces for faster annotation
- `video_cropped/`: Focus annotation on face regions only
- `audio/`: Synchronized audio for multi-modal annotation

### **4. Quality Analysis**
- Compare good vs poor quality results side by side
- Analyze correlation between video quality and audio clarity
- Study face detection accuracy across conditions

## 🔍 **Quality Assurance**

- ✅ **Syntax Check**: Script compiles without errors
- ✅ **Live Testing**: Successfully processed 47 real chunks
- ✅ **Output Validation**: All 4 directories created with correct content
- ✅ **Performance**: Efficient parallel processing
- ✅ **Error Handling**: Graceful failure handling
- ✅ **Documentation**: Comprehensive usage guide

## 📋 **Requirements**

- **Python 3.6+** with standard libraries
- **FFmpeg** (for video conversion and audio extraction)
- **Input**: SyncNet results directory with expected structure
- **Dependencies**: Threading, subprocess, pathlib (all standard library)

The script is production-ready and successfully organizes your SyncNet results into the exactly 4 directories you requested: `video_normal`, `video_bbox`, `video_cropped`, and `audio`! 🎉
