"""
Simple Video Rotation Task Module
Simple task to rotate video files using ffmpeg
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

def get_rotation_options():
    """Get list of rotation options"""
    return {
        '1': {
            'name': 'Rotate 90° Clockwise',
            'filter': 'transpose=1',
            'description': 'Rotate video 90 degrees clockwise'
        },
        '2': {
            'name': 'Rotate 90° Counter-Clockwise',
            'filter': 'transpose=2',
            'description': 'Rotate video 90 degrees counter-clockwise'
        },
        '3': {
            'name': 'Rotate 180°',
            'filter': 'transpose=1,transpose=1',
            'description': 'Rotate video 180 degrees (upside down)'
        },
        '4': {
            'name': 'Flip Horizontal',
            'filter': 'hflip',
            'description': 'Flip video horizontally (mirror effect)'
        },
        '5': {
            'name': 'Flip Vertical',
            'filter': 'vflip',
            'description': 'Flip video vertically'
        },
        '6': {
            'name': 'Transpose (Flip + 90° CW)',
            'filter': 'transpose=0',
            'description': 'Flip vertically and rotate 90° clockwise'
        }
    }

def rotate_video(input_file, output_file, rotation_filter, copy_streams=True):
    """Rotate video using ffmpeg"""
    try:
        cmd = ['ffmpeg', '-i', input_file]
        
        if copy_streams:
            # Fast rotation using stream copy (for compatible rotations)
            cmd.extend(['-vf', rotation_filter, '-c:a', 'copy'])
        else:
            # Re-encode video and audio
            cmd.extend(['-vf', rotation_filter, '-c:v', 'libx264', '-c:a', 'aac'])
        
        # Add output file and overwrite flag
        cmd.extend([output_file, '-y'])
        
        print(f"[*] Rotating video...")
        print(f"Input: {input_file}")
        print(f"Output: {output_file}")
        print(f"Rotation: {rotation_filter}")
        print(f"Mode: {'Stream copy (fast)' if copy_streams else 'Re-encode (slower)'}")
        print("[*] Processing...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Video rotated successfully!")
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
                
                if copy_streams:
                    print("[+] Audio stream copied without re-encoding")
                else:
                    print("[+] Video and audio re-encoded")
        else:
            print("[!] Error during rotation:")
            print(result.stderr)
            if copy_streams:
                print("\n[!] Try using re-encode mode if stream copy fails.")
            
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
    
    print("[*] Simple Video Rotator")
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
            choice = input("\n> Enter the number of the video file to rotate: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_file = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select rotation option
    print("\n[*] Rotation options:")
    rotations = get_rotation_options()
    for key, value in rotations.items():
        print(f"{key}. {value['name']}")
        print(f"   {value['description']}")
    
    try:
        rotation_choice = input("\n> Enter rotation choice: ").strip()
        
        if rotation_choice in rotations:
            rotation_info = rotations[rotation_choice]
            rotation_filter = rotation_info['filter']
            rotation_name = rotation_info['name']
        else:
            print("[!] Invalid rotation choice")
            return
        
        # Select processing mode
        print("\n[*] Processing options:")
        print("1. Fast (Stream copy - preserves quality, faster)")
        print("2. Re-encode (Slower but more compatible)")
        
        mode_choice = input("> Enter processing mode (or press Enter for fast): ").strip()
        copy_streams = mode_choice != '2'
        
        # Generate output filename
        base_name, ext = os.path.splitext(selected_file)
        rotation_suffix = rotation_name.lower().replace(' ', '_').replace('°', 'deg')
        output_file = f"{base_name}_{rotation_suffix}{ext}"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform rotation
        rotate_video(selected_file, output_file, rotation_filter, copy_streams)
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()