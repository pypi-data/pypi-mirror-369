"""
Audio Replacement Task Module
Replace video audio tracks with external audio files using ffmpeg
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

def list_audio_files():
    """List all audio files in the current directory"""
    audio_extensions = ['*.mp3', '*.wav', '*.aac', '*.flac', '*.ogg', '*.m4a', '*.wma']
    audio_files = []
    
    for extension in audio_extensions:
        audio_files.extend(glob.glob(extension))
        audio_files.extend(glob.glob(extension.upper()))
    
    return sorted(audio_files)

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

def get_audio_duration(audio_file):
    """Get audio duration using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except:
        pass
    return None

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    if seconds is None:
        return "Unknown"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def replace_audio(video_file, audio_file, output_file, audio_handling='replace', audio_codec='aac'):
    """Replace video audio with external audio file using ffmpeg"""
    try:
        # Get durations for information
        video_duration = get_video_duration(video_file)
        audio_duration = get_audio_duration(audio_file)
        
        print(f"[*] Video duration: {format_duration(video_duration)}")
        print(f"[*] Audio duration: {format_duration(audio_duration)}")
        
        if video_duration and audio_duration:
            if audio_duration < video_duration:
                print(f"[!] Warning: Audio is shorter than video by {format_duration(video_duration - audio_duration)}")
            elif audio_duration > video_duration:
                print(f"[!] Warning: Audio is longer than video by {format_duration(audio_duration - video_duration)}")
        
        cmd = ['ffmpeg', '-i', video_file, '-i', audio_file]
        
        if audio_handling == 'replace':
            # Replace audio completely
            cmd.extend([
                '-c:v', 'copy',  # Copy video stream without re-encoding
                '-c:a', audio_codec,  # Encode audio with specified codec
                '-map', '0:v:0',  # Map video from first input
                '-map', '1:a:0',  # Map audio from second input
                '-shortest'  # Stop at shortest stream duration
            ])
        elif audio_handling == 'mix':
            # Mix original audio with new audio
            cmd.extend([
                '-filter_complex', '[0:a][1:a]amix=inputs=2[aout]',
                '-c:v', 'copy',  # Copy video stream
                '-c:a', audio_codec,  # Encode mixed audio
                '-map', '0:v:0',  # Map video from first input
                '-map', '[aout]',  # Map mixed audio
                '-shortest'
            ])
        elif audio_handling == 'overlay':
            # Overlay new audio on top of original (ducking original)
            cmd.extend([
                '-filter_complex', '[0:a]volume=0.3[bg];[bg][1:a]amix=inputs=2[aout]',
                '-c:v', 'copy',
                '-c:a', audio_codec,
                '-map', '0:v:0',
                '-map', '[aout]',
                '-shortest'
            ])
        
        # Add output file and overwrite flag
        cmd.extend([output_file, '-y'])
        
        print(f"[*] Replacing audio...")
        print(f"Video: {video_file}")
        print(f"Audio: {audio_file}")
        print(f"Output: {output_file}")
        print(f"Mode: {audio_handling}")
        print(f"Audio codec: {audio_codec}")
        print("[*] Processing...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[+] Audio replaced successfully!")
            print(f"Output file: {output_file}")
            
            # Show file size comparison
            if os.path.exists(output_file):
                def format_size(size):
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if size < 1024.0:
                            return f"{size:.1f} {unit}"
                        size /= 1024.0
                    return f"{size:.1f} TB"
                
                video_size = os.path.getsize(video_file)
                output_size = os.path.getsize(output_file)
                
                print(f"Original video: {format_size(video_size)}")
                print(f"Output video: {format_size(output_size)}")
                
                # Get output duration
                output_duration = get_video_duration(output_file)
                if output_duration:
                    print(f"Output duration: {format_duration(output_duration)}")
        else:
            print("[!] Error during audio replacement:")
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
    audio_files = list_audio_files()
    
    if not video_files:
        print("[!] No video files found in the current directory.")
        return
    
    if not audio_files:
        print("[!] No audio files found in the current directory.")
        return
    
    print("[*] Audio Replacement Tool")
    print("=" * 40)
    
    # Select video file
    if len(video_files) == 1:
        selected_video = video_files[0]
        print(f"Selected video: {selected_video}")
    else:
        print("Available video files:")
        for i, video_file in enumerate(video_files, 1):
            size = os.path.getsize(video_file) / (1024*1024)  # MB
            duration = get_video_duration(video_file)
            duration_str = format_duration(duration) if duration else "Unknown"
            print(f"{i}. {video_file} ({size:.1f}MB, {duration_str})")
        
        try:
            choice = input("\n> Enter the number of the video file: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(video_files):
                selected_video = video_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select audio file
    if len(audio_files) == 1:
        selected_audio = audio_files[0]
        print(f"Selected audio: {selected_audio}")
    else:
        print("\nAvailable audio files:")
        for i, audio_file in enumerate(audio_files, 1):
            size = os.path.getsize(audio_file) / (1024*1024)  # MB
            duration = get_audio_duration(audio_file)
            duration_str = format_duration(duration) if duration else "Unknown"
            print(f"{i}. {audio_file} ({size:.1f}MB, {duration_str})")
        
        try:
            choice = input("\n> Enter the number of the audio file: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(audio_files):
                selected_audio = audio_files[index]
            else:
                print("[!] Invalid selection")
                return
        except (ValueError, KeyboardInterrupt):
            print("[!] Invalid input")
            return
    
    # Select audio handling method
    print("\n[*] Audio handling options:")
    print("1. Replace (remove original audio completely)")
    print("2. Mix (blend original and new audio)")
    print("3. Overlay (new audio over quieter original)")
    
    try:
        handling_choice = input("\n> Enter handling choice (or press Enter for replace): ").strip()
        handling_map = {
            '1': 'replace',
            '2': 'mix',
            '3': 'overlay'
        }
        audio_handling = handling_map.get(handling_choice, 'replace')
        
        # Select audio codec
        print("\n[*] Audio codec options:")
        print("1. AAC (recommended, good compatibility)")
        print("2. MP3 (universal compatibility)")
        print("3. Copy (keep original audio codec if possible)")
        
        codec_choice = input("> Enter codec choice (or press Enter for AAC): ").strip()
        codec_map = {
            '1': 'aac',
            '2': 'mp3',
            '3': 'copy'
        }
        audio_codec = codec_map.get(codec_choice, 'aac')
        
        # Generate output filename
        base_name = os.path.splitext(selected_video)[0]
        audio_name = os.path.splitext(os.path.basename(selected_audio))[0]
        output_file = f"{base_name}_with_{audio_name}.mp4"
        
        # Check if output file exists
        if os.path.exists(output_file):
            overwrite = input(f"[!] {output_file} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("[!] Operation cancelled")
                return
        
        # Perform audio replacement
        success = replace_audio(selected_video, selected_audio, output_file, audio_handling, audio_codec)
        
        if not success:
            print("[!] Audio replacement failed")
        
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled")

if __name__ == "__main__":
    main()