"""
List Videos and Audio Files Task Module
Simple task to list all video and audio files in the current directory
"""

import os
import glob

def list_video_files():
    """List all video files in the current directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
    video_files = []
    
    for extension in video_extensions:
        video_files.extend(glob.glob(extension))
        # Don't add uppercase versions as they're already covered by glob
    
    return sorted(video_files)

def list_audio_files():
    """List all audio files in the current directory"""
    audio_extensions = ['*.mp3', '*.wav', '*.aac', '*.flac', '*.ogg', '*.m4a', '*.wma']
    audio_files = []
    
    for extension in audio_extensions:
        audio_files.extend(glob.glob(extension))
        # Don't add uppercase versions as they're already covered by glob
    
    return sorted(audio_files)

def get_file_size(filepath):
    """Get file size in human readable format"""
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def main():
    """Main function to execute the task"""
    print("[*] Scanning for video and audio files...")
    print("=" * 50)
    
    video_files = list_video_files()
    audio_files = list_audio_files()
    
    if not video_files and not audio_files:
        print("[!] No video or audio files found in the current directory.")
        return
    
    if video_files:
        print(f"[+] Found {len(video_files)} video file(s):")
        print("-" * 40)
        
        for i, video_file in enumerate(video_files, 1):
            size = get_file_size(video_file)
            print(f"{i:2d}. {video_file} ({size})")
        
        print("-" * 40)
        print(f"Total: {len(video_files)} video files")
    
    if audio_files:
        print(f"\n[+] Found {len(audio_files)} audio file(s):")
        print("-" * 40)
        
        for i, audio_file in enumerate(audio_files, 1):
            size = get_file_size(audio_file)
            print(f"{i:2d}. {audio_file} ({size})")
        
        print("-" * 40)
        print(f"Total: {len(audio_files)} audio files")
    
    print(f"\nGrand Total: {len(video_files) + len(audio_files)} files")

if __name__ == "__main__":
    main()