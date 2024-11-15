import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QSettings, pyqtSignal
from PyQt5.QtGui import QKeySequence
from moviepy.editor import VideoFileClip
from urllib.parse import unquote, urlparse
import re
import subprocess
import yt_dlp
from yt_dlp import YoutubeDL
import tkinter as tk
from datetime import timedelta
import threading
import glob
import time
from tkinter import simpledialog as sd

ydl_opts = {
    'writesubtitles': True,  # Write subtitle file
    'writeautomaticsub': True,  # Write automatic subtitle file (YouTube only)
    'subtitleslangs': ['en'],  # Languages of subtitles to download
    'skip_download': True,  # Skip downloading the video
}

'''
# Specify the path to the FFmpeg binary
ffmpeg_bin = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ffmpeg-master-latest-win64-gpl', 'bin', 'ffmpeg')

# Check if FFmpeg binary exists
if not os.path.isfile(ffmpeg_bin):
    print("FFmpeg binary not found. Please check the path.")
else:
    # Ask the user if they want to convert all MP4 files
    answer = input("Do you want to convert all MP4 files to H.264 (yes/no)? ")

    if answer.lower() == "yes":
        # Get a list of all MP4 files in the current directory
        files = [f for f in os.listdir('.') if f.endswith('.mp4')]

        for file in files:
            # Construct the output file name
            output_file = os.path.splitext(file)[0] + '_converted.mp4'

            # Skip if the file has already been converted
            if os.path.isfile(output_file):
                print(f"File {file} has already been converted. Skipping.")
                continue

            # Construct the FFmpeg command
            command = [ffmpeg_bin, '-i', file, '-c:v', 'libx264', '-c:a', 'aac', output_file]

            # Run the command
            subprocess.run(command)

            # Delete the original file
            os.remove(file)
    else:
        print("No files were converted.")
'''

