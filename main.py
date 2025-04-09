import os
import sys
import subprocess
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from download import DownloadThread
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                            QPushButton, QFileDialog, QVBoxLayout, QWidget, 
                            QComboBox, QListWidget, QDockWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor, QIcon
from PyQt6.QtWidgets import QDockWidget, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QColor, QBrush



AUDIO_FORMATS = ["MP3", "WAV", "AAC", "OGG"]
DEFAULT_THEME = "dark"
MAX_LINKS = 15
 



class YouTubeDownloader(QMainWindow):



    def __init__(self):
        super().__init__()

        self.output_folder = self.init_paths()
        self.current_theme = self.load_theme_config()

        self.init_ui()
        self.set_theme(self.current_theme)
        self.set_window_icon()



    def init_paths(self):
        output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Musics")
        os.makedirs(output_folder, exist_ok=True)
        self.config_folder = os.path.join(os.getenv('LOCALAPPDATA', ''), "YouTubeExtractor")
        self.config_path = os.path.join(self.config_folder, "config.txt")
        os.makedirs(self.config_folder, exist_ok=True)
        return output_folder
    



    def load_theme_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    theme = f.read().strip()
                    return theme if self.validate_theme(theme) else DEFAULT_THEME
            else:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    f.write(DEFAULT_THEME)
                return DEFAULT_THEME
        except Exception as e:
            print(f"Config error: {e}")
            return DEFAULT_THEME
        



    def validate_theme(self, theme):
        return theme in ("dark", "light")
    



    def set_window_icon(self):
        icon_path = os.path.abspath("logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            if hasattr(QApplication.instance(), 'setWindowIcon'):
                QApplication.instance().setWindowIcon(QIcon(icon_path))




    def create_menu_button(self):
        self.menu_button = QPushButton(self)
        self.menu_button.setGeometry(20, 20, 40, 40)
        self.menu_button.setObjectName("menuButton")
        self.menu_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.menu_button.setIconSize(QSize(32, 32))
        self.update_menu_icon()
        self.menu = QMenu(self)
        self.create_menu_actions()
        self.menu_button.clicked.connect(lambda: self.menu.exec(self.menu_button.mapToGlobal(
        self.menu_button.rect().bottomLeft())))




    def create_menu_actions(self):
        about_action = QAction("About", self)
        settings_action = QAction("Settings", self)
        exit_action = QAction("Exit", self)

        exit_action.triggered.connect(self.close)

        self.menu.addAction(about_action)
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)




    def update_menu_icon(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"Current theme: {self.current_theme}")
        icon_file = os.path.join(base_path, 'assets', f'burger_{self.current_theme}.png')
        print(f"Looking for icon at: {icon_file}")  # Debug
        if os.path.exists(icon_file):
            self.menu_button.setIcon(QIcon(icon_file))
            self.menu_button.setIconSize(QSize(32, 32))




    def init_ui(self):
        self.setWindowTitle("YouTube Audio Downloader")
        self.setGeometry(100, 100, 850, 550)
        self.setFixedSize(850, 550)
        layout = QVBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.create_url_input()
        self.create_menu_button()
        self.create_format_selector()
        self.create_url_input()
        self.create_action_buttons()
        self.create_status_display()
        self.create_quality_selector()
        self.create_theme_button()
        self.create_copyright_label()
        self.create_side_panel()
        self.setup_connections()




    def create_url_input(self):
        self.url_label = QLabel("Enter YouTube Video URL:", self)
        self.url_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.url_label.setGeometry(70, 70, 600, 30)
        self.url_label.setObjectName("urlLabel")
        self.url_input = QLineEdit(self)
        self.url_input.setObjectName("urlInput")
        self.url_input.setGeometry(70, 100, 600, 30)
        self.url_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)




    def create_action_buttons(self):
        self.open_links_button = QPushButton("Open links.txt", self)
        self.open_links_button.setObjectName("linkButton")
        self.open_links_button.setGeometry(70, 150, 115, 35)
        self.open_links_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.download_button = QPushButton("Download MP3", self)
        self.download_button.setObjectName("downloadButton")
        self.download_button.setGeometry(210, 150, 610, 35)
        self.download_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.folder_button = QPushButton("Saving folder", self)
        self.folder_button.setObjectName("folderButton")
        self.folder_button.setGeometry(645, 150, 115, 35)
        self.folder_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))




    def create_status_display(self):
        self.status_label = QLabel("Waiting for input...", self)
        self.status_label.setObjectName("statusLabel")
        self.status_label.setGeometry(70, 440, 400, 50)
        self.status_label.setWordWrap(True)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.setGeometry(700, 440, 90, 25)
        self.cancel_button.setVisible(False)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_button.clicked.connect(self.cancel_downloads)




    def create_side_panel(self):
        self.side_panel = QDockWidget("Menu", self)
        self.side_panel.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.side_panel.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        side_widget = QWidget(self)
        side_layout = QVBoxLayout(side_widget)
        self.side_panel.setFixedWidth(220)
        self.history_list = QListWidget(self)
        side_widget.setObjectName("sidePanel")
        side_layout.addWidget(self.history_list)
        side_widget.setLayout(side_layout)
        self.side_panel.setWidget(side_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.side_panel)
        self.side_panel.setVisible(False)
        item1 = QListWidgetItem("Downloaded Video 1 - 2025-04-07")
        item1.setForeground(QBrush(QColor("white")))
        self.history_list.addItem(item1)
        item2 = QListWidgetItem("Downloaded Video 2 - 2025-04-09")
        item2.setForeground(QBrush(QColor("white")))
        self.history_list.addItem(item2)




    def create_menu_button(self):
        self.menu_button = QPushButton(self)
        self.menu_button.setGeometry(20, 20, 40, 40)
        self.menu_button.setObjectName("menuButton")
        self.menu_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.menu_button.setIconSize(QSize(32, 32))
        self.update_menu_icon()
        self.menu = QMenu(self)
        self.create_menu_actions()
        self.menu_button.clicked.connect(lambda: self.toggle_side_panel())



        
    def toggle_side_panel(self):
        if self.side_panel.isVisible():
            self.side_panel.hide()
        else:
            self.side_panel.show()




    def create_quality_selector(self):
        self.quality_label = QLabel("Select Audio Quality:", self)
        self.quality_label.setGeometry(70, 230, 200, 30)
        self.quality_label.setObjectName("qualityLabel")
        self.quality_dropdown = QComboBox(self)
        self.quality_dropdown.setGeometry(230, 230, 150, 30)
        self.quality_dropdown.addItems(["64kbps", "128kbps", "192kbps", "320kbps"])
        self.quality_dropdown.setCurrentIndex(1)  # Default to 128kbps
        self.quality_dropdown.setObjectName("qualityDropdown")




    def create_format_selector(self):
        self.format_label = QLabel("Select Audio Format:", self)
        self.format_label.setGeometry(70, 270, 200, 30)
        self.format_label.setObjectName("formatLabel")
        
        self.format_dropdown = QComboBox(self)
        self.format_dropdown.setGeometry(230, 270, 150, 30)
        self.format_dropdown.addItems(AUDIO_FORMATS)
        self.format_dropdown.setCurrentIndex(0)  # Default to MP3
        self.format_dropdown.setObjectName("formatDropdown")
        



    def create_theme_button(self):
        self.theme_button = QPushButton(self)
        self.theme_button.setGeometry(790, 20, 40, 40)
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.theme_button.clicked.connect(self.toggle_theme)




    def create_copyright_label(self):
        self.copyright_label = QLabel("© 2025 Abdulaziz.K. All rights reserved.", self)
        self.copyright_label.setGeometry(660, 515, 300, 30)
        self.copyright_label.setObjectName("copyrightLabel")




    def setup_connections(self):
        self.open_links_button.clicked.connect(self.open_links_file)
        self.download_button.clicked.connect(self.start_download)
        self.folder_button.clicked.connect(self.select_folder)




    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(self.current_theme)
        self.save_theme()




    def set_theme(self, theme):
        if not self.validate_theme(theme):
            theme = DEFAULT_THEME
        self.current_theme = theme
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        theme_file = os.path.join(base_path, f'{theme}.qss')
        if os.path.exists(theme_file):
            with open(theme_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        icon_file = os.path.join(base_path, 'assets', f'{theme}.png')
        if os.path.exists(icon_file):
            self.theme_button.setIcon(QIcon(icon_file))
        self.update_menu_icon()




    def save_theme(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write(self.current_theme)
        except Exception as e:
            print(f"Failed to save theme: {e}")




    def open_links_file(self):
        file_path = "links.txt"
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
        try:
            if os.name == "nt":
                os.startfile(file_path)
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            self.status_label.setText(f"Error opening file: {str(e)}")




    def start_download(self):
        self.download_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        link = self.url_input.text().strip()
        if link:
            links = [link]
        else:
            links = self.get_links_from_file()
            if not links:
                return
        quality_map = {
            "64kbps": "64",
            "128kbps": "128",
            "192kbps": "192",
            "320kbps": "320"
        }
        selected_quality = self.quality_dropdown.currentText()
        preferred_quality = quality_map.get(selected_quality, "192")
        self.status_label.setText("Starting download...")
        self.start_download_threads(links, preferred_quality)




    def get_links_from_file(self):
        file_path = "links.txt"
        if not os.path.exists(file_path):
            self.show_error("Error: links.txt not found.")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip()]
        if not links:
            self.show_error("No links found in links.txt.")
            return None
        if len(links) > MAX_LINKS:
            self.show_error(f"Error: Too many links! Limit is {MAX_LINKS}")
            return None
        return links
    



    def start_download_threads(self, links, quality):
        self.threads = []
        for link in links:
            if not self.validate_url(link):
                self.show_error(f"Invalid URL: {link}")
                continue
            download_thread = DownloadThread(link, self.output_folder, quality)
            download_thread.progress_signal.connect(self.update_progress)
            download_thread.error_signal.connect(self.show_error)
            download_thread.finished.connect(self.check_all_downloads_done)
            download_thread.start()
            self.threads.append(download_thread)




    def cancel_downloads(self):
        for thread in self.threads:
            thread.stop()
        self.status_label.setText("Download canceled")
        self.download_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        QTimer.singleShot(2500, lambda: self.status_label.setText("Waiting for input..."))




    def validate_url(self, url):
        return "youtube.com" in url or "youtu.be" in url
    



    def update_progress(self, message):
        self.status_label.setText(message)




    def show_error(self, message):
        self.status_label.setText(message)
        self.download_button.setEnabled(True)
        QTimer.singleShot(3000, lambda: self.status_label.setText("Waiting for input..."))




    def check_all_downloads_done(self):
        if all(not thread.isRunning() for thread in self.threads):
            self.download_button.setEnabled(True)
            self.status_label.setText("All downloads complete!")
            self.cancel_button.setVisible(False)
            QTimer.singleShot(3000, lambda: self.status_label.setText("Waiting for input..."))




    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.output_folder = folder
            self.status_label.setText(f"Saving to: {self.output_folder}")
    



def main():
    app = QApplication(sys.argv)
    icon_path = os.path.abspath("logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()