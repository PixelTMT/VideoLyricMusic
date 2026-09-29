"""Video overlay module for adding cinematic effects.

This module provides functionality to apply video overlays to specific sections
of a video composition, with support for brightness-based masking, opacity
control, and transitions between sections.
"""

from dataclasses import dataclass, field
from typing import Literal, TypedDict

import os

import numpy as np
from moviepy import CompositeVideoClip, VideoClip, VideoFileClip, vfx


__all__ = [
    "OverlayConfig",
    "OverlayConfigDict",
    "SectionName",
    "VIDEO_EXTENSIONS",
    "validate_overlay_files",
    "validate_overlay_config",
    "process_overlays",
]


SectionName = Literal["intro", "main", "outro"]
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")


class OverlayConfigDict(TypedDict, total=False):
    """TypedDict for UI state serialization of overlay configurations."""

    video_path: str | None
    mask_threshold: float
    opacity: float
    loop: bool
    muted: bool
    target_sections: list[SectionName]
    transition_type: str
    transition_duration: float


@dataclass
class OverlayConfig:
    """Configuration for video overlay effects.

    This class defines how an overlay video should be applied to specific sections
    of the main video composition, including transparency and transition settings.

    Attributes:
        video_path (str | None): Path to the video file to be used as an overlay.
        mask_threshold (float): Threshold for the luminance-based mask (0.0 to 1.0).
            Defaults to 0.2.
        opacity (float): Overall opacity of the overlay layer (0.0 to 1.0).
            Defaults to 1.0.
        loop (bool): Whether the overlay video should loop if it's shorter than the section.
            Defaults to False.
        muted (bool): Whether the audio from the overlay video should be muted.
            Defaults to True.
        target_sections (set[SectionName]): Set of section names where this overlay
            should be applied. Defaults to {"main"}.
        transition_type (str): Type of transition effect to use (e.g., "crossfade").
            Defaults to "crossfade".
        transition_duration (float): Duration of the transition in seconds.
            Defaults to 1.0.

    Example:
        >>> config = OverlayConfig(
        ...     video_path="overlays/particles.mp4",
        ...     mask_threshold=0.1,
        ...     target_sections={"intro", "main"}
        ... )
        >>> print(config.video_path)
        overlays/particles.mp4
    """

    video_path: str | None = None
    mask_threshold: float = 0.2
    opacity: float = 1.0
    loop: bool = False
    muted: bool = True
    target_sections: set[SectionName] = field(default_factory=lambda: {"main"})
    transition_type: str = "crossfade"
    transition_duration: float = 1.0

    def __post_init__(self) -> None:
        """Validates the configuration after initialization.

        Raises:
            ValueError: If target_sections contains invalid section names.
        """
        valid_sections: set[SectionName] = {"intro", "main", "outro"}
        invalid = self.target_sections - valid_sections
        if invalid:
            raise ValueError(
                f"Invalid section names in target_sections: {invalid}. "
                f"Must be one of {valid_sections}"
            )


def create_brightness_mask(clip: VideoClip, threshold: float) -> VideoClip:
    """Creates a binary mask based on the brightness of the clip.

    This function converts each frame to grayscale and applies a threshold.
    Pixels with a mean brightness (across RGB) greater than the threshold
    will be opaque (1.0), while others will be transparent (0.0).

    Args:
        clip (VideoClip): The input clip to generate the mask from.
        threshold (float): Brightness threshold between 0.0 and 1.0.

    Returns:
        VideoClip: A new clip containing the generated binary mask.
    """
    return clip.image_transform(
        lambda im: (im.mean(axis=2) > threshold * 255).astype(float)
    )


