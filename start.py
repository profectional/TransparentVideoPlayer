import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QUrl
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QSettings
from moviepy.editor import VideoFileClip
from urllib.parse import unquote, urlparse
import re
import subprocess
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
import pyperclip
from yt_dlp import YoutubeDL

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
    VOLUME_MULTIPLIER = 2 
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Video Player')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.settings = QSettings("YourOrganization", "YourApplication")
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        # Create a playlist
        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        # Add all .mp4 files in the same directory to the playlist
        directory = os.path.dirname(os.path.realpath(__file__))
        mp4_files = [file for file in os.listdir(directory) if file.endswith(".mp4")]
        for i, file in enumerate(mp4_files, start=1):
          print(f"({i}) {file}")
        for file in os.listdir(directory):
            if file.endswith(".mp4"):
                url = QUrl.fromLocalFile(os.path.join(directory, file))
                self.playlist.addMedia(QMediaContent(url))
        print("Press r to replay the video, s to skip to the next video, p to go to the previous video, up to increase the window opacity, down to decrease the window opacity, w to increase the volume, e to decrease the volume, and space to pause/play the video")
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
        # Currently not working
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
            
        elif event.key() == Qt.Key_E:
            volume = self.mediaPlayer.volume() * self.VOLUME_MULTIPLIER
            volume -= 10
            self.mediaPlayer.setVolume(min(volume, 100))
            self.settings.setValue("volume", volume)

            # Write the change to a text file
            with open("changes.txt", "a") as f:
                f.write(f"Decreased volume of {url} by 10%\n")
        elif event.key() == Qt.Key_U:
             self.playlist.shuffle()

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

        # Create a playlist
        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

        # Add the YouTube video to the playlist
        ydl_opts = {'format': 'best'}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_url = info_dict.get('url', None)
            self.playlist.addMedia(QMediaContent(QUrl(video_url)))

        print("Press r to replay the video, s to skip to the next video, p to go to the previous video, up to increase the window opacity, down to decrease the window opacity, w to increase the volume, e to decrease the volume, and space to pause/play the video")
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
        # Currently not working
        elif event.key() == Qt.Key_U:
             self.playlist.shuffle()

        elif event.key() == Qt.Key_Space:  # Check if the pressed key is space
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()  # Pause the video
            else:
                self.mediaPlayer.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Ask the user for input
    choice = input("Enter 1 to run the video player, paste to play a YouTube link: ")

    if choice == '1':
        # Run the video player
        player = VideoPlayer()
        player.show()
    else:
        # If the user input is anything other than '1', treat it as a YouTube video URL
        player = YTVideoPlayer(choice)
        player.show()

    sys.exit(app.exec_())
