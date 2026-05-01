# Multimedia Player MULe - Documentation

## Overview

Multimedia Player MULe is a simple desktop media player built with PyQt5 and VLC. It allows you to play audio and video files with a clean interface and useful features.

## How the Code Works

### Architecture

The application is built using a single main class `MultimediaPlayer` that inherits from `QMainWindow`. This class manages the entire application state and UI.

### Main Components

#### 1. **ClickableSlider Class**
A custom slider widget that extends PyQt5's `QSlider`. It overrides the `mousePressEvent` method to detect clicks anywhere on the slider bar, not just dragging. When you click on the slider:
- It calculates the position based on where you clicked
- Emits a `clicked` signal with the value
- Updates the slider position instantly

This is used for both the progress bar and volume slider, allowing you to click anywhere to change the value.

#### 2. **VLC Backend**
The player uses the VLC library (`python-vlc`) as the multimedia engine. VLC handles:
- Media decoding for various formats
- Audio/video playback
- Streaming and codec support

The application creates a VLC instance in `__init__` and creates a media player object that is attached to the video display widget.

#### 3. **UI Components**

**Video Display**: A black `QWidget` that displays video content. On Windows, it's attached to VLC using the widget's window ID via `set_hwnd()`.

**Sliders**: 
- Progress slider: Shows playback position (0-1000 range, normalized to 0-1 for VLC)
- Volume slider: Controls audio volume (0-100%)

**Labels**: Display current time, duration, and volume percentage.

**Buttons**: Control playback, settings, and information display.

### How Playback Works

1. **Load Media**: When you open a file, `load_media()` is called which:
   - Stores the file path in `self.current_file`
   - Creates a VLC media object
   - Attaches it to the video display widget

2. **Play**: `play_media()` starts playback and begins a timer that updates the UI every 500ms

3. **Seek**: When you click the progress bar:
   - `on_slider_changed()` is triggered with the new value (0-1000)
   - This calls `player.set_position()` with the normalized value (0-1.0)

4. **Update UI**: The timer fires `update_ui()` which:
   - Gets the current position and duration from VLC
   - Updates the progress bar and time labels
   - Handles end-of-file logic

### Key Features Implementation

**Click-to-Seek**: 
- Uses the custom `ClickableSlider` class
- When you click on the progress bar, `on_slider_changed()` updates the position immediately

**Volume Control**:
- The volume slider is also a `ClickableSlider`
- Both dragging and clicking update the volume via `on_volume_changed()`

**Keyboard Shortcuts**:
- Created using `QShortcut` objects
- Each key is connected to a specific action (play/pause, seek, etc.)
- These work globally, even when the window isn't focused

**Playback Speed**:
- Stores speeds in `self.playback_speeds` list
- `cycle_playback_speed()` cycles through them
- `apply_playback_speed()` calls VLC's `set_rate()` method

**Mute Toggle**:
- Stores the previous volume before muting
- When unmuting, restores the previous volume level

**Fullscreen**:
- Toggles between fullscreen and normal mode
- Updates button text to show current state

### FFprobe Integration

For advanced media information:
- `find_ffprobe_executable()` searches for FFprobe on the system
- `get_ffprobe_info()` runs FFprobe as a subprocess and parses JSON output
- This provides detailed codec, bitrate, resolution, and other technical data

### Data Flow

```
User clicks progress bar
         ↓
ClickableSlider.mousePressEvent() triggered
         ↓
Calculates click position and emits clicked signal
         ↓
on_slider_changed() called with value
         ↓
player.set_position() updates VLC position
         ↓
Timer's update_ui() gets new position from VLC
         ↓
UI updates (progress bar, time label)
```

## Features

- **Play/Pause/Stop**: Control playback of media files
- **Progress Bar**: Click anywhere on the timeline to jump to that position
- **Volume Control**: Adjust volume by clicking on the volume slider
- **Playback Speed**: Cycle through different playback speeds (1x, 2x, 0.5x)
- **Mute**: Toggle mute on/off with volume memory
- **Fullscreen**: Watch videos in fullscreen mode
- **Media Info**: View detailed information about the loaded file
- **Export Info**: Save technical information as JSON
- **Academic Analysis**: Get a detailed analysis of video compression and codecs
- **Texture Themes**: Change the appearance of the video container
- **Keyboard Shortcuts**: Use shortcuts for quick control

## Supported Formats

- Audio: MP3, WAV
- Video: MP4, AVI, MKV, MOV

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Install VLC media player on your system
4. Run the application:
   ```
   python multimedia_player.py
   ```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Play/Pause |
| Left Arrow | Seek back 10 seconds |
| Right Arrow | Seek forward 10 seconds |
| M | Mute/Unmute |
| R | Restart playback |
| S | Change playback speed |
| T | Change texture theme |
| F | Toggle fullscreen |
| Esc | Exit fullscreen |

## How to Use

1. Click "Open File" to select a media file
2. Click "Play" to start playback
3. Use the progress bar to seek through the file
4. Adjust volume with the volume slider
5. Use buttons for additional controls (mute, speed, info, etc.)

## Technical Features

- **Click-to-Seek**: Click anywhere on the progress bar to jump to that position instantly
- **Click Volume**: Click on the volume slider to set volume to any level
- **FFprobe Integration**: Automatically extracts detailed technical information from media files
- **VLC Backend**: Uses VLC library for reliable playback across different formats

## System Requirements

- Windows, Linux, or macOS
- Python 3.7+
- VLC media player installed
- FFprobe (optional, for advanced media information)

## Project Structure

```
multimedia_player.py    - Main application file
requirements.txt        - Python dependencies
DOCUMENTATION.md        - This file
```

## Notes

- The player automatically detects VLC installation on Windows
- FFprobe is searched in common installation directories
- All shortcuts use the Application context for better compatibility
