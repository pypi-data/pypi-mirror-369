"""
Simple Video Merge Task Module
Simple task to merge multiple video files into one using ffmpeg
"""

import os
import glob
import subprocess
import tempfile

def list_video_files():
    """List all video files in the current directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
    video_files = []
    
    for extension in video_extensions:
        video_files.extend(glob.glob(extension))
        video_files.extend(glob.glob(extension.upper()))
    
    return sorted(video_files)

def get_video_info(video_file):
    """Get basic video information using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_streams', '-select_streams', 'v:0', video_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            if 'streams' in data and data['streams']:
                stream = data['streams'][0]
                return {
                    'width': stream.get('width', 'Unknown'),
                    'height': stream.get('height', 'Unknown'),
                    'codec': stream.get('codec_name', 'Unknown')
                }
    except:
        pass
    return {'width': 'Unknown', 'height': 'Unknown', 'codec': 'Unknown'}

def create_file_list(video_files, temp_dir):
    """Create a temporary file list for ffmpeg concat"""
    file_list_path = os.path.join(temp_dir, 'file_list.txt')
    with open(file_list_path, 'w') as f:
        for video_file in video_files:
            # Use absolute path and escape single quotes
            abs_path = os.path.abspath(video_file).replace("'", "'\"'\"'")
            f.write(f"file '{abs_path}'\n")
    return file_list_path

def merge_videos(video_files, output_file, merge_method='concat'):
    """Merge videos using ffmpeg"""
    try:
        if merge_method == 'concat':
            # Method 1: Simple concatenation (same format, codec, resolution)
            with tempfile.TemporaryDirectory() as temp_dir:
                file_list_path = create_file_list(video_files, temp_dir)
                
                cmd = [
                    'ffmpeg', '-f', 'concat', '-safe', '0',
                    '-i', file_list_path, '-c', 'copy', output_file, '-y'
                ]
        elif merge_method == 'filter':
            # Method 2: Using filter_complex (handles different formats/resolutions)
            cmd = ['ffmpeg']
            
            # Add input files
            for video_file in video_files:
                cmd.extend(['-i', video_file])
            
            # Create filter_complex for concatenation
            filter_parts = []
            for i in range(len(video_files)):
                filter_parts.append(f'[{i}:v][{i}:a]')
            
            filter_complex = ''.join(filter_parts) + f'concat=n={len(video_files)}:v=1:a=1[outv][outa]'
            
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[outv]', '-map', '[outa]',
                output_file, '-y'
            ])
        
        print(f"[*] Merging {len(video_files)} videos...")
        print(f"Method: {merge_method}")
        print(f"Output: {output_file}")
        print("Input files:")
        for i, video_file in enumerate(video_files, 1):
            print(f"  {i}. {video_file}")
        print("[*] Processing (this may take a while)...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Videos merged successfully!")
            print(f"Output file: {output_file}")
            
            # Show file size
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                
                def format_size(size):
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if size < 1024.0:
                            return f"{size:.1f} {unit}"
                        size /= 1024.0
                    return f"{size:.1f} TB"
                
                print(f"Output size: {format_size(size)}")
        else:
            print("[!] Error during merging:")
            print(result.stderr)
            if merge_method == 'concat':
                print("\n[!] Try using the 'filter' method if videos have different formats/resolutions.")
            
    except FileNotFoundError:
        print("[!] ffmpeg not found. Please install ffmpeg to use this feature.")
    except Exception as e:
        print(f"[!] Error: {e}")

def main():
    """Main function to execute the task"""
    video_files = list_video_files()
    
    if not video_files:
        print("[!] No video files found in the current directory.")
        return
    
    if len(video_files) < 2:
        print("[!] At least 2 video files are required for merging.")
        return
    
    print("[*] Simple Video Merger")
    print("=" * 40)
    
    # Show available video files with info
    print("Available video files:")
    for i, video_file in enumerate(video_files, 1):
        info = get_video_info(video_file)
        size = os.path.getsize(video_file) / (1024*1024)  # MB
        print(f"{i}. {video_file}")
        print(f"   Resolution: {info['width']}x{info['height']}, Codec: {info['codec']}, Size: {size:.1f}MB")
    
    try:
        # Select videos to merge
        print(f"\n[*] Select videos to merge (e.g., 1,2,3 or 1-3):")
        selection = input("> Enter selection: ").strip()
        
        selected_indices = []
        if '-' in selection:
            # Range selection (e.g., 1-3)
            start, end = map(int, selection.split('-'))
            selected_indices = list(range(start-1, end))
        else:
            # Individual selection (e.g., 1,2,3)
            selected_indices = [int(x.strip())-1 for x in selection.split(',')]
        
        # Validate indices
        selected_files = []
        for idx in selected_indices:
            if 0 <= idx < len(video_files):
                selected_files.append(video_files[idx])
            else:
                print(f"[!] Invalid index: {idx+1}")
                return
        
        if len(selected_files) < 2:
            print("[!] Please select at least 2 videos to merge.")
            return
        
        # Choose merge method
        print("\n[*] Merge methods:")
        print("1. Concat (Fast, for identical format/resolution)")
        print("2. Filter (Slower, handles different formats/resolutions)")
        
        method_choice = input("> Enter method choice (or press Enter for concat): ").strip()
        method_map = {'1': 'concat', '2': 'filter'}
        merge_method = method_map.get(method_choice, 'concat')
        
        # Generate output filename
        base_name = os.path.splitext(selected_files[0])[0]
        output_file = f"{base_name}_merged.mp4"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Check for format consistency if using concat method
        if merge_method == 'concat':
            print("\n[!] Note: Concat method requires videos to have the same format, codec, and resolution.")
            print("    If you encounter errors, try the 'filter' method instead.")
            confirm = input("    Continue with concat method? (y/n): ").strip().lower()
            if confirm != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform merging
        merge_videos(selected_files, output_file, merge_method)
        
    except (ValueError, KeyboardInterrupt):
        print("\n[!] Invalid input or operation cancelled")

if __name__ == "__main__":
    main()