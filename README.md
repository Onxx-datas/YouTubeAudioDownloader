# 🎧 YouTubeAudioDownloader

A Python desktop app to extract audio from YouTube videos. Built with **PyQt6**, styled with **QSS**, and packed with smart features like batch downloading, theme switching, and format selection.

> ⚠️ This project is still in active development! Bugs or incomplete features may exist. Use at your own risk.

---

## ✨ Features

- 🎵 Download audio from YouTube videos
- 📁 Choose audio format: MP3, WAV, AAC, or OGG
- 📂 Batch downloads via `links.txt`
- 🌘 Light & Dark theme support
- 🔁 Auto-renames duplicate files to avoid overwrite
- 📜 Download history panel (burger menu)
- 🛡️ Planned password protection

---

## 🧰 Tech Stack

- Python 3.10+
- PyQt6
- pytube
- ffmpeg (recommended for format conversion)

---

## 📦 Installation

```bash
git clone https://github.com/Onxx-datas/YouTubeAudioReceiver.git
cd YouTubeAudioReceiver
pip install -r requirements.txt
python main.py
