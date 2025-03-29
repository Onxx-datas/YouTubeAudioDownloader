from libs import os, time, yt_dlp, socket, urllib, tkinter as tk
from tkinter import messagebox, filedialog

# Default output folder
output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Musics")
os.makedirs(output_folder, exist_ok=True)

# GUI Window
root = tk.Tk()
root.title("YouTube Audio Downloader")
root.geometry("500x300")

# Function to update the GUI label dynamically
def update_status(text):
    status_label.config(text=text)
    root.update_idletasks()

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        title = d.get('filename', 'Unknown Song').split("\\")[-1].replace(".webm", "").replace(".mp4", "")
        update_status(f"{title} {percent} downloading")
    if d['status'] == 'finished':
        title = d.get('filename', 'Unknown Song').split("\\")[-1].replace(".webm", "").replace(".mp4", "")
        update_status(f"{title} Downloaded Completely!")

def download_audio():
    video_url = url_entry.get().strip()
    if not video_url:
        messagebox.showwarning("Warning", "Please enter a YouTube URL!")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
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
        update_status("Starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        messagebox.showinfo("Success", "Download Completed!")
        update_status("Download Ready!")
    except socket.timeout:
        messagebox.showerror("Error", "Network Timeout. Please check your connection.")
        update_status("Network Timeout.")
    except urllib.error.URLError:
        messagebox.showerror("Error", "Could not reach YouTube. Check your internet connection.")
        update_status("Connection Failed.")
    except yt_dlp.utils.ExtractorError:
        messagebox.showerror("Error", "Video is unavailable (private or removed).")
        update_status("Video Unavailable.")
    except yt_dlp.utils.DownloadError:
        messagebox.showerror("Error", "Failed to download. It may be restricted.")
        update_status("Download Failed.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
        update_status("Unexpected Error.")

def select_folder():
    global output_folder
    folder = filedialog.askdirectory()
    if folder:
        output_folder = folder
        folder_label.config(text=f"Saving to: {output_folder}")

# UI Elements
tk.Label(root, text="Enter YouTube Video URL:", font=("Arial", 12)).pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

download_btn = tk.Button(root, text="Download MP3", command=download_audio, font=("Arial", 12), bg="green", fg="white")
download_btn.pack(pady=10)

folder_btn = tk.Button(root, text="Select Save Folder", command=select_folder, font=("Arial", 10))
folder_btn.pack(pady=5)

folder_label = tk.Label(root, text=f"Saving to: {output_folder}", font=("Arial", 10), fg="gray")
folder_label.pack(pady=5)

status_label = tk.Label(root, text="Waiting for input...", font=("Arial", 12), fg="blue")
status_label.pack(pady=10)

# Start GUI
root.mainloop()
