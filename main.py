import os
import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QIcon

output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Musics")
os.makedirs(output_folder, exist_ok=True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

        icon_path = os.path.abspath("logo.ico")
        self.setWindowIcon(QIcon(icon_path))

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(base_path, 'style.qss')
        with open(style_path, "r") as f:
            self.setStyleSheet(f.read())

    def init_ui(self):
        self.setWindowTitle("YouTube Audio Downloader")
        self.setGeometry(100, 100, 850, 550)
        self.setFixedSize(850, 550)

        layout = QVBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.url_label = QLabel("Enter YouTube Video URL:", self)
        self.url_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.url_label.setGeometry(70, 50, 600, 30)

        self.url_input = QLineEdit(self)
        self.url_input.setObjectName("urlInput")
        self.url_input.setGeometry(70, 80, 600, 30)  # x, y, width, height

        self.open_links_button = QPushButton("Open links.txt", self)
        self.open_links_button.setObjectName("linkButton")
        self.open_links_button.setGeometry(70, 130, 115, 35)

        self.download_button = QPushButton("Download MP3", self)
        self.download_button.setObjectName("downloadButton")
        self.download_button.setGeometry(210, 130, 610, 35)

        self.folder_button = QPushButton("Saving folder", self)
        self.folder_button.setObjectName("folderButton")
        self.folder_button.setGeometry(645, 130, 115, 35)

        self.status_label = QLabel("Waiting for input...", self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setGeometry(70, 230, 400, 50)
        self.status_label.setWordWrap(True)

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
        link = self.url_input.text().strip()

        if link:
            links = [link]
        else:
            file_path = "links.txt"
            MAX_LINKS = 12

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
            if len(links) > MAX_LINKS:
                self.status_label.setText(f"Error: Too many links! Limit is {MAX_LINKS}")
                self.download_button.setEnabled(True)
                return

        self.status_label.setText("Starting downloading...")

        self.threads = []

        for link in links:
            download_thread = self.DownloadThread(link, output_folder)
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
    icon_path = os.path.abspath("logo.ico")
    app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
