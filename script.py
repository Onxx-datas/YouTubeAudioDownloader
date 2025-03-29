from libs import os, time, yt_dlp, AudioSegment, socket, urllib






def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        title = d.get('filename', 'Unknown Song').split("\\")[-1].replace(".webm", "").replace(".mp4", "")
        print(f"\r{title} {percent} downloading", end="", flush=True)
    if d['status'] == 'finished':
        title = d.get('filename', 'Unknown Song').split("\\")[-1].replace(".webm", "").replace(".mp4", "")
        print(f"\n{title} Downloaded Completely!")






def download_audio(video_url, output_folder="C:\\Users\\user\\Desktop\\Musics"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'concurrent_fragment_downloads': 5,
        'quiet': True,
        'noprogress': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook], 
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("Waiting for next link...")
    except socket.timeout:
        print(f"Network error: Timeout while downloading {video_url}. Retrying in 10 seconds...")
        time.sleep(10)
        download_audio(video_url, output_folder)
    except urllib.error.URLError:
        print(f"Network Error: Could not reach YouTube for {video_url}. Check your internet connection.")
    except yt_dlp.utils.ExtractorError:
        print(f"Error: The video {video_url} is unavailable (private or removed). Skipping...")
    except yt_dlp.utils.DownloadError:
        print(f"Error: Failed to download {video_url}. It may be restricted.")
    except FileNotFoundError:
        print(f"Error: Output folder '{output_folder}' not found. Check folder path.")
    except PermissionError:
        print(f"Error: No permission to save files in '{output_folder}'. Try another location.")
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