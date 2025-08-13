"""
Simple Video Conversion Task Module
Simple task to convert video files between different formats using ffmpeg
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

def get_supported_formats():
    """Get list of supported output formats"""
    return {
        '1': {'name': 'MP4 (H.264)', 'extension': '.mp4', 'codec': 'libx264'},
        '2': {'name': 'AVI (Xvid)', 'extension': '.avi', 'codec': 'libxvid'},
        '3': {'name': 'MOV (H.264)', 'extension': '.mov', 'codec': 'libx264'},
        '4': {'name': 'MKV (H.264)', 'extension': '.mkv', 'codec': 'libx264'},
        '5': {'name': 'WMV (WMV2)', 'extension': '.wmv', 'codec': 'wmv2'},
        '6': {'name': 'WebM (VP9)', 'extension': '.webm', 'codec': 'libvpx-vp9'},
        '7': {'name': 'FLV (H.264)', 'extension': '.flv', 'codec': 'libx264'},
        '8': {'name': 'MP4 (H.265/HEVC)', 'extension': '.mp4', 'codec': 'libx265'}
    }

def convert_video(input_file, output_file, codec, quality='medium'):
    """Convert video using ffmpeg"""
    try:
        # Quality settings for different codecs
        quality_settings = {
            'libx264': {
                'fast': ['-preset', 'fast', '-crf', '28'],
                'medium': ['-preset', 'medium', '-crf', '23'],
                'high': ['-preset', 'slow', '-crf', '18']
            },
            'libx265': {
                'fast': ['-preset', 'fast', '-crf', '30'],
                'medium': ['-preset', 'medium', '-crf', '25'],
                'high': ['-preset', 'slow', '-crf', '20']
            },
            'libvpx-vp9': {
                'fast': ['-b:v', '2M'],
                'medium': ['-b:v', '1M'],
                'high': ['-b:v', '500K']
            },
            'default': {
                'fast': ['-q:v', '5'],
                'medium': ['-q:v', '3'],
                'high': ['-q:v', '1']
            }
        }
        
        cmd = ['ffmpeg', '-i', input_file]
        
        # Add codec
        cmd.extend(['-c:v', codec])
        
        # Add quality settings
        codec_quality = quality_settings.get(codec, quality_settings['default'])
        cmd.extend(codec_quality.get(quality, codec_quality['medium']))
        
        # Copy audio stream
        cmd.extend(['-c:a', 'copy'])
        
        # Add output file and overwrite flag
        cmd.extend([output_file, '-y'])
        
        print(f"[*] Converting video...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Codec: {codec}")
        print(f"Quality: {quality}")
        print("[*] Processing (this may take a while)...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Video converted successfully!")
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
            print("[!] Error during conversion:")
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
    
    print("[*] Simple Video Converter")
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
            choice = input("\n> Enter the number of the video file to convert: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select output format
    print("\n[*] Available output formats:")
    formats = get_supported_formats()
    for key, value in formats.items():
        print(f"{key}. {value['name']}")
    
    try:
        format_choice = input("\n> Enter format choice: ").strip()
        
        if format_choice in formats:
            format_info = formats[format_choice]
            codec = format_info['codec']
            extension = format_info['extension']
        else:
            print("[!] Invalid format choice")
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
        base_name = os.path.splitext(selected_file)[0]
        output_file = f"{base_name}_converted{extension}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform conversion
        convert_video(selected_file, output_file, codec, quality)
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()