def apply_mask_with_opacity(
    clip: VideoClip, mask: VideoClip, opacity: float
) -> VideoClip:
    """Applies a mask to a clip and adjusts its overall opacity.

    Args:
        clip (VideoClip): The clip to be masked.
        mask (VideoClip): The mask clip (values 0.0 to 1.0).
        opacity (float): Global opacity multiplier (0.0 to 1.0).

    Returns:
        VideoClip: The masked clip with modified opacity.
    """
    masked_clip = clip.with_mask(mask)
    if opacity < 1.0:
        return masked_clip.with_opacity(opacity)
    return masked_clip


def validate_overlay_config(config: OverlayConfig) -> tuple[bool, str | None]:
    """Validates a single OverlayConfig for file existence and format.

    Args:
        config (OverlayConfig): The configuration to validate.

    Returns:
        tuple[bool, str | None]: A tuple of (is_valid, error_message).
    """
    if config.video_path is None:
        return True, None

    # Check file extension
    ext = os.path.splitext(config.video_path)[1].lower()
    if ext not in VIDEO_EXTENSIONS:
        return (
            False,
            f"Overlay file has unsupported format: {config.video_path}",
        )

    # Check file exists
    if not os.path.exists(config.video_path):
        return False, f"Overlay file not found: {config.video_path}"

    # Check file is readable
    try:
        with open(config.video_path, "rb") as f:
            f.read(1)
    except (IOError, OSError) as e:
        return (
            False,
            f"Overlay file is not readable: {config.video_path} ({e})",
        )

    return True, None


def validate_overlay_files(
    overlays: list[OverlayConfig],
) -> tuple[bool, str | None]:
    """Validates a list of OverlayConfig objects.

    Iterates through each overlay in the list and performs validation
    on the video files. Returns (False, error_message) on the first failure.

    Args:
        overlays (list[OverlayConfig]): List of configurations to validate.

    Returns:
        tuple[bool, str | None]: A tuple of (is_valid, error_message).
    """
    for config in overlays:
        is_valid, error_message = validate_overlay_config(config)
        if not is_valid:
            return False, error_message

    return True, None


def apply_overlay_to_clip(
    base_clip: VideoClip,
    overlay_config: OverlayConfig,
    target_resolution: tuple[int, int],
) -> VideoClip:
    """Applies an overlay video to a base clip with masking and opacity.

    Loads the overlay video, stretches it to the target resolution, applies
    a brightness-based transparency mask, and composites it over the base clip.

    Args:
        base_clip (VideoClip): The base video clip to overlay onto.
        overlay_config (OverlayConfig): Configuration for the overlay effect,
            including video path, mask threshold, opacity, loop, and mute settings.
        target_resolution (tuple[int, int]): Target resolution (width, height)
            to stretch the overlay to.

    Returns:
        VideoClip: A CompositeVideoClip with the overlay applied on top of
            the base clip, centered.

    Raises:
        ValueError: If overlay_config.video_path is None or the file cannot
            be loaded.
    """
    if overlay_config.video_path is None:
        raise ValueError("overlay_config.video_path cannot be None")

    # Load overlay video and stretch to target resolution
    overlay_clip = VideoFileClip(overlay_config.video_path).resized(target_resolution)

    # Apply brightness mask with threshold
    brightness_mask = create_brightness_mask(
        overlay_clip, overlay_config.mask_threshold
    )
    overlay_clip = apply_mask_with_opacity(
        overlay_clip, brightness_mask, overlay_config.opacity
    )

    # Handle duration matching
    base_duration = base_clip.duration
    overlay_duration = overlay_clip.duration

    if overlay_duration < base_duration:
        if overlay_config.loop:
            # Loop overlay to match base duration
            overlay_clip = overlay_clip.with_effects([vfx.Loop(duration=base_duration)])
        else:
            # Extend last frame to match base duration
            overlay_clip = overlay_clip.with_duration(base_duration)
    elif overlay_duration > base_duration:
        # Trim overlay to match base duration
        overlay_clip = overlay_clip.subclipped(0, base_duration)

    # Handle audio muting
    if overlay_config.muted:
        overlay_clip = overlay_clip.without_audio()

    # Return composited clip with overlay centered on top
    return CompositeVideoClip(
        [base_clip, overlay_clip.with_position("center")],
        size=target_resolution,
    )


