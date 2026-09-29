A web application that generates synchronized music videos with lyrics. Upload your audio file, LRC lyrics file, and background image/video to create a complete music video with karaoke-style lyrics.

## Usage

1. **Upload Media Files**
   - Audio file (MP3, WAV, etc.)
   - LRC lyrics file (with timestamped lyrics)
   - Background image or video

2. **Configure Settings**
   - Lyrics position (top, center, bottom)
   - Font size and color
   - Animation style

3. **Preview & Render**
   - Preview the synchronized lyrics
   - Generate and download the final video

## Intro/Outro Videos

Add professional intro and outro videos to your lyric music videos.

### Features
- Upload optional intro and outro videos
- Three transition types: Crossfade, Hard Cut, Fade to Black
- Configurable transition duration (0.1-3.0 seconds)
- Option to include intro/outro audio
- Automatic resolution scaling with letterboxing

### Supported Formats
- .mp4, .mov, .avi, .mkv, .webm

### Usage
1. Upload your intro video (optional)
2. Upload your outro video (optional)
3. Select transition type
4. Set transition duration
5. Enable "Include intro/outro audio" if desired
6. Click "Full Render with Intro/Outro"

## Local Development Setup

```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:7860`.
