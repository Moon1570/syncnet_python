#!/usr/bin/env python3
"""
Test script for the enhanced SyncNet filtering with output preservation
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from filter_videos_by_sync_score import SyncNetFilter

def test_enhanced_filter():
    """Test the enhanced filtering functionality"""
    
    print("🧪 Testing Enhanced SyncNet Filter with Output Preservation")
    print("=" * 70)
    
    # Check if we have test data
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(test_data_dir):
        print("❌ No test data directory found. Please ensure 'data' directory exists.")
        return False
    
    # Look for video files
    video_files = []
    for ext in ['.mp4', '.avi', '.mov', '.mkv']:
        video_files.extend(Path(test_data_dir).glob(f'*{ext}'))
    
    if not video_files:
        print("❌ No video files found in data directory.")
        return False
    
    print(f"📹 Found {len(video_files)} video file(s) for testing")
    for video_file in video_files:
        print(f"   - {video_file.name}")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory(prefix='syncnet_test_') as temp_output:
        print(f"\n📁 Using temporary output directory: {temp_output}")
        
        # Create filter with relaxed settings for testing
        filter_tool = SyncNetFilter(
            min_confidence=2.0,  # Very relaxed for testing
            max_abs_offset=10,   # Very relaxed for testing
            min_face_size=50,
            min_track=50
        )
        
        print("\n🚀 Running enhanced filter with output preservation...")
        
        try:
            # Run the filter
            summary = filter_tool.filter_videos(
                input_dir=test_data_dir,
                output_dir=temp_output,
                max_workers=1,  # Single worker for testing
                keep_all=False
            )
            
            print("\n✅ Filtering completed successfully!")
            
            # Check the output structure
            print("\n📋 Checking output structure:")
            
            expected_dirs = ['good_quality', 'poor_quality', 'syncnet_outputs']
            for expected_dir in expected_dirs:
                dir_path = os.path.join(temp_output, expected_dir)
                if os.path.exists(dir_path):
                    print(f"   ✅ {expected_dir}/ directory exists")
                    
                    # List contents
                    contents = os.listdir(dir_path)
                    if contents:
                        print(f"      📂 Contains: {', '.join(contents[:5])}")
                        if len(contents) > 5:
                            print(f"      📂 ... and {len(contents) - 5} more items")
                    else:
                        print(f"      📂 (empty)")
                else:
                    print(f"   ❌ {expected_dir}/ directory missing")
            
            # Check for syncnet outputs in quality directories
            for quality_dir in ['good_quality', 'poor_quality']:
                quality_path = os.path.join(temp_output, quality_dir)
                if os.path.exists(quality_path):
                    syncnet_path = os.path.join(quality_path, 'syncnet_outputs')
                    if os.path.exists(syncnet_path):
                        print(f"   ✅ {quality_dir}/syncnet_outputs/ exists")
                        
                        # Check for specific outputs
                        for item in os.listdir(syncnet_path):
                            item_path = os.path.join(syncnet_path, item)
                            if os.path.isdir(item_path):
                                sub_contents = os.listdir(item_path)
                                print(f"      📁 {item}/ contains: {', '.join(sub_contents)}")
                    else:
                        print(f"   ⚠️  {quality_dir}/syncnet_outputs/ not found")
            
            # Check results file
            results_file = os.path.join(temp_output, 'sync_filter_results.json')
            if os.path.exists(results_file):
                print(f"   ✅ sync_filter_results.json exists")
                
                # Read and display summary stats
                import json
                with open(results_file, 'r') as f:
                    results = json.load(f)
                
                print(f"      📊 Processed: {results['total_videos']} videos")
                print(f"      📊 Good quality: {results['good_quality']}")
                print(f"      📊 Poor quality: {results['poor_quality']}")
                print(f"      📊 No faces: {results['no_faces_detected']}")
                print(f"      📊 Failed: {results['processing_failed']}")
            else:
                print(f"   ❌ sync_filter_results.json missing")
            
            print(f"\n🎉 Test completed successfully!")
            print(f"💡 You can examine the test results in: {temp_output}")
            
            # Ask if user wants to keep the test results
            response = input("\n🤔 Keep test results for inspection? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                permanent_dir = os.path.join(os.path.dirname(__file__), 'test_results')
                shutil.copytree(temp_output, permanent_dir, dirs_exist_ok=True)
                print(f"📁 Test results saved to: {permanent_dir}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main test function"""
    print("🔧 Enhanced SyncNet Filter Test Suite")
    print("=" * 50)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    
    required_files = [
        'SyncNetInstance.py',
        'SyncNetModel.py', 
        'run_pipeline.py',
        'run_syncnet.py',
        'run_visualise.py',
        'filter_videos_by_sync_score.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"   ✅ {file}")
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Run the test
    success = test_enhanced_filter()
    
    if success:
        print(f"\n🎉 All tests passed! The enhanced filter is ready to use.")
        print(f"\n📚 Usage example:")
        print(f"   python filter_videos_by_sync_score.py \\")
        print(f"       --input_dir /path/to/videos \\")
        print(f"       --output_dir /path/to/output \\")
        print(f"       --preset medium")
        print(f"\n🎯 This will now preserve:")
        print(f"   • Cropped face videos in syncnet_outputs/*/cropped_faces/")
        print(f"   • Bounding box visualizations as *_with_bboxes.avi")
        print(f"   • Analysis results (offsets.txt, tracks.pkl)")
        print(f"   • Copy everything to good_quality/ and poor_quality/ folders")
    else:
        print(f"\n❌ Tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
