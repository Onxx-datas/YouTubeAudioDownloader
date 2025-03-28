# Importing required libraries
import yt_dlp  # YouTube downloader library
from pydub import AudioSegment  # Library for processing audio files
import os  # Library for interacting with the operating system (file handling)
import time  # Library for adding delays between downloads

def download_audio(video_url, output_folder="C:\\Users\\user\\Desktop\\Musics"): # Creating function to download mp3's
    ydl_opts = { # Define options for yt-dlp downloader
        'format': 'bestaudio/best',  # Select the best available audio format
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),  # Output filename format (title of the video)
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract the audio
            'preferredcodec': 'mp3',  # Convert the extracted audio to MP3 format
            'preferredquality': '192',  # Set the MP3 quality to 192kbps
        }],
    }
    
    try: # Tries below procedures ▼
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: # Using yt-dlp to download the audio
            ydl.download([video_url])  # Download the video and extract audio based on the above options
        print(f"Downloaded: {video_url}")  # Print success message after download completes
    except Exception as e: # Expecting specific error and ▼
        print(f"Error downloading {video_url}: {e}")  # Print specific error message if any issue occurs
def process_links(file_path="links.txt"): # Function to read video links from a file
    try: # Tries below code sections ▼
        with open(file_path, "r") as file: # Open the file containing YouTube video links
            links = file.readlines()  # Read all lines (each line contains a YouTube video URL)
        for link in links: # Iterate through each link in the file
            link = link.strip()  # Remove any leading/trailing spaces or newline characters
            if link:  # If the link is not empty
                download_audio(link)  # Call the function to download the audio
                time.sleep(4)  # Wait for 4 seconds before downloading the next video (to avoid being blocked)
    except FileNotFoundError: # Expecting FNFE and prints ▼
        print("Error: links.txt file not found.")  # Print an error message if the file is missing

if __name__ == "__main__": # Running the script
    process_links() # Start processing the links when the script is executed
