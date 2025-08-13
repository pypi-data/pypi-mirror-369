# Clivid - CLI Video Assistant

[![PyPI version](https://badge.fury.io/py/clivid.svg)](https://badge.fury.io/py/clivid)
[![Python Support](https://img.shields.io/pypi/pyversions/clivid.svg)](https://pypi.org/project/clivid/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered video processing assistant that allows users to perform complex video operations using natural language commands. No more remembering complex FFmpeg syntax!

## 🚀 Features

- **Natural Language Interface**: Simply tell it what you want to do with your videos
- **Smart Parameter Extraction**: Automatically understands filenames, time ranges, resolutions, and formats
- **Multi-Step Operations**: Chain operations together (e.g., "extract audio from video.mp4 then use it in other.mp4")
- **Secure API Key Management**: Your Mistral AI API key is stored securely on your local machine
- **Comprehensive Video Operations**:
  - Video trimming and cutting
  - Format conversion (MP4, AVI, MOV, MKV, etc.)
  - Audio extraction and replacement
  - Video compression and resizing
  - Video rotation and flipping
  - Video merging and splitting
  - And much more!

## 🛠️ Installation

### Prerequisites

1. **Python 3.7+** is required
2. **FFmpeg** must be installed on your system:
   - **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

### Install via pip

```bash
pip install clivid
```

### Get Your Mistral AI API Key

1. Go to [https://console.mistral.ai/](https://console.mistral.ai/)
2. Sign up or log in to your account
3. Navigate to 'API Keys' section
4. Create a new API key
5. Copy the key (you'll be prompted to enter it on first run)

## 🎯 Quick Start

After installation, run the assistant:

```bash
clivid
```

Or use the short alias:

```bash
cv
```

On first run, you'll be prompted to enter your Mistral AI API key. It will be saved securely for future use.

## 💬 Example Commands

The AI understands natural language! Here are some examples:

### Basic Operations
```
"Show me all video files"
"Get info about video.mp4"
"What's the resolution of my_video.mp4?"
```

### Video Editing
```
"Trim video.mp4 from 0:30 to 2:15"
"Cut the first 10 seconds from my_video.mp4"
"Resize video.mp4 to 720p"
"Convert video.mov to mp4"
"Compress my_video.mp4 with high compression"
```

### Audio Operations
```
"Extract audio from video.mp4"
"Extract audio from video.mp4 from 1:30 to 2:45 as MP3"
"Replace audio in video.mp4 with new_audio.mp3"
"Mix new_audio.mp3 with original audio in video.mp4"
```

### Advanced Multi-Step Operations
```
"Extract 50-60 seconds of video.mp4 as mp3 then use it in other_video.mp4"
"Get audio from 1:30 to 2:45 from source.mp4 then replace audio in target.mp4"
"Trim video.mp4 from 0:30 to 2:00 then compress it heavily"
```

### Other Operations
```
"Merge video1.mp4 and video2.mp4"
"Split video.mp4 into 3 equal parts"
"Rotate video.mp4 90 degrees clockwise"
"Flip video.mp4 horizontally"
```

## 🔧 Commands

- `help` - Show detailed examples and usage
- `history` - Show recent conversation history
- `reset api key` - Change your Mistral AI API key
- `clear` - Clear the screen
- `exit` or `quit` - Exit the application

## 🔒 Security

- Your Mistral AI API key is stored locally in `~/.clivid/config.json`
- The configuration file has restricted permissions for security
- No data is sent anywhere except to Mistral AI for natural language processing

## 🆘 Troubleshooting

### Common Issues

1. **"FFmpeg not found"**: Make sure FFmpeg is installed and in your system PATH
2. **"Invalid API key"**: Check your Mistral AI API key and internet connection
3. **"No video files found"**: Make sure you're in a directory with video files

### Getting Help

```bash
clivid
> help
```

This will show detailed examples and usage instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Mistral AI](https://mistral.ai/) for natural language processing
- Uses [FFmpeg](https://ffmpeg.org/) for video processing
- Inspired by the need for user-friendly video editing tools

## 📊 System Requirements

- **Python**: 3.7 or higher
- **FFmpeg**: Latest stable version
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 1GB RAM minimum (more for large video files)
- **Storage**: Varies based on video file sizes

---

**Made with ❤️ for video creators and developers who want powerful, simple video processing tools.**
