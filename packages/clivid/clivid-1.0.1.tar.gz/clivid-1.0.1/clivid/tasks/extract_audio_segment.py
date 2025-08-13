"""
Time-based Audio Extraction Task Module
Extract audio from specific time segments of video files using ffmpeg
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

def parse_time_format(time_str):
    """Parse time string and validate format"""
    if not time_str:
        return None
    
    # Support formats: 10, 1:30, 01:30, 1:30:45, 01:30:45
    try:
        parts = time_str.split(':')
        if len(parts) == 1:
            # Just seconds - convert to proper HH:MM:SS format
            total_seconds = float(parts[0])
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        elif len(parts) == 2:
            # MM:SS - handle seconds >= 60
            minutes = int(parts[0])
            seconds = float(parts[1])
            
            # Convert excess seconds to minutes
            if seconds >= 60:
                extra_minutes = int(seconds // 60)
                minutes += extra_minutes
                seconds = seconds % 60
            
            hours = minutes // 60
            minutes = minutes % 60
            
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        elif len(parts) == 3:
            # HH:MM:SS - handle seconds >= 60 and minutes >= 60
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            
            # Convert excess seconds to minutes
            if seconds >= 60:
                extra_minutes = int(seconds // 60)
                minutes += extra_minutes
                seconds = seconds % 60
            
            # Convert excess minutes to hours
            if minutes >= 60:
                extra_hours = minutes // 60
                hours += extra_hours
                minutes = minutes % 60
            
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        else:
            raise ValueError("Invalid time format")
    except (ValueError, IndexError):
        raise ValueError(f"Invalid time format: {time_str}. Use formats like: 10, 1:30, or 1:30:45")

def extract_audio_segment(input_file, output_file, start_time, end_time=None, codec='mp3', quality='medium'):
    """Extract audio segment using ffmpeg"""
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
        
        # Parse and validate time formats
        start_time_formatted = parse_time_format(start_time)
        end_time_formatted = parse_time_format(end_time) if end_time else None
        
        # Build ffmpeg command with time seeking
        cmd = ['ffmpeg', '-ss', start_time_formatted, '-i', input_file]
        
        if end_time_formatted:
            cmd.extend(['-to', end_time_formatted])
        
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
        
        print(f"[*] Extracting audio segment...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Start: {start_time_formatted}")
        if end_time_formatted:
            print(f"End: {end_time_formatted}")
        print(f"Codec: {codec}")
        if codec not in ['pcm_s16le', 'flac']:
            print(f"Quality: {quality}")
        print("[*] Processing...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Audio segment extracted successfully!")
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
            return False
            
        return True
            
    except FileNotFoundError:
        print("[!] ffmpeg not found. Please install ffmpeg to use this feature.")
        return False
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def main():
    """Main function to execute the task"""
    video_files = list_video_files()
    
    if not video_files:
        print("[!] No video files found in the current directory.")
        return
    
    print("[*] Time-based Audio Segment Extractor")
    print("=" * 50)
    
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
            choice = input("\n> Enter the number of the video file: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Get time range
    print(f"\n[*] Time range extraction from: {selected_file}")
    print("Time formats supported: 10 (seconds), 1:30 (MM:SS), 1:30:45 (HH:MM:SS)")
    
    try:
        start_time = input("> Enter start time: ").strip()
        if not start_time:
            print("[!] Start time is required")
            return
        
        end_time = input("> Enter end time (or press Enter for until end): ").strip()
        if not end_time:
            end_time = None
        
        # Validate time formats
        try:
            parse_time_format(start_time)
            if end_time:
                parse_time_format(end_time)
        except ValueError as e:
            print(f"[!] {e}")
            return
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")
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
        start_suffix = start_time.replace(':', '_')
        end_suffix = f"_to_{end_time.replace(':', '_')}" if end_time else "_to_end"
        output_file = f"{base_name}_audio_{start_suffix}{end_suffix}{extension}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform extraction
        success = extract_audio_segment(selected_file, output_file, start_time, end_time, codec, quality)
        
        if not success:
            print("[!] Audio segment extraction failed")
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()