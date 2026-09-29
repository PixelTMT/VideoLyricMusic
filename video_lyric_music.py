import os
import pathlib
from moviepy import (
    TextClip,
    ImageClip,
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    vfx,
)
from lrc_parser import parse_lrc, filter_lyrics
from Helper import soft_wrap_text


def create_lyric_video(
    audio_path: str,
    lrc_path: str,
    output_path: str,
    background_path: str,
    # Video settings
    resolution: tuple[int, int] = (1920, 1080),
    fps: int = 24,
    # Text styling
    font_path: str | None = None,
    font_size: int = 60,
    font_color: str = "#FFFFFF",
    stroke_color: str = "#000000",
    stroke_width: int = 2,
    text_align: str = "center",
    # Text position
    text_position: str = "center",  # "top", "center", "bottom"
    position_x_offset: int = 0,
    position_y_offset: int = 0,
    # Text wrapping
    max_text_width: int | None = None,  # pixels, auto = 80% of resolution width
    # Fade effect
    fade_enabled: bool = True,
    fade_in_duration: float = 0.3,
    fade_out_duration: float = 0.3,
    # Partial render
    start_time: float | None = None,
    end_time: float | None = None,
    # Encoding
    codec: str = "libx264",
    audio_codec: str = "aac",
    bitrate: str = "5000k",
    threads: int = 4,
    logger: str = "bar",
) -> str:
    """Creates a lyric video from an audio file and an LRC file.

    Args:
        audio_path: Path to the input audio file.
        lrc_path: Path to the input LRC lyric file.
        output_path: Path where the output video will be saved.
        background_path: Path to the background image or video.
        resolution: Output video resolution (width, height).
        fps: Frames per second for the output video.
        font_path: Path to the font file. If None, uses default font.
        font_size: Size of the lyric text font.
        font_color: Color of the lyric text.
        stroke_color: Color of the text stroke/outline.
        stroke_width: Width of the text stroke/outline.
        text_align: Text alignment within the wrapping box.
        text_position: Vertical position of lyrics ("top", "center", "bottom").
        position_x_offset: Horizontal offset for text from center.
        position_y_offset: Vertical offset for text from its base position.
        max_text_width: Max width for text wrapping in pixels.
        fade_enabled: Whether to enable fade in/out for lyrics.
        fade_in_duration: Duration of fade in effect in seconds.
        fade_out_duration: Duration of fade out effect in seconds.
        start_time: Optional start time for partial render in seconds.
        end_time: Optional end time for partial render in seconds.
        codec: Video codec for encoding.
        audio_codec: Audio codec for encoding.
        bitrate: Bitrate for the output video.
        threads: Number of threads to use for rendering.
        logger: Logger type for MoviePy progress updates.

    Returns:
        The path to the created video file.

    Raises:
        FileNotFoundError: If any of the input files are missing.
        ValueError: If parameters are invalid or background extension is unsupported.

    Example:
        >>> create_lyric_video("song.mp3", "song.lrc", "output.mp4", "bg.jpg")
        'output.mp4'
    """
    # Step 1 — Input validation
    for path in (audio_path, lrc_path, background_path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

    if text_position not in ("top", "center", "bottom"):
        raise ValueError(f"Invalid text_position: {text_position}")

    if not (
        isinstance(resolution, tuple)
        and len(resolution) == 2
        and all(isinstance(x, int) and x > 0 for x in resolution)
    ):
        raise ValueError("Resolution must be a tuple of 2 positive integers")

    # Step 2 — Parse lyrics
    print("Parsing lyrics...")
    lyrics = parse_lrc(lrc_path)
    if start_time is not None and end_time is not None:
        lyrics = filter_lyrics(lyrics, start_time, end_time)

    # Step 3 — Audio setup
    print("Loading audio...")
    audio_clip = AudioFileClip(audio_path)
    if start_time is not None and end_time is not None:
        audio_clip = audio_clip.subclipped(start_time, end_time)
    total_duration = audio_clip.duration

    # Step 4 — Background setup
    suffix = pathlib.Path(background_path).suffix.lower()
    img_exts = (".png", ".jpg", ".jpeg", ".bmp", ".webp")
    vid_exts = (".mp4", ".avi", ".mov", ".mkv", ".webm")

    bg_clip = None
    if suffix in img_exts:
        bg_clip = (
            ImageClip(background_path).resized(resolution).with_duration(total_duration)
        )
    elif suffix in vid_exts:
        bg_clip = VideoFileClip(background_path).resized(resolution)
        if bg_clip.duration < total_duration:
            bg_clip = bg_clip.with_effects([vfx.Loop(duration=total_duration)])
        if bg_clip.duration > total_duration:
            bg_clip = bg_clip.subclipped(0, total_duration)
    else:
        audio_clip.close()
        raise ValueError(f"Unsupported background extension: {suffix}")

    # Step 5 — Compute max_text_width
    if max_text_width is None:
        max_text_width = int(resolution[0] * 0.8)

    lyric_clips = []
    final_clip = None

    try:
        # Step 6 — Calculate lyric durations and create TextClips
        for i, lyric in enumerate(lyrics):
            adjusted_ts = lyric.timestamp - (start_time or 0.0)
            if adjusted_ts >= total_duration:
                continue

            # Calculate duration
            if i < len(lyrics) - 1:
                next_adjusted_ts = lyrics[i + 1].timestamp - (start_time or 0.0)
                lyric_duration = next_adjusted_ts - adjusted_ts
            else:
                lyric_duration = min(5.0, total_duration - adjusted_ts)

            if lyric_duration <= 0:
                continue

            # Cap duration to not exceed audio end
            if adjusted_ts + lyric_duration > total_duration:
                lyric_duration = total_duration - adjusted_ts

            wrap_text = soft_wrap_text(
                lyric.text,
                font_family=font_path,
                fontsize=font_size,
                letter_spacing=12,
                max_width=max_text_width,
            )

            txt_clip = TextClip(
                font=font_path,
                text=wrap_text,
                font_size=font_size,
                color=font_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method="caption",
                size=(max_text_width, resolution[1]),
                text_align=text_align,
                duration=lyric_duration,
            )

            # Set position
            x = resolution[0] // 2 - txt_clip.w // 2 + position_x_offset
            if text_position == "top":
                y = 50 + position_y_offset
            elif text_position == "center":
                y = resolution[1] // 2 - txt_clip.h // 2 + position_y_offset
            else:  # bottom
                y = resolution[1] - 150 + position_y_offset

            txt_clip = txt_clip.with_position((x, y)).with_start(adjusted_ts)

            if fade_enabled:
                txt_clip = txt_clip.with_effects(
                    [
                        vfx.CrossFadeIn(fade_in_duration),
                        vfx.CrossFadeOut(fade_out_duration),
                    ]
                )

            lyric_clips.append(txt_clip)

        # Step 7 — Composite
        print("Compositing clips...")
        final_clip = CompositeVideoClip([bg_clip] + lyric_clips, size=resolution)

        # Step 8 — Set audio
        final_clip = final_clip.with_audio(audio_clip)

        # Step 9 — Write output
        print(f"Rendering video to {output_path}...")
        final_clip.write_videofile(
            output_path,
            fps=fps,
            codec=codec,
            audio_codec=audio_codec,
            bitrate=bitrate,
            threads=threads,
            logger=logger,
        )

    finally:
        # Step 10 — Cleanup
        for clip in lyric_clips:
            clip.close()
        if bg_clip:
            bg_clip.close()
        if audio_clip:
            audio_clip.close()
        if final_clip:
            final_clip.close()

    return output_path
