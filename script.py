import yt_dlp
from pydub import AudioSegment # Audio Transcription library
import os # Interacting with Operation System
import time

def download_audio(video_url, output_folder="C:\\Users\\user\\Desktop\\Musics"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Downloaded: {video_url}")
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")

def process_links(file_path="links.txt"):
    try:
        with open(file_path, "r") as file:
            links = file.readlines()
        for link in links:
            link = link.strip()
            if link:
                download_audio(link)
                time.sleep(4)
    except FileNotFoundError:
        print("Error: links.txt file not found.")

if __name__ == "__main__":
    process_links()