class VideoPlayer(QWidget):
    # This is a constant that is used to adjust the volume level of the media player.
    VOLUME_MULTIPLIER = 2 

    def __init__(self):
        super().__init__()

        # Set the window title to 'Video Player'.
        self.setWindowTitle('Video Player')

        # Set the window flags to always stay on top and ignore user input.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)

        # Create a QSettings object to store application settings.
        self.settings = QSettings("YourOrganization", "YourApplication")

        # Create a QMediaPlayer object with a video surface.
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create a QVideoWidget object to display the video.
        self.videoWidget = QVideoWidget()

        # Create a QMediaPlaylist object to manage a playlist of media content.
        self.playlist = QMediaPlaylist()

        # Set the playback mode of the playlist to loop.
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        # Get the directory of the current file.
        current_directory = os.path.dirname(os.path.realpath(__file__))
        def add_files_to_playlist(directory):
            file_toltal = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".mp4") or file.endswith(".webp"):
                        full_path = os.path.join(root, file)
                        file_toltal += 1
                        print(f"Adding No.{file_toltal}: ( {full_path} ) to playlist")
                        url = QUrl.fromLocalFile(full_path)
                        self.playlist.addMedia(QMediaContent(url))

        # Get the directory of the current file.
        current_directory = os.path.dirname(os.path.realpath(__file__))

        root = tk.Tk()
        root.withdraw()

        settings = QSettings("anon", "transparent_video_player")
        target_directory = settings.value("directory")
        if target_directory is None:
            target_directory = sd.askstring("Input", "Enter the directory for your music ex: C:/Users/username/Music:")
            settings.setValue("directory", target_directory)

        # Add files from the current directory to the playlist.
        add_files_to_playlist(current_directory)

        # Add files from the targeted directory to the playlist.
        add_files_to_playlist(target_directory)

        print("Press r to replay the video, s to skip to the next video, p to go to the previous video, up to increase the window opacity, down to decrease the window opacity, w to increase the volume, e to decrease the volume, u to shuffle, and space to pause/play the video")

        # Set the playlist for the media player.
        self.mediaPlayer.setPlaylist(self.playlist)

        # Set the video output of the media player to the video widget.
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Start playing the media content.
        self.mediaPlayer.play()

        # Create a QVBoxLayout object to manage the layout of the widget.
        self.layout = QVBoxLayout()

        # Add the video widget to the layout.
        self.layout.addWidget(self.videoWidget)

        # Set the layout of the widget.
        self.setLayout(self.layout)

        # Get the volume setting from the QSettings object.
        volume = self.settings.value("volume", 50, type=int)

        # Set the volume of the media player.
        self.mediaPlayer.setVolume(int(volume / self.VOLUME_MULTIPLIER))  # Convert to int

        # Remove margins
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Make the window full screen
        self.showFullScreen()

        # Set the window opacity to 50%
        self.setWindowOpacity(0.5)

    def get_position(self):
        return self.mediaPlayer.position()
    def set_position(self, position):
        self.mediaPlayer.setPosition(position)
        
    # Override keyPressEvent
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        elif event.key() == Qt.Key_R:
            self.playlist.setCurrentIndex(0)
            self.mediaPlayer.play()
        elif event.key() == Qt.Key_S:
            self.playlist.next()
        elif event.key() == Qt.Key_P:
            self.playlist.previous()
        elif event.key() == Qt.Key_Up:
            o = self.windowOpacity()
            self.setWindowOpacity(o+0.05)
        elif event.key() == Qt.Key_Down:
            o = self.windowOpacity()
            self.setWindowOpacity(o-0.05)

        elif event.key() == Qt.Key_W:
            # Get the URL of the current media item
            url = self.playlist.currentMedia().canonicalUrl().toString()

            # Convert the file URL to a normal file path
            path = unquote(urlparse(url).path)

            # Convert the file URL to a normal file path
            path = unquote(urlparse(url).path)

            # Remove leading slash if on Windows
            if os.name == 'nt' and path.startswith('/'):
                path = path[1:]

            # Load the video
            clip = VideoFileClip(path)

            # Increase the volume by 10%
            clip = clip.volumex(self.VOLUME_MULTIPLIER)

            # Write the result to a file
            new_path = path.replace(".mp4", "_louder.mp4")
            clip.write_videofile(new_path)

            # Load the new video into the media player
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(new_path)))
            self.playlist.setCurrentIndex(0)
            self.mediaPlayer.play()
            # Write the change to a text file
            with open("changes.txt", "a", encoding="utf-8") as f:
                f.write(f"Increased volume of {url} by 10%\n")
            
        elif event.key() == Qt.Key_Z:
            volume = self.mediaPlayer.volume() * self.VOLUME_MULTIPLIER
            volume -= 10
            self.mediaPlayer.setVolume(min(volume, 100))
            self.settings.setValue("volume", volume)

        elif event.key() == Qt.Key_X:
            volume = self.mediaPlayer.volume() * self.VOLUME_MULTIPLIER
            volume += 10
            self.mediaPlayer.setVolume(min(volume, 100))
            self.settings.setValue("volume", volume)

            # Write the change to a text file
            with open("changes.txt", "a") as f:
                f.write(f"Decreased volume of {url} by 10%\n")
        elif event.key() == Qt.Key_U:
             self.playlist.shuffle()
        elif event.key() == Qt.Key_Right:
            new_position = self.get_position() + 5000
            if new_position <= self.mediaPlayer.duration():
                self.set_position(new_position)
        elif event.key() == Qt.Key_Left:
            new_position = max(self.get_position() - 5000, 0)
            if new_position >= 0:
                self.set_position(new_position)

        elif event.key() == Qt.Key_1:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.1
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_2:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.2
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_3:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.3
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_4:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.4
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_5:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.5
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_6:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.6
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_7:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.7
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_8:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.8
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_9:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.9
            self.set_position(int(round(new_position)))

        elif event.key() == Qt.Key_Space:  # Check if the pressed key is space
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()  # Pause the video
            else:
                self.mediaPlayer.play()

