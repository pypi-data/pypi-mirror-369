"""
Simple Resize Task Module
Simple task to resize a video file using ffmpeg
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

def get_common_resolutions():
    """Get list of common video resolutions"""
    return {
        '1': {'name': '480p (SD)', 'resolution': '854x480'},
        '2': {'name': '720p (HD)', 'resolution': '1280x720'},
        '3': {'name': '1080p (Full HD)', 'resolution': '1920x1080'},
        '4': {'name': '1440p (2K)', 'resolution': '2560x1440'},
        '5': {'name': '2160p (4K)', 'resolution': '3840x2160'},
        '6': {'name': 'Custom', 'resolution': 'custom'}
    }

def validate_resolution(resolution):
    """Validate custom resolution format (WIDTHxHEIGHT)"""
    try:
        if 'x' not in resolution:
            return False
        width, height = resolution.split('x')
        width, height = int(width), int(height)
        return width > 0 and height > 0
    except ValueError:
        return False

def resize_video(input_file, output_file, resolution, quality='medium'):
    """Resize video using ffmpeg"""
    try:
        # Quality settings
        quality_settings = {
            'fast': ['-preset', 'fast', '-crf', '28'],
            'medium': ['-preset', 'medium', '-crf', '23'],
            'high': ['-preset', 'slow', '-crf', '18']
        }
        
        cmd = ['ffmpeg', '-i', input_file]
        
        # Add resolution filter
        cmd.extend(['-vf', f'scale={resolution}'])
        
        # Add quality settings
        cmd.extend(quality_settings.get(quality, quality_settings['medium']))
        
        # Add output file and overwrite flag
        cmd.extend([output_file, '-y'])
        
        print(f"[*] Resizing video...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Resolution: {resolution}")
        print(f"Quality: {quality}")
        print("[*] Processing (this may take a while)...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Video resized successfully!")
            print(f"Output file: {output_file}")
            
            # Show file sizes comparison
            if os.path.exists(output_file):
                input_size = os.path.getsize(input_file)
                output_size = os.path.getsize(output_file)
                
                def format_size(size):
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if size < 1024.0:
                            return f"{size:.1f} {unit}"
                        size /= 1024.0
                    return f"{size:.1f} TB"
                
                print(f"Original size: {format_size(input_size)}")
                print(f"New size: {format_size(output_size)}")
                
                if output_size < input_size:
                    reduction = ((input_size - output_size) / input_size) * 100
                    print(f"Size reduction: {reduction:.1f}%")
                elif output_size > input_size:
                    increase = ((output_size - input_size) / input_size) * 100
                    print(f"Size increase: {increase:.1f}%")
        else:
            print("[!] Error during resizing:")
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
    
    print("[*] Simple Video Resizer")
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
            choice = input("\n> Enter the number of the video file to resize: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select resolution
    print("\n[*] Available resolutions:")
    resolutions = get_common_resolutions()
    for key, value in resolutions.items():
        print(f"{key}. {value['name']} - {value['resolution']}")
    
    try:
        resolution_choice = input("\n> Enter resolution choice: ").strip()
        
        if resolution_choice in resolutions:
            if resolutions[resolution_choice]['resolution'] == 'custom':
                custom_resolution = input("> Enter custom resolution (WIDTHxHEIGHT, e.g., 1280x720): ").strip()
                if not validate_resolution(custom_resolution):
                    print("[!] Invalid resolution format")
                    return
                resolution = custom_resolution
            else:
                resolution = resolutions[resolution_choice]['resolution']
        else:
            print("[!] Invalid resolution choice")
            return
        
        # Select quality
        print("\n[*] Quality options:")
        print("1. Fast (lower quality, faster processing)")
        print("2. Medium (balanced quality and speed)")
        print("3. High (higher quality, slower processing)")
        
        quality_choice = input("> Enter quality choice (or press Enter for medium): ").strip()
        quality_map = {'1': 'fast', '2': 'medium', '3': 'high'}
        quality = quality_map.get(quality_choice, 'medium')
        
        # Generate output filename
        base_name, ext = os.path.splitext(selected_file)
        resolution_suffix = resolution.replace('x', 'x')
        output_file = f"{base_name}_{resolution_suffix}{ext}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform resizing
        resize_video(selected_file, output_file, resolution, quality)
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()