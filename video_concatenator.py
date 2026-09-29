"""Video concatenation module with transition support.

This module provides functionality to concatenate intro, lyric video, and outro
clips with various transition effects.
"""

import os
from video_overlay import OverlayConfig, process_overlays, validate_overlay_files
from moviepy import (
    VideoClip,
    VideoFileClip,
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx,
)

# Supported video file extensions
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")


def validate_intro_outro_files(
    intro_path: str | None,
    outro_path: str | None,
) -> tuple[bool, str | None]:
    """Validates intro and outro video files for format and accessibility.

    Args:
        intro_path: Path to intro video file. Can be None if no intro provided.
        outro_path: Path to outro video file. Can be None if no outro provided.

    Returns:
        A tuple of (is_valid, error_message) where:
            - is_valid: True if both files are valid or both are None.
            - error_message: None if valid, or a descriptive error message.

    Example:
        >>> validate_intro_outro_files(None, None)
        (True, None)
        >>> validate_intro_outro_files("intro.mp4", "outro.txt")
        (False, "Intro file has unsupported format: intro.txt")
    """
    for label, path in [("Intro", intro_path), ("Outro", outro_path)]:
        if path is None:
            continue

        # Check file extension
        ext = os.path.splitext(path)[1].lower()
        if ext not in VIDEO_EXTENSIONS:
            return (False, f"{label} file has unsupported format: {path}")

        # Check file exists
        if not os.path.exists(path):
            return (False, f"{label} file not found: {path}")

        # Check file is readable
        try:
            with open(path, "rb") as f:
                f.read(1)
        except (IOError, OSError) as e:
            return (False, f"{label} file is not readable: {path} ({e})")

    return (True, None)


