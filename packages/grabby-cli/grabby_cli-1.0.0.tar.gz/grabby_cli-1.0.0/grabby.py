#!/usr/bin/env python3
import os
import sys
import yt_dlp

BROWSER = "chrome"  # Change to "chrome" if needed

# Base download directories
BASE_DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "grabby_downloads")
VIDEO_DIR = os.path.join(BASE_DOWNLOAD_DIR, "video")
AUDIO_DIR = os.path.join(BASE_DOWNLOAD_DIR, "audio")

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

COMMON_OPTS = {
    'windowsfilenames': False,
    'restrictfilenames': False,
    'trim_file_name': 0,
    'cookiesfrombrowser': (BROWSER,)
}

def download_video(url):
    ydl_opts = COMMON_OPTS.copy()
    ydl_opts.update({
        'outtmpl': os.path.join(VIDEO_DIR, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_audio(url):
    ydl_opts = COMMON_OPTS.copy()
    ydl_opts.update({
        'outtmpl': os.path.join(AUDIO_DIR, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    if len(sys.argv) < 2:
        print("Usage: grabby <YouTube_URL>")
        sys.exit(1)

    url = sys.argv[1]

    print("\nWhat would you like to download?")
    print("1. Video only")
    print("2. Audio only")
    print("3. Both video and audio")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        download_video(url)
    elif choice == "2":
        download_audio(url)
    elif choice == "3":
        download_video(url)
        download_audio(url)
    else:
        print("Invalid choice! Exiting.")

if __name__ == "__main__":
    main()
