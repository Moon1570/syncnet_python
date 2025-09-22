#!/usr/bin/env python3
"""
Directory Preparation Script for SyncNet Results

This script takes a directory containing SyncNet results (e.g., results/video1/good_quality)
and organizes the content into 4 structured directories with optional video ID prefixing:

1. video_normal - Original chunk videos (all chunks) 
2. video_bbox - Bounding box visualization videos (converted to MP4)
3. video_cropped - Cropped face videos (converted to MP4, renamed to chunk IDs)
4. audio - Audio extracted from normal chunk videos

The script can automatically prefix all output files with a video ID (e.g., YouTube ID)
to create names like "h9OrOkhODmY_chunk_000.mp4" instead of "chunk_000.mp4".

Usage:
    python directory_prepare.py --input_dir results/video1/good_quality --output_dir h9OrOkhODmY
    python directory_prepare.py --input_dir results/video1/good_quality --output_dir organized --video_id h9OrOkhODmY
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DirectoryPreparer:
    """
    Organizes SyncNet results into structured directories
    """
    
    def __init__(self, input_dir, output_dir, max_workers=4, video_id=None):
        """
        Initialize the directory preparer
        
        Args:
            input_dir: Path to input directory (e.g., results/video1/good_quality)
            output_dir: Path to output directory where organized folders will be created
            max_workers: Number of parallel workers for processing
            video_id: Optional video ID to use as prefix for chunk names (e.g., YouTube ID)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.video_id = video_id or Path(output_dir).name  # Use output_dir name as default ID
        
        # Define output subdirectories
        self.video_normal_dir = self.output_dir / "video_normal"
        self.video_bbox_dir = self.output_dir / "video_bbox"
        self.video_cropped_dir = self.output_dir / "video_cropped"
        self.audio_dir = self.output_dir / "audio"
        
        # Validate input
        self._validate_input()
        
        logger.info(f"🎯 Using video ID prefix: {self.video_id}")
        
    def _get_output_name(self, chunk_name):
        """
        Generate output name with video ID prefix
        
        Args:
            chunk_name: Original chunk name (e.g., 'chunk_000')
            
        Returns:
            str: Prefixed name (e.g., 'h9OrOkhODmY_chunk_000')
        """
        return f"{self.video_id}_{chunk_name}"
        
    def _validate_input(self):
        """Validate input directory structure"""
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")
        
        # Check for expected structure
        syncnet_outputs = self.input_dir / "syncnet_outputs"
        if not syncnet_outputs.exists():
            raise ValueError(f"syncnet_outputs directory not found in: {self.input_dir}")
            
        logger.info(f"✅ Input directory validated: {self.input_dir}")
    
    def _create_output_directories(self):
        """Create all output directories"""
        directories = [
            self.video_normal_dir,
            self.video_bbox_dir, 
            self.video_cropped_dir,
            self.audio_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
    
    def _get_chunk_list(self):
        """Get list of all chunk directories"""
        syncnet_outputs = self.input_dir / "syncnet_outputs"
        chunks = []
        
        for item in syncnet_outputs.iterdir():
            if item.is_dir() and item.name.startswith('chunk_'):
                chunks.append(item.name)
        
        chunks.sort()  # Sort to ensure consistent processing order
        logger.info(f"📋 Found {len(chunks)} chunks to process")
        return chunks
    
    def _convert_avi_to_mp4(self, input_path, output_path):
        """
        Convert AVI video to MP4 using ffmpeg
        
        Args:
            input_path: Path to input AVI file
            output_path: Path to output MP4 file
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-c:v', 'libx264',      # Video codec
                '-c:a', 'aac',          # Audio codec  
                '-preset', 'medium',     # Encoding speed/quality balance
                '-crf', '23',           # Quality setting (18-28 is good range)
                '-movflags', '+faststart', # Enable fast start for web
                '-y',                   # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ FFmpeg conversion failed for {input_path}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error converting {input_path}: {e}")
            return False
    
    def _extract_audio(self, input_path, output_path):
        """
        Extract audio from video file
        
        Args:
            input_path: Path to input video file
            output_path: Path to output audio file
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vn',                  # No video
                '-acodec', 'pcm_s16le', # Audio codec
                '-ar', '16000',         # Sample rate (16kHz for speech)
                '-ac', '1',             # Mono channel
                '-y',                   # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Audio extraction failed for {input_path}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error extracting audio from {input_path}: {e}")
            return False
    
    def _process_chunk_normal_video(self, chunk_name):
        """Process normal video for a chunk"""
        input_video = self.input_dir / f"{chunk_name}.mp4"
        output_name = self._get_output_name(chunk_name)
        output_video = self.video_normal_dir / f"{output_name}.mp4"
        
        if input_video.exists():
            try:
                shutil.copy2(input_video, output_video)
                logger.info(f"✅ Copied normal video: {output_name}.mp4")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to copy normal video {chunk_name}: {e}")
                return False
        else:
            logger.warning(f"⚠️  Normal video not found: {input_video}")
            return False
    
    def _process_chunk_bbox_video(self, chunk_name):
        """Process bounding box video for a chunk"""
        input_bbox = self.input_dir / "syncnet_outputs" / chunk_name / f"{chunk_name}_with_bboxes.avi"
        output_name = self._get_output_name(chunk_name)
        output_bbox = self.video_bbox_dir / f"{output_name}_with_bboxes.mp4"
        
        if input_bbox.exists():
            success = self._convert_avi_to_mp4(input_bbox, output_bbox)
            if success:
                logger.info(f"✅ Converted bbox video: {output_name}_with_bboxes.mp4")
                return True
            else:
                logger.error(f"❌ Failed to convert bbox video: {chunk_name}")
                return False
        else:
            logger.warning(f"⚠️  Bbox video not found: {input_bbox}")
            return False
    
    def _process_chunk_cropped_video(self, chunk_name):
        """Process cropped face video for a chunk"""
        input_cropped = self.input_dir / "syncnet_outputs" / chunk_name / "cropped_faces" / "00000.avi"
        output_name = self._get_output_name(chunk_name)
        output_cropped = self.video_cropped_dir / f"{output_name}.mp4"
        
        if input_cropped.exists():
            success = self._convert_avi_to_mp4(input_cropped, output_cropped)
            if success:
                logger.info(f"✅ Converted cropped video: {output_name}.mp4")
                return True
            else:
                logger.error(f"❌ Failed to convert cropped video: {chunk_name}")
                return False
        else:
            logger.warning(f"⚠️  Cropped video not found: {input_cropped}")
            return False
    
    def _process_chunk_audio(self, chunk_name):
        """Extract audio from normal video for a chunk"""
        input_video = self.input_dir / f"{chunk_name}.mp4"
        output_name = self._get_output_name(chunk_name)
        output_audio = self.audio_dir / f"{output_name}.wav"
        
        if input_video.exists():
            success = self._extract_audio(input_video, output_audio)
            if success:
                logger.info(f"✅ Extracted audio: {output_name}.wav")
                return True
            else:
                logger.error(f"❌ Failed to extract audio: {chunk_name}")
                return False
        else:
            logger.warning(f"⚠️  Normal video not found for audio extraction: {input_video}")
            return False
    
    def _process_single_chunk(self, chunk_name):
        """Process all outputs for a single chunk"""
        results = {
            'chunk': chunk_name,
            'normal_video': False,
            'bbox_video': False,
            'cropped_video': False,
            'audio': False
        }
        
        # Process each type
        results['normal_video'] = self._process_chunk_normal_video(chunk_name)
        results['bbox_video'] = self._process_chunk_bbox_video(chunk_name)
        results['cropped_video'] = self._process_chunk_cropped_video(chunk_name)
        results['audio'] = self._process_chunk_audio(chunk_name)
        
        return results
    
    def prepare_directories(self):
        """
        Main method to prepare all directories
        
        Returns:
            dict: Summary of processing results
        """
        logger.info(f"🚀 Starting directory preparation")
        logger.info(f"📥 Input: {self.input_dir}")
        logger.info(f"📤 Output: {self.output_dir}")
        
        # Create output directories
        self._create_output_directories()
        
        # Get list of chunks to process
        chunks = self._get_chunk_list()
        
        if not chunks:
            logger.warning("⚠️  No chunks found to process")
            return {'total_chunks': 0, 'results': []}
        
        # Process chunks in parallel
        results = []
        completed = 0
        
        logger.info(f"🔄 Processing {len(chunks)} chunks with {self.max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_chunk = {
                executor.submit(self._process_single_chunk, chunk): chunk
                for chunk in chunks
            }
            
            # Collect results
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Show progress
                    success_count = sum([
                        result['normal_video'],
                        result['bbox_video'], 
                        result['cropped_video'],
                        result['audio']
                    ])
                    
                    logger.info(f"📊 [{completed}/{len(chunks)}] {chunk}: {success_count}/4 operations successful")
                    
                except Exception as e:
                    logger.error(f"❌ [{completed+1}/{len(chunks)}] {chunk}: Exception - {e}")
                    completed += 1
        
        # Generate summary
        summary = self._generate_summary(results)
        
        return summary
    
    def _generate_summary(self, results):
        """Generate processing summary"""
        total_chunks = len(results)
        
        counts = {
            'normal_video': sum(r['normal_video'] for r in results),
            'bbox_video': sum(r['bbox_video'] for r in results),
            'cropped_video': sum(r['cropped_video'] for r in results),
            'audio': sum(r['audio'] for r in results)
        }
        
        summary = {
            'total_chunks': total_chunks,
            'successful_operations': counts,
            'results': results,
            'output_directories': {
                'video_normal': str(self.video_normal_dir),
                'video_bbox': str(self.video_bbox_dir),
                'video_cropped': str(self.video_cropped_dir),
                'audio': str(self.audio_dir)
            }
        }
        
        # Print summary
        logger.info(f"\n{'='*80}")
        logger.info("📊 DIRECTORY PREPARATION SUMMARY")
        logger.info(f"{'='*80}")
        logger.info(f"Total chunks processed: {total_chunks}")
        logger.info(f"✅ Normal videos: {counts['normal_video']}/{total_chunks}")
        logger.info(f"📦 Bbox videos: {counts['bbox_video']}/{total_chunks}")
        logger.info(f"👤 Cropped videos: {counts['cropped_video']}/{total_chunks}")
        logger.info(f"🔊 Audio files: {counts['audio']}/{total_chunks}")
        
        logger.info(f"\n📁 Output directories:")
        for name, path in summary['output_directories'].items():
            file_count = len(list(Path(path).glob('*'))) if Path(path).exists() else 0
            logger.info(f"   {name}: {path} ({file_count} files)")
        
        return summary


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Prepare SyncNet results into organized directory structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage (uses output directory name as video ID)
    python directory_prepare.py --input_dir results/video1/good_quality --output_dir h9OrOkhODmY
    
    # With explicit video ID
    python directory_prepare.py --input_dir results/video1/good_quality --output_dir organized_output --video_id h9OrOkhODmY
    
    # With custom worker count
    python directory_prepare.py --input_dir results/video1/good_quality --output_dir h9OrOkhODmY --max_workers 8
        """
    )
    
    parser.add_argument(
        '--input_dir', 
        required=True,
        help='Input directory containing SyncNet results (e.g., results/video1/good_quality)'
    )
    
    parser.add_argument(
        '--output_dir',
        required=True, 
        help='Output directory where organized folders will be created'
    )
    
    parser.add_argument(
        '--max_workers',
        type=int,
        default=4,
        help='Number of parallel workers for processing (default: 4)'
    )
    
    parser.add_argument(
        '--video_id',
        help='Video ID to use as prefix for chunk names (default: uses output directory name)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.input_dir):
        logger.error(f"❌ Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    # Check ffmpeg availability
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ FFmpeg not found. Please install FFmpeg to use this script.")
        logger.error("   Install with: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)")
        sys.exit(1)
    
    # Create preparer and run
    try:
        preparer = DirectoryPreparer(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            max_workers=args.max_workers,
            video_id=args.video_id
        )
        
        summary = preparer.prepare_directories()
        
        logger.info(f"\n🎉 Directory preparation completed successfully!")
        logger.info(f"📁 Results available in: {args.output_dir}")
        
    except Exception as e:
        logger.error(f"❌ Directory preparation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
