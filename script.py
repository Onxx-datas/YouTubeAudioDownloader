from libs import os, time, yt_dlp, AudioSegment






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
        print("Starting next procedure...")
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