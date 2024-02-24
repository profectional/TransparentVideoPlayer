import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QKeySequence

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Video Player')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        # Create a playlist
        self.playlist = QMediaPlaylist()

        # Add all .mp4 files in the same directory to the playlist
        directory = os.path.dirname(os.path.realpath(__file__))
        for file in os.listdir(directory):
            if file.endswith(".mp4"):
                url = QUrl.fromLocalFile(os.path.join(directory, file))
                self.playlist.addMedia(QMediaContent(url))

        # Set the playlist for the media player
        self.mediaPlayer.setPlaylist(self.playlist)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.play()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.videoWidget)
        self.setLayout(self.layout)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())