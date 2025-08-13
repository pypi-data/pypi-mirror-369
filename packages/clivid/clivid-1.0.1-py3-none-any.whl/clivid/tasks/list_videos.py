"""
List Videos Task Module
Simple task to list all video files in the current directory
"""

import os
import glob

def list_video_files():
    """List all video files in the current directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
    video_files = []
    
    for extension in video_extensions:
        video_files.extend(glob.glob(extension))
        video_files.extend(glob.glob(extension.upper()))
    
    return sorted(video_files)

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
    print("[*] Scanning for video files...")
    print("=" * 40)
    
    video_files = list_video_files()
    
    if not video_files:
        print("[!] No video files found in the current directory.")
        return
    
    print(f"[+] Found {len(video_files)} video file(s):")
    print("-" * 40)
    
    for i, video_file in enumerate(video_files, 1):
        size = get_file_size(video_file)
        print(f"{i:2d}. {video_file} ({size})")
    
    print("-" * 40)
    print(f"Total: {len(video_files)} video files")

if __name__ == "__main__":
    main()