import os
import socket
import urllib
import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal

def check_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)  # Signal to update UI with progress

    def __init__(self, video_url, output_folder):
        super().__init__()
        self.video_url = video_url
        self.output_folder = output_folder

    def run(self):
        if not check_connection():
            self.progress_signal.emit("Error: No internet connection.")
            return
        if "youtube.com" not in self.video_url and "youtube.be" not in self.video_url:
            self.progress_signal.emit(f"Invalid URL: {self.video_url} Skipping...")
            return
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%').strip()
                title = d.get('filename', 'Unknown Song').split("\\")[-1].replace(".webm", "").replace(".mp4", "")
                self.progress_signal.emit(f"{title} {percent} downloading...")
            elif d['status'] == 'finished':
                title = d.get('filename', 'Unknown Song').split("\\")[-1].replace(".webm", "").replace(".mp4", "")
                self.progress_signal.emit(f"{title} Downloaded Completely!")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'noprogress': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook], 
        }
        try:
            self.progress_signal.emit("Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            self.progress_signal.emit("Download Complete!")
        except socket.timeout:
            self.progress_signal.emit("Error: Network Timeout. Check connection.")
        except urllib.error.URLError:
            self.progress_signal.emit("Error: Cannot reach YouTube.")
        except yt_dlp.utils.ExtractorError:
            self.progress_signal.emit("Error: Video unavailable.")
        except yt_dlp.utils.DownloadError:
            self.progress_signal.emit("Error: Download failed.")
        except Exception as e:
            self.progress_signal.emit(f"Unexpected Error: {e}")

