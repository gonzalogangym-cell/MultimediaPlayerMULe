
import sys
import os
import json
import subprocess

# ================================
# PYQT5 IMPORTS (GUI)
# ================================
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QShortcut, QMessageBox
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

        # Detect ffprobe availability for technical metadata extraction
        self.ffprobe_executable = self.find_ffprobe_executable()

        # State variables
        self.current_file = None
        self.is_fullscreen = False
        self.pending_seek_ms = 0
        self.is_muted = False
        self.last_volume_before_mute = 50
        self.playback_speeds = [1.0, 2.0, 0.5]
        self.playback_speed_index = 0
        self.texture_colors = ["#2f3a4a", "#0f5f1f", "#7a1f1f", "#153d8a"]
        self.texture_labels = ["Default", "Green", "Red", "Blue"]
        self.texture_index = 0

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

        self.setWindowTitle("Multimedia Player MULe")
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
        self.video_container = QWidget()
        video_layout = QVBoxLayout()
        video_layout.setContentsMargins(8, 8, 8, 8)
        self.video_container.setLayout(video_layout)

        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setMinimumHeight(550)
        video_layout.addWidget(self.video_frame)
        main_layout.addWidget(self.video_container, 1)

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

        self.speed_button = QPushButton("Speed x1")
        self.speed_button.clicked.connect(self.cycle_playback_speed)
        buttons_layout.addWidget(self.speed_button)

        self.texture_button = QPushButton("Texture: Default")
        self.texture_button.clicked.connect(self.cycle_texture)
        buttons_layout.addWidget(self.texture_button)

        self.info_button = QPushButton("Info")
        self.info_button.clicked.connect(self.show_media_info)
        buttons_layout.addWidget(self.info_button)

        self.export_button = QPushButton("Export Info")
        self.export_button.clicked.connect(self.export_media_info)
        buttons_layout.addWidget(self.export_button)

        self.academic_button = QPushButton("Academic Analysis")
        self.academic_button.clicked.connect(self.show_academic_analysis)
        buttons_layout.addWidget(self.academic_button)

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
        info_label = QLabel("Shortcuts: Space play/pause, Left/Right seek 10s, M mute, R restart, S speed, T texture, F full screen, Esc exit")
        main_layout.addWidget(info_label)

        central_widget.setLayout(main_layout)

        # Set initial volume
        self.player.audio_set_volume(50)
        self.apply_dark_theme()
        self.apply_texture_background()
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

        self.shortcut_speed = QShortcut(QKeySequence(Qt.Key_S), self)
        self.shortcut_speed.setContext(Qt.ApplicationShortcut)
        self.shortcut_speed.activated.connect(self.cycle_playback_speed)

        self.shortcut_texture = QShortcut(QKeySequence(Qt.Key_T), self)
        self.shortcut_texture.setContext(Qt.ApplicationShortcut)
        self.shortcut_texture.activated.connect(self.cycle_texture)

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
            self.apply_playback_speed()
            QTimer.singleShot(40, self.apply_playback_speed)

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

    def apply_playback_speed(self):
        speed = self.playback_speeds[self.playback_speed_index]
        self.player.set_rate(speed)

    def cycle_playback_speed(self):
        self.playback_speed_index = (self.playback_speed_index + 1) % len(self.playback_speeds)
        speed = self.playback_speeds[self.playback_speed_index]
        self.speed_button.setText(f"Speed x{speed:g}")
        if self.current_file:
            self.apply_playback_speed()

    def apply_texture_background(self):
        color = self.texture_colors[self.texture_index]
        self.video_container.setStyleSheet(
            f"background-color: #0f1319; border: 2px solid {color}; border-radius: 12px;"
        )
        self.video_frame.setStyleSheet("background-color: black; border: none;")
        texture_label = self.texture_labels[self.texture_index]
        self.texture_button.setText(f"Texture: {texture_label}")

    def cycle_texture(self):
        self.texture_index = (self.texture_index + 1) % len(self.texture_colors)
        self.apply_texture_background()

    def toggle_play_pause(self):
        if not self.current_file:
            return
        if self.player.is_playing():
            self.pause_media()
        else:
            self.play_media()

    def readable_track_name(self, name):
        if isinstance(name, bytes):
            try:
                return name.decode('utf-8', errors='replace')
            except Exception:
                return str(name)
        return str(name)

    def find_ffprobe_executable(self):
        candidates = []
        env_path = os.getenv('FFPROBE_PATH')
        if env_path:
            candidates.append(env_path)
        if sys.platform == 'win32':
            candidates.extend([
                r'C:\Program Files\ffmpeg\bin\ffprobe.exe',
                r'C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe',
            ])
        candidates.append('ffprobe')
        for cmd in candidates:
            if not cmd:
                continue
            try:
                result = subprocess.run([cmd, '-version'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    return cmd
            except Exception:
                continue
        return None

    def get_ffprobe_info(self, file_path):
        """Extract technical information using ffprobe"""
        if not self.ffprobe_executable:
            return None
        try:
            cmd = [
                self.ffprobe_executable, '-v', 'error', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None

    def format_bitrate(self, bitrate_str):
        """Convert bitrate from string to human-readable format"""
        if not bitrate_str:
            return "N/A"
        try:
            bitrate = int(bitrate_str)
            if bitrate >= 1000000:
                return f"{bitrate / 1000000:.2f} Mbps"
            elif bitrate >= 1000:
                return f"{bitrate / 1000:.2f} kbps"
            else:
                return f"{bitrate} bps"
        except:
            return bitrate_str

    def show_media_info(self):
        if not self.current_file:
            QMessageBox.information(self, "Media Information", "No media file is loaded.")
            return

        media = self.player.get_media()
        if media is None:
            QMessageBox.warning(self, "Media Information", "No media object available.")
            return

        try:
            media.parse()
        except Exception:
            pass

        duration_ms = media.get_duration()
        duration_text = self.format_time(duration_ms) if duration_ms and duration_ms > 0 else "Unknown"

        title = media.get_meta(vlc.Meta.Title) or "N/A"
        artist = media.get_meta(vlc.Meta.Artist) or "N/A"
        genre = media.get_meta(vlc.Meta.Genre) or "N/A"

        info_text = (
            f"FILE INFORMATION\n"
            f"File: {os.path.basename(self.current_file)}\n"
            f"Title: {title}\n"
            f"Artist: {artist}\n"
            f"Genre: {genre}\n"
            f"Duration: {duration_text}\n\n"
        )

        # Get technical information from ffprobe
        ffprobe_data = self.get_ffprobe_info(self.current_file)
        if ffprobe_data:
            format_info = ffprobe_data.get('format', {})
            streams = ffprobe_data.get('streams', [])

            # Container/Format info
            format_name = format_info.get('format_name', 'N/A')
            info_text += f"CONTAINER / FORMAT\n"
            info_text += f"Container: {format_name}\n"
            if 'bit_rate' in format_info:
                info_text += f"Overall Bitrate: {self.format_bitrate(format_info.get('bit_rate'))}\n"
            info_text += "\n"

            # Count streams
            video_streams = [s for s in streams if s.get('codec_type') == 'video']
            audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
            subtitle_streams = [s for s in streams if s.get('codec_type') == 'subtitle']

            info_text += f"STREAM SUMMARY\n"
            info_text += f"Video Tracks: {len(video_streams)}\n"
            info_text += f"Audio Tracks: {len(audio_streams)}\n"
            info_text += f"Subtitle Tracks: {len(subtitle_streams)}\n\n"

            # Video codec details
            if video_streams:
                info_text += f"VIDEO CODEC INFORMATION\n"
                for i, stream in enumerate(video_streams, 1):
                    if len(video_streams) > 1:
                        info_text += f"Track {i}:\n"
                    codec_name = stream.get('codec_name', 'N/A')
                    codec_long = stream.get('codec_long_name', 'N/A')
                    width = stream.get('width', 'N/A')
                    height = stream.get('height', 'N/A')
                    fps = stream.get('r_frame_rate', 'N/A')
                    bit_rate = stream.get('bit_rate', 'N/A')

                    info_text += f"Codec: {codec_name} ({codec_long})\n"
                    info_text += f"Resolution: {width}x{height}\n"
                    info_text += f"Frame Rate: {fps} FPS\n"
                    info_text += f"Bitrate: {self.format_bitrate(bit_rate)}\n"
                    if 'duration' in stream:
                        info_text += f"Duration: {float(stream['duration']):.2f}s\n"
                    info_text += "\n"

            # Audio codec details
            if audio_streams:
                info_text += f"AUDIO CODEC INFORMATION\n"
                for i, stream in enumerate(audio_streams, 1):
                    if len(audio_streams) > 1:
                        info_text += f"Track {i}:\n"
                    codec_name = stream.get('codec_name', 'N/A')
                    codec_long = stream.get('codec_long_name', 'N/A')
                    sample_rate = stream.get('sample_rate', 'N/A')
                    channels = stream.get('channels', 'N/A')
                    bit_rate = stream.get('bit_rate', 'N/A')
                    lang = stream.get('tags', {}).get('language', 'Unknown')

                    info_text += f"Codec: {codec_name} ({codec_long})\n"
                    info_text += f"Language: {lang}\n"
                    info_text += f"Sample Rate: {sample_rate} Hz\n"
                    info_text += f"Channels: {channels}\n"
                    info_text += f"Bitrate: {self.format_bitrate(bit_rate)}\n"
                    info_text += "\n"

            # Subtitle info
            if subtitle_streams:
                info_text += f"SUBTITLE INFORMATION\n"
                for i, stream in enumerate(subtitle_streams, 1):
                    codec_name = stream.get('codec_name', 'N/A')
                    lang = stream.get('tags', {}).get('language', 'Unknown')
                    info_text += f"{i}. {codec_name} - {lang}\n"
                info_text += "\n"
        else:
            info_text += f"STREAM INFORMATION (from VLC)\n"

        audio_desc = self.player.audio_get_track_description()
        if audio_desc:
            info_text += "Audio tracks:\n"
            if isinstance(audio_desc, (list, tuple)):
                for item in audio_desc:
                    if isinstance(item, tuple) and len(item) >= 2:
                        info_text += f"  - {self.readable_track_name(item[1])} (id={item[0]})\n"
                    elif hasattr(item, 'name') and hasattr(item, 'id'):
                        info_text += f"  - {self.readable_track_name(item.name)} (id={item.id})\n"
            else:
                while audio_desc:
                    info_text += f"  - {self.readable_track_name(audio_desc.name)} (id={audio_desc.id})\n"
                    audio_desc = audio_desc.next
        else:
            info_text += "Audio tracks: None\n"

        spu_desc = self.player.video_get_spu_description()
        if spu_desc:
            info_text += "\nSubtitle tracks:\n"
            if isinstance(spu_desc, (list, tuple)):
                for item in spu_desc:
                    if isinstance(item, tuple) and len(item) >= 2:
                        info_text += f"  - {self.readable_track_name(item[1])} (id={item[0]})\n"
                    elif hasattr(item, 'name') and hasattr(item, 'id'):
                        info_text += f"  - {self.readable_track_name(item.name)} (id={item.id})\n"
            else:
                while spu_desc:
                    info_text += f"  - {self.readable_track_name(spu_desc.name)} (id={spu_desc.id})\n"
                    spu_desc = spu_desc.next
        else:
            info_text += "\nSubtitle tracks: None\n"

        QMessageBox.information(self, "Media Information", info_text)

    def export_media_info(self):
        if not self.current_file:
            QMessageBox.information(self, "Export Media Information", "No media file is loaded.")
            return

        # Get the ffprobe data
        ffprobe_data = self.get_ffprobe_info(self.current_file)
        if not ffprobe_data:
            QMessageBox.warning(self, "Export Media Information", "Could not extract technical information.")
            return

        # Ask user for save location
        file_filter = "JSON Files (*.json);;All Files (*)"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Media Information",
            os.path.splitext(self.current_file)[0] + "_info.json",
            file_filter
        )

        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(ffprobe_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "Export Successful", f"Media information exported to:\n{save_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"Error saving file: {str(e)}")

    def show_academic_analysis(self):
        if not self.current_file:
            QMessageBox.information(self, "Academic Analysis", "No media file is loaded.")
            return

        ffprobe_data = self.get_ffprobe_info(self.current_file)
        if not ffprobe_data:
            QMessageBox.warning(self, "Academic Analysis", "Could not extract technical information.")
            return

        analysis_text = "MULTIMEDIA ACADEMIC ANALYSIS\n\n"

        format_info = ffprobe_data.get('format', {})
        streams = ffprobe_data.get('streams', [])

        # Basic file info
        try:
            file_size = int(format_info.get('size', 0))
        except (ValueError, TypeError):
            file_size = 0
        
        try:
            duration = float(format_info.get('duration', 0))
        except (ValueError, TypeError):
            duration = 0.0
        
        try:
            bitrate = int(format_info.get('bit_rate', 0))
        except (ValueError, TypeError):
            bitrate = 0

        analysis_text += "FILE INFORMATION\n"
        analysis_text += f"Size: {file_size / (1024*1024):.2f} MB\n"
        analysis_text += f"Duration: {duration:.2f} seconds\n"
        analysis_text += f"Total Bitrate: {bitrate / 1000:.0f} kbps\n\n"

        video_streams = [s for s in streams if s.get('codec_type') == 'video']
        if video_streams:
            video = video_streams[0]
            width = int(video.get('width', 0))
            height = int(video.get('height', 0))
            fps_str = video.get('r_frame_rate', '30/1')
            try:
                if '/' in fps_str:
                    num, den = fps_str.split('/')
                    fps = float(num) / float(den)
                else:
                    fps = float(fps_str)
            except:
                fps = 30.0
            try:
                video_bitrate = int(video.get('bit_rate', 0)) / 1000
            except (ValueError, TypeError):
                video_bitrate = 0.0
            codec = video.get('codec_name', '').upper()

            analysis_text += "VIDEO ANALYSIS\n"
            analysis_text += f"Codec: {codec}\n"
            analysis_text += f"Resolution: {width}x{height}\n"
            analysis_text += f"Frame Rate: {fps:.2f} FPS\n"
            analysis_text += f"Video Bitrate: {video_bitrate:.0f} kbps\n"

            if width >= 3840:
                res_cat = "8K Ultra HD"
            elif width >= 1920:
                res_cat = "Full HD (1080p)"
            elif width >= 1280:
                res_cat = "HD (720p)"
            else:
                res_cat = "SD"
            analysis_text += f"Category: {res_cat}\n"

            if 'H264' in codec:
                analysis_text += "• Standard: H.264/AVC (MPEG-4 Part 10)\n"
                analysis_text += "• Year: 2003\n"
                analysis_text += "• Efficiency: Good compression with quality\n"
            elif 'H265' in codec or 'HEVC' in codec:
                analysis_text += "• Standard: H.265/HEVC\n"
                analysis_text += "• Year: 2013\n"
                analysis_text += "• Efficiency: 50% better than H.264\n"

            uncompressed_size = (width * height * 24 * duration * fps) / 8 / (1024*1024*1024)
            compressed_size = file_size / (1024*1024*1024)
            if uncompressed_size > 0 and compressed_size > 0:
                compression_ratio = uncompressed_size / compressed_size
                space_saved = (1 - 1/compression_ratio) * 100
                analysis_text += f"\nCOMPRESSION ANALYSIS\n"
                analysis_text += f"Uncompressed Size: {uncompressed_size:.2f} GB\n"
                analysis_text += f"Compressed Size: {compressed_size:.2f} GB\n"
                analysis_text += f"Compression Ratio: {compression_ratio:.0f}:1\n"
                analysis_text += f"Space Saved: {space_saved:.1f}%\n"

        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
        if audio_streams:
            audio = audio_streams[0]
            audio_codec = audio.get('codec_name', '').upper()
            sample_rate = int(audio.get('sample_rate', 0))
            channels = int(audio.get('channels', 0))
            try:
                audio_bitrate = int(audio.get('bit_rate', 0)) / 1000
            except (ValueError, TypeError):
                audio_bitrate = 0.0

            analysis_text += f"\nAUDIO ANALYSIS\n"
            analysis_text += f"Codec: {audio_codec}\n"
            analysis_text += f"Sample Rate: {sample_rate} Hz\n"
            analysis_text += f"Channels: {channels}\n"
            analysis_text += f"Audio Bitrate: {audio_bitrate:.0f} kbps\n"

            if sample_rate >= 44100 and audio_bitrate >= 128:
                quality = "High quality"
            elif sample_rate >= 22050 and audio_bitrate >= 64:
                quality = "Medium quality"
            else:
                quality = "Low quality"
            analysis_text += f"Estimated Quality: {quality}\n"

        container = format_info.get('format_name', '').split(',')[0].upper()
        analysis_text += f"\nCONTAINER ANALYSIS\n"
        analysis_text += f"Format: {container}\n"
        if 'MP4' in container:
            analysis_text += "• Standard: MPEG-4 Part 14\n"
            analysis_text += "• Usage: Streaming, storage\n"
        elif 'MKV' in container:
            analysis_text += "• Format: Matroska\n"
            analysis_text += "• Advantage: Multiple tracks, metadata\n"

        analysis_text += f"\nACADEMIC CONCLUSIONS\n"
        analysis_text += "• The file uses industry standard codecs\n"
        analysis_text += "• Compression enables efficient distribution\n"
        analysis_text += "• Compatible with most modern devices\n"
        if video_streams:
            analysis_text += f"• Resolution suitable for {res_cat.lower()}\n"

        QMessageBox.information(self, "Academic Analysis", analysis_text)

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
