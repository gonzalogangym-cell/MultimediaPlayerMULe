# Simple Multimedia Player

A beginner-friendly multimedia player built with Python, PyQt5 and VLC.

## Features

✅ Open and play audio and video files
✅ Play, Pause, and Stop controls
✅ Volume slider (0-100%)
✅ Progress bar (seek through media)
✅ Display current file name
✅ Show current time and total duration
✅ Full screen mode (button + keyboard shortcut)
✅ Simple and easy-to-understand code
✅ Single file implementation

## Requirements

* Python 3.6+
* PyQt5
* VLC Media Player (installed on your system)

## Installation

### Step 1: Install Python 3

Download from: https://www.python.org/

### Step 2: Install Required Libraries

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
pip install PyQt5 python-vlc
```

Or:

```bash
pip3 install PyQt5 python-vlc
```

### Step 3: Install VLC Media Player

Download and install from:

https://www.videolan.org/vlc/

⚠️ Make sure VLC is installed (required for media playback).

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

   * Click "Full Screen" button
   * Press **F** to toggle full screen
   * Press **Esc** to exit full screen

## Supported Formats

Supported formats depend on VLC, including:

* **Audio**: MP3, WAV, FLAC, AAC, OGG
* **Video**: MP4, AVI, MKV, MOV, FLV, WebM
* And many more

## Code Structure

The application is implemented in a single file:

* **MultimediaPlayer class** → Main window and player logic
* **setup_ui()** → Creates the graphical interface
* **load_media()** → Loads media into VLC
* **play_media(), pause_media(), stop_media()** → Playback controls
* **change_volume()** → Volume control
* **set_position()** → Seek through media
* **update_ui()** → Updates progress bar and time

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

* Make sure VLC is installed
* Ensure Python and VLC have the same architecture (both 64-bit recommended)

### Video does not display

* Make sure the file format is supported
* Try a different video file

## Notes

* This is a simple educational multimedia player
* PyQt5 is used for the interface
* VLC is used as the playback engine to ensure compatibility with multiple formats
* The project focuses on clarity and simplicity

Feel free to modify and extend it!
