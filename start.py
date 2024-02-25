import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QUrl
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QSettings

class VideoPlayer(QWidget):
    VOLUME_MULTIPLIER = 1.1
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Video Player')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.settings = QSettings("YourOrganization", "YourApplication")
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        # Create a playlist
        self.playlist = QMediaPlaylist()

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
            self.playlist.previous()  # Go to the previous video
        elif event.key() == Qt.Key_Up:
            o = self.windowOpacity()
            self.setWindowOpacity(o+0.05)
        elif event.key() == Qt.Key_Down:
            o = self.windowOpacity()
            self.setWindowOpacity(o-0.05)
        
        elif event.key() == Qt.Key_E:
            volume = self.mediaPlayer.volume() * self.VOLUME_MULTIPLIER
            volume -= 10
            self.mediaPlayer.setVolume(min(volume, 100))
            self.settings.setValue("volume", volume)

            # Write the change to a text file
            with open("changes.txt", "a") as f:
                f.write(f"Decreased volume of {url} by 10%\n")

        elif event.key() == Qt.Key_Space:  # Check if the pressed key is space
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()  # Pause the video
            else:
                self.mediaPlayer.play()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
