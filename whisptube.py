import os
import argparse
import glob
import subprocess
import json
from tqdm import tqdm

def download_playlist(playlist_url, output_dir):
    """
    Download all videos from a YouTube playlist to the specified output directory using yt-dlp.
    Skip videos that have already been downloaded.
    
    Args:
        playlist_url (str): URL of the YouTube playlist
        output_dir (str): Directory where videos will be saved
    
    Returns:
        list: List of paths to downloaded video files
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Get playlist info
    print(f"Getting playlist info for: {playlist_url}")
    # Command to get playlist info in JSON format
    cmd = [
        'yt-dlp',
        '--dump-json',
        '--flat-playlist',
        playlist_url
    ]
    
    try:
        # Run command and capture output
        playlist_info = subprocess.run(cmd, capture_output=True, text=True, check=True)
        videos = [json.loads(line) for line in playlist_info.stdout.strip().split('\n') if line]
        print(f"Found {len(videos)} videos in playlist")
    except subprocess.CalledProcessError as e:
        print(f"Error getting playlist info: {e}")
        print(f"Error output: {e.stderr}")
        return []
    except Exception as e:
        print(f"Unexpected error getting playlist info: {e}")
        return []
        
    video_paths = []
    
    # Download each video
    for i, video in enumerate(videos):
        video_id = video.get('id')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Format template for output filename
        output_template = os.path.join(output_dir, f"%(title)s.%(ext)s")
        
        try:
            # Check if file already exists before downloading
            # First get the expected filename
            expected_filename = subprocess.run(
                ['yt-dlp', '--print', 'filename', '-o', output_template, '--no-download', video_url],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            
            # Also check for any files with the video ID in the name
            existing_files = glob.glob(os.path.join(output_dir, f"*{video_id}*.mp4"))
            
            if os.path.exists(expected_filename) or existing_files:
                # File already exists, skip download
                print(f"Skipping video {i+1}/{len(videos)}: {video.get('title', video_id)} (already downloaded)")
                
                if os.path.exists(expected_filename):
                    video_paths.append(expected_filename)
                else:
                    video_paths.append(existing_files[0])
                continue
                
            print(f"Downloading video {i+1}/{len(videos)}: {video.get('title', video_id)}")
            
            # Command to download video
            cmd = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '--merge-output-format', 'mp4',
                '-o', output_template,
                '--no-playlist',
                video_url
            ]
            
            # Run download command
            subprocess.run(cmd, check=True)
            
            print(f"Downloaded {video.get('title', video_id)}")


            # Find the downloaded file
            if os.path.exists(expected_filename):
                video_paths.append(expected_filename)
            else:
                # Try to find any file with the video ID in the name
                possible_files = glob.glob(os.path.join(output_dir, f"*{video_id}*.mp4"))
                if possible_files:
                    video_paths.append(possible_files[0])
                    
        except subprocess.CalledProcessError as e:
            print(f"Error downloading video {video_id}: {e}")
            print(f"Error output: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error downloading video {video_id}: {e}")
    
    return video_paths

def format_timestamp(seconds):
    """
    Format seconds into a timestamp string (HH:MM:SS).
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def transcribe_videos(video_paths, output_dir, model_name="base"):
    """
    Transcribe videos using OpenAI's Whisper and save transcriptions to text files.
    
    Args:
        video_paths (list): List of paths to video files
        output_dir (str): Directory where transcriptions will be saved
        model_name (str): Whisper model to use (tiny, base, small, medium, large)
        
    Returns:
        list: List of paths to transcription files
    """
    # Import OpenAI's Whisper correctly
    try:
        import whisper as openai_whisper
    except ImportError:
        print("Error: OpenAI Whisper is not installed. Installing the correct package...")
        subprocess.run(["pip", "install", "openai-whisper"], check=True)
        import whisper as openai_whisper
    
    # Create transcription directory if it doesn't exist
    transcription_dir = os.path.join(output_dir, "transcriptions")
    if not os.path.exists(transcription_dir):
        os.makedirs(transcription_dir)
    
    # Load Whisper model
    print(f"Loading Whisper model: {model_name}")
    model = openai_whisper.load_model(model_name)
    
    transcription_paths = []
    all_text_with_timestamps = ""
    all_text_without_timestamps = ""
    all_text_segmented = ""
    
    # Process each video
    for video_path in tqdm(video_paths, desc="Transcribing videos"):
        try:
            # Get base filename without extension
            video_basename = os.path.basename(video_path)
            video_name = os.path.splitext(video_basename)[0]
            output_file = os.path.join(transcription_dir, f"{video_name}.txt")
            output_file_no_timestamps = os.path.join(transcription_dir, f"{video_name}_no_timestamps.txt")
            output_file_segmented = os.path.join(transcription_dir, f"{video_name}_segmented.txt")
            
            # Skip if already transcribed
            if os.path.exists(output_file) and os.path.exists(output_file_segmented):
                print(f"Skipping already transcribed video: {video_name}")
                with open(output_file, 'r', encoding='utf-8') as f:
                    file_text = f.read()
                    all_text_with_timestamps += file_text + "\n\n"
                with open(output_file_no_timestamps, 'r', encoding='utf-8') as f:
                    file_text = f.read()
                    all_text_without_timestamps += file_text + "\n\n"
                with open(output_file_segmented, 'r', encoding='utf-8') as f:
                    file_text = f.read()
                    all_text_segmented += file_text + "\n\n"
                transcription_paths.append(output_file)
                continue
            
            print(f"Transcribing: {video_name}")
            
            # Transcribe video with word-level timestamps
            result = model.transcribe(video_path, word_timestamps=True)
            
            # Extract text without timestamps
            transcription_text = result["text"]
            
            # Create text with timestamps
            text_with_timestamps = ""
            text_segmented = ""
            segments = result.get("segments", [])
            
            for segment in segments:
                start_time = format_timestamp(segment["start"])
                text_with_timestamps += f"[{start_time}] {segment['text'].strip()}\n"
                # For segmented text, just include the text without timestamps but keep line breaks
                text_segmented += f"{segment['text'].strip()}\n"
            
            # Save individual transcription with timestamps
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_with_timestamps)
            
            # Save individual transcription without timestamps (full paragraph)
            with open(output_file_no_timestamps, 'w', encoding='utf-8') as f:
                f.write(transcription_text)
                
            # Save individual transcription segmented (line breaks but no timestamps)
            with open(output_file_segmented, 'w', encoding='utf-8') as f:
                f.write(text_segmented)
            
            # Add to combined text
            all_text_with_timestamps += text_with_timestamps + "\n\n"
            all_text_without_timestamps += transcription_text + "\n\n"
            all_text_segmented += text_segmented + "\n\n"
            
            transcription_paths.append(output_file)
            
        except Exception as e:
            print(f"Error transcribing video: {e}")
            import traceback
            traceback.print_exc()
    
    # Save combined transcriptions
    combined_file = os.path.join(transcription_dir, "combined_transcription_with_timestamps.txt")
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write(all_text_with_timestamps)
    
    combined_file_no_timestamps = os.path.join(transcription_dir, "combined_transcription.txt")
    with open(combined_file_no_timestamps, 'w', encoding='utf-8') as f:
        f.write(all_text_without_timestamps)
        
    combined_file_segmented = os.path.join(transcription_dir, "combined_transcription_segmented.txt")
    with open(combined_file_segmented, 'w', encoding='utf-8') as f:
        f.write(all_text_segmented)
    
    return transcription_paths

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Download YouTube playlist and transcribe videos")
    parser.add_argument("playlist_url", help="URL of the YouTube playlist")
    parser.add_argument("--output", "-o", default="youtube_downloads", help="Output directory for videos and transcriptions")
    parser.add_argument("--model", "-m", default="base", choices=["tiny", "base", "small", "medium", "large"],  help="Whisper model to use (tiny, base, small, medium, large)")
    parser.add_argument("--skip-download", action="store_true", help="Skip downloading videos and only transcribe existing ones")
    parser.add_argument("--skip-transcribe", action="store_true", help="Skip transcribing and only download unexisting videos")

    args = parser.parse_args()
    
    # Download videos if not skipped
    if not args.skip_download:
        video_paths = download_playlist(args.playlist_url, args.output)

    video_paths = glob.glob(os.path.join(args.output, "*.mp4"))
    print(f"Found {len(video_paths)} existing videos")
    
    # Transcribe videos
    if video_paths and not args.skip_transcribe:
        transcription_paths = transcribe_videos(video_paths, args.output, args.model)
        print(f"Transcribed {len(transcription_paths)} videos")
        print(f"Combined transcription files saved to the transcriptions directory:")
        print(f"  - With timestamps: combined_transcription_with_timestamps.txt")
        print(f"  - Without timestamps (paragraph): combined_transcription.txt")
        print(f"  - Segmented (no timestamps): combined_transcription_segmented.txt")
    else:
        print("No pending trabscriptions")

if __name__ == "__main__":
    main()