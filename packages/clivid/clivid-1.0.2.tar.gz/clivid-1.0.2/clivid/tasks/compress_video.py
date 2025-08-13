"""
Simple Video Compression Task Module
Simple task to compress video files to reduce file size using ffmpeg
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

def get_compression_presets():
    """Get list of compression presets"""
    return {
        '1': {
            'name': 'Light Compression (High Quality)',
            'description': 'Slight size reduction with minimal quality loss',
            'crf': '20',
            'preset': 'medium'
        },
        '2': {
            'name': 'Medium Compression (Balanced)',
            'description': 'Good balance between size and quality',
            'crf': '23',
            'preset': 'medium'
        },
        '3': {
            'name': 'High Compression (Smaller Size)',
            'description': 'Significant size reduction with some quality loss',
            'crf': '28',
            'preset': 'fast'
        },
        '4': {
            'name': 'Maximum Compression (Smallest Size)',
            'description': 'Maximum size reduction with noticeable quality loss',
            'crf': '32',
            'preset': 'fast'
        },
        '5': {
            'name': 'Custom Settings',
            'description': 'Set your own CRF and preset values',
            'crf': 'custom',
            'preset': 'custom'
        }
    }

def get_video_bitrate(video_file):
    """Get video bitrate using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
            '-show_entries', 'stream=bit_rate', '-of', 'csv=p=0', video_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            bitrate = int(result.stdout.strip())
            return bitrate // 1000  # Convert to kbps
    except:
        pass
    return None

def compress_video(input_file, output_file, crf, preset, target_resolution=None):
    """Compress video using ffmpeg"""
    try:
        cmd = ['ffmpeg', '-i', input_file]
        
        # Add video codec and compression settings
        cmd.extend(['-c:v', 'libx264'])
        cmd.extend(['-crf', str(crf)])
        cmd.extend(['-preset', preset])
        
        # Add resolution scaling if specified
        if target_resolution:
            cmd.extend(['-vf', f'scale={target_resolution}'])
        
        # Copy audio stream (or compress slightly)
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        
        # Add output file and overwrite flag
        cmd.extend([output_file, '-y'])
        
        print(f"[*] Compressing video...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"CRF: {crf} (lower = better quality)")
        print(f"Preset: {preset}")
        if target_resolution:
            print(f"Resolution: {target_resolution}")
        print("[*] Processing (this may take a while)...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Video compressed successfully!")
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
                print(f"Compressed size: {format_size(output_size)}")
                
                if output_size < input_size:
                    reduction = ((input_size - output_size) / input_size) * 100
                    space_saved = input_size - output_size
                    print(f"Size reduction: {reduction:.1f}% ({format_size(space_saved)} saved)")
                else:
                    print("[!] Warning: Output file is larger than input!")
        else:
            print("[!] Error during compression:")
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
    
    print("[*] Simple Video Compressor")
    print("=" * 40)
    
    # Select video file
    if len(video_files) == 1:
        selected_file = video_files[0]
        print(f"Selected file: {selected_file}")
    else:
        print("Available video files:")
        for i, video_file in enumerate(video_files, 1):
            size = os.path.getsize(video_file) / (1024*1024)  # MB
            bitrate = get_video_bitrate(video_file)
            bitrate_info = f", ~{bitrate}kbps" if bitrate else ""
            print(f"{i}. {video_file} ({size:.1f}MB{bitrate_info})")
        
        try:
            choice = input("\n> Enter the number of the video file to compress: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select compression preset
    print("\n[*] Compression presets:")
    presets = get_compression_presets()
    for key, value in presets.items():
        print(f"{key}. {value['name']}")
        print(f"   {value['description']}")
    
    try:
        preset_choice = input("\n> Enter preset choice: ").strip()
        
        if preset_choice in presets:
            preset_info = presets[preset_choice]
            
            if preset_info['crf'] == 'custom':
                # Custom settings
                print("\n[*] Custom Settings:")
                print("CRF (0-51): Lower values = better quality, higher file size")
                print("Common values: 18 (high quality), 23 (default), 28 (lower quality)")
                
                crf = input("> Enter CRF value (18-32 recommended): ").strip()
                try:
                    crf = int(crf)
                    if not (0 <= crf <= 51):
                        print("[!] CRF must be between 0 and 51")
                        return
                except ValueError:
                    print("[!] Invalid CRF value")
                    return
                
                print("\nPreset options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow")
                preset = input("> Enter preset (or press Enter for 'medium'): ").strip()
                if not preset:
                    preset = 'medium'
            else:
                crf = int(preset_info['crf'])
                preset = preset_info['preset']
        else:
            print("[!] Invalid preset choice")
            return
        
        # Optional resolution scaling
        print("\n[*] Resolution options:")
        print("1. Keep original resolution")
        print("2. Scale to 1080p (1920x1080)")
        print("3. Scale to 720p (1280x720)")
        print("4. Scale to 480p (854x480)")
        print("5. Custom resolution")
        
        resolution_choice = input("> Enter resolution choice (or press Enter for original): ").strip()
        target_resolution = None
        
        if resolution_choice == '2':
            target_resolution = '1920x1080'
        elif resolution_choice == '3':
            target_resolution = '1280x720'
        elif resolution_choice == '4':
            target_resolution = '854x480'
        elif resolution_choice == '5':
            custom_res = input("> Enter custom resolution (WIDTHxHEIGHT): ").strip()
            if 'x' in custom_res:
                try:
                    w, h = custom_res.split('x')
                    int(w), int(h)  # Validate
                    target_resolution = custom_res
                except ValueError:
                    print("[!] Invalid resolution format")
                    return
        
        # Generate output filename
        base_name, ext = os.path.splitext(selected_file)
        suffix = f"_crf{crf}"
        if target_resolution:
            suffix += f"_{target_resolution.replace('x', 'x')}"
        output_file = f"{base_name}{suffix}_compressed{ext}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Show estimated processing info
        print(f"\n[*] Compression settings:")
        print(f"CRF: {crf}")
        print(f"Preset: {preset}")
        if target_resolution:
            print(f"Target resolution: {target_resolution}")
        
        # Perform compression
        compress_video(selected_file, output_file, crf, preset, target_resolution)
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()