"""
Simple Audio Extraction Task Module
Simple task to extract audio from video files using ffmpeg
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

def get_audio_formats():
    """Get list of supported audio formats"""
    return {
        '1': {'name': 'MP3 (Most compatible)', 'extension': '.mp3', 'codec': 'mp3'},
        '2': {'name': 'WAV (Uncompressed)', 'extension': '.wav', 'codec': 'pcm_s16le'},
        '3': {'name': 'AAC (High quality)', 'extension': '.aac', 'codec': 'aac'},
        '4': {'name': 'FLAC (Lossless)', 'extension': '.flac', 'codec': 'flac'},
        '5': {'name': 'OGG (Open source)', 'extension': '.ogg', 'codec': 'libvorbis'},
        '6': {'name': 'M4A (Apple format)', 'extension': '.m4a', 'codec': 'aac'}
    }

def extract_audio(input_file, output_file, codec, quality='medium'):
    """Extract audio using ffmpeg"""
    try:
        # Quality settings for different codecs
        quality_settings = {
            'mp3': {
                'fast': ['-b:a', '128k'],
                'medium': ['-b:a', '192k'],
                'high': ['-b:a', '320k']
            },
            'aac': {
                'fast': ['-b:a', '128k'],
                'medium': ['-b:a', '192k'],
                'high': ['-b:a', '256k']
            },
            'libvorbis': {
                'fast': ['-q:a', '3'],
                'medium': ['-q:a', '6'],
                'high': ['-q:a', '9']
            },
            'default': {
                'fast': ['-b:a', '128k'],
                'medium': ['-b:a', '192k'],
                'high': ['-b:a', '256k']
            }
        }
        
        cmd = ['ffmpeg', '-i', input_file]
        
        # Add codec
        cmd.extend(['-c:a', codec])
        
        # Add quality settings (except for lossless formats)
        if codec not in ['pcm_s16le', 'flac']:
            codec_quality = quality_settings.get(codec, quality_settings['default'])
            cmd.extend(codec_quality.get(quality, codec_quality['medium']))
        
        # Disable video stream
        cmd.extend(['-vn'])
        
        # Add output file and overwrite flag
        cmd.extend([output_file, '-y'])
        
        print(f"[*] Extracting audio...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Codec: {codec}")
        if codec not in ['pcm_s16le', 'flac']:
            print(f"Quality: {quality}")
        print("[*] Processing...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Audio extracted successfully!")
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
                
                # Get audio duration if possible
                try:
                    duration_cmd = [
                        'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1', output_file
                    ]
                    duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
                    if duration_result.returncode == 0:
                        duration = float(duration_result.stdout.strip())
                        minutes, seconds = divmod(int(duration), 60)
                        print(f"Duration: {minutes}:{seconds:02d}")
                except:
                    pass
        else:
            print("[!] Error during extraction:")
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
    
    print("[*] Simple Audio Extractor")
    print("=" * 40)
    
    # Select video file
    if len(video_files) == 1:
        selected_file = video_files[0]
        print(f"Selected file: {selected_file}")
    else:
        print("Available video files:")
        for i, video_file in enumerate(video_files, 1):
            size = os.path.getsize(video_file) / (1024*1024)  # MB
            print(f"{i}. {video_file} ({size:.1f}MB)")
        
        try:
            choice = input("\n> Enter the number of the video file to extract audio from: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select audio format
    print("\n[*] Available audio formats:")
    formats = get_audio_formats()
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
        
        # Select quality (skip for lossless formats)
        quality = 'medium'
        if codec not in ['pcm_s16le', 'flac']:
            print("\n[*] Quality options:")
            print("1. Fast (lower quality, smaller file)")
            print("2. Medium (balanced quality and size)")
            print("3. High (higher quality, larger file)")
            
            quality_choice = input("> Enter quality choice (or press Enter for medium): ").strip()
            quality_map = {'1': 'fast', '2': 'medium', '3': 'high'}
            quality = quality_map.get(quality_choice, 'medium')
        
        # Generate output filename
        base_name = os.path.splitext(selected_file)[0]
        output_file = f"{base_name}_audio{extension}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform extraction
        extract_audio(selected_file, output_file, codec, quality)
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()