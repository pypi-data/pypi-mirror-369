"""
Simple Trim Task Module
Simple task to trim a video file using ffmpeg
"""

import os
import glob
import subprocess

def list_video_files():
    """List all video files in the current directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
    video_files = []
    
    for extension in video_extensions:
        video_files.extend(glob.glob(extension))
        video_files.extend(glob.glob(extension.upper()))
    
    return sorted(video_files)

def validate_time_format(time_str):
    """Validate time format (HH:MM:SS or MM:SS or SS)"""
    try:
        parts = time_str.split(':')
        if len(parts) == 1:  # SS
            seconds = int(parts[0])
            return seconds >= 0
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes >= 0 and 0 <= seconds < 60
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours >= 0 and 0 <= minutes < 60 and 0 <= seconds < 60
        return False
    except ValueError:
        return False

def trim_video(input_file, output_file, start_time, end_time=None):
    """Trim video using ffmpeg"""
    try:
        # Place -ss before input for faster seeking and better performance
        cmd = ['ffmpeg', '-ss', start_time, '-i', input_file]
        
        if end_time:
            cmd.extend(['-to', end_time])
        
        # Add proper timestamp handling to avoid playback issues
        cmd.extend(['-c', 'copy', '-avoid_negative_ts', 'make_zero', output_file, '-y'])  # -y to overwrite
        
        print(f"[*] Trimming video...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Start: {start_time}")
        if end_time:
            print(f"End: {end_time}")
        print("[*] Processing...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Video trimmed successfully!")
            print(f"Output file: {output_file}")
            
            # Show file size
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        size_str = f"{size:.1f} {unit}"
                        break
                    size /= 1024.0
                else:
                    size_str = f"{size:.1f} TB"
                print(f"Output size: {size_str}")
        else:
            print("[!] Error during trimming:")
            print(result.stderr)
            
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
    
    print("[*] Simple Video Trimmer")
    print("=" * 40)
    
    # Select video file
    if len(video_files) == 1:
        selected_file = video_files[0]
        print(f"Selected file: {selected_file}")
    else:
        print("Available video files:")
        for i, video_file in enumerate(video_files, 1):
            print(f"{i}. {video_file}")
        
        try:
            choice = input("\n> Enter the number of the video file to trim: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Get trim parameters
    print("\n[*] Time Format: HH:MM:SS or MM:SS or SS")
    print("   Examples: 10 (10 seconds), 1:30 (1 min 30 sec), 0:01:30 (1 min 30 sec)")
    
    try:
        start_time = input("> Enter start time: ").strip()
        if not validate_time_format(start_time):
            print("[!] Invalid start time format")
            return
        
        end_time = input("> Enter end time (or press Enter for till end): ").strip()
        if end_time and not validate_time_format(end_time):
            print("[!] Invalid end time format")
            return
        
        # Generate output filename
        base_name, ext = os.path.splitext(selected_file)
        output_file = f"{base_name}_trimmed{ext}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform trimming
        trim_video(selected_file, output_file, start_time, end_time if end_time else None)
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()