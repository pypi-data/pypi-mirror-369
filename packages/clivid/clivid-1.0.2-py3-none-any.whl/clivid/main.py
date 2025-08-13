"""
AI Video Chat Interface
Natural language chat interface for video operations using Mistral API
"""

import sys
import os
import subprocess
import json
import requests
import glob
import stat
import getpass
from datetime import datetime
from pathlib import Path
import glob
from datetime import datetime
import getpass
from pathlib import Path

class AIVideoChatInterface:
    def __init__(self):
        self.api_key = None
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.config_dir = Path.home() / ".clivid"
        self.config_file = self.config_dir / "config.json"
        
        # Get the correct path to tasks directory
        self.tasks_dir = self._get_tasks_directory()
        
        # Load or setup API key
        self._setup_api_key()
        
        # Conversation history
        self.conversation_history = []
        self.max_history = 10  # Keep last 10 exchanges
        
        # Recent file tracking for multi-step operations
        self.recent_files = {
            "created": [],  # Files created in recent operations
            "processed": [],  # Files that were input to recent operations
            "last_audio": None,  # Last audio file created/processed
            "last_video": None,  # Last video file created/processed
        }
        self.max_recent_files = 5  # Keep track of last 5 files per category
        
        # Available task modules
        self.available_tasks = {
            "list_videos": "List all video files in the directory",
            "video_info": "Get detailed information about a video file", 
            "simple_trim": "Trim/cut a video file by time range",
            "simple_resize": "Resize/scale a video to different resolution",
            "convert_video": "Convert video between different formats (MP4, AVI, MOV, etc.)",
            "merge_videos": "Merge/combine multiple video files into one",
            "extract_audio": "Extract audio from video files in various formats",
            "extract_audio_segment": "Extract audio from specific time segments of video files",
            "replace_audio": "Replace or mix video audio with external audio files",
            "compress_video": "Compress video to reduce file size",
            "rotate_video": "Rotate or flip video files",
            "split_video": "Split a video into multiple parts"
        }
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _get_tasks_directory(self):
        """Get the correct path to the tasks directory"""
        # First, try to find tasks relative to this file (for development)
        current_dir = Path(__file__).parent
        tasks_path = current_dir / "tasks"
        
        if tasks_path.exists():
            return str(tasks_path)
            
        # If not found, try relative to cwd (backward compatibility)
        cwd_tasks = Path.cwd() / "tasks"
        if cwd_tasks.exists():
            return str(cwd_tasks)
            
        # If still not found, try to find within installed package
        try:
            import clivid.tasks
            return str(Path(clivid.tasks.__file__).parent)
        except ImportError:
            pass
            
        # Last resort: return the path relative to this file
        return str(current_dir / "tasks")
        
    def _import_task_module(self, module_name):
        """Safely import a task module"""
        try:
            # Try to import from clivid.tasks first (installed package)
            module = __import__(f'clivid.tasks.{module_name}', fromlist=[module_name])
            return module
        except ImportError:
            try:
                # Fallback to adding tasks directory to path (development)
                if self.tasks_dir not in sys.path:
                    sys.path.append(self.tasks_dir)
                module = __import__(module_name)
                return module
            except ImportError as e:
                print(f"[!] Failed to import task module {module_name}: {e}")
                return None
                
    def get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f}{unit}"
                size /= 1024.0
            return f"{size:.1f}TB"
        except:
            return "Unknown size"
        
    def _setup_api_key(self):
        """Setup and load API key from config file or prompt user"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(exist_ok=True)
            
            # Try to load existing API key
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('mistral_api_key')
                    
                if self.api_key and self._validate_api_key(self.api_key):
                    print(f"[+] Loaded saved API key from {self.config_file}")
                    return
                else:
                    print(f"[!] Saved API key is invalid or missing")
            
            # No valid API key found, prompt user
            self._prompt_for_api_key()
            
        except Exception as e:
            print(f"[!] Error setting up API key: {e}")
            self._prompt_for_api_key()
    
    def _validate_api_key(self, api_key, silent=False):
        """Validate API key by making a test request"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                if not silent:
                    print("[+] API key validated successfully!")
                return True
            elif response.status_code == 401:
                if not silent:
                    print("[!] Invalid API key - authentication failed")
                return False
            else:
                if not silent:
                    print(f"[!] API validation failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            if not silent:
                print(f"[!] Error validating API key: {e}")
            return False
    
    def _prompt_for_api_key(self):
        """Prompt user for API key and save it"""
        print("\n" + "=" * 60)
        print("CLIVID - CLI Video Assistant - API KEY SETUP")
        print("=" * 60)
        print("Welcome! To use Clivid, you need a Mistral API key.")
        print("\nHow to get your Mistral API key:")
        print("1. Go to https://console.mistral.ai/")
        print("2. Sign up or log in to your account")
        print("3. Navigate to 'API Keys' section")
        print("4. Create a new API key")
        print("5. Copy the key and paste it below")
        print("\nYour API key will be saved securely on your local machine.")
        print("=" * 60)
        
        while True:
            try:
                api_key = getpass.getpass("Enter your Mistral API key (input will be hidden): ").strip()
                
                if not api_key:
                    print("[!] API key cannot be empty. Please try again.")
                    continue
                
                print("\n[*] Validating API key...")
                
                if self._validate_api_key(api_key):
                    # Save the API key
                    self._save_api_key(api_key)
                    self.api_key = api_key
                    print("[+] API key saved successfully!")
                    break
                else:
                    print("[!] Invalid API key. Please check your key and try again.")
                    retry = input("Would you like to try again? (y/n): ").strip().lower()
                    if retry not in ['y', 'yes']:
                        print("Exiting application. Please restart when you have a valid API key.")
                        sys.exit(1)
                        
            except KeyboardInterrupt:
                print("\n\nSetup cancelled. Exiting application.")
                sys.exit(1)
            except Exception as e:
                print(f"[!] Error during setup: {e}")
                retry = input("Would you like to try again? (y/n): ").strip().lower()
                if retry not in ['y', 'yes']:
                    sys.exit(1)
    
    def _save_api_key(self, api_key):
        """Save API key to config file"""
        try:
            config = {'mistral_api_key': api_key}
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Set restrictive permissions on config file (Windows compatible)
            try:
                os.chmod(self.config_file, 0o600)
            except:
                pass  # Windows may not support chmod
                
        except Exception as e:
            print(f"[!] Error saving API key: {e}")
            
    def reset_api_key(self):
        """Reset API key - useful for switching accounts"""
        try:
            if self.config_file.exists():
                os.remove(self.config_file)
            print("[+] API key configuration reset.")
            self._prompt_for_api_key()
        except Exception as e:
            print(f"[!] Error resetting API key: {e}")
        
    def add_to_history(self, user_message, ai_response, action_taken=None):
        """Add exchange to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "user": user_message,
            "ai_response": ai_response,
            "action": action_taken
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_context_for_ai(self):
        """Get recent conversation context for AI"""
        context = ""
        
        # Add recent file context
        if self.recent_files["created"] or self.recent_files["last_audio"] or self.recent_files["last_video"]:
            context += "\n\nRecent file operations:"
            
            # Recently created files
            if self.recent_files["created"]:
                context += "\nFiles just created:"
                for file_info in self.recent_files["created"][:3]:  # Last 3 created files
                    context += f"\n- {file_info['name']} ({file_info['type']}) at {file_info['timestamp']}"
            
            # Last audio and video files
            if self.recent_files["last_audio"]:
                context += f"\nLast audio file: {self.recent_files['last_audio']['name']}"
            if self.recent_files["last_video"]:
                context += f"\nLast video file: {self.recent_files['last_video']['name']}"
        
        # Add conversation history
        if self.conversation_history:
            context += "\n\nRecent conversation context:"
            for exchange in self.conversation_history[-3:]:  # Last 3 exchanges
                context += f"\nUser: {exchange['user']}"
                if exchange['action']:
                    context += f"\nAction taken: {exchange['action']}"
        
        return context
        
    def get_video_files(self):
        """Get list of available video files"""
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
        video_files = []
        
        for extension in video_extensions:
            video_files.extend(glob.glob(extension))
            video_files.extend(glob.glob(extension.upper()))
        
        # Remove duplicates that can occur on case-insensitive filesystems
        return sorted(list(set(video_files)))
        
    def call_mistral_api(self, user_message, video_files_list):
        """Call Mistral API to understand user intent and extract parameters"""
        
        video_files_str = ", ".join(video_files_list) if video_files_list else "No video files found"
        context = self.get_context_for_ai()
        
        system_prompt = f"""You are an AI assistant that helps with video file operations. 

Available video files: {video_files_str}

Available operations:
- list_videos: List all video files in directory (no parameters needed)
- video_info: Get information about video files (needs: video_file)
- simple_trim: Trim/cut video files (needs: video_file, start_time, end_time optional)
- simple_resize: Resize/scale video files (needs: video_file, resolution like "1280x720" or preset like "720p")
- convert_video: Convert video formats (needs: video_file, target_format like "mp4", "avi", "mov", quality optional)
- merge_videos: Merge multiple videos (needs: video_files as array, merge_method optional)
- extract_audio: Extract audio from video (needs: video_file, audio_format like "mp3", "wav", "aac")
- extract_audio_segment: Extract audio from specific time segments (needs: video_file, start_time, end_time optional, audio_format, quality optional)
- replace_audio: Replace video audio with external audio (needs: video_file, audio_file, audio_handling like "replace", "mix", "overlay", audio_codec optional)
- compress_video: Compress video to reduce size (needs: video_file, compression_level like "light", "medium", "high")
- rotate_video: Rotate or flip video (needs: video_file, rotation like "90_cw", "90_ccw", "180", "flip_h", "flip_v")
- split_video: Split video into parts (needs: video_file, split_method like "parts", "duration", "size", split_value)

IMPORTANT - FILE REFERENCE HANDLING:
When user refers to files like "extracted audio", "new audio", "created file", "last file", "that audio", etc., 
they are referring to files created in recent operations. Use these exact phrases as the parameter values:
- "extracted_audio" for recently extracted audio files
- "new_audio" for newly created audio files  
- "last_video" for recently created video files
- "created_file" for any recently created file
- "audio_segment" for extracted audio segments

For multi-step operations, recognize when user wants to use output from previous step.

Examples:
- "extract audio from video.mp4 then use it in other.mp4" → first extract_audio_segment, then replace_audio with audio_file="extracted_audio"
- "use the new audio file" → audio_file="new_audio"
- "replace with extracted audio" → audio_file="extracted_audio"
- "use that audio segment" → audio_file="audio_segment"

Analyze the user's message and respond with ONLY a JSON object in this format:
{{
    "intent": "operation_name",
    "confidence": 0.0-1.0,
    "parameters": {{
        "video_file": "filename.mp4 or null",
        "video_files": ["array of filenames for merge operations"],
        "audio_file": "filename.mp3/.wav/.aac or file reference like 'extracted_audio', 'new_audio' or null",
        "start_time": "MM:SS or HH:MM:SS or null",
        "end_time": "MM:SS or HH:MM:SS or null", 
        "resolution": "WIDTHxHEIGHT or preset like 720p or null",
        "target_format": "mp4, avi, mov, mkv, wmv, webm, flv or null",
        "audio_format": "mp3, wav, aac, flac, ogg, m4a or null",
        "audio_handling": "replace, mix, overlay or null",
        "audio_codec": "aac, mp3, copy or null",
        "compression_level": "light, medium, high, maximum or null",
        "rotation": "90_cw, 90_ccw, 180, flip_h, flip_v or null",
        "split_method": "parts, duration, size or null",
        "split_value": "number for parts/minutes/MB or null",
        "quality": "fast, medium, high or null",
        "merge_method": "concat, filter or null"
    }},
    "multi_step_operations": [
        {{
            "step": 1,
            "intent": "operation_name",
            "parameters": {{
                "video_file": "filename.mp4 or null",
                "video_files": ["array of filenames for merge operations"],
                "audio_file": "filename.mp3/.wav/.aac or file reference like 'extracted_audio', 'new_audio' or null",
                "start_time": "MM:SS or HH:MM:SS or null",
                "end_time": "MM:SS or HH:MM:SS or null", 
                "resolution": "WIDTHxHEIGHT or preset like 720p or null",
                "target_format": "mp4, avi, mov, mkv, wmv, webm, flv or null",
                "audio_format": "mp3, wav, aac, flac, ogg, m4a or null",
                "audio_handling": "replace, mix, overlay or null",
                "audio_codec": "aac, mp3, copy or null",
                "compression_level": "light, medium, high, maximum or null",
                "rotation": "90_cw, 90_ccw, 180, flip_h, flip_v or null",
                "split_method": "parts, duration, size or null",
                "split_value": "number for parts/minutes/MB or null",
                "quality": "fast, medium, high or null",
                "merge_method": "concat, filter or null"
            }}
        }},
        {{
            "step": 2, 
            "intent": "operation_name",
            "parameters": {{
                "video_file": "filename.mp4 or null",
                "video_files": ["array of filenames for merge operations"],
                "audio_file": "filename.mp3/.wav/.aac or file reference like 'extracted_audio', 'new_audio' or null",
                "start_time": "MM:SS or HH:MM:SS or null",
                "end_time": "MM:SS or HH:MM:SS or null", 
                "resolution": "WIDTHxHEIGHT or preset like 720p or null",
                "target_format": "mp4, avi, mov, mkv, wmv, webm, flv or null",
                "audio_format": "mp3, wav, aac, flac, ogg, m4a or null",
                "audio_handling": "replace, mix, overlay or null",
                "audio_codec": "aac, mp3, copy or null",
                "compression_level": "light, medium, high, maximum or null",
                "rotation": "90_cw, 90_ccw, 180, flip_h, flip_v or null",
                "split_method": "parts, duration, size or null",
                "split_value": "number for parts/minutes/MB or null",
                "quality": "fast, medium, high or null",
                "merge_method": "concat, filter or null"
            }}
        }}
    ],
    "explanation": "brief explanation of what you understood",
    "needs_clarification": true/false,
    "missing_params": ["list of missing required parameters"]
}}

Rules:
- Extract video filenames from user message if mentioned
- Extract time ranges like "from 10 seconds to 30 seconds" or "trim from 1:30 to 2:45"
- Extract resolutions like "720p", "1080p", "1280x720"
- Extract formats like "mp4", "avi", "convert to mov"
- Extract audio formats like "mp3", "extract as wav"
- Extract compression levels like "compress heavily", "light compression"
- Extract rotation instructions like "rotate 90 degrees", "flip horizontally"
- Extract split instructions like "split into 3 parts", "split every 5 minutes", "split into 100MB parts"
- For merge operations, extract multiple video files
- If the user wants to exit/quit, use intent: "exit"
- If unclear or missing required params, use needs_clarification: true
- If video file not specified but required, ask for clarification
- Use conversation context to understand references like "that video", "the same file", "it", etc.
- If user refers to previous operations, use context to understand what they mean

MULTI-STEP OPERATION DETECTION:
- If user says "then", "and then", "after that", "use that to", "use it in", etc., this indicates multiple operations
- For multi-step operations, use "multi_step_operations" array instead of single intent
- Common patterns:
  * "extract audio from X then use it in Y" = extract_audio_segment + replace_audio
  * "extract X to Y seconds then replace audio in Z" = extract_audio_segment + replace_audio  
  * "get audio segment then mix with video" = extract_audio_segment + replace_audio
- For multi-step, set main intent to "multi_step" and confidence to 0.9
- Each step should have complete parameters, use "extracted_audio" for file references between steps"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "mistral-small-latest",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.1,
                "max_tokens": 300
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                # Extract JSON from response
                try:
                    start = ai_response.find('{')
                    end = ai_response.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = ai_response[start:end]
                        return json.loads(json_str)
                except:
                    pass
                    
                return {
                    "intent": "clarify",
                    "confidence": 0.0,
                    "parameters": {},
                    "explanation": "Could not parse AI response",
                    "needs_clarification": True,
                    "missing_params": []
                }
            else:
                return {
                    "intent": "error",
                    "confidence": 0.0,
                    "parameters": {},
                    "explanation": f"API error: {response.status_code}",
                    "needs_clarification": True,
                    "missing_params": []
                }
                
        except Exception as e:
            return {
                "intent": "error", 
                "confidence": 0.0,
                "parameters": {},
                "explanation": f"Connection error: {str(e)}",
                "needs_clarification": True,
                "missing_params": []
            }
    
    def execute_task_with_params(self, intent, parameters):
        """Execute task with extracted parameters"""
        
        # Handle multi-step operations
        if intent == "multi_step":
            return self.execute_multi_step_operations(parameters)
        
        if intent == "list_videos":
            return self.execute_list_videos()
            
        elif intent == "video_info":
            video_file = parameters.get("video_file")
            return self.execute_video_info(video_file)
            
        elif intent == "simple_trim":
            video_file = parameters.get("video_file")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            return self.execute_trim(video_file, start_time, end_time)
            
        elif intent == "simple_resize":
            video_file = parameters.get("video_file")
            resolution = parameters.get("resolution")
            return self.execute_resize(video_file, resolution)
            
        elif intent == "convert_video":
            video_file = parameters.get("video_file")
            target_format = parameters.get("target_format")
            quality = parameters.get("quality")
            return self.execute_convert_video(video_file, target_format, quality)
            
        elif intent == "merge_videos":
            video_files = parameters.get("video_files", [])
            merge_method = parameters.get("merge_method")
            return self.execute_merge_videos(video_files, merge_method)
            
        elif intent == "extract_audio":
            video_file = parameters.get("video_file")
            audio_format = parameters.get("audio_format")
            quality = parameters.get("quality")
            return self.execute_extract_audio(video_file, audio_format, quality)
            
        elif intent == "extract_audio_segment":
            video_file = parameters.get("video_file")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            audio_format = parameters.get("audio_format")
            quality = parameters.get("quality")
            return self.execute_extract_audio_segment(video_file, start_time, end_time, audio_format, quality)
            
        elif intent == "replace_audio":
            video_file = parameters.get("video_file")
            audio_file = parameters.get("audio_file")
            audio_handling = parameters.get("audio_handling")
            audio_codec = parameters.get("audio_codec")
            return self.execute_replace_audio(video_file, audio_file, audio_handling, audio_codec)
            
        elif intent == "compress_video":
            video_file = parameters.get("video_file")
            compression_level = parameters.get("compression_level")
            return self.execute_compress_video(video_file, compression_level)
            
        elif intent == "rotate_video":
            video_file = parameters.get("video_file")
            rotation = parameters.get("rotation")
            return self.execute_rotate_video(video_file, rotation)
            
        elif intent == "split_video":
            video_file = parameters.get("video_file")
            split_method = parameters.get("split_method")
            split_value = parameters.get("split_value")
            return self.execute_split_video(video_file, split_method, split_value)
            
        else:
            print(f"[!] Unknown task: {intent}")
            return f"Unknown task: {intent}"
            
    def execute_list_videos(self):
        """Execute list videos task"""
        try:
            # Import the list_videos module
            list_videos_module = self._import_task_module('list_videos')
            if not list_videos_module:
                return "Error: Could not import list_videos module"
            
            # Get video files and display them
            video_files = self.get_video_files()
            
            if not video_files:
                print("[*] No video files found in current directory")
                return "No video files found"
            
            print(f"[*] I found {len(video_files)} video file(s) in your directory:")
            for i, video_file in enumerate(video_files, 1):
                file_size = self.get_file_size(video_file)
                print(f"  {i}. {video_file} ({file_size})")
            
            return "Listed all video files"
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
            
    def execute_video_info(self, video_file):
        """Execute video info with specific file"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return
            
        # If no specific file mentioned, ask user to choose
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    # Check if it matches a filename
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found or not specified")
            return "Video file not found"
            
        # Call video_info module directly with the file
        try:
            # Import and use the video_info module directly
            video_info_module = self._import_task_module('video_info')
            if not video_info_module:
                return "Error: Could not import video_info module"
            video_info_module.display_video_info(video_file)
            return f"Displayed info for {video_file}"
        except Exception as e:
            print(f"[!] Error getting video info: {e}")
            return f"Error getting video info: {e}"
            
    def execute_trim(self, video_file, start_time, end_time):
        """Execute trim with parameters"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to trim? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing start time
        if not start_time:
            start_time = input("> Start time (MM:SS or HH:MM:SS): ").strip()
            
        # End time is optional
        if not end_time:
            end_time_input = input("> End time (optional, press Enter to trim till end): ").strip()
            if end_time_input:
                end_time = end_time_input
                
        print(f"[*] Trimming {video_file} from {start_time}" + (f" to {end_time}" if end_time else " to end"))
        
        # Execute trim operation
        try:
            import os
            base_name, ext = os.path.splitext(video_file)
            output_file = f"{base_name}_trimmed{ext}"
            
            # Place -ss before input for faster seeking and better performance
            cmd = ['ffmpeg', '-ss', start_time, '-i', video_file]
            if end_time:
                cmd.extend(['-to', end_time])
            # Add proper timestamp handling to avoid playback issues
            cmd.extend(['-c', 'copy', '-avoid_negative_ts', 'make_zero', output_file, '-y'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"[+] Video trimmed successfully: {output_file}")
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="video", operation="created")
                return f"Trimmed {video_file} to {output_file}"
            else:
                print(f"[!] Error during trimming: {result.stderr}")
                return f"Error trimming video: {result.stderr}"
                
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
            
    def execute_resize(self, video_file, resolution):
        """Execute resize with parameters"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to resize? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing resolution
        if not resolution:
            print("Common resolutions:")
            print("  1. 720p (1280x720)")
            print("  2. 1080p (1920x1080)")
            print("  3. 480p (854x480)")
            resolution_input = input("> Resolution (e.g., 720p, 1280x720): ").strip()
            if resolution_input:
                resolution = resolution_input
                
        # Convert presets to actual resolution
        preset_map = {
            "480p": "854x480",
            "720p": "1280x720", 
            "1080p": "1920x1080",
            "1440p": "2560x1440",
            "4k": "3840x2160"
        }
        
        if resolution.lower() in preset_map:
            resolution = preset_map[resolution.lower()]
            
        print(f"[*] Resizing {video_file} to {resolution}")
        
        # Execute resize operation
        try:
            import os
            base_name, ext = os.path.splitext(video_file)
            output_file = f"{base_name}_{resolution.replace('x', 'x')}{ext}"
            
            cmd = ['ffmpeg', '-i', video_file, '-vf', f'scale={resolution}', '-preset', 'medium', '-crf', '23', output_file, '-y']
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"[+] Video resized successfully: {output_file}")
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="video", operation="created")
                return f"Resized {video_file} to {output_file}"
            else:
                print(f"[!] Error during resizing: {result.stderr}")
                return f"Error resizing video: {result.stderr}"
                
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_convert_video(self, video_file, target_format, quality):
        """Execute video conversion"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to convert? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing format
        if not target_format:
            print("Available formats:")
            print("  1. MP4  2. AVI  3. MOV  4. MKV  5. WMV  6. WebM")
            format_input = input("> Target format (e.g., mp4, avi, mov): ").strip().lower()
            if format_input:
                target_format = format_input
                
        if not target_format:
            print("[!] Target format required")
            return "Target format required"
            
        # Set default quality if not specified
        if not quality:
            quality = 'medium'
            
        print(f"[*] Converting {video_file} to {target_format}")
        
        try:
            # Convert format to codec mapping
            codec_map = {
                'mp4': 'libx264',
                'avi': 'libxvid', 
                'mov': 'libx264',
                'mkv': 'libx264',
                'wmv': 'wmv2',
                'webm': 'libvpx-vp9',
                'flv': 'libx264'
            }
            
            # Quality settings
            quality_settings = {
                'fast': ['-preset', 'fast', '-crf', '28'],
                'medium': ['-preset', 'medium', '-crf', '23'],
                'high': ['-preset', 'slow', '-crf', '18']
            }
            
            codec = codec_map.get(target_format.lower(), 'libx264')
            base_name = os.path.splitext(video_file)[0]
            output_file = f"{base_name}_converted.{target_format}"
            
            cmd = ['ffmpeg', '-i', video_file, '-c:v', codec]
            cmd.extend(quality_settings.get(quality, quality_settings['medium']))
            cmd.extend(['-c:a', 'copy', output_file, '-y'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"[+] Video converted successfully: {output_file}")
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="video", operation="created")
                return f"Converted {video_file} to {target_format}"
            else:
                print(f"[!] Error during conversion: {result.stderr}")
                return f"Error converting video: {result.stderr}"
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_merge_videos(self, video_files, merge_method):
        """Execute video merging"""
        all_video_files = self.get_video_files()
        
        if not all_video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        if len(all_video_files) < 2:
            print("[!] Need at least 2 video files to merge")
            return "Need at least 2 video files to merge"
            
        # Handle missing video files selection
        selected_files = []
        if not video_files or len(video_files) < 2:
            print("Available video files:")
            for i, vf in enumerate(all_video_files, 1):
                print(f"  {i}. {vf}")
            try:
                selection = input("\n> Select videos to merge (e.g., 1,2,3 or 1-3 or all): ").strip()
                
                if selection.lower() == 'all':
                    selected_files = all_video_files
                elif '-' in selection and ',' not in selection:
                    # Range selection (e.g., 1-3)
                    start, end = map(int, selection.split('-'))
                    for i in range(start-1, min(end, len(all_video_files))):
                        if 0 <= i < len(all_video_files):
                            selected_files.append(all_video_files[i])
                else:
                    # Individual selection (e.g., 1,2,3)
                    indices = [int(x.strip())-1 for x in selection.split(',')]
                    for idx in indices:
                        if 0 <= idx < len(all_video_files):
                            selected_files.append(all_video_files[idx])
            except:
                print("[!] Invalid selection")
                return "Invalid selection"
        else:
            selected_files = video_files
            
        if len(selected_files) < 2:
            print("[!] Please select at least 2 videos to merge")
            return "Need at least 2 videos to merge"
        
        if not merge_method:
            merge_method = 'concat'  # Default method
            
        print(f"[*] Merging {len(selected_files)} videos using {merge_method} method...")
        for i, vf in enumerate(selected_files, 1):
            print(f"  {i}. {vf}")
        
        try:
            base_name = os.path.splitext(selected_files[0])[0]
            output_file = f"{base_name}_merged.mp4"
            
            if merge_method.lower() == 'filter':
                # Method 2: Using filter_complex (handles different formats/resolutions)
                cmd = ['ffmpeg']
                
                # Add input files
                for video_file in selected_files:
                    cmd.extend(['-i', video_file])
                
                # Create filter_complex for concatenation
                filter_parts = []
                for i in range(len(selected_files)):
                    filter_parts.append(f'[{i}:v][{i}:a]')
                
                filter_complex = ''.join(filter_parts) + f'concat=n={len(selected_files)}:v=1:a=1[outv][outa]'
                
                cmd.extend([
                    '-filter_complex', filter_complex,
                    '-map', '[outv]', '-map', '[outa]',
                    output_file, '-y'
                ])
                
            else:  # concat method (default)
                # Method 1: Simple concatenation using file list
                import tempfile
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    for video_file in selected_files:
                        abs_path = os.path.abspath(video_file).replace("'", "'\"'\"'")
                        f.write(f"file '{abs_path}'\n")
                    file_list_path = f.name
                
                cmd = [
                    'ffmpeg', '-f', 'concat', '-safe', '0',
                    '-i', file_list_path, '-c', 'copy', output_file, '-y'
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # Clean up temp file if using concat method
            if merge_method.lower() != 'filter' and 'file_list_path' in locals():
                try:
                    os.unlink(file_list_path)
                except:
                    pass
            
            if result.returncode == 0:
                print(f"[+] Videos merged successfully: {output_file}")
                
                # Show file size
                if os.path.exists(output_file):
                    size = os.path.getsize(output_file) / (1024*1024)
                    print(f"Output size: {size:.1f}MB")
                
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="video", operation="created")
                return "Videos merged successfully"
            else:
                print(f"[!] Error during merging: {result.stderr}")
                if merge_method.lower() == 'concat':
                    print("[!] Try using the 'filter' method if videos have different formats/resolutions.")
                return f"Error merging videos: {result.stderr}"
                
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_extract_audio(self, video_file, audio_format, quality):
        """Execute audio extraction"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to extract audio from? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing audio format
        if not audio_format:
            print("Available audio formats:")
            print("  1. MP3  2. WAV  3. AAC  4. FLAC  5. OGG")
            format_input = input("> Audio format (e.g., mp3, wav, aac): ").strip().lower()
            if format_input:
                audio_format = format_input
                
        if not audio_format:
            audio_format = 'mp3'  # Default format
            
        # Set default quality if not specified
        if not quality:
            quality = 'medium'
                
        print(f"[*] Extracting audio from {video_file} as {audio_format}")
        
        try:
            # Audio codec mapping
            codec_map = {
                'mp3': 'mp3',
                'wav': 'pcm_s16le',
                'aac': 'aac',
                'flac': 'flac',
                'ogg': 'libvorbis',
                'm4a': 'aac'
            }
            
            # Quality settings for lossy formats
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
                }
            }
            
            codec = codec_map.get(audio_format.lower(), 'mp3')
            base_name = os.path.splitext(video_file)[0]
            output_file = f"{base_name}_audio.{audio_format}"
            
            cmd = ['ffmpeg', '-i', video_file, '-c:a', codec, '-vn']
            
            # Add quality settings for lossy formats
            if codec in quality_settings:
                cmd.extend(quality_settings[codec].get(quality, quality_settings[codec]['medium']))
            
            cmd.extend([output_file, '-y'])
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"[+] Audio extracted successfully: {output_file}")
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="audio", operation="created")
                return f"Extracted audio from {video_file}"
            else:
                print(f"[!] Error during extraction: {result.stderr}")
                return f"Error extracting audio: {result.stderr}"
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_extract_audio_segment(self, video_file, start_time, end_time=None, audio_format=None, quality=None):
        """Execute audio segment extraction"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to extract audio from? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing start time
        if not start_time:
            print("Time formats: 10 (seconds), 1:30 (MM:SS), 1:30:45 (HH:MM:SS)")
            start_time = input("> Enter start time: ").strip()
            
        if not start_time:
            print("[!] Start time is required")
            return "Start time is required"
            
        # Handle missing end time (optional)
        if end_time is None:
            end_time_input = input("> Enter end time (or press Enter for until end): ").strip()
            end_time = end_time_input if end_time_input else None
            
        # Handle missing audio format
        if not audio_format:
            print("Audio formats: 1=MP3, 2=WAV, 3=AAC, 4=FLAC, 5=OGG")
            format_choice = input("> Choose format (or press Enter for MP3): ").strip()
            format_map = {'1': 'mp3', '2': 'wav', '3': 'aac', '4': 'flac', '5': 'ogg'}
            audio_format = format_map.get(format_choice, 'mp3')
            
        # Handle missing quality
        if not quality:
            quality = 'medium'  # Default quality
            
        print(f"[*] Extracting audio segment from {video_file}")
        print(f"    Start: {start_time}")
        print(f"    End: {end_time if end_time else 'until end'}")
        print(f"    Format: {audio_format}")
        
        try:
            audio_segment_module = self._import_task_module('extract_audio_segment')
            if not audio_segment_module:
                return "Error: Could not import extract_audio_segment module"
            
            # Audio codec mapping
            codec_map = {
                'mp3': 'mp3',
                'wav': 'pcm_s16le',
                'aac': 'aac',
                'flac': 'flac',
                'ogg': 'libvorbis',
                'm4a': 'aac'
            }
            
            codec = codec_map.get(audio_format.lower(), 'mp3')
            
            # Generate output filename
            import os
            base_name = os.path.splitext(video_file)[0]
            start_suffix = start_time.replace(':', '_')
            end_suffix = f"_to_{end_time.replace(':', '_')}" if end_time else "_to_end"
            extension_map = {'mp3': '.mp3', 'wav': '.wav', 'aac': '.aac', 'flac': '.flac', 'ogg': '.ogg'}
            extension = extension_map.get(audio_format.lower(), '.mp3')
            output_file = f"{base_name}_audio_{start_suffix}{end_suffix}{extension}"
            
            success = audio_segment_module.extract_audio_segment(
                video_file, output_file, start_time, end_time, codec, quality
            )
            
            if success:
                # Track the created audio file for multi-step operations
                self.track_file_creation(output_file, "audio", "created")
                print(f"[+] File tracked for multi-step operations: {output_file}")
                return f"Extracted audio segment from {video_file}"
            else:
                return "Error extracting audio segment"
                
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_replace_audio(self, video_file, audio_file, audio_handling=None, audio_codec=None):
        """Execute audio replacement"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Get available audio files
        audio_extensions = ['*.mp3', '*.wav', '*.aac', '*.flac', '*.ogg', '*.m4a', '*.wma']
        audio_files = []
        import glob
        for extension in audio_extensions:
            audio_files.extend(glob.glob(extension))
            audio_files.extend(glob.glob(extension.upper()))
        audio_files = sorted(list(set(audio_files)))
        
        if not audio_files:
            print("[!] No audio files found in directory")
            return "No audio files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing audio file
        if not audio_file:
            print("Available audio files:")
            for i, af in enumerate(audio_files, 1):
                print(f"  {i}. {af}")
            try:
                choice = input("\n> Which audio file? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(audio_files):
                        audio_file = audio_files[idx]
                else:
                    matches = [af for af in audio_files if choice.lower() in af.lower()]
                    if matches:
                        audio_file = matches[0]
            except:
                pass
        else:
            # Try smart file resolution for references like "extracted audio", "new audio", etc.
            resolved_file = self.resolve_file_reference(audio_file, "audio")
            if resolved_file:
                print(f"[+] Resolved '{audio_file}' to '{resolved_file}'")
                audio_file = resolved_file
                
        # Check if audio file exists, either as a real file or resolved file
        if not audio_file:
            print("[!] Audio file not specified")
            return "Audio file not specified"
        elif audio_file not in audio_files and not os.path.exists(audio_file):
            print(f"[!] Audio file not found: {audio_file}")
            return "Audio file not found"
            
        # Handle missing audio handling method
        if not audio_handling:
            print("Audio handling options:")
            print("  1. Replace (remove original audio)")
            print("  2. Mix (blend with original)")
            print("  3. Overlay (new audio over quieter original)")
            handling_choice = input("> Choose method (or press Enter for replace): ").strip()
            handling_map = {'1': 'replace', '2': 'mix', '3': 'overlay'}
            audio_handling = handling_map.get(handling_choice, 'replace')
            
        # Handle missing audio codec
        if not audio_codec:
            audio_codec = 'aac'  # Default codec
            
        print(f"[*] Replacing audio in {video_file}")
        print(f"    Audio source: {audio_file}")
        print(f"    Method: {audio_handling}")
        
        try:
            replace_audio_module = self._import_task_module('replace_audio')
            if not replace_audio_module:
                return "Error: Could not import replace_audio module"
            import os
            
            # Generate output filename
            base_name = os.path.splitext(video_file)[0]
            audio_name = os.path.splitext(os.path.basename(audio_file))[0]
            output_file = f"{base_name}_with_{audio_name}.mp4"
            
            success = replace_audio_module.replace_audio(
                video_file, audio_file, output_file, audio_handling, audio_codec
            )
            
            if success:
                # Track the created video file for multi-step operations
                self.track_file_creation(output_file, "video", "created")
                print(f"[+] File tracked for multi-step operations: {output_file}")
                return f"Replaced audio in {video_file}"
            else:
                return "Error replacing audio"
                
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_compress_video(self, video_file, compression_level):
        """Execute video compression"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to compress? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing compression level
        if not compression_level:
            print("Compression levels:")
            print("  1. Light  2. Medium  3. High  4. Maximum")
            level_input = input("> Compression level: ").strip().lower()
            if level_input:
                compression_level = level_input
                
        if not compression_level:
            compression_level = 'medium'  # Default compression
                
        print(f"[*] Compressing {video_file} with {compression_level} compression")
        
        try:
            # Compression level to CRF mapping
            compression_map = {
                'light': {'crf': '20', 'preset': 'medium'},
                'medium': {'crf': '23', 'preset': 'medium'},
                'high': {'crf': '28', 'preset': 'fast'},
                'maximum': {'crf': '32', 'preset': 'fast'}
            }
            
            settings = compression_map.get(compression_level.lower(), compression_map['medium'])
            base_name, ext = os.path.splitext(video_file)
            output_file = f"{base_name}_compressed{ext}"
            
            cmd = [
                'ffmpeg', '-i', video_file,
                '-c:v', 'libx264',
                '-crf', settings['crf'],
                '-preset', settings['preset'],
                '-c:a', 'aac', '-b:a', '128k',
                output_file, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"[+] Video compressed successfully: {output_file}")
                
                # Show file size comparison
                if os.path.exists(output_file):
                    input_size = os.path.getsize(video_file) / (1024*1024)
                    output_size = os.path.getsize(output_file) / (1024*1024)
                    reduction = ((input_size - output_size) / input_size) * 100
                    print(f"Original: {input_size:.1f}MB → Compressed: {output_size:.1f}MB ({reduction:.1f}% reduction)")
                
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="video", operation="created")
                return f"Compressed {video_file}"
            else:
                print(f"[!] Error during compression: {result.stderr}")
                return f"Error compressing video: {result.stderr}"
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_rotate_video(self, video_file, rotation):
        """Execute video rotation"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to rotate? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing rotation
        if not rotation:
            print("Rotation options:")
            print("  1. 90° CW  2. 90° CCW  3. 180°  4. Flip H  5. Flip V")
            rotation_input = input("> Rotation type: ").strip()
            if rotation_input:
                rotation = rotation_input
                
        if not rotation:
            rotation = '90_cw'  # Default rotation
                
        print(f"[*] Rotating {video_file} - {rotation}")
        
        try:
            # Rotation to ffmpeg filter mapping
            rotation_map = {
                '90_cw': 'transpose=1',
                '90_ccw': 'transpose=2',
                '180': 'transpose=1,transpose=1',
                'flip_h': 'hflip',
                'flip_v': 'vflip',
                'transpose': 'transpose=0'
            }
            
            # Map common user inputs to our keys
            rotation_aliases = {
                '90': '90_cw',
                'clockwise': '90_cw',
                'cw': '90_cw',
                'counterclockwise': '90_ccw',
                'ccw': '90_ccw',
                'counter-clockwise': '90_ccw',
                'horizontal': 'flip_h',
                'vertical': 'flip_v',
                'upside': '180',
                'upsidedown': '180'
            }
            
            # Normalize rotation input
            rotation_key = rotation.lower().replace('°', '').replace(' ', '_')
            rotation_key = rotation_aliases.get(rotation_key, rotation_key)
            
            filter_cmd = rotation_map.get(rotation_key, rotation_map['90_cw'])
            base_name, ext = os.path.splitext(video_file)
            rotation_suffix = rotation_key.replace('_', '')
            output_file = f"{base_name}_{rotation_suffix}{ext}"
            
            cmd = [
                'ffmpeg', '-i', video_file,
                '-vf', filter_cmd,
                '-c:a', 'copy',
                output_file, '-y'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                print(f"[+] Video rotated successfully: {output_file}")
                # Track the created file for multi-step operations
                self.track_file_creation(output_file, file_type="video", operation="created")
                return f"Rotated {video_file}"
            else:
                print(f"[!] Error during rotation: {result.stderr}")
                return f"Error rotating video: {result.stderr}"
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def execute_split_video(self, video_file, split_method, split_value):
        """Execute video splitting"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("[!] No video files found in directory")
            return "No video files found"
            
        # Handle missing video file
        if not video_file:
            print("Available video files:")
            for i, vf in enumerate(video_files, 1):
                print(f"  {i}. {vf}")
            try:
                choice = input("\n> Which video file to split? (number or name): ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(video_files):
                        video_file = video_files[idx]
                else:
                    matches = [vf for vf in video_files if choice.lower() in vf.lower()]
                    if matches:
                        video_file = matches[0]
            except:
                pass
                
        if not video_file or video_file not in video_files:
            print("[!] Video file not found")
            return "Video file not found"
            
        # Handle missing split parameters
        if not split_method or not split_value:
            print("Split methods:")
            print("  1. By parts (equal duration)")
            print("  2. By duration (minutes per part)")
            print("  3. By size (MB per part)")
            if not split_method:
                method_input = input("> Split method: ").strip()
                split_method = method_input
            if not split_value:
                value_input = input("> Split value: ").strip()
                split_value = value_input
                
        if not split_method:
            split_method = 'parts'  # Default method
        if not split_value:
            split_value = '2'  # Default value
                
        print(f"[*] Splitting {video_file} by {split_method} - {split_value}")
        
        try:
            # Get video duration first
            duration_cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', video_file
            ]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True)
            
            if duration_result.returncode != 0:
                print("[!] Could not determine video duration")
                return "Could not determine video duration"
                
            total_duration = float(duration_result.stdout.strip())
            base_name, ext = os.path.splitext(video_file)
            
            # Calculate split parameters based on method
            if split_method.lower() in ['parts', 'part', 'equal']:
                num_parts = int(split_value)
                part_duration = total_duration / num_parts
                print(f"[*] Splitting into {num_parts} parts of {part_duration:.1f} seconds each")
                
            elif split_method.lower() in ['duration', 'minutes', 'time']:
                part_duration = float(split_value) * 60  # Convert minutes to seconds
                num_parts = int(total_duration / part_duration) + 1
                print(f"[*] Splitting into {part_duration/60:.1f} minute parts")
                
            elif split_method.lower() in ['size', 'mb', 'filesize']:
                # For size-based splitting, estimate parts based on file size
                input_size_mb = os.path.getsize(video_file) / (1024*1024)
                target_size_mb = float(split_value)
                num_parts = int(input_size_mb / target_size_mb) + 1
                part_duration = total_duration / num_parts
                print(f"[*] Splitting into ~{target_size_mb}MB parts")
                
            else:
                num_parts = int(split_value)
                part_duration = total_duration / num_parts
            
            # Create the parts
            for i in range(num_parts):
                start_time = i * part_duration
                if start_time >= total_duration:
                    break
                    
                remaining_duration = total_duration - start_time
                actual_duration = min(part_duration, remaining_duration)
                
                output_file = f"{base_name}_part{i+1:02d}{ext}"
                
                cmd = [
                    'ffmpeg', '-ss', str(start_time), '-i', video_file,
                    '-t', str(actual_duration),
                    '-c', 'copy', '-avoid_negative_ts', 'make_zero',
                    output_file, '-y'
                ]
                
                print(f"[*] Creating part {i+1}/{num_parts}: {output_file}")
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    size = os.path.getsize(output_file) / (1024*1024)
                    print(f"    ✓ Created successfully ({size:.1f}MB)")
                    # Track the created file for multi-step operations
                    self.track_file_creation(output_file, file_type="video", operation="created")
                else:
                    print(f"    ✗ Error creating part {i+1}: {result.stderr}")
                    return f"Error splitting video at part {i+1}"
            
            print(f"[+] Video split successfully into {num_parts} parts!")
            return f"Split {video_file} into {num_parts} parts"
            
        except Exception as e:
            print(f"[!] Error: {e}")
            return f"Error: {e}"
    
    def show_help(self):
        """Show help with examples"""
        print("\n=== CLI AI VIDEO EDITOR ===")
        print("I understand natural language! Here are some examples:")
        print("")
        print("  === Basic Operations ===")
        print("  'Show me all video files'")
        print("  'Get info about 1.mp4'")
        print("  'What's the resolution of t.mp4?'")
        print("")
        print("  === Trimming & Editing ===")
        print("  'Trim 1.mp4 from 0:30 to 2:15'")
        print("  'Cut the first 10 seconds from 2.mp4'")
        print("  'Extract 1:30 to 3:45 from video.mp4'")
        print("  'Resize 3.mp4 to 720p'")
        print("  'Make t.mp4 1280x720 resolution'")
        print("")
        print("  === Audio Operations ===")
        print("  'Extract audio from 2.mp4'")
        print("  'Extract audio from 1.mp4 from 0:30 to 2:00 as MP3'")
        print("  'Get audio segment from t.mp4 starting at 1:15'")
        print("  'Replace audio in 1.mp4 with w_audio.mp3'")
        print("  'Mix w_audio.mp3 with original audio in 2.mp4'")
        print("  'Extract audio from 2.mp4 as MP3'")
        print("  'Convert video.mov to mp4'")
        print("  'Extract audio as WAV from t.mp4'")
        print("")
        print("  === Multi-Step Operations (AUTO-COMPLETE) ===")
        print("  'Extract 50-60 seconds of w.mp4 as mp3 then use it in t.mp4'")
        print("  'Get audio from 1:30 to 2:45 from video.mp4 then replace audio in target.mp4'")
        print("  'Extract audio segment then use extracted audio in other video'")
        print("  'Trim 1.mp4 from 0:30 to 2:00 then compress it heavily'")
        print("  'Extract audio then mix it with another video'")
        print("")
        print("  === Video Processing ===")
        print("  'Compress 3.mp4 with medium compression'")
        print("  'Rotate 1.mp4 90 degrees clockwise'")
        print("  'Flip 2.mp4 horizontally'")
        print("  'Compress video.mp4 heavily'")
        print("")
        print("  === Advanced Operations ===")
        print("  'Merge 1.mp4 and 2.mp4 into one video'")
        print("  'Split t.mp4 into 3 equal parts'")
        print("  'Split video.mp4 every 5 minutes'")
        print("  'Merge all videos together'")
        print("")
        print("I remember our conversation, so you can say:")
        print("  'Do the same for video 2.mp4'")
        print("  'Resize that video to 1080p'")
        print("  'Show me info about it'")
        print("")
        print("  === Commands ===")
        print("  'history' - show recent conversation")
        print("  'reset api key' - change your Mistral API key")
        print("  'exit' or 'quit' to leave")
        print("========================\n")
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("[*] No conversation history yet.")
            return
            
        print("\n=== Recent Conversation ===")
        for i, exchange in enumerate(self.conversation_history[-5:], 1):
            print(f"{i}. [{exchange['timestamp']}]")
            print(f"   You: {exchange['user']}")
            if exchange['action']:
                print(f"   Action: {exchange['action']}")
            print()
        print("========================\n")
    
    def run(self):
        """Main chat loop"""
        self.clear_screen()
        print("CLIVID - CLI Video Assistant v1.0")
        print("=" * 40)
        print("Hi! I can help you work with video files using natural language.")
        print("Your API key is securely stored and managed locally.")
        print("I can understand parameters like file names, time ranges, resolutions!")
        print("I also remember our conversation for context.")
        print("Type 'help' for examples, 'reset api key' to change your key,")
        print("or just tell me what you want to do!")
        print("=" * 40)
        
        # Automatically show available video files
        video_files = self.get_video_files()
        if video_files:
            print(f"\n[*] I found {len(video_files)} video file(s) in your directory:")
            for i, video_file in enumerate(video_files, 1):
                try:
                    size = os.path.getsize(video_file) / (1024*1024)  # MB
                    print(f"  {i}. {video_file} ({size:.1f}MB)")
                except:
                    print(f"  {i}. {video_file}")
            print("\nJust tell me what you'd like to do with these videos!")
        else:
            print("\n[!] No video files found in the current directory.")
            print("Please add some video files (.mp4, .avi, .mov, .mkv, .wmv, .flv, .webm) and restart.")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                # Handle basic commands directly
                if user_input.lower() in ['help', 'h']:
                    self.show_help()
                    continue
                    
                if user_input.lower() in ['history', 'hist']:
                    self.show_history()
                    continue
                    
                if user_input.lower() in ['reset api key', 'reset apikey', 'change api key', 'change apikey']:
                    print("\n[*] Resetting API key...")
                    self.reset_api_key()
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("Goodbye! Hope I was helpful!")
                    break

                if user_input.lower() in ['clear', 'cls']:
                    self.clear_screen()
                    continue

                # Get available video files
                video_files = self.get_video_files()

                # Use AI to understand intent and extract parameters
                print("[*] Understanding your request...")

                ai_result = self.call_mistral_api(user_input, video_files)

                if ai_result["intent"] == "exit":
                    print("Goodbye! Hope I was helpful!")
                    break
                    
                elif ai_result["intent"] == "error":
                    print(f"[!] {ai_result['explanation']}")
                    print("Try rephrasing your request or type 'help' for examples.")
                    self.add_to_history(user_input, ai_result['explanation'])
                    
                elif ai_result["intent"] == "clarify" or ai_result["needs_clarification"]:
                    print(f"[?] {ai_result['explanation']}")
                    if "missing_params" in ai_result and ai_result["missing_params"]:
                        print(f"    Missing: {', '.join(ai_result['missing_params'])}")
                    print("Could you be more specific? Type 'help' to see examples.")
                    self.add_to_history(user_input, ai_result['explanation'])
                    
                elif ai_result["intent"] in self.available_tasks:
                    print(f"[+] I understand: {ai_result['explanation']}")
                    
                    # Show extracted parameters
                    params = ai_result.get("parameters", {})
                    if any(v for v in params.values() if v):
                        print("[*] Extracted parameters:")
                        for key, value in params.items():
                            if value:
                                print(f"    {key}: {value}")
                    
                    print(f"[*] Executing {ai_result['intent']}...")
                    action_result = self.execute_task_with_params(ai_result["intent"], params)
                    
                    # Add to conversation history
                    self.add_to_history(user_input, ai_result['explanation'], action_result)
                    
                elif ai_result["intent"] == "multi_step":
                    print(f"[+] I understand: {ai_result['explanation']}")
                    
                    # Show multi-step workflow
                    multi_steps = ai_result.get("multi_step_operations", [])
                    if multi_steps:
                        print(f"[*] Detected {len(multi_steps)}-step workflow:")
                        for step_info in multi_steps:
                            step_num = step_info.get("step", 0)
                            intent = step_info.get("intent")
                            print(f"    Step {step_num}: {intent}")
                    
                    action_result = self.execute_task_with_params(ai_result["intent"], ai_result)
                    
                    # Add to conversation history
                    self.add_to_history(user_input, ai_result['explanation'], action_result)
                    
                else:
                    print("[?] I understand what you want, but I don't know how to do that yet.")
                    print("Type 'help' to see what I can currently do.")
                    self.add_to_history(user_input, "Unsupported operation")
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"[!] Unexpected error: {e}")

    def execute_multi_step_operations(self, ai_result):
        """Execute multiple operations in sequence from a single command"""
        multi_steps = ai_result.get("multi_step_operations", [])
        
        if not multi_steps:
            return "No multi-step operations found"
        
        print(f"[*] Executing {len(multi_steps)}-step workflow:")
        results = []
        
        for step_info in multi_steps:
            step_num = step_info.get("step", 0)
            intent = step_info.get("intent")
            parameters = step_info.get("parameters", {})
            
            # Resolve file references for steps after the first one
            if step_num > 1:
                resolved_params = {}
                for key, value in parameters.items():
                    if isinstance(value, str) and value in ["extracted_audio", "new_audio", "audio_segment", "created_file"]:
                        resolved_file = self.resolve_file_reference(value, "audio" if "audio" in key else None)
                        if resolved_file:
                            print(f"[+] Resolved '{value}' → '{resolved_file}' for Step {step_num}")
                            resolved_params[key] = resolved_file
                        else:
                            resolved_params[key] = value
                    else:
                        resolved_params[key] = value
                parameters = resolved_params
            
            print(f"\n[*] Step {step_num}: {intent}")
            
            # Execute each step
            if intent == "extract_audio_segment":
                result = self.execute_extract_audio_segment(
                    parameters.get("video_file"),
                    parameters.get("start_time"),
                    parameters.get("end_time"),
                    parameters.get("audio_format"),
                    parameters.get("quality")
                )
            elif intent == "replace_audio":
                result = self.execute_replace_audio(
                    parameters.get("video_file"),
                    parameters.get("audio_file"),
                    parameters.get("audio_handling"),
                    parameters.get("audio_codec")
                )
            elif intent == "simple_trim":
                result = self.execute_trim(
                    parameters.get("video_file"),
                    parameters.get("start_time"),
                    parameters.get("end_time")
                )
            elif intent == "extract_audio":
                result = self.execute_extract_audio(
                    parameters.get("video_file"),
                    parameters.get("audio_format"),
                    parameters.get("quality")
                )
            elif intent == "merge_videos":
                result = self.execute_merge_videos(
                    parameters.get("video_files", []),
                    parameters.get("merge_method")
                )
            else:
                result = f"Unknown step operation: {intent}"
            
            results.append(f"Step {step_num}: {result}")
            print(f"[+] Step {step_num} completed: {result}")
        
        # Summary
        print(f"\n[+] Multi-step workflow completed! ({len(multi_steps)} steps)")
        return "; ".join(results)

    def track_file_creation(self, filepath, file_type="unknown", operation="created"):
        """Track newly created files for context in multi-step operations"""
        import os
        
        if not os.path.exists(filepath):
            print(f"[DEBUG] File tracking failed - file does not exist: {filepath}")
            return
            
        file_info = {
            "path": filepath,
            "name": os.path.basename(filepath),
            "type": file_type,
            "operation": operation,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        print(f"[DEBUG] Tracking file: {filepath} (type: {file_type}, operation: {operation})")
        
        # Add to created files list
        if operation == "created":
            self.recent_files["created"].insert(0, file_info)
            if len(self.recent_files["created"]) > self.max_recent_files:
                self.recent_files["created"] = self.recent_files["created"][:self.max_recent_files]
        
        # Add to processed files list
        if operation == "processed":
            self.recent_files["processed"].insert(0, file_info)
            if len(self.recent_files["processed"]) > self.max_recent_files:
                self.recent_files["processed"] = self.recent_files["processed"][:self.max_recent_files]
        
        # Update type-specific tracking
        if file_type == "audio":
            self.recent_files["last_audio"] = file_info
            print(f"[DEBUG] Set last_audio to: {filepath}")
        elif file_type == "video":
            self.recent_files["last_video"] = file_info
            print(f"[DEBUG] Set last_video to: {filepath}")
            
        print(f"[DEBUG] Total created files tracked: {len(self.recent_files['created'])}")

    def resolve_file_reference(self, file_reference, file_type=None):
        """Resolve file references like 'extracted audio', 'new file', 'last video' to actual filenames"""
        import os
        
        if not file_reference:
            return None
            
        # If it's already a valid filename, return it
        if os.path.exists(file_reference):
            return file_reference
            
        # Normalize the reference
        ref_lower = file_reference.lower().strip()
        
        print(f"[DEBUG] Resolving file reference: '{file_reference}' (type: {file_type})")
        print(f"[DEBUG] Recent files tracked: {len(self.recent_files['created'])} created, last_audio: {self.recent_files['last_audio'] is not None}")
        
        # Handle specific references used in multi-step operations
        if ref_lower in ['extracted_audio', 'extracted audio', 'audio_segment', 'audio segment']:
            if self.recent_files["last_audio"]:
                print(f"[DEBUG] Found last_audio: {self.recent_files['last_audio']['path']}")
                return self.recent_files["last_audio"]["path"]
            # Look for recently created audio files
            for file_info in self.recent_files["created"]:
                if file_info["type"] == "audio":
                    print(f"[DEBUG] Found created audio: {file_info['path']}")
                    return file_info["path"]
                    
        if ref_lower in ['new_audio', 'new audio', 'created_audio', 'created audio']:
            if self.recent_files["last_audio"]:
                return self.recent_files["last_audio"]["path"]
            for file_info in self.recent_files["created"]:
                if file_info["type"] == "audio":
                    return file_info["path"]
                    
        if ref_lower in ['new_video', 'new video', 'created_video', 'created video', 'last_video', 'last video']:
            if self.recent_files["last_video"]:
                return self.recent_files["last_video"]["path"]
            for file_info in self.recent_files["created"]:
                if file_info["type"] == "video":
                    return file_info["path"]
                    
        if ref_lower in ['created_file', 'created file', 'new_file', 'new file', 'last_file', 'last file']:
            if self.recent_files["created"]:
                return self.recent_files["created"][0]["path"]  # Most recent
                
        # Try to find files that contain the reference text
        all_files = []
        if file_type == "audio":
            audio_extensions = ['*.mp3', '*.wav', '*.aac', '*.flac', '*.ogg', '*.m4a', '*.wma']
            for ext in audio_extensions:
                all_files.extend(glob.glob(ext))
                all_files.extend(glob.glob(ext.upper()))
        elif file_type == "video":
            video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.wmv', '*.flv', '*.webm']
            for ext in video_extensions:
                all_files.extend(glob.glob(ext))
                all_files.extend(glob.glob(ext.upper()))
        else:
            # Search all files
            all_files.extend(glob.glob("*.*"))
            
        # Find files containing the reference text
        matches = [f for f in all_files if ref_lower.replace(' ', '_') in f.lower()]
        if matches:
            # Sort by modification time, newest first
            matches.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            print(f"[DEBUG] Found file by text match: {matches[0]}")
            return matches[0]
            
        print(f"[DEBUG] Could not resolve file reference: '{file_reference}'")
        return None

if __name__ == "__main__":
    app = AIVideoChatInterface()
    app.run()