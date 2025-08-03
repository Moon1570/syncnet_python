#!/usr/bin/env python3
"""
Filter Videos by SyncNet Score
Batch process videos and filter based on audio-visual synchronization quality
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class SyncNetFilter:
    def __init__(self, min_confidence=5.0, max_abs_offset=3, min_face_size=50, min_track=50):
        """
        Initialize SyncNet filter with quality thresholds
        
        Args:
            min_confidence: Minimum confidence score to keep video
            max_abs_offset: Maximum absolute offset (frames) to keep video
            min_face_size: Minimum face size for detection
            min_track: Minimum track length for processing
        """
        self.min_confidence = min_confidence
        self.max_abs_offset = max_abs_offset
        self.min_face_size = min_face_size
        self.min_track = min_track
        
    def process_single_video(self, video_path, output_dir, temp_dir):
        """
        Process a single video with SyncNet and return quality metrics
        
        Args:
            video_path: Path to input video file
            output_dir: Directory for final results
            temp_dir: Temporary directory for processing
            
        Returns:
            Dict with processing results and quality metrics
        """
        video_name = Path(video_path).stem
        print(f"🔄 Processing: {video_name}")
        
        result = {
            'video_name': video_name,
            'video_path': str(video_path),
            'status': 'failed',
            'start_time': time.time()
        }
        
        try:
            # Create temporary processing directory
            temp_video_dir = os.path.join(temp_dir, video_name)
            os.makedirs(temp_video_dir, exist_ok=True)
            
            # Step 1: Run pipeline
            python_exec = sys.executable
            pipeline_cmd = [
                python_exec, 'run_pipeline.py',
                '--videofile', str(video_path),
                '--reference', video_name,
                '--data_dir', temp_video_dir,
                '--min_face_size', str(self.min_face_size),
                '--min_track', str(self.min_track)
            ]
            
            pipeline_result = subprocess.run(
                pipeline_cmd, 
                capture_output=True, 
                text=True,
                cwd=os.getcwd()
            )
            
            if pipeline_result.returncode != 0:
                result['error'] = f"Pipeline failed: {pipeline_result.stderr}"
                return result
            
            # Check if tracks were created
            tracks_file = os.path.join(temp_video_dir, 'pywork', video_name, 'tracks.pckl')
            if not os.path.exists(tracks_file):
                result['status'] = 'no_faces'
                result['message'] = 'No face tracks detected'
                return result
            
            # Step 2: Run SyncNet
            syncnet_cmd = [
                python_exec, 'run_syncnet.py',
                '--videofile', str(video_path),
                '--reference', video_name,
                '--data_dir', temp_video_dir
            ]
            
            syncnet_result = subprocess.run(
                syncnet_cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if syncnet_result.returncode != 0:
                result['error'] = f"SyncNet failed: {syncnet_result.stderr}"
                return result
            
            # Step 3: Parse results
            offsets_file = os.path.join(temp_video_dir, 'pywork', video_name, 'offsets.txt')
            if os.path.exists(offsets_file):
                with open(offsets_file, 'r') as f:
                    content = f.read().strip()
                    
                # Parse the offsets file
                lines = content.split('\n')
                tracks = []
                
                for line in lines:
                    if 'TRACK' in line and 'OFFSET' in line and 'CONF' in line:
                        try:
                            # Parse: "TRACK 0: OFFSET 0, CONF 7.996"
                            parts = line.split(': OFFSET ')
                            if len(parts) >= 2:
                                offset_conf_part = parts[1].split(', CONF ')
                                if len(offset_conf_part) >= 2:
                                    offset = int(offset_conf_part[0])
                                    confidence = float(offset_conf_part[1])
                                    tracks.append({
                                        'offset': offset,
                                        'confidence': confidence
                                    })
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Could not parse line '{line}': {e}")
                            continue
                
                # Use the track with highest confidence
                if tracks:
                    best_track = max(tracks, key=lambda x: x['confidence'])
                    result['offset'] = best_track['offset']
                    result['confidence'] = best_track['confidence']
                    result['all_tracks'] = tracks
            
            # Check if we got the metrics
            if 'confidence' not in result:
                result['error'] = 'Could not parse SyncNet results'
                return result
            
            # Determine quality
            abs_offset = abs(result['offset'])
            passes_confidence = result['confidence'] >= self.min_confidence
            passes_offset = abs_offset <= self.max_abs_offset
            
            result['passes_quality'] = passes_confidence and passes_offset
            result['quality_reasons'] = []
            
            if not passes_confidence:
                result['quality_reasons'].append(f"Low confidence: {result['confidence']:.3f} < {self.min_confidence}")
            if not passes_offset:
                result['quality_reasons'].append(f"High offset: {abs_offset} > {self.max_abs_offset}")
            
            result['status'] = 'success'
            
        except Exception as e:
            result['error'] = str(e)
        finally:
            result['end_time'] = time.time()
            result['processing_time'] = result['end_time'] - result['start_time']
            
            # Clean up temporary files
            try:
                if os.path.exists(temp_video_dir):
                    shutil.rmtree(temp_video_dir)
            except:
                pass
        
        return result
    
    def filter_videos(self, input_dir, output_dir, max_workers=2, keep_all=False):
        """
        Batch process and filter videos from input directory
        
        Args:
            input_dir: Directory containing input videos
            output_dir: Directory for filtered results
            max_workers: Number of parallel processing workers
            keep_all: If True, keep all videos but mark quality in results
        """
        # Find all video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.mp3', '.wav']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(Path(input_dir).glob(f'*{ext}'))
            video_files.extend(Path(input_dir).glob(f'*{ext.upper()}'))
        
        video_files = sorted(set(video_files))
        
        if not video_files:
            print(f"❌ No video files found in {input_dir}")
            return
        
        print(f"📹 Found {len(video_files)} video files")
        print(f"🎯 Quality thresholds: confidence≥{self.min_confidence}, |offset|≤{self.max_abs_offset}")
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        
        if not keep_all:
            good_dir = os.path.join(output_dir, 'good_quality')
            poor_dir = os.path.join(output_dir, 'poor_quality')
            os.makedirs(good_dir, exist_ok=True)
            os.makedirs(poor_dir, exist_ok=True)
        
        temp_dir = os.path.join(output_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process videos
        results = []
        completed = 0
        
        print(f"🚀 Starting batch processing with {max_workers} workers...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_video = {
                executor.submit(self.process_single_video, video_path, output_dir, temp_dir): video_path
                for video_path in video_files
            }
            
            # Collect results
            for future in as_completed(future_to_video):
                video_path = future_to_video[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    # Print progress
                    if result['status'] == 'success':
                        quality = "✅ GOOD" if result['passes_quality'] else "❌ POOR"
                        conf = result.get('confidence', 0)
                        offset = result.get('offset', 0)
                        print(f"{quality} [{completed}/{len(video_files)}] {result['video_name']}: "
                              f"Conf={conf:.3f}, Offset={offset}")
                        
                        # Copy file to appropriate directory
                        if not keep_all:
                            src_path = result['video_path']
                            dst_dir = good_dir if result['passes_quality'] else poor_dir
                            dst_path = os.path.join(dst_dir, os.path.basename(src_path))
                            shutil.copy2(src_path, dst_path)
                            
                    else:
                        status_emoji = "⚠️" if result['status'] == 'no_faces' else "❌"
                        message = result.get('message', result.get('error', 'Unknown error'))
                        print(f"{status_emoji} [{completed}/{len(video_files)}] {result['video_name']}: {message}")
                        
                except Exception as e:
                    print(f"❌ [{completed+1}/{len(video_files)}] {os.path.basename(video_path)}: Exception - {e}")
                    completed += 1
        
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        # Generate summary
        successful = [r for r in results if r['status'] == 'success']
        good_quality = [r for r in successful if r['passes_quality']]
        poor_quality = [r for r in successful if not r['passes_quality']]
        no_faces = [r for r in results if r['status'] == 'no_faces']
        failed = [r for r in results if r['status'] == 'failed']
        
        summary = {
            'filter_settings': {
                'min_confidence': self.min_confidence,
                'max_abs_offset': self.max_abs_offset,
                'min_face_size': self.min_face_size,
                'min_track': self.min_track
            },
            'total_videos': len(video_files),
            'successful_processing': len(successful),
            'good_quality': len(good_quality),
            'poor_quality': len(poor_quality),
            'no_faces_detected': len(no_faces),
            'processing_failed': len(failed),
            'results': results,
            'timestamp': time.time()
        }
        
        # Save detailed results
        results_file = os.path.join(output_dir, 'sync_filter_results.json')
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\\n{'='*80}")
        print("📊 SYNC QUALITY FILTERING SUMMARY")
        print(f"{'='*80}")
        print(f"Total videos processed: {summary['total_videos']}")
        print(f"✅ Successfully processed: {summary['successful_processing']}")
        print(f"🎯 Good quality (kept): {summary['good_quality']}")
        print(f"❌ Poor quality (filtered): {summary['poor_quality']}")
        print(f"⚠️  No faces detected: {summary['no_faces_detected']}")
        print(f"💥 Processing failed: {summary['processing_failed']}")
        print(f"📄 Detailed results: {results_file}")
        
        if good_quality:
            print(f"\\n🏆 TOP QUALITY VIDEOS:")
            sorted_good = sorted(good_quality, key=lambda x: x['confidence'], reverse=True)
            for result in sorted_good[:10]:  # Show top 10
                print(f"  {result['video_name']}: Conf={result['confidence']:.3f}, Offset={result['offset']}")
        
        if poor_quality:
            print(f"\\n⚠️  FILTERED OUT (reasons):")
            for result in poor_quality[:10]:  # Show first 10
                reasons = ', '.join(result['quality_reasons'])
                print(f"  {result['video_name']}: {reasons}")
        
        return summary


def main():
    parser = argparse.ArgumentParser(description="Filter videos by SyncNet quality scores")
    parser.add_argument('--input_dir', required=True, help='Directory containing input videos')
    parser.add_argument('--output_dir', required=True, help='Output directory for filtered results')
    parser.add_argument('--min_confidence', type=float, default=5.0, 
                       help='Minimum confidence score to keep video (default: 5.0)')
    parser.add_argument('--max_abs_offset', type=int, default=3,
                       help='Maximum absolute offset (frames) to keep video (default: 3)')
    parser.add_argument('--min_face_size', type=int, default=50,
                       help='Minimum face size for detection (default: 50)')
    parser.add_argument('--min_track', type=int, default=50,
                       help='Minimum track length for processing (default: 50)')
    parser.add_argument('--max_workers', type=int, default=2,
                       help='Number of parallel workers (default: 2)')
    parser.add_argument('--keep_all', action='store_true',
                       help='Keep all videos, just analyze quality (don\'t copy to folders)')
    parser.add_argument('--preset', choices=['strict', 'high', 'medium', 'relaxed'],
                       help='Use quality preset instead of manual thresholds')
    
    args = parser.parse_args()
    
    # Apply preset if specified
    if args.preset:
        presets = {
            'strict': {'min_confidence': 8.0, 'max_abs_offset': 2},
            'high': {'min_confidence': 6.0, 'max_abs_offset': 3},
            'medium': {'min_confidence': 4.0, 'max_abs_offset': 5},
            'relaxed': {'min_confidence': 2.0, 'max_abs_offset': 8}
        }
        preset_config = presets[args.preset]
        args.min_confidence = preset_config['min_confidence']
        args.max_abs_offset = preset_config['max_abs_offset']
        print(f"🎯 Using '{args.preset}' preset: confidence≥{args.min_confidence}, |offset|≤{args.max_abs_offset}")
    
    # Validate inputs
    if not os.path.exists(args.input_dir):
        print(f"❌ Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    # Create filter and run
    filter_tool = SyncNetFilter(
        min_confidence=args.min_confidence,
        max_abs_offset=args.max_abs_offset,
        min_face_size=args.min_face_size,
        min_track=args.min_track
    )
    
    filter_tool.filter_videos(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        keep_all=args.keep_all
    )


if __name__ == "__main__":
    main()