class YTVideoPlayer(QWidget):
    VOLUME_MULTIPLIER = 2 
    def __init__(self, video_url):
        super().__init__()
        self.setWindowTitle('YouTube Video Player')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.settings = QSettings("YourOrganization", "YourApplication")
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.page_url = video_url  # YouTube page URL
        # Create a playlist
        self.playlist = QMediaPlaylist()
        self.YTplaylist = []
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        ydl_opts = {
            'format': 'best',  # Updated format syntax
        }

        self.index_of_list = video_url.find("list")
        if self.index_of_list != -1:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                entries = info_dict.get('entries', [])
                for entry in entries:
                    video_url = entry.get('url', None)
                    if video_url:
                        self.playlist.addMedia(QMediaContent(QUrl(video_url)))
        else:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                video_url = info_dict.get('url', None)
                self.playlist.addMedia(QMediaContent(QUrl(video_url)))

        print("Press d to download the video, r to replay the video, s to skip to the next video, p to go to the previous video, up_arrow/down to increase/decrease the window opacity, z/x to lower/incr volume, w to make a new clone file then increase the volume PERMARNETLY for that file, and space to pause/play the video")
        # Set the playlist for the media player
        self.mediaPlayer.setPlaylist(self.playlist)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.play()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.videoWidget)
        self.setLayout(self.layout)

        volume = self.settings.value("volume", 50, type=int)
        self.mediaPlayer.setVolume(int(volume / self.VOLUME_MULTIPLIER))  # Convert to int

        # Remove margins
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Make the window full screen
        self.showFullScreen()

        # Set the window opacity to 50%
        self.setWindowOpacity(0.5)


    def get_position(self):
        return self.mediaPlayer.position()

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pid = os.getpid()
            os.kill(pid, 9)
            QApplication.quit()
        elif event.key() == Qt.Key_C:
            self.subtitle_loaded = threading.Event()
            self.set_position(0)
            self.mediaPlayer.pause()

            def run_app():
                self.app = self.subtitle_reader(choice)

            # Create a new thread for the Tkinter app
            app_thread = threading.Thread(target=run_app)
            app_thread.start()
            self.subtitle_loaded.wait()
            self.mediaPlayer.play()

        elif event.key() == Qt.Key_Z:
            volume = self.mediaPlayer.volume() * self.VOLUME_MULTIPLIER
            volume -= 10
            self.mediaPlayer.setVolume(min(volume, 100))
            self.settings.setValue("volume", volume)

        elif event.key() == Qt.Key_X:
            volume = self.mediaPlayer.volume() * self.VOLUME_MULTIPLIER
            volume += 10
            self.mediaPlayer.setVolume(min(volume, 100))
            self.settings.setValue("volume", volume)
            
        elif event.key() == Qt.Key_D: # download the video
            def download():
                print(f"Downloading video: {self.page_url}")
                ydl_opts = {
                    'quiet': False
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.page_url])
            threading.Thread(target=download, daemon=False).start()

        elif event.key() == Qt.Key_S:
            self.playlist.next()
        elif event.key() == Qt.Key_P:
            self.playlist.previous()
        elif event.key() == Qt.Key_Up:
            o = self.windowOpacity()
            self.setWindowOpacity(o+0.05)
        elif event.key() == Qt.Key_Down:
            o = self.windowOpacity()
            self.setWindowOpacity(o-0.05)
        # Currently not working
        elif event.key() == Qt.Key_U:
             self.playlist.shuffle()
        elif event.key() == Qt.Key_R:
             self.set_position(0)
        elif event.key() == Qt.Key_Right:
            new_position = self.get_position() + 5000
            if new_position <= self.mediaPlayer.duration():
                self.set_position(new_position)
        elif event.key() == Qt.Key_Left:
            new_position = max(self.get_position() - 5000, 0)
            if new_position >= 0:
                self.set_position(new_position)
        elif event.key() == Qt.Key_Space:
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
            else:
                self.mediaPlayer.play()
        elif event.key() == Qt.Key_1:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.1
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_2:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.2
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_3:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.3
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_4:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.4
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_5:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.5
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_6:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.6
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_7:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.7
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_8:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.8
            self.set_position(int(round(new_position)))
        elif event.key() == Qt.Key_9:
            video_length = self.mediaPlayer.duration()
            new_position = video_length * 0.9
            self.set_position(int(round(new_position)))


    def subtitle_reader(self, choice):
        ydl_opts = {
            'writesubtitles': True,  # Write subtitle file
            'writeautomaticsub': True,  # Write automatic subtitle file (YouTube only)
            'subtitleslangs': ['en'],  # Languages of subtitles to download
            'skip_download': True,  # Skip downloading the video
        }

        def get_sub(choice):
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(choice, download=True)
                video_title = info_dict.get('title', None)
                return video_title

        def detect_format(subtitle_file):
            with open(subtitle_file, 'r') as file:
                first_line = file.readline().strip()
            print(f"First line of the file: {first_line}")  # Print the first line of the file
            format = 'WEBVTT' if first_line.startswith('WEBVTT') else 'SRT'
            print(f"Detected format: {format}")  # Print the detected format
            return format

        def load_subtitles(subtitle_file):
            format = detect_format(subtitle_file)
            if format == 'WEBVTT':
                return load_webvtt_subtitles(subtitle_file)
            else:
                return load_srt_subtitles(subtitle_file)

        def load_srt_subtitles(subtitle_file):
            print("Loading SRT subtitles...")
            with open(subtitle_file, 'r') as file:
                data = file.read().split('\n\n')[1:]  # Skip the first line
                subtitles = [(parse_time(sub.split('\n')[0].split(' --> ')[0]), '\n'.join(sub.split('\n')[1:])) for sub in data if sub]
            return subtitles

        def load_webvtt_subtitles(subtitle_file):
            print("Loading WEBVTT subtitles...")

            # Open the subtitle file in read mode.
            with open(subtitle_file, 'r') as file:
                # Read the entire file, split it into chunks by double newlines, and skip the first two chunks.
                data = file.read().split('\n\n')[2:]

                # Initialize an empty list to store the subtitles.
                subtitles = []

                # Iterate over each chunk in the data.
                for sub in data:
                    # Split the chunk into lines, ignoring lines that start with 'align:' or 'position:'.
                    lines = [line for line in sub.split('\n') if not line.startswith(('align:', 'position:'))]

                    # If there are at least two lines and the first line contains '-->', it's a subtitle line.
                    if len(lines) >= 2 and '-->' in lines[0]:
                        # Parse the timestamp from the first line.
                        time = parse_time(lines[0].split(' --> ')[0])

                        # Join the remaining lines into a single string, ignoring lines that start with '<'.
                        text = '\n'.join(line for line in lines[1:] if not line.startswith('<'))

                        # Remove nested timestamps from the text.
                        text = re.sub(r'<\d\d:\d\d:\d\d.\d\d\d>', '', text)

                        # Remove <c> tags from the text.
                        text = re.sub(r'<c>', '', text)

                        # Remove </c> tags from the text.
                        text = re.sub(r'</c>', '', text)

                        # Append the timestamp and text as a tuple to the subtitles list.
                        subtitles.append((time, text))

            # Return the list of subtitles.
            return subtitles

        def parse_time(time_str):
            h, m, s = map(float, time_str.split(':'))
            return timedelta(hours=h, minutes=m, seconds=s).total_seconds() * 1000
