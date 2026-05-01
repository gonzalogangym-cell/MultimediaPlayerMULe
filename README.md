# Multimedia Player MULe

A simple and clean multimedia player built with Python, PyQt5, and VLC. Perfect for playing audio and video files with keyboard shortcuts and technical analysis features.

## Features

- 🎬 Play, pause, and stop controls
- 🔊 Volume control with click-to-set support
- ⏩ Click anywhere on the progress bar to seek
- ⌨️ Keyboard shortcuts for quick control
- 🖥️ Fullscreen mode
- 📊 Media info and technical analysis
- 💾 Export metadata to JSON
- 🎨 Multiple texture themes

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Make sure VLC is installed** on your system

3. **Run the player:**
   ```bash
   python multimedia_player.py
   ```

## Usage

- **Open File**: Click "Open File" to load a media file
- **Play/Pause/Stop**: Use the control buttons
- **Seek**: Click anywhere on the progress bar to jump to that position
- **Volume**: Click on the volume slider to adjust
- **Fullscreen**: Press `F` or click the "Full Screen" button

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Play/Pause |
| ← / → | Seek ±10 seconds |
| M | Mute/Unmute |
| R | Restart |
| S | Change speed |
| T | Change theme |
| F | Fullscreen |
| Esc | Exit fullscreen |

## Supported Formats

**Audio**: MP3, WAV  
**Video**: MP4, AVI, MKV, MOV

## System Requirements

- Python 3.7+
- PyQt5
- VLC Media Player
- FFprobe (optional, for advanced info)

## Documentation

For detailed information about the code structure and how everything works, see [DOCUMENTATION.md](DOCUMENTATION.md)

## Project Structure

```
multimedia_player.py    - Main application
requirements.txt        - Dependencies
DOCUMENTATION.md        - Full documentation
install.bat            - Windows installation helper
```

## License

Academic project - MULe Multimedia Learning


6. **Progress Bar**
   Drag the slider to move through the media

7. **Time Display**
   View current time and total duration

8. **Full Screen**
   - Click "Full Screen" button
   - Press **F** to toggle full screen
   - Press **Esc** to exit full screen

## Supported Formats

Supported formats depend on VLC, including:

- **Audio**: MP3, WAV, FLAC, AAC, OGG
- **Video**: MP4, AVI, MKV, MOV, FLV, WebM

## Code Structure

The application is implemented in a single file:

- **MultimediaPlayer class** → Main window and player logic
- **setup_ui()** → Creates the graphical interface
- **load_media()** → Loads media into VLC
- **play_media(), pause_media(), stop_media()** → Playback controls
- **change_volume()** → Volume control
- **set_position()** → Seek through media
- **update_ui()** → Updates progress bar and time

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt5'"

Run:

```bash
pip install PyQt5
```

### "ModuleNotFoundError: No module named 'vlc'"

Run:

```bash
pip install python-vlc
```

### VLC not found (libvlc.dll error)

- Make sure VLC is installed
- Ensure Python and VLC have the same architecture (both 64-bit recommended)

### Video does not display

- Make sure the file format is supported
- Try a different video file

## Notes

- This is a simple educational multimedia player
- PyQt5 is used for the interface
- VLC is used as the playback engine to ensure compatibility with multiple formats
- The project focuses on clarity and simplicity
