from pytube import YouTube
from pydub import AudioSegment
import os

# Function to download audio from a YouTube link
def download_audio(video_url, output_folder="downloads"):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Download audio
        temp_file = audio_stream.download(output_folder)
        base, ext = os.path.splitext(temp_file)
        mp3_file = base + ".mp3"

        # Convert to MP3 using pydub
        audio = AudioSegment.from_file(temp_file)
        audio.export(mp3_file, format="mp3")
        
        # Remove original audio file
        os.remove(temp_file)

        print(f"Downloaded: {yt.title} -> {mp3_file}")
    except Exception as e:
        print(f"Error downloading {video_url}: {e}")

# Read links from file and download
def process_links(file_path="links.txt"):
    try:
        with open(file_path, "r") as file:
            links = file.readlines()

        for link in links:
            link = link.strip()
            if link:
                download_audio(link)
    except FileNotFoundError:
        print("Error: links.txt file not found.")

# Run the script
if __name__ == "__main__":
    process_links()
