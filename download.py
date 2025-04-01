import os
import socket
import urllib
import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtCore import Qt, QTimer

def check_connection():
    """Check internet connection"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False


class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, video_url, output_folder):
        super().__init__()
        self.video_url = video_url
        self.output_folder = output_folder

    def run(self):
        """Main function to download audio"""
        if not check_connection():
            self.error_signal.emit("Error: No internet connection.")
            return
        
        if "youtube.com" not in self.video_url and "youtu.be" not in self.video_url:
            self.progress_signal.emit(f"Invalid URL: {self.video_url} Skipping...")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'progress_hooks': [self.progress_hook],  # Correct function reference
        }
        try:
            self.progress_signal.emit("Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_url])
            QTimer.singleShot(2000, lambda: self.progress_signal.emit("Download Complete!"))
            QTimer.singleShot(2000, lambda: self.status_label.setText("Waiting for input..."))

        except socket.timeout:
            self.progress_signal.emit("Error: Network Timeout. Check connection.")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Waiting for input..."))
        except urllib.error.URLError:
            self.progress_signal.emit("Error: Cannot reach YouTube.")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Waiting for input..."))
        except yt_dlp.utils.ExtractorError:
            self.progress_signal.emit("Error: Video unavailable.")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Waiting for input..."))
        except yt_dlp.utils.DownloadError:
            self.progress_signal.emit("Error: Download failed.")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Waiting for input..."))
        except Exception as e:
            self.progress_signal.emit(f"Unexpected Error: {e}")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Waiting for input..."))

    def progress_hook(self, d):
        """Handles download progress updates"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip() if '_percent_str' in d else '0%'
            title = d.get('info_dict', {}).get('title', 'Unknown title')
            self.progress_signal.emit(f"{title} {percent} downloading...")

        elif d['status'] == 'finished':
            title = d.get('info_dict', {}).get('title', 'Unknown title')
            self.progress_signal.emit(f"{title} Downloaded Completely!")