def concatenate_videos_with_transitions(
    intro_path: str | None,
    lyric_video_path: str,
    outro_path: str | None,
    output_path: str,
    transition_type: str = "crossfade",
    transition_duration: float = 0.5,
    include_intro_outro_audio: bool = True,
    target_resolution: tuple[int, int] = (1920, 1080),
    target_fps: int = 24,
    codec: str = "libx264",
    audio_codec: str = "aac",
    bitrate: str = "5000k",
    threads: int = 4,
    logger: str = "bar",
    overlays: list[OverlayConfig] | None = None,
) -> str:
    """Concatenates intro, lyric video, and outro with transitions.

    Args:
        intro_path: Path to intro video file. If None, intro is skipped.
        lyric_video_path: Path to the main lyric video file.
        outro_path: Path to outro video file. If None, outro is skipped.
        output_path: Path where the output video will be saved.
        transition_type: Type of transition between clips. Options:
            "crossfade" - Smooth crossfade between clips.
            "hard_cut" - Direct cut without transition.
            "fade_to_black" - Fade out to black, then fade in from black.
        transition_duration: Duration of transition in seconds (0.1 to 3.0).
        include_intro_outro_audio: Whether to include audio from intro/outro.
        target_resolution: Output video resolution (width, height).
        target_fps: Frames per second for the output video.
        codec: Video codec for encoding.
        audio_codec: Audio codec for encoding.
        bitrate: Bitrate for the output video.
        threads: Number of threads to use for rendering.
        logger: Logger type for MoviePy progress updates.
        overlays: List of overlay configurations to apply. If None, no overlays
            are applied.

    Returns:
        The path to the created video file.

    Raises:
        FileNotFoundError: If lyric_video_path or specified intro/outro files
            are missing.
        ValueError: If transition_type is invalid or transition_duration is
            out of range.

    Example:
        >>> concatenate_videos_with_transitions(
        ...     intro_path="intro.mp4",
        ...     lyric_video_path="lyrics.mp4",
        ...     outro_path="outro.mp4",
        ...     output_path="final.mp4",
        ...     transition_type="crossfade",
        ...     transition_duration=0.5,
        ... )
        'final.mp4'
    """
    # Input validation
    if transition_type not in ("crossfade", "hard_cut", "fade_to_black"):
        raise ValueError(
            f"Invalid transition_type: {transition_type}. "
            "Must be 'crossfade', 'hard_cut', or 'fade_to_black'."
        )

    if not 0.1 <= transition_duration <= 3.0:
        raise ValueError(
            f"transition_duration must be between 0.1 and 3.0, "
            f"got {transition_duration}"
        )

    if not os.path.exists(lyric_video_path):
        raise FileNotFoundError(f"File not found: {lyric_video_path}")

    if intro_path is not None and not os.path.exists(intro_path):
        raise FileNotFoundError(f"File not found: {intro_path}")

    if outro_path is not None and not os.path.exists(outro_path):
        raise FileNotFoundError(f"File not found: {outro_path}")

    # Validate overlay files if provided
    if overlays:
        is_valid, error_msg = validate_overlay_files(overlays)
        if not is_valid:
            raise ValueError(f"Overlay validation failed: {error_msg}")

    # Collect all clips for cleanup
    all_clips = []
    final_clip = None

    try:
        # Load and process clips
        clips_to_concat = []

        # Load lyric video (required)
        print("Loading lyric video...")
        lyric_clip = VideoFileClip(lyric_video_path)
        all_clips.append(lyric_clip)
        # Lyric video should ALWAYS keep its audio
        lyric_clip = _prepare_clip(lyric_clip, target_resolution, include_audio=True)
        all_clips.append(lyric_clip)

        # Load intro if provided
        intro_clip = None
        if intro_path is not None:
            print("Loading intro video...")
            intro_clip = VideoFileClip(intro_path)
            all_clips.append(intro_clip)
            intro_clip = _prepare_clip(
                intro_clip, target_resolution, include_intro_outro_audio
            )
            all_clips.append(intro_clip)

        # Load outro if provided
        outro_clip = None
        if outro_path is not None:
            print("Loading outro video...")
            outro_clip = VideoFileClip(outro_path)
            all_clips.append(outro_clip)
            outro_clip = _prepare_clip(
                outro_clip, target_resolution, include_intro_outro_audio
            )
            all_clips.append(outro_clip)

        # Apply overlays if provided (must be before transitions)
        if overlays:
            print(f"Applying {len(overlays)} overlay(s)...")
            clips_dict = {
                "intro": intro_clip,
                "main": lyric_clip,
                "outro": outro_clip,
            }
            processed_clips = process_overlays(clips_dict, overlays, target_resolution)
            intro_clip = processed_clips["intro"]
            lyric_clip = processed_clips["main"]
            outro_clip = processed_clips["outro"]

        # Build clips list in order
        if intro_clip is not None:
            clips_to_concat.append(intro_clip)
        clips_to_concat.append(lyric_clip)
        if outro_clip is not None:
            clips_to_concat.append(outro_clip)

        # Apply transitions based on type
        print(f"Applying {transition_type} transitions...")
        if transition_type == "hard_cut":
            final_clip = _concatenate_hard_cut(clips_to_concat, target_resolution)
        elif transition_type == "crossfade":
            final_clip = _concatenate_crossfade(
                clips_to_concat, transition_duration, target_resolution
            )
        else:  # fade_to_black
            final_clip = _concatenate_fade_to_black(
                clips_to_concat, transition_duration, target_resolution
            )

        all_clips.append(final_clip)

        # Write output
        print(f"Rendering video to {output_path}...")
        final_clip.write_videofile(
            output_path,
            fps=target_fps,
            codec=codec,
            audio_codec=audio_codec,
            bitrate=bitrate,
            threads=threads,
            logger=logger,
        )

    finally:
        # Cleanup all clips
        for clip in all_clips:
            if clip is not None:
                try:
                    clip.close()
                except Exception:
                    pass

    return output_path


