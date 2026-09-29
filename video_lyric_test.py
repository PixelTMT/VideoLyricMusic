"""
Integration test script for video_lyric_music.

Run this script to generate a test video. Edit the CONFIGURATION section
below with your actual file paths before running.
"""

import os
import sys
import time

from video_lyric_music import create_lyric_video

# ============================================================
# CONFIGURATION — Fill in your file paths before running
# ============================================================
LRC_FILE = r"D:\Default Folder\Download\lyric.lrc"  # Audio file (mp3, wav, flac, ogg)
AUDIO_FILE = r"D:\Default Folder\Music\GIRLS BAND CRY TOGENASHI TOGEARI - Hazete Saku mp3\01.爆ぜて咲く.mp3"  # LRC lyrics file
BACKGROUND_FILE = (
    r"D:\Default Folder\Music\GIRLS BAND CRY TOGENASHI TOGEARI - Hazete Saku mp3\Cover.jpg"  # Background image (png, jpg) or video (mp4, mov)
)
OUTPUT_FILE = "output_test.mp4"  # Output video file path
FONT_FILE = r"D:\Default Folder\Download\tokyo-dream\Tokyo Dream.ttf"  # Optional: path to .ttf/.otf font file

# Partial render for fast testing (set both to None for full render)
START_TIME = 20.0  # Start time in seconds
END_TIME = 40.0  # End time in seconds (30s for quick test)
# ============================================================


def validate_inputs() -> bool:
    """Validates that all required input files exist.

    Returns:
        True if all inputs are valid, False otherwise.
    """
    valid = True
    for label, path in [
        ("Audio file", AUDIO_FILE),
        ("LRC file", LRC_FILE),
        ("Background file", BACKGROUND_FILE),
    ]:
        if not os.path.exists(path):
            print(f"ERROR: {label} not found: {path}")
            valid = False
    if FONT_FILE is not None and not os.path.exists(FONT_FILE):
        print(f"ERROR: Font file not found: {FONT_FILE}")
        valid = False
    return valid


def main() -> None:
    """Runs the lyric video generation test."""
    print("=== Video Lyric Music — Integration Test ===")
    print(f"Audio:      {AUDIO_FILE}")
    print(f"LRC:        {LRC_FILE}")
    print(f"Background: {BACKGROUND_FILE}")
    print(f"Output:     {OUTPUT_FILE}")
    if START_TIME is not None and END_TIME is not None:
        print(f"Partial render: {START_TIME}s — {END_TIME}s")
    print()

    if not validate_inputs():
        print()
        print("Please edit the CONFIGURATION section at the top of test.py")
        print("with the actual paths to your files, then run again.")
        sys.exit(1)

    start = time.time()

    create_lyric_video(
        audio_path=AUDIO_FILE,
        lrc_path=LRC_FILE,
        output_path=OUTPUT_FILE,
        background_path=BACKGROUND_FILE,
        resolution=(1920, 1080),
        fps=24,
        font_path=FONT_FILE,
        font_size=120,
        font_color="#FFFFFF",
        stroke_color="#000000",
        stroke_width=2,
        text_align="center",
        text_position="center",
        position_x_offset=0,
        position_y_offset=0,
        max_text_width=None,
        fade_enabled=True,
        fade_in_duration=0.3,
        fade_out_duration=0.3,
        start_time=START_TIME,
        end_time=END_TIME,
        bitrate="1000k"
    )

    elapsed = time.time() - start
    print(f"\nRender completed in {elapsed:.1f}s")

    # Post-render verification
    if os.path.exists(OUTPUT_FILE):
        size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"Output file: {OUTPUT_FILE} ({size_mb:.2f} MB)")

        # Attempt to read duration via moviepy
        try:
            from moviepy import VideoFileClip

            clip = VideoFileClip(OUTPUT_FILE)
            print(f"Duration: {clip.duration:.1f}s")
            print(f"Size: {clip.size}")
            clip.close()
        except Exception as e:
            print(f"Note: Could not read output metadata: {e}")
    else:
        print(f"ERROR: Output file was not created: {OUTPUT_FILE}")
        sys.exit(1)


if __name__ == "__main__":
    main()
