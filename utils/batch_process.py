#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_single_chunk(chunk_info):
    """
    Process a single video chunk with SyncNet
    
    Args:
        chunk_info: Dictionary with chunk information
        
    Returns:
        Dictionary with processing results
    """
    chunk_path = chunk_info['chunk_path']
    reference_name = chunk_info['reference_name']
    data_dir = chunk_info['data_dir']
    syncnet_dir = chunk_info['syncnet_dir']
    min_track = chunk_info.get('min_track', 5)
    min_face_size = chunk_info.get('min_face_size', 10)
    
    print(f"🔄 Processing {reference_name}...")
    
    result = {
        'reference_name': reference_name,
        'chunk_path': chunk_path,
        'status': 'failed',
        'start_time': time.time()
    }
    
    try:
        # Step 1: Run preprocessing pipeline
        pipeline_cmd = f'python run_pipeline.py --videofile "{chunk_path}" --reference {reference_name} --data_dir "{data_dir}" --min_track {min_track} --min_face_size {min_face_size}'
        
        print(f"Debug: Executing command: {pipeline_cmd}")
        print(f"Debug: Working directory: {syncnet_dir}")
        
        pipeline_result = subprocess.run(
            pipeline_cmd, 
            capture_output=True, 
            text=True, 
            shell=True,
            cwd=syncnet_dir
        )
        
        if pipeline_result.returncode != 0:
            result['error'] = f"Pipeline failed: {pipeline_result.stderr}"
            return result
        
        # Check if face tracks were found
        crop_dir = os.path.join(data_dir, 'pycrop', reference_name)
        crop_files = []
        if os.path.exists(crop_dir):
            crop_files = [f for f in os.listdir(crop_dir) if f.endswith('.avi')]
        
        if not crop_files:
            result['status'] = 'no_faces'
            result['message'] = 'No face tracks found'
            return result
        
        result['face_tracks'] = len(crop_files)
        
        # Step 2: Run SyncNet analysis
        syncnet_cmd = f'python run_syncnet.py --videofile "{os.path.join(crop_dir, crop_files[0])}" --reference {reference_name} --data_dir "{data_dir}"'
        
        syncnet_result = subprocess.run(
            syncnet_cmd,
            capture_output=True,
            text=True,
            shell=True,
            cwd=syncnet_dir
        )
        
        if syncnet_result.returncode != 0:
            result['error'] = f"SyncNet failed: {syncnet_result.stderr}"
            return result
        
        # Step 3: Parse results
        offsets_file = os.path.join(data_dir, 'pywork', reference_name, 'offsets.txt')
        
        if os.path.exists(offsets_file):
            with open(offsets_file, 'r') as f:
                content = f.read().strip()
                if content:
                    # Parse multiple tracks: "TRACK 0: OFFSET -1, CONF 7.183"
                    lines = content.split('\n')
                    tracks = []
                    
                    for line in lines:
                        line = line.strip()
                        if line and 'TRACK' in line:
                            try:
                                # Parse: "TRACK 0: OFFSET -1, CONF 7.183"
                                parts = line.split(', ')
                                if len(parts) >= 2:
                                    offset_part = parts[0].split(': OFFSET ')
                                    conf_part = parts[1].split('CONF ')
                                    
                                    if len(offset_part) >= 2 and len(conf_part) >= 2:
                                        track_info = {
                                            "offset": int(offset_part[1]),
                                            "confidence": float(conf_part[1])
                                        }
                                        tracks.append(track_info)
                            except (ValueError, IndexError) as e:
                                print(f"Warning: Could not parse line '{line}': {e}")
                    
                    # Use the track with highest confidence
                    if tracks:
                        best_track = max(tracks, key=lambda x: x['confidence'])
                        result['offset'] = best_track["offset"]
                        result['confidence'] = best_track["confidence"]
                        result['all_tracks'] = tracks
        
        result['status'] = 'success'
        result['offsets_file'] = offsets_file
        
    except Exception as e:
        result['error'] = str(e)
    
    finally:
        result['end_time'] = time.time()
        result['processing_time'] = result['end_time'] - result['start_time']
    
    return result

