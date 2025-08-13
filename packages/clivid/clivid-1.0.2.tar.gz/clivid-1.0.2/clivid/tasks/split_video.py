"""
Simple Video Split Task Module
Simple task to split a video file into multiple parts using ffmpeg
"""

import os
import glob
import subprocess
import math

def list_video_files():
    """List all video files in the current directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
    video_files = []
    
    for extension in video_extensions:
        video_files.extend(glob.glob(extension))
        video_files.extend(glob.glob(extension.upper()))
    
    return sorted(video_files)

def get_video_duration(video_file):
    """Get video duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return None

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def split_by_parts(input_file, output_prefix, num_parts):
    """Split video into equal parts"""
    duration = get_video_duration(input_file)
    if not duration:
        print("[!] Could not determine video duration")
        return False
    
    part_duration = duration / num_parts
    base_name, ext = os.path.splitext(input_file)
    
    print(f"[*] Splitting video into {num_parts} parts...")
    print(f"Total duration: {format_duration(duration)}")
    print(f"Part duration: {format_duration(part_duration)}")
    
    for i in range(num_parts):
        start_time = i * part_duration
        output_file = f"{output_prefix}_part{i+1:02d}{ext}"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(start_time),
            '-t', str(part_duration),
            '-c', 'copy',
            output_file, '-y'
        ]
        
        print(f"\n[*] Creating part {i+1}/{num_parts}: {output_file}")
        print(f"    Start: {format_duration(start_time)}")
        print(f"    Duration: {format_duration(part_duration)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / (1024*1024)  # MB
                print(f"    ✓ Created successfully ({size:.1f}MB)")
            else:
                print(f"    ✗ Failed to create {output_file}")
        else:
            print(f"    ✗ Error creating part {i+1}:")
            print(f"    {result.stderr}")
            return False
    
    return True

def split_by_duration(input_file, output_prefix, part_duration_minutes):
    """Split video by duration (minutes per part)"""
    duration = get_video_duration(input_file)
    if not duration:
        print("[!] Could not determine video duration")
        return False
    
    part_duration_seconds = part_duration_minutes * 60
    num_parts = math.ceil(duration / part_duration_seconds)
    base_name, ext = os.path.splitext(input_file)
    
    print(f"[*] Splitting video into {part_duration_minutes}-minute parts...")
    print(f"Total duration: {format_duration(duration)}")
    print(f"Estimated parts: {num_parts}")
    
    for i in range(num_parts):
        start_time = i * part_duration_seconds
        remaining_duration = duration - start_time
        actual_duration = min(part_duration_seconds, remaining_duration)
        
        if actual_duration <= 0:
            break
            
        output_file = f"{output_prefix}_part{i+1:02d}{ext}"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(start_time),
            '-t', str(actual_duration),
            '-c', 'copy',
            output_file, '-y'
        ]
        
        print(f"\n[*] Creating part {i+1}: {output_file}")
        print(f"    Start: {format_duration(start_time)}")
        print(f"    Duration: {format_duration(actual_duration)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / (1024*1024)  # MB
                print(f"    ✓ Created successfully ({size:.1f}MB)")
            else:
                print(f"    ✗ Failed to create {output_file}")
        else:
            print(f"    ✗ Error creating part {i+1}:")
            print(f"    {result.stderr}")
            return False
    
    return True

def split_by_size(input_file, output_prefix, target_size_mb):
    """Split video by target file size (MB per part)"""
    input_size_mb = os.path.getsize(input_file) / (1024*1024)
    duration = get_video_duration(input_file)
    
    if not duration:
        print("[!] Could not determine video duration")
        return False
    
    # Estimate number of parts based on size
    estimated_parts = math.ceil(input_size_mb / target_size_mb)
    part_duration = duration / estimated_parts
    
    base_name, ext = os.path.splitext(input_file)
    
    print(f"[*] Splitting video into ~{target_size_mb}MB parts...")
    print(f"Input size: {input_size_mb:.1f}MB")
    print(f"Estimated parts: {estimated_parts}")
    print(f"Estimated duration per part: {format_duration(part_duration)}")
    
    for i in range(estimated_parts):
        start_time = i * part_duration
        remaining_duration = duration - start_time
        actual_duration = min(part_duration, remaining_duration)
        
        if actual_duration <= 0:
            break
            
        output_file = f"{output_prefix}_part{i+1:02d}{ext}"
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(start_time),
            '-t', str(actual_duration),
            '-c', 'copy',
            output_file, '-y'
        ]
        
        print(f"\n[*] Creating part {i+1}: {output_file}")
        print(f"    Start: {format_duration(start_time)}")
        print(f"    Duration: {format_duration(actual_duration)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / (1024*1024)  # MB
                print(f"    ✓ Created successfully ({size:.1f}MB)")
            else:
                print(f"    ✗ Failed to create {output_file}")
        else:
            print(f"    ✗ Error creating part {i+1}:")
            print(f"    {result.stderr}")
            return False
    
    return True

def main():
    """Main function to execute the task"""
    video_files = list_video_files()
    
    if not video_files:
        print("[!] No video files found in the current directory.")
        return
    
    print("[*] Simple Video Splitter")
    print("=" * 40)
    
    # Select video file
    if len(video_files) == 1:
        selected_file = video_files[0]
        print(f"Selected file: {selected_file}")
    else:
        print("Available video files:")
        for i, video_file in enumerate(video_files, 1):
            size = os.path.getsize(video_file) / (1024*1024)  # MB
            duration = get_video_duration(video_file)
            duration_str = format_duration(duration) if duration else "Unknown"
            print(f"{i}. {video_file} ({size:.1f}MB, {duration_str})")
        
        try:
            choice = input("\n> Enter the number of the video file to split: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Show video info
    duration = get_video_duration(selected_file)
    size = os.path.getsize(selected_file) / (1024*1024)  # MB
    
    print(f"\n[*] Video Information:")
    print(f"File: {selected_file}")
    print(f"Size: {size:.1f}MB")
    if duration:
        print(f"Duration: {format_duration(duration)}")
    
    # Select split method
    print("\n[*] Split methods:")
    print("1. Split into equal parts (specify number of parts)")
    print("2. Split by duration (specify minutes per part)")
    print("3. Split by file size (specify MB per part)")
    
    try:
        method_choice = input("\n> Enter split method: ").strip()
        
        # Generate output prefix
        base_name = os.path.splitext(selected_file)[0]
        output_prefix = f"{base_name}_split"
        
        success = False
        
        if method_choice == '1':
            # Split by number of parts
            num_parts = input("> Enter number of parts: ").strip()
            try:
                num_parts = int(num_parts)
                if num_parts < 2:
                    print("[!] Number of parts must be at least 2")
                    return
                success = split_by_parts(selected_file, output_prefix, num_parts)
            except ValueError:
                print("[!] Invalid number of parts")
                return
                
        elif method_choice == '2':
            # Split by duration
            part_duration = input("> Enter minutes per part: ").strip()
            try:
                part_duration = float(part_duration)
                if part_duration <= 0:
                    print("[!] Duration must be greater than 0")
                    return
                success = split_by_duration(selected_file, output_prefix, part_duration)
            except ValueError:
                print("[!] Invalid duration")
                return
                
        elif method_choice == '3':
            # Split by size
            target_size = input("> Enter MB per part: ").strip()
            try:
                target_size = float(target_size)
                if target_size <= 0:
                    print("[!] Size must be greater than 0")
                    return
                success = split_by_size(selected_file, output_prefix, target_size)
            except ValueError:
                print("[!] Invalid size")
                return
                
        else:
            print("[!] Invalid split method choice")
            return
        
        if success:
            print("\n[+] Video split completed successfully!")
        else:
            print("\n[!] Video split failed or was incomplete")
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")
    except FileNotFoundError:
        print("[!] ffmpeg not found. Please install ffmpeg to use this feature.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()