def _prepare_clip(
    clip: VideoFileClip,
    target_resolution: tuple[int, int],
    include_audio: bool,
) -> VideoClip:
    """Prepares a clip by scaling and adding letterboxing if needed.

    Args:
        clip: The video clip to prepare.
        target_resolution: Target resolution (width, height).
        include_audio: Whether to keep the audio track.

    Returns:
        The prepared video clip with proper resolution and aspect ratio.
    """
    # Remove audio if not included
    if not include_audio:
        clip = clip.without_audio()

    # Calculate aspect ratios
    clip_ratio = clip.w / clip.h
    target_ratio = target_resolution[0] / target_resolution[1]

    if clip_ratio == target_ratio:
        # Same aspect ratio - just resize
        return clip.resized(target_resolution)
    else:
        # Different aspect ratios - need letterboxing
        # Scale to fit within target while maintaining aspect ratio
        if clip_ratio > target_ratio:
            # Clip is wider - fit to width, add bars top/bottom
            new_width = target_resolution[0]
            new_height = int(target_resolution[0] / clip_ratio)
        else:
            # Clip is taller - fit to height, add bars left/right
            new_height = target_resolution[1]
            new_width = int(target_resolution[1] * clip_ratio)

        # Resize the clip
        resized = clip.resized((new_width, new_height))

        # Create black background and composite
        background = ColorClip(
            size=target_resolution,
            color=(0, 0, 0),
            duration=clip.duration,
        )

        # Center the resized clip on the black background
        x_offset = (target_resolution[0] - new_width) // 2
        y_offset = (target_resolution[1] - new_height) // 2

        # Composite the resized clip onto the black background
        return CompositeVideoClip(
            [background, resized.with_position((x_offset, y_offset))],
            size=target_resolution,
        ).with_duration(clip.duration)


def _concatenate_hard_cut(
    clips: list[VideoClip],
    target_resolution: tuple[int, int],
) -> VideoClip:
    """Concatenates clips with hard cuts (no transitions).

    Args:
        clips: List of video clips to concatenate.
        target_resolution: Target resolution for output.

    Returns:
        Concatenated video clip.
    """
    return concatenate_videoclips(clips, method="compose")


def _concatenate_crossfade(
    clips: list[VideoClip],
    transition_duration: float,
    target_resolution: tuple[int, int],
) -> VideoClip:
    """Concatenates clips with crossfade transitions.

    Uses overlapping clips with CrossFadeIn effect for smooth transitions.

    Args:
        clips: List of video clips to concatenate.
        transition_duration: Duration of each crossfade in seconds.
        target_resolution: Target resolution for output.

    Returns:
        Concatenated video clip with crossfade transitions.
    """
    if len(clips) == 1:
        return clips[0]

    # Build composite with overlapping clips
    composite_clips = []
    current_time = 0.0

    for i, clip in enumerate(clips):
        if i == 0:
            # First clip - just add CrossFadeOut at the end
            processed = clip.with_effects([vfx.CrossFadeOut(transition_duration)])
            composite_clips.append(processed.with_start(current_time))
            current_time += clip.duration - transition_duration
        elif i == len(clips) - 1:
            # Last clip - add CrossFadeIn at the start
            processed = clip.with_effects([vfx.CrossFadeIn(transition_duration)])
            composite_clips.append(processed.with_start(current_time))
        else:
            # Middle clips - both CrossFadeIn and CrossFadeOut
            processed = clip.with_effects(
                [
                    vfx.CrossFadeIn(transition_duration),
                    vfx.CrossFadeOut(transition_duration),
                ]
            )
            composite_clips.append(processed.with_start(current_time))
            current_time += clip.duration - transition_duration

    return CompositeVideoClip(composite_clips, size=target_resolution)


def _concatenate_fade_to_black(
    clips: list[VideoClip],
    transition_duration: float,
    target_resolution: tuple[int, int],
) -> VideoClip:
    """Concatenates clips with fade to/from black transitions.

    Each clip fades out to black, then the next clip fades in from black.

    Args:
        clips: List of video clips to concatenate.
        transition_duration: Duration of each fade in seconds.
        target_resolution: Target resolution for output.

    Returns:
        Concatenated video clip with fade to black transitions.
    """
    if len(clips) == 1:
        return clips[0]

    processed_clips = []

    for i, clip in enumerate(clips):
        if i == 0:
            # First clip - only fade out to black
            processed = clip.with_effects([vfx.FadeOut(transition_duration)])
        elif i == len(clips) - 1:
            # Last clip - only fade in from black
            processed = clip.with_effects([vfx.FadeIn(transition_duration)])
        else:
            # Middle clips - both fade in and fade out
            processed = clip.with_effects(
                [
                    vfx.FadeIn(transition_duration),
                    vfx.FadeOut(transition_duration),
                ]
            )
        processed_clips.append(processed)

    # Concatenate with padding for black frames between clips
    # Use negative padding to create space for the black fades
    return concatenate_videoclips(
        processed_clips,
        method="compose",
        bg_color=(0, 0, 0),
    )
