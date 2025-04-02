import os
import threading
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
    progress_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, video_url, output_folder, quality="192"):
        super().__init__()
        self.video_url = video_url
        self.output_folder = output_folder
        self.quality = quality
        self._stop_event = threading.Event()  # Event for stopping

    def run(self):
        if not check_connection():
            self.error_signal.emit("Error: No internet connection.")
            self.finished.emit()
            return
        
        if not ("youtube.com" in self.video_url or "youtu.be" in self.video_url):
            self.error_signal.emit(f"Invalid URL: {self.video_url}")
            self.finished.emit()
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            }],
            'quiet': True,
            'progress_hooks': [self.progress_hook],
        }

        try:
            self.progress_signal.emit(f"Downloading {self.video_url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.video_url, download=False)
                title = info.get('title', 'Unknown')

                if self._stop_event.is_set():
                    self.progress_signal.emit(f"{title} - Canceled")
                    self.finished.emit()
                    return
                
                ydl.download([self.video_url])  # Start the download

                if self._stop_event.is_set():
                    self.progress_signal.emit(f"{title} - Canceled")
                    self.finished.emit()
                    return

        except Exception as e:
            self.error_signal.emit(f"Download failed: {str(e)}")
        finally:
            self.finished.emit()

    def progress_hook(self, d):
        if self._stop_event.is_set():
            raise Exception("Download stopped by user")

        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            title = d.get('info_dict', {}).get('title', 'Unknown')
            self.progress_signal.emit(f"{title} - {percent}")
        elif d['status'] == 'finished':
            title = d.get('info_dict', {}).get('title', 'Unknown')
            self.progress_signal.emit(f"✅ {title} - Complete!")

    def stop(self):
        self._stop_event.set()