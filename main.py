import os
import sys
import subprocess
import yt_dlp
import socket
import re
import urllib
from download import DownloadThread
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import Qt

output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Musics")
os.makedirs(output_folder, exist_ok=True)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        with open("style.qss", "r") as f:
            self.setStyleSheet(f.read())

    def init_ui(self):
        self.setWindowTitle("YouTube Audio Downloader")
        self.setGeometry(100, 100, 850, 550)
        self.setFixedSize(850, 550)

        # URL Input
        self.url_label = QLabel("Enter YouTube Video URL:", self)
        self.url_label.setObjectName("urlLabelText")
        self.url_label.move(70, 50)

        self.url_input = QLineEdit(self)
        self.url_input.setObjectName("urlInput")
        self.url_input.setGeometry(70, 80, 600, 30)  # x, y, width, height

        # Link Opener Button
        self.open_links_button = QPushButton("Open links.txt", self)
        self.open_links_button.setObjectName("linkButton")
        self.open_links_button.setGeometry(70, 130, 115, 35)

        # Download Button
        self.download_button = QPushButton("Download MP3", self)
        self.download_button.setObjectName("downloadButton")
        self.download_button.setGeometry(210, 130, 610, 35)

        # Folder Selection
        self.folder_button = QPushButton("Saving folder", self)
        self.folder_button.setObjectName("folderButton")
        self.folder_button.setGeometry(645, 130, 115, 35)

        # Status Label
        self.status_label = QLabel("Waiting for input...", self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setGeometry(70, 230, 400, 50)
        self.status_label.setWordWrap(True)

        # Connect buttons to functions
        self.open_links_button.clicked.connect(self.open_links_file)
        self.download_button.clicked.connect(self.start_download)
        self.folder_button.clicked.connect(self.select_folder)

        self.open_links_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.folder_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.url_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def open_links_file(self):
        file_path = "links.txt"

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("")
        if os.name == "nt":
            os.startfile(file_path)
        else:
            subprocess.run(["xdg-open", file_path])

    def start_download(self):
        self.download_button.setEnabled(False)

        file_path = "links.txt"

        if not os.path.exists(file_path):
            self.status_label.setText("Error: links.txt not found.")
            self.download_button.setEnabled(True)
            return

        with open(file_path, "r") as f:
            links = [line.strip() for line in f if line.strip()]

        if not links:
            self.status_label.setText("No links found in links.txt.")
            self.download_button.setEnabled(True)
            return

        self.status_label.setText("Starting downloading...")

        self.threads = []

        for link in links:
            download_thread = DownloadThread(link, output_folder)
            download_thread.progress_signal.connect(self.status_label.setText)
            download_thread.finished.connect(self.check_all_downloads_done)
            download_thread.start()
            self.threads.append(download_thread)

    def check_all_downloads_done(self):
        if all(not thread.isRunning() for thread in self.threads):
            self.download_button.setEnabled(True)

    def select_folder(self):
        global output_folder
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            output_folder = folder
            self.status_label.setText(f"Saving to: {output_folder}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
