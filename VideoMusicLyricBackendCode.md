# Video Lyric Music Generator

Python tool that composites time-synced LRC lyrics over PNG/video background with audio, producing MP4.

## Prerequisites

- Python 3.10+
- FFmpeg installed and in PATH
- `uv` package manager

## Setup

It is highly recommended to use the `uv` package manager for dependency management.

1. **Create a virtual environment:**
   ```bash
   uv venv .venv
   ```

2. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **Unix/macOS:**
     ```bash
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

## Usage

### Function Signature

```python
create_lyric_video(
    audio_path: str,                    # Path to audio file (mp3, wav, flac, ogg)
    lrc_path: str,                      # Path to LRC lyrics file
    output_path: str,                   # Path for output MP4 file
    background_path: str,               # Path to background PNG/JPG image or video (mp4, mov)
    resolution: tuple[int, int] = (1920, 1080),   # Output video resolution
    fps: int = 24,                      # Frames per second
    font_path: str | None = None,       # Path to .ttf/.otf font file (required on Windows for non-ASCII text)
    font_size: int = 60,                # Font size in pixels
    font_color: str = "#FFFFFF",        # Font color as hex string
    stroke_color: str = "#000000",      # Text stroke/outline color as hex string
    stroke_width: int = 2,              # Text stroke width in pixels (0 to disable)
    text_align: str = "center",         # Text alignment: "left", "center", "right"
    text_position: str = "center",      # Vertical position: "top", "center", "bottom"
    position_x_offset: int = 0,         # Horizontal offset from base position in pixels
    position_y_offset: int = 0,         # Vertical offset from base position in pixels
    max_text_width: int | None = None,  # Max width for text wrapping (default: 80% of video width)
    fade_enabled: bool = True,          # Enable fade-in/out effect on each lyric line
    fade_in_duration: float = 0.3,      # Fade-in duration in seconds
    fade_out_duration: float = 0.3,     # Fade-out duration in seconds
    start_time: float | None = None,    # Partial render start time in seconds
    end_time: float | None = None,      # Partial render end time in seconds
    codec: str = "libx264",             # Video codec
    audio_codec: str = "aac",           # Audio codec
    bitrate: str = "5000k",             # Video bitrate
    threads: int = 4,                   # FFmpeg encoding threads
    logger: str = "bar",                # MoviePy logger: "bar" (progress bar) or None
)
```

> **Note for Windows Users:** For non-ASCII text rendering, you MUST provide an explicit `font_path` to a `.ttf` or `.otf` file as system font discovery can be unreliable for non-standard characters.

### Full Example Call

```python
from video_lyric_music import create_lyric_video

create_lyric_video(
    audio_path="song.mp3",
    lrc_path="lyrics.lrc",
    output_path="output_video.mp4",
    background_path="background.png",
    resolution=(1920, 1080),
    fps=24,
    font_path="fonts/Roboto-Bold.ttf",
    font_size=64,
    font_color="#FFFFFF",
    stroke_color="#000000",
    stroke_width=3,
    text_align="center",
    text_position="center",
    position_x_offset=0,
    position_y_offset=0,
    max_text_width=1500,
    fade_enabled=True,
    fade_in_duration=0.5,
    fade_out_duration=0.5,
    start_time=None,
    end_time=None,
    codec="libx264",
    audio_codec="aac",
    bitrate="5000k",
    threads=4,
    logger="bar"
)
```

### Partial Render

To perform a test render of a specific segment (e.g., the first 30 seconds):

```python
create_lyric_video(
    audio_path="song.mp3",
    lrc_path="lyrics.lrc",
    output_path="test_render.mp4",
    background_path="background.png",
    start_time=0.0,
    end_time=30.0
)
```

## LRC Format

The LRC file should follow the standard format with metadata tags and timestamped lyrics.

```lrc
[ti:Song Title]
[ar:Artist Name]
[al:Album Name]
[au:Author]
[by:Creator]
[offset:0]

[00:12.30]First line of lyrics
[00:15.45]Second line of lyrics
[00:20.10]...and so on
```