def _apply_overlay_to_section(
    base_clip: VideoClip,
    overlay_config: OverlayConfig,
    target_resolution: tuple[int, int],
    fade_in: bool = False,
    fade_out: bool = False,
) -> VideoClip:
    """Applies overlay to a section with optional transition effects.

    This is an internal function that handles overlay application with
    transition effects for section boundaries.

    Args:
        base_clip (VideoClip): The base video clip to overlay onto.
        overlay_config (OverlayConfig): Configuration for the overlay effect.
        target_resolution (tuple[int, int]): Target resolution (width, height).
        fade_in (bool): Whether to apply fade-in effect at the start.
            Defaults to False.
        fade_out (bool): Whether to apply fade-out effect at the end.
            Defaults to False.

    Returns:
        VideoClip: A CompositeVideoClip with the overlay applied.

    Raises:
        ValueError: If overlay_config.video_path is None.
    """
    if overlay_config.video_path is None:
        raise ValueError("overlay_config.video_path cannot be None")

    # Load overlay video and stretch to target resolution
    overlay_clip = VideoFileClip(overlay_config.video_path).resized(target_resolution)

    # Apply brightness mask with threshold
    brightness_mask = create_brightness_mask(
        overlay_clip, overlay_config.mask_threshold
    )
    overlay_clip = apply_mask_with_opacity(
        overlay_clip, brightness_mask, overlay_config.opacity
    )

    # Apply transition effects based on transition type
    effects = []
    transition_type = overlay_config.transition_type
    transition_duration = overlay_config.transition_duration

    if fade_in:
        if transition_type == "crossfade":
            effects.append(vfx.CrossFadeIn(transition_duration))
        elif transition_type == "fade_to_black":
            effects.append(vfx.FadeIn(transition_duration))

    if fade_out:
        if transition_type == "crossfade":
            effects.append(vfx.CrossFadeOut(transition_duration))
        elif transition_type == "fade_to_black":
            effects.append(vfx.FadeOut(transition_duration))

    if effects:
        overlay_clip = overlay_clip.with_effects(effects)

    # Handle duration matching
    base_duration = base_clip.duration
    overlay_duration = overlay_clip.duration

    if overlay_duration < base_duration:
        if overlay_config.loop:
            overlay_clip = overlay_clip.with_effects([vfx.Loop(duration=base_duration)])
        else:
            overlay_clip = overlay_clip.with_duration(base_duration)
    elif overlay_duration > base_duration:
        overlay_clip = overlay_clip.subclipped(0, base_duration)

    # Handle audio muting
    if overlay_config.muted:
        overlay_clip = overlay_clip.without_audio()

    return CompositeVideoClip(
        [base_clip, overlay_clip.with_position("center")],
        size=target_resolution,
    )


