"""
Video Info Task Module
Simple task to get basic information about a video file
"""

import os
import glob
import subprocess
import json

def list_video_files():
    """List all video files in the current directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
    video_files = []
    
    for extension in video_extensions:
        video_files.extend(glob.glob(extension))
        video_files.extend(glob.glob(extension.upper()))
    
    return sorted(video_files)

def get_video_info_ffprobe(video_file):
    """Get video information using ffprobe"""
    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            '-show_streams', 
            video_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return None
            
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        return None

def get_basic_info(video_file):
    """Get basic file information"""
    if not os.path.exists(video_file):
        return None
        
    stat = os.stat(video_file)
    size = stat.st_size
    
    # Convert size to human readable format
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            size_str = f"{size:.1f} {unit}"
            break
        size /= 1024.0
    else:
        size_str = f"{size:.1f} TB"
    
    return {
        'filename': video_file,
        'size': size_str,
        'size_bytes': stat.st_size
    }

def display_video_info(video_file):
    """Display comprehensive video information"""
    print(f"[*] Video Information: {video_file}")
    print("=" * 50)
    
    # Basic file info
    basic_info = get_basic_info(video_file)
    if not basic_info:
        print("[!] File not found or inaccessible")
        return
    
    print(f"File: {basic_info['filename']}")
    print(f"Size: {basic_info['size']}")
    
    # Try to get detailed info with ffprobe
    detailed_info = get_video_info_ffprobe(video_file)
    
    if detailed_info:
        format_info = detailed_info.get('format', {})
        
        if format_info:
            duration = float(format_info.get('duration', 0))
            bitrate = format_info.get('bit_rate', 'Unknown')
            format_name = format_info.get('format_name', 'Unknown')
            
            print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            print(f"Format: {format_name}")
            if bitrate != 'Unknown':
                print(f"Bitrate: {int(bitrate)//1000} kbps")
        
        # Video stream info
        video_streams = [s for s in detailed_info.get('streams', []) if s.get('codec_type') == 'video']
        if video_streams:
            video_stream = video_streams[0]
            width = video_stream.get('width', 'Unknown')
            height = video_stream.get('height', 'Unknown')
            codec = video_stream.get('codec_name', 'Unknown')
            fps = video_stream.get('r_frame_rate', '0/1')
            
            print(f"Resolution: {width}x{height}")
            print(f"Video Codec: {codec}")
            if '/' in str(fps):
                try:
                    num, den = map(int, fps.split('/'))
                    if den != 0:
                        fps_value = num / den
                        print(f"Frame Rate: {fps_value:.2f} fps")
                except:
                    pass
        
        # Audio stream info
        audio_streams = [s for s in detailed_info.get('streams', []) if s.get('codec_type') == 'audio']
        if audio_streams:
            audio_stream = audio_streams[0]
            codec = audio_stream.get('codec_name', 'Unknown')
            sample_rate = audio_stream.get('sample_rate', 'Unknown')
            channels = audio_stream.get('channels', 'Unknown')
            
            print(f"Audio Codec: {codec}")
            print(f"Sample Rate: {sample_rate} Hz")
            print(f"Channels: {channels}")
    else:
        print("[!] Detailed video information not available (ffprobe not found or failed)")
    
    print("=" * 50)

def main():
    """Main function to execute the task"""
    video_files = list_video_files()
    
    if not video_files:
        print("[!] No video files found in the current directory.")
        return
    
    if len(video_files) == 1:
        display_video_info(video_files[0])
    else:
        print("[*] Multiple video files found:")
        for i, video_file in enumerate(video_files, 1):
            print(f"{i}. {video_file}")
        
        try:
            choice = input("\n> Enter the number of the video file to analyze (or press Enter for first): ").strip()
            
            if not choice:
                index = 0
            else:
                index = int(choice) - 1
                
            if 0 <= index < len(video_files):
                print()
                display_video_info(video_files[index])
            else:
                print("[!] Invalid selection")
                
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")

if __name__ == "__main__":
    main()