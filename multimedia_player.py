
import sys
import os

# ================================
# PYQT5 IMPORTS (GUI)
# ================================
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent

# ================================
# DETECT VLC PATH (WINDOWS ONLY)
# ================================
# This allows Python to find VLC's internal DLLs (libvlc.dll)
if sys.platform == "win32":
    if os.path.exists(r"C:\Program Files\VideoLAN\VLC"):
        os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
    elif os.path.exists(r"C:\Program Files (x86)\VideoLAN\VLC"):
        os.add_dll_directory(r"C:\Program Files (x86)\VideoLAN\VLC")

# Import VLC (multimedia backend)
import vlc


# ================================
# MAIN PLAYER CLASS
# ================================
class MultimediaPlayer(QMainWindow):

    def __init__(self):
        super().__init__()

        # Create VLC instance
        self.instance = vlc.Instance()

        # Create VLC media player
        self.player = self.instance.media_player_new()

        # State variables
        self.current_file = None
        self.is_fullscreen = False

        # Build the interface
        self.setup_ui()

        # Timer to update UI (progress bar + time)
        self.timer = QTimer(self)
        self.timer.setInterval(500)  # update every 500 ms
        self.timer.timeout.connect(self.update_ui)

    # ================================
    # CREATE USER INTERFACE
    # ================================
    def setup_ui(self):

        self.setWindowTitle("Simple Multimedia Player")
        self.setGeometry(100, 100, 1100, 750)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # ================================
        # FILE NAME LABEL
        # ================================
        self.file_label = QLabel("No file loaded")
        main_layout.addWidget(self.file_label)

        # ================================
        # VIDEO DISPLAY AREA
        # ================================
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumHeight(550)
        main_layout.addWidget(self.video_frame, 1)

        # ================================
        # OPEN FILE BUTTON
        # ================================
        open_layout = QHBoxLayout()

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_file)
        open_layout.addWidget(self.open_button)

        main_layout.addLayout(open_layout)

        # ================================
        # CONTROL BUTTONS
        # ================================
        buttons_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_media)
        buttons_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_media)
        buttons_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_media)
        buttons_layout.addWidget(self.stop_button)

        # Fullscreen button
        self.fullscreen_button = QPushButton("Full Screen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        buttons_layout.addWidget(self.fullscreen_button)

        main_layout.addLayout(buttons_layout)

        # ================================
        # PROGRESS BAR (TIMELINE)
        # ================================
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        main_layout.addWidget(self.position_slider)

        # ================================
        # TIME LABELS (CURRENT / TOTAL)
        # ================================
        time_layout = QHBoxLayout()

        self.current_time_label = QLabel("00:00")
        time_layout.addWidget(self.current_time_label)

        time_layout.addStretch()

        self.duration_label = QLabel("00:00")
        time_layout.addWidget(self.duration_label)

        main_layout.addLayout(time_layout)

        # ================================
        # VOLUME CONTROL
        # ================================
        volume_layout = QHBoxLayout()

        volume_text = QLabel("Volume:")
        volume_layout.addWidget(volume_text)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("50%")
        volume_layout.addWidget(self.volume_label)

        main_layout.addLayout(volume_layout)

        # ================================
        # INFO LABEL (SHORTCUTS)
        # ================================
        info_label = QLabel("Shortcut: press F for full screen, Esc to exit")
        main_layout.addWidget(info_label)

        central_widget.setLayout(main_layout)

        # Set initial volume
        self.player.audio_set_volume(50)

    # ================================
    # OPEN FILE DIALOG
    # ================================
    def open_file(self):

        file_filter = "Media Files (*.mp3 *.mp4 *.wav *.avi *.mkv *.mov);;All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Media File",
            "",
            file_filter
        )

        if file_path:
            self.load_media(file_path)

    # ================================
    # LOAD MEDIA INTO VLC
    # ================================
    def load_media(self, file_path):

        self.current_file = file_path

        # Show file name
        file_name = os.path.basename(file_path)
        self.file_label.setText(f"File: {file_name}")

        # Create VLC media object
        media = self.instance.media_new(file_path)
        self.player.set_media(media)

        # Attach video output to PyQt widget
        win_id = int(self.video_frame.winId())

        if sys.platform.startswith("linux"):
            self.player.set_xwindow(win_id)
        elif sys.platform == "win32":
            self.player.set_hwnd(win_id)
        elif sys.platform == "darwin":
            self.player.set_nsobject(win_id)

    # ================================
    # PLAY / PAUSE / STOP
    # ================================
    def play_media(self):
        if self.current_file:
            self.player.play()
            self.timer.start()

    def pause_media(self):
        self.player.pause()

    def stop_media(self):
        self.player.stop()
        self.timer.stop()
        self.position_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.duration_label.setText("00:00")

    # ================================
    # VOLUME CONTROL
    # ================================
    def change_volume(self, value):
        self.player.audio_set_volume(value)
        self.volume_label.setText(f"{value}%")

    # ================================
    # SEEK POSITION (SLIDER)
    # ================================
    def set_position(self, value):
        # VLC uses values from 0.0 to 1.0
        self.player.set_position(value / 1000)

    # ================================
    # UPDATE UI (TIME + SLIDER)
    # ================================
    def update_ui(self):

        position = self.player.get_position()

        if position >= 0:
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(int(position * 1000))
            self.position_slider.blockSignals(False)

        current_ms = self.player.get_time()
        total_ms = self.player.get_length()

        if current_ms >= 0:
            self.current_time_label.setText(self.format_time(current_ms))

        if total_ms >= 0:
            self.duration_label.setText(self.format_time(total_ms))

    # ================================
    # FORMAT TIME (MM:SS)
    # ================================
    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    # ================================
    # FULLSCREEN TOGGLE
    # ================================
    def toggle_fullscreen(self):

        if self.is_fullscreen:
            self.showNormal()
            self.fullscreen_button.setText("Full Screen")
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.fullscreen_button.setText("Exit Full Screen")
            self.is_fullscreen = True

    # ================================
    # KEYBOARD SHORTCUTS
    # ================================
    def keyPressEvent(self, event: QKeyEvent):

        if event.key() == Qt.Key_F:
            self.toggle_fullscreen()

        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()

        else:
            super().keyPressEvent(event)


# ================================
# MAIN FUNCTION
# ================================
def main():
    app = QApplication(sys.argv)
    window = MultimediaPlayer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