def apply_overlays_to_sections(
    intro_clip: VideoClip | None,
    main_clip: VideoClip,
    outro_clip: VideoClip | None,
    overlays: list[OverlayConfig],
    resolution: tuple[int, int],
) -> tuple[VideoClip | None, VideoClip, VideoClip | None]:
    """Applies overlays to video sections with transition handling.

    For each overlay, determines which sections it targets and applies the
    overlay to each targeted section's clip. When an overlay spans multiple
    consecutive sections, applies transition effects at section boundaries.

    Transition types:
        - "crossfade": Fade out overlay at end of section A, fade in at start
          of section B using CrossFadeIn/CrossFadeOut effects.
        - "hard_cut": No special treatment, overlay appears/disappears
          instantly at section boundaries.
        - "fade_to_black": Overlay fades with section using FadeIn/FadeOut
          effects.

    Args:
        intro_clip (VideoClip | None): Optional intro video clip.
        main_clip (VideoClip): Main video clip (required).
        outro_clip (VideoClip | None): Optional outro video clip.
        overlays (list[OverlayConfig]): List of overlay configurations.
        resolution (tuple[int, int]): Target resolution (width, height).

    Returns:
        tuple[VideoClip | None, VideoClip, VideoClip | None]: Tuple of
            (intro_clip, main_clip, outro_clip) with overlays applied.
            Clips may be modified or unchanged depending on overlay targets.

    Example:
        >>> overlays = [
        ...     OverlayConfig(
        ...         video_path="particles.mp4",
        ...         target_sections={"intro", "main"},
        ...         transition_type="crossfade",
        ...     )
        ... ]
        >>> intro, main, outro = apply_overlays_to_sections(
        ...     intro_clip, main_clip, outro_clip, overlays, (1920, 1080)
        ... )
    """
    for overlay in overlays:
        if overlay.video_path is None:
            continue

        target_sections = overlay.target_sections
        transition_type = overlay.transition_type

        # Skip transition effects for hard_cut
        apply_transitions = transition_type != "hard_cut"

        # Determine which sections are targeted (considering None clips)
        has_intro = "intro" in target_sections and intro_clip is not None
        has_main = "main" in target_sections
        has_outro = "outro" in target_sections and outro_clip is not None

        # Determine fade requirements for section boundaries
        # Intro fades out if continuing to main
        intro_fade_out = apply_transitions and has_intro and has_main
        # Main fades in if coming from intro
        main_fade_in = apply_transitions and has_intro and has_main
        # Main fades out if continuing to outro
        main_fade_out = apply_transitions and has_main and has_outro
        # Outro fades in if coming from main
        outro_fade_in = apply_transitions and has_main and has_outro

        # Apply overlay to intro if targeted
        if has_intro:
            intro_clip = _apply_overlay_to_section(
                intro_clip,
                overlay,
                resolution,
                fade_in=False,  # Never fade in at start of intro
                fade_out=intro_fade_out,
            )

        # Apply overlay to main if targeted
        if has_main:
            main_clip = _apply_overlay_to_section(
                main_clip,
                overlay,
                resolution,
                fade_in=main_fade_in,
                fade_out=main_fade_out,
            )

        # Apply overlay to outro if targeted
        if has_outro:
            outro_clip = _apply_overlay_to_section(
                outro_clip,
                overlay,
                resolution,
                fade_in=outro_fade_in,
                fade_out=False,  # Never fade out at end of outro
            )

    return intro_clip, main_clip, outro_clip


def process_overlays(
    clips_dict: dict[str, VideoClip | None],
    overlays: list[OverlayConfig],
    resolution: tuple[int, int],
) -> dict[str, VideoClip | None]:
    """Processes and applies multiple overlays to a set of video clips.

    This function serves as the main entry point for applying cinematic overlays
    to different parts of the video (intro, main, outro).

    Args:
        clips_dict (dict[str, VideoClip | None]): Dictionary containing the
            video clips for each section. Must contain keys "intro", "main",
            and "outro". Values can be None if a section is missing.
        overlays (list[OverlayConfig]): List of overlay configurations to apply.
        resolution (tuple[int, int]): Target resolution (width, height) for the
            final composition.

    Returns:
        dict[str, VideoClip | None]: A new dictionary with the same keys,
            where the values are the clips with overlays applied.
    """
    intro_clip = clips_dict.get("intro")
    main_clip = clips_dict.get("main")
    outro_clip = clips_dict.get("outro")

    if main_clip is None:
        # main_clip is required by apply_overlays_to_sections logic,
        # though we should handle the dictionary interface gracefully.
        return clips_dict.copy()

    processed_intro, processed_main, processed_outro = apply_overlays_to_sections(
        intro_clip,
        main_clip,
        outro_clip,
        overlays,
        resolution,
    )

    return {
        "intro": processed_intro,
        "main": processed_main,
        "outro": processed_outro,
    }