#    def get_position(self):
#        return self.mediaPlayer.position()

#    def set_position(self, position):
#        self.mediaPlayer.setPosition(position)
        def display_next_subtitle():
            if subtitles:
                time, text = subtitles.pop(0)
                for _ in range(1):  # Display 2 subtitles at once
                    if subtitles:
                        _, extra_text = subtitles.pop(0)
                        text += '\n' + extra_text
                label.config(text=text)
                if subtitles:  # Check if there are more subtitles
                    next_time, _ = subtitles[0]
                    delay = round(next_time - time)  # Round the delay to the nearest millisecond
                else:
                    delay = 0
                root.after(int(delay), display_next_subtitle)

        root = tk.Tk()
        root.overrideredirect(True)
        # Get screen width and height + window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = root.winfo_reqwidth()
        window_height = root.winfo_reqheight()

        # Calculate offsets
        OFFSET_X = (screen_width - window_width) // 2
        OFFSET_Y = screen_height - window_height

        # Position the window
        root.geometry(f'+{OFFSET_X}+{OFFSET_Y}')
        root.lift()
        root.wm_attributes('-topmost', True)
        root.wm_attributes('-disabled', True)
        SACRIFICIAL_COLOR = 'white'  # or any other color that you won't use in your window

        # Set the sacrificial color as the window background and the transparent color
        root.config(bg=SACRIFICIAL_COLOR)
        root.wm_attributes('-transparentcolor', SACRIFICIAL_COLOR)

        label = tk.Label(root, bg=SACRIFICIAL_COLOR)
        label.config(fg='#39FF14')
        label.config(font=('Arial', 20))
        label.pack()
        sub_name = get_sub(choice)
        subtitle_file = glob.glob(sub_name + '*.vtt')[0]
        subtitles = load_subtitles(subtitle_file)
        self.subtitle_loaded.set()
        display_next_subtitle()
        root.mainloop()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Ask the user for input
    choice = input("Enter 1 to run the video player, paste to play a YouTube link: ")

    if choice == '1':
        # Run the video player
        player1 = VideoPlayer()
        player1.show()
    else:
        player2 = YTVideoPlayer(choice)

    sys.exit(app.exec_())
