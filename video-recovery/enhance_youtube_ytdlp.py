import os
from pathlib import Path
import yt_dlp
import sys

VIDEO_URL = "https://www.youtube.com/watch?v=AJrUO3E8Kq8&t=1393s"
OUTPUT_DIR = Path("output")
VIDEO_DIR = OUTPUT_DIR / "video"
AUDIO_DIR = OUTPUT_DIR / "audio"
ENHANCED_DIR = OUTPUT_DIR / "enhanced"

def download_video():
    """Скачивает видео с YouTube"""
    print("📥 Downloading video...")
    video_path_template = str(VIDEO_DIR / "%(title)s.%(ext)s")
    
    ydl_opts = {
        'outtmpl': video_path_template,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(VIDEO_URL, download=True)
            video_filename = ydl.prepare_filename(info)
            
            if not Path(video_filename).exists():
                video_files = list(VIDEO_DIR.glob(f"*{info.get('id', '')}*.mp4"))
                if video_files:
                    video_filename = str(video_files[0])
                else:
                    video_files = list(VIDEO_DIR.glob("*.mp4"))
                    if video_files:
                        video_filename = str(video_files[0])
                    else:
                        raise Exception("Could not find downloaded video file")
            
            return Path(video_filename)
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
            return None

def extract_audio(video_path):
    """Извлекает аудио из видео"""
    print("🎵 Extracting audio...")
    audio_path = AUDIO_DIR / "input.wav"
    os.system(f'ffmpeg -y -i "{video_path}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}"')
    
    if audio_path.exists():
        print(f"✅ Extracted audio: {audio_path}")
        print(f"📊 Audio size: {audio_path.stat().st_size / 1024 / 1024:.2f} MB")
        return audio_path
    else:
        print("❌ Failed to extract audio")
        return None

def enhance_audio(audio_path):
    """Улучшает аудио с помощью resemble-enhance"""
    print("🔊 Running audio enhancement...")
    os.system(f"resemble-enhance {audio_path} {ENHANCED_DIR}")
    print("✅ Enhanced audio saved in:", ENHANCED_DIR)

def main():
    # Создаем директории
    OUTPUT_DIR.mkdir(exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    ENHANCED_DIR.mkdir(exist_ok=True)
    
    # Проверяем аргументы командной строки
    skip_download = "--skip-download" in sys.argv
    skip_extract = "--skip-extract" in sys.argv
    
    # Проверяем наличие уже скачанного видео
    existing_videos = list(VIDEO_DIR.glob("*.mp4"))
    existing_audio = AUDIO_DIR / "input.wav"
    
    # 1. Скачивание видео (если нужно)
    video_path = None
    if skip_download:
        print("⏭️ Skipping download (--skip-download)")
        if existing_videos:
            video_path = existing_videos[0]
            print(f"📁 Using existing video: {video_path}")
        else:
            print("❌ No existing video found in", VIDEO_DIR)
            return
    else:
        if existing_videos and not skip_extract:
            print(f"📁 Found existing video: {existing_videos[0]}")
            response = input("Use existing video? (y/n): ").lower()
            if response == 'y':
                video_path = existing_videos[0]
            else:
                video_path = download_video()
        else:
            video_path = download_video()
    
    if not video_path:
        print("❌ No video available")
        return
    
    # 2. Извлечение аудио (если нужно)
    audio_path = None
    if skip_extract:
        print("⏭️ Skipping extraction (--skip-extract)")
        if existing_audio.exists():
            audio_path = existing_audio
            print(f"📁 Using existing audio: {audio_path}")
        else:
            print("❌ No existing audio found")
            return
    else:
        if existing_audio.exists():
            print(f"📁 Found existing audio: {existing_audio}")
            response = input("Use existing audio? (y/n): ").lower()
            if response == 'y':
                audio_path = existing_audio
            else:
                audio_path = extract_audio(video_path)
        else:
            audio_path = extract_audio(video_path)
    
    if not audio_path:
        print("❌ No audio available")
        return
    
    # 3. Улучшение аудио
    enhance_audio(audio_path)

if __name__ == "__main__":
    main()