def batch_process_chunks(chunks_dir, output_dir, syncnet_dir, max_workers=2, min_track=5, min_face_size=10):
    """
    Process multiple video chunks in parallel
    
    Args:
        chunks_dir: Directory containing video chunks
        output_dir: Output directory for SyncNet results
        syncnet_dir: Path to SyncNet python directory
        max_workers: Maximum number of parallel workers
        min_track: Minimum track length for SyncNet
        min_face_size: Minimum face size for SyncNet
    """
    # Find all video chunks
    chunk_files = []
    for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv']:
        chunk_files.extend(Path(chunks_dir).glob(ext))
    
    chunk_files = sorted(chunk_files)
    
    if not chunk_files:
        print(f"❌ No video files found in {chunks_dir}")
        return
    
    print(f"📹 Found {len(chunk_files)} video chunks")
    
    # Create SyncNet data directory
    syncnet_data_dir = os.path.join(output_dir, 'syncnet_data')
    os.makedirs(syncnet_data_dir, exist_ok=True)
    
    # Prepare chunk information
    chunk_infos = []
    for chunk_file in chunk_files:
        chunk_name = chunk_file.stem
        chunk_infos.append({
            'chunk_path': os.path.abspath(str(chunk_file)),
            'reference_name': chunk_name,
            'data_dir': os.path.abspath(syncnet_data_dir),
            'syncnet_dir': syncnet_dir,
            'min_track': min_track,
            'min_face_size': min_face_size
        })
    
    # Process chunks in parallel
    results = []
    completed = 0
    
    print(f"🚀 Starting batch processing with {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_chunk = {
            executor.submit(process_single_chunk, chunk_info): chunk_info
            for chunk_info in chunk_infos
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_chunk):
            chunk_info = future_to_chunk[future]
            
            try:
                result = future.result()
                results.append(result)
                completed += 1
                
                # Print progress
                status_emoji = "✅" if result['status'] == 'success' else "⚠️" if result['status'] == 'no_faces' else "❌"
                status_msg = f"Offset={result.get('offset', '?')}, Conf={result.get('confidence', '?'):.3f}" if result['status'] == 'success' else result.get('message', result.get('error', 'Unknown'))
                
                print(f"{status_emoji} [{completed}/{len(chunk_infos)}] {result['reference_name']}: {status_msg}")
                
            except Exception as e:
                print(f"❌ [{completed}/{len(chunk_infos)}] {chunk_info['reference_name']}: Exception - {e}")
                results.append({
                    'reference_name': chunk_info['reference_name'],
                    'chunk_path': chunk_info['chunk_path'],
                    'status': 'exception',
                    'error': str(e)
                })
                completed += 1
    
    # Save results summary
    summary = {
        'total_chunks': len(chunk_files),
        'successful': len([r for r in results if r['status'] == 'success']),
        'no_faces': len([r for r in results if r['status'] == 'no_faces']),
        'failed': len([r for r in results if r['status'] in ['failed', 'exception']]),
        'results': results,
        'processing_timestamp': time.time()
    }
    
    summary_file = os.path.join(output_dir, 'batch_processing_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print final summary
    print(f"\n{'='*60}")
    print("📊 BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total chunks: {summary['total_chunks']}")
    print(f"✅ Successful: {summary['successful']}")
    print(f"⚠️  No faces: {summary['no_faces']}")
    print(f"❌ Failed: {summary['failed']}")
    print(f"📄 Summary saved: {summary_file}")
    
    # Print detailed results for successful analyses
    successful_results = [r for r in results if r['status'] == 'success']
    if successful_results:
        print(f"\n📈 SUCCESSFUL SYNC ANALYSIS:")
        for result in successful_results:
            offset = result.get('offset', '?')
            conf = result.get('confidence', '?')
            time_taken = result.get('processing_time', '?')
            print(f"  {result['reference_name']}: Offset={offset}, Conf={conf:.3f}, Time={time_taken:.1f}s")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Batch process video chunks with SyncNet")
    parser.add_argument('--chunks_dir', required=True, help='Directory containing video chunks')
    parser.add_argument('--output_dir', required=True, help='Output directory for results')
    parser.add_argument('--syncnet_dir', required=True, help='Path to SyncNet python directory')
    parser.add_argument('--max_workers', type=int, default=2, help='Maximum parallel workers (default: 2)')
    parser.add_argument('--min_track', type=int, default=5, help='Minimum track length for SyncNet (default: 5)')
    parser.add_argument('--min_face_size', type=int, default=10, help='Minimum face size for SyncNet (default: 10)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.chunks_dir):
        print(f"❌ Chunks directory not found: {args.chunks_dir}")
        sys.exit(1)
    
    if not os.path.exists(args.syncnet_dir):
        print(f"❌ SyncNet directory not found: {args.syncnet_dir}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run batch processing
    batch_process_chunks(
        chunks_dir=args.chunks_dir,
        output_dir=args.output_dir,
        syncnet_dir=args.syncnet_dir,
        max_workers=args.max_workers,
        min_track=args.min_track,
        min_face_size=args.min_face_size
    )

if __name__ == "__main__":
    main()
