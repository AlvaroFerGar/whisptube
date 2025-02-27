# Whisptube ▶️👂✍️

A tool to download YouTube playlists and automatically transcribe them using OpenAI's [Whisper](https://github.com/openai/whisper).

This script allows you to:
- ▶️ Download all videos from a YouTube playlist
- 👂 Transcribe the videos using Whisper (that fancy speech-to-text model from OpenAI)
- ✍️ Get your transcriptions in multiple formats (with timestamps, without timestamps, or segmented)

## 🛠️ Requirements

- Python 3.6+
- ffpmeg

## 🚀 Installation

1. Clone this repo
2. Install ffpmeg
```bash
sudo apt install ffpmeg
```
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## 👨‍💻 How to use it

Basic usage:

```bash
python youtube_transcriber.py https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID
```

By default, it'll download all videos from the playlist and transcribe them using the "base" Whisper model.

### 🔧 Options to tweak things:

You have some options to configure the way it works

```bash
usage: whisptube.py [-h] [--output OUTPUT] [--model {tiny,base,small,medium,large}] [--skip-download] [--skip-transcribe] [--debug] playlist_url

YouTube Playlist Downloader and Transcriber

positional arguments:
  playlist_url          URL of the YouTube playlist

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory for videos and transcriptions (default: youtube_downloads)
  --model {tiny, tiny.en, base, base.en, small, small.en, medium, medium.en, large", turbo}, -m {tiny,base,small,medium,large}
                        Whisper model to use (default: base) - larger models are more accurate but slower
  --skip-download       Skip downloading videos and only transcribe existing ones
  --skip-transcribe     Skip transcribing and only download missing videos
  --debug               Enable debug logging
```


```bash
# Use a bigger (more accurate but slower) Whisper model
python youtube_transcriber.py https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID --model medium

# Just download the videos, no transcription
python youtube_transcriber.py https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID --skip-transcribe

# Just transcribe videos you've already downloaded
python youtube_transcriber.py https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID --skip-download

# Save everything to a specific folder
python youtube_transcriber.py https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID --output my_cool_videos

# Turn on debug mode if things go sideways
python youtube_transcriber.py https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID --debug
```
### 💡 Pro tips

This are the available whisper models. Choose wisely the one that better fits your task.

| 🏷️ Size  | 🔢 Parameters | 🇬🇧 English-only model | 🌍 Multilingual model | 🎮 Required VRAM | ⚡ Relative speed |
|---------|------------|-------------------|--------------------|--------------|---------------|
| tiny    | 39 M       | tiny.en           | tiny              | ~1 GB        | ~10x          |
| base    | 74 M       | base.en           | base              | ~1 GB        | ~7x           |
| small   | 244 M      | small.en          | small             | ~2 GB        | ~4x           |
| medium  | 769 M      | medium.en         | medium            | ~5 GB        | ~2x           |
| large   | 1550 M     | N/A               | large             | ~10 GB       | 1x            |
| turbo   | 809 M      | N/A               | turbo             | ~6 GB        | ~8x           |

## 📋 What you'll get

When it's done, you'll find:

- All the videos from the playlist in your output directory (default: `youtube_downloads`)
- A `transcriptions` folder containing:
  - Individual transcriptions for each video in multiple formats:
    - `video_name.txt` - With timestamps like `[00:01:23] Text goes here...`
    - `video_name_no_timestamps.txt` - Just the text as a continuous paragraph
    - `video_name_segmented.txt` - Text broken into segments (like sentences or phrases)
  - Combined transcription files with all videos:
    - `combined_transcription_with_timestamps.txt`
    - `combined_transcription.txt`
    - `combined_transcription_segmented.txt`

## 📝 License

Feel free to use this however you want!