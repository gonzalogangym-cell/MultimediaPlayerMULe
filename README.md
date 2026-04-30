# Multimedia Player MULe

A simple yet powerful multimedia player for academic multimedia analysis, built with Python, PyQt5 and VLC.

## Features

✅ **Basic playback**: Play, Pause, Stop, Volume, Seek
✅ **Fullscreen** with keyboard shortcuts
✅ **Technical information**: Codec, resolution, bitrate, audio/video tracks
✅ **Export metadata**: Save technical information to JSON
✅ **Academic Analysis**: Technical interpretation with multimedia explanations
✅ **Simple interface**: No unnecessary complications
✅ **Clean code**: Easy to understand and modify

## Requirements

- Python 3.6+
- PyQt5
- VLC Media Player
- FFmpeg (for technical analysis)

## Installation

### 1. Install Python 3

Download from: https://www.python.org/

### 2. Install libraries

```bash
pip install PyQt5 python-vlc
```

### 3. Install VLC

Download from: https://www.videolan.org/vlc/

### 4. Install FFmpeg (for technical analysis)

```bash
winget install --id=Gyan.FFmpeg
```

## Usage

```bash
python multimedia_player.py
```

### Controls:

- **Open File**: Load multimedia file
- **Play/Pause/Stop**: Basic controls
- **Info**: View technical information of the file
- **Export Info**: Save metadata to JSON
- **Academic Analysis**: Technical interpretation with multimedia explanations

### Keyboard shortcuts:

- **Space**: Play/Pause
- **Arrows**: Seek ±10s
- **M**: Mute
- **F**: Fullscreen
- **Esc**: Exit fullscreen

## What is **pycache**?

It is a folder that Python creates automatically to store compiled bytecode files (.pyc) that speed up execution. **It is not part of your source code** - you can ignore it or delete it. It is already in .gitignore so Git won't track it.

## How to Run

1. Open Command Prompt in the folder where `multimedia_player.py` is located
2. Run:

```bash
python multimedia_player.py
```

Or:

```bash
python3 multimedia_player.py
```

## How to Use

1. **Open a File**
   Click the "Open File" button and select a media file

2. **Play**
   Click "Play" to start playback

3. **Pause**
   Click "Pause" to pause (click Play to resume)

4. **Stop**
   Click "Stop" to stop playback and reset

5. **Volume**
   Use the slider to adjust volume (0–100%)

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
- And many more

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

Feel free to modify and extend it!
