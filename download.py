import os
import threading
import socket
import time
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

    def __init__(self, video_urls, output_folder, quality="192", format="mp3"):
        super().__init__()
        self.video_urls = video_urls if isinstance(video_urls, list) else [video_urls]
        self.output_folder = output_folder
        self.quality = quality
        self.format = format.lower()
        self._stop_event = threading.Event()

    def run(self):
        if not check_connection():
            self.error_signal.emit("Error: No internet connection.")
            time.sleep(2)
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'quiet': True,
            'progress_hooks': [self.progress_hook],
        }

        if self.format in ["mp3", "wav", "aac"]:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.format,
                'preferredquality': self.quality,
            }]

        try:
            for url in self.video_urls:
                if not ("youtube.com" in url or "youtu.be" in url):
                    self.error_signal.emit(f"Invalid URL: {url}")
                    time.sleep(2)
                    continue
                if self._stop_event.is_set():
                    self.progress_signal.emit("Download canceled")
                    time.sleep(2)
                    break
                self.progress_signal.emit(f"Downloading {url}...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    if self._stop_event.is_set():
                        self.progress_signal.emit("Download canceled")
                        time.sleep(2)
                        break
                    ydl.download([url])
                    if self._stop_event.is_set():
                        self.progress_signal.emit("Download canceled")
                        time.sleep(2)
                        break
        except Exception as e:
            if str(e) == "Download stopped by user":
                self.progress_signal.emit("Download canceled")
                time.sleep(2)
            else:
                self.error_signal.emit(f"Download failed: {str(e)}")
                time.sleep(2)
        finally:
            self.finished.emit()





    def progress_hook(self, d):
        if self._stop_event.is_set():
            raise Exception("Download stopped by user")
            time.sleep(2)
        status = d.get('status')
        title = d.get('info_dict', {}).get('title', 'Unknown')

        if status == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            self.progress_signal.emit(f"Downloading {title}: {percent}")
        elif status == 'finished':
            time.sleep(2)
            self.progress_signal.emit(f"Finished downloading: {title}")
            time.sleep(2)

    def stop(self):
        self._stop_event.set()
