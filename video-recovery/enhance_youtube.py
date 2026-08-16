import os
from pathlib import Path

from pytubefix import YouTube

VIDEO_URL = "https://www.youtube.com/watch?v=AJrUO3E8Kq8&t=1393s"
OUTPUT_DIR = Path("output")
VIDEO_DIR = OUTPUT_DIR / "video"
AUDIO_DIR = OUTPUT_DIR / "audio"
ENHANCED_DIR = OUTPUT_DIR / "enhanced"

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    ENHANCED_DIR.mkdir(exist_ok=True)

    # 1. Download video with better error handling
    yt = YouTube(VIDEO_URL, 'ANDROID')
    print(f"Video title: {yt.title}")
    
    # Try multiple stream types
    stream = None
    
    # Try progressive streams first (video+audio in one file)
    progressive_streams = yt.streams.filter(progressive=True)
    if progressive_streams:
        stream = progressive_streams.get_highest_resolution()
    
    # If no progressive stream, try adaptive streams (need to combine later)
    if not stream:
        adaptive_streams = yt.streams.filter(adaptive=True)
        if adaptive_streams:
            # Get highest video only stream
            stream = adaptive_streams.filter(only_video=True).get_highest_resolution()
    
    # If still no stream, get any available stream
    if not stream:
        all_streams = yt.streams.all()
        if all_streams:
            stream = all_streams[0]  # First available stream
    
    if not stream:
        print("No streams available for this video. It might be age-restricted or region-locked.")
        print("Available streams:")
        for s in yt.streams.all():
            print(f"  - {s}")
        return
    
    print(f"Downloading: {stream}")
    video_path = stream.download(output_path=str(VIDEO_DIR))
    print("Downloaded video:", video_path)

    # 2. Extract audio to audio/input.wav using ffmpeg
    audio_path = AUDIO_DIR / "input.wav"
    os.system(f'ffmpeg -y -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}"')
    print("Extracted audio:", audio_path)

    # 3. Run resemble-enhance on the audio file
    audio_file = AUDIO_DIR / "input.wav"
    os.system(f"resemble-enhance {audio_file} {ENHANCED_DIR}")
    print("Enhanced audio saved in:", ENHANCED_DIR)

if __name__ == "__main__":
    main()
