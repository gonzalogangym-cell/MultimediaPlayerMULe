
import sys
import os

# ================================
# PYQT5 IMPORTS (GUI)
# ================================
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QShortcut
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent, QKeySequence

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
        self.pending_seek_ms = 0
        self.is_muted = False
        self.last_volume_before_mute = 50

        # Build the interface
        self.setup_ui()

        # Timer to update UI (progress bar + time)
        self.timer = QTimer(self)
        self.timer.setInterval(500)  # update every 500 ms
        self.timer.timeout.connect(self.update_ui)

        # Debounced seek timer to avoid flooding VLC with many seeks.
        self.seek_timer = QTimer(self)
        self.seek_timer.setSingleShot(True)
        self.seek_timer.setInterval(150)
        self.seek_timer.timeout.connect(self.apply_pending_seek)

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

        self.mute_button = QPushButton("Mute")
        self.mute_button.clicked.connect(self.toggle_mute)
        buttons_layout.addWidget(self.mute_button)

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
        info_label = QLabel("Shortcuts: Space play/pause, Left/Right seek 10s, M mute, R restart, F full screen, Esc exit")
        main_layout.addWidget(info_label)

        central_widget.setLayout(main_layout)

        # Set initial volume
        self.player.audio_set_volume(50)
        self.apply_dark_theme()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        self.shortcut_space = QShortcut(QKeySequence(Qt.Key_Space), self)
        self.shortcut_space.setContext(Qt.ApplicationShortcut)
        self.shortcut_space.activated.connect(self.toggle_play_pause)

        self.shortcut_right = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut_right.setContext(Qt.ApplicationShortcut)
        self.shortcut_right.activated.connect(lambda: self.seek_relative_ms(10000))

        self.shortcut_left = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut_left.setContext(Qt.ApplicationShortcut)
        self.shortcut_left.activated.connect(lambda: self.seek_relative_ms(-10000))

        self.shortcut_mute = QShortcut(QKeySequence(Qt.Key_M), self)
        self.shortcut_mute.setContext(Qt.ApplicationShortcut)
        self.shortcut_mute.activated.connect(self.toggle_mute)

        self.shortcut_restart = QShortcut(QKeySequence(Qt.Key_R), self)
        self.shortcut_restart.setContext(Qt.ApplicationShortcut)
        self.shortcut_restart.activated.connect(self.restart_media)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #12161d;
                color: #e6e9ef;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 13px;
            }
            QLabel {
                color: #d6dbea;
            }
            QPushButton {
                background-color: #1f2630;
                color: #f2f4f8;
                border: 1px solid #2f3a4a;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #2a3340;
            }
            QPushButton:pressed {
                background-color: #364256;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 8px;
                background: #2b3340;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4ba3ff;
                border: none;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #3f7fbf;
                border-radius: 4px;
            }
        """)

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

    def restart_media(self):
        if not self.current_file:
            return
        self.pending_seek_ms = 0
        if self.player.get_state() == vlc.State.Ended:
            # In Ended state VLC can ignore set_time(0), so reload media first.
            self.load_media(self.current_file)
            self.player.play()
            self.timer.start()
            QTimer.singleShot(120, lambda: self.player.set_time(0))
        else:
            self.player.set_time(0)
        self.position_slider.setValue(0)
        self.current_time_label.setText("00:00")
        if not self.player.is_playing():
            self.play_media()

    def toggle_play_pause(self):
        if not self.current_file:
            return
        if self.player.is_playing():
            self.pause_media()
        else:
            self.play_media()

    def toggle_mute(self):
        self.is_muted = not self.is_muted

        if self.is_muted:
            self.last_volume_before_mute = self.volume_slider.value()
            self.player.audio_set_mute(True)
            self.volume_slider.setValue(0)
            self.mute_button.setText("Unmute")
        else:
            self.player.audio_set_mute(False)
            self.volume_slider.setValue(self.last_volume_before_mute)
            self.mute_button.setText("Mute")

    def seek_relative_ms(self, delta_ms):
        if not self.current_file:
            return
        self.pending_seek_ms += delta_ms
        if not self.seek_timer.isActive():
            self.seek_timer.start()

    def apply_pending_seek(self):
        if not self.current_file or self.pending_seek_ms == 0:
            return

        total_ms = self.player.get_length()
        current_ms = self.player.get_time()
        if current_ms < 0 and total_ms > 0:
            current_ms = int((self.position_slider.value() / 1000) * total_ms)
        current_ms = max(0, current_ms)

        seek_delta = self.pending_seek_ms
        target_ms = current_ms + seek_delta
        self.pending_seek_ms = 0

        if total_ms > 0:
            # Avoid exact end-of-stream, which can leave VLC in a sticky end state.
            end_guard_ms = 300
            max_target = max(0, total_ms - end_guard_ms)
            target_ms = min(max(0, target_ms), max_target)
        else:
            target_ms = max(0, target_ms)

        if self.player.get_state() == vlc.State.Ended:
            if seek_delta > 0:
                # At end-of-video, forward seek should not trigger reload/scene changes.
                return
            # VLC may ignore backward seeks in Ended state. Reload media to unlock.
            self.load_media(self.current_file)
            self.player.play()
            self.timer.start()
            def seek_after_reload(t=int(target_ms), total=total_ms):
                self.player.set_time(t)
                if total > 0:
                    slider_value = int((t / total) * 1000)
                    self.position_slider.blockSignals(True)
                    self.position_slider.setValue(slider_value)
                    self.position_slider.blockSignals(False)
            QTimer.singleShot(120, seek_after_reload)
            return

        self.player.set_time(int(target_ms))

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

        state = self.player.get_state()
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

        # If playback is very close to the end, show a full progress bar in UI.
        # VLC may stop a little before the exact end timestamp.
        close_to_end = total_ms > 0 and current_ms >= total_ms - 1000
        near_end_stopped = (
            total_ms > 0
            and state in (vlc.State.Ended, vlc.State.Stopped)
            and self.position_slider.value() >= 970
        )
        if close_to_end or near_end_stopped:
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(1000)
            self.position_slider.blockSignals(False)
            self.current_time_label.setText(self.format_time(total_ms))

        if state == vlc.State.Ended and total_ms > 0:
            # Keep UI consistent at the end of playback.
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(1000)
            self.position_slider.blockSignals(False)
            self.current_time_label.setText(self.format_time(total_ms))

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
