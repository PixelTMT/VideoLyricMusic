"""
Video Lyric Music Generator - Gradio Web Application
"""

import tempfile
import os
import gradio as gr
from video_lyric_music import create_lyric_video
from video_concatenator import (
    concatenate_videos_with_transitions,
    validate_intro_outro_files,
)
from video_overlay import validate_overlay_files, OverlayConfig, SectionName


def collect_overlay_configs(
    overlay_1_file,
    overlay_1_loop,
    overlay_1_mask_threshold,
    overlay_1_opacity,
    overlay_1_muted,
    overlay_1_target_intro,
    overlay_1_target_main,
    overlay_1_target_outro,
    overlay_1_transition_type,
    overlay_1_transition_duration,
    overlay_2_file,
    overlay_2_loop,
    overlay_2_mask_threshold,
    overlay_2_opacity,
    overlay_2_muted,
    overlay_2_target_intro,
    overlay_2_target_main,
    overlay_2_target_outro,
    overlay_2_transition_type,
    overlay_2_transition_duration,
    overlay_3_file,
    overlay_3_loop,
    overlay_3_mask_threshold,
    overlay_3_opacity,
    overlay_3_muted,
    overlay_3_target_intro,
    overlay_3_target_main,
    overlay_3_target_outro,
    overlay_3_transition_type,
    overlay_3_transition_duration,
) -> list[OverlayConfig]:
    """Collect overlay configurations from UI components.

    Args:
        overlay_1_file to overlay_3_transition_duration: UI component values.

    Returns:
        List of OverlayConfig objects for active overlays.
    """
    configs = []

    # Process Overlay 1
    if overlay_1_file:
        target_sections: set[SectionName] = set()
        if overlay_1_target_intro:
            target_sections.add("intro")
        if overlay_1_target_main:
            target_sections.add("main")
        if overlay_1_target_outro:
            target_sections.add("outro")

        if not target_sections:
            target_sections = {"main"}

        configs.append(
            OverlayConfig(
                video_path=overlay_1_file,
                mask_threshold=overlay_1_mask_threshold,
                opacity=overlay_1_opacity,
                loop=overlay_1_loop,
                muted=overlay_1_muted,
                target_sections=target_sections,
                transition_type=overlay_1_transition_type.lower().replace(" ", "_"),
                transition_duration=overlay_1_transition_duration,
            )
        )

    # Process Overlay 2
    if overlay_2_file:
        target_sections: set[SectionName] = set()
        if overlay_2_target_intro:
            target_sections.add("intro")
        if overlay_2_target_main:
            target_sections.add("main")
        if overlay_2_target_outro:
            target_sections.add("outro")

        if not target_sections:
            target_sections = {"main"}

        configs.append(
            OverlayConfig(
                video_path=overlay_2_file,
                mask_threshold=overlay_2_mask_threshold,
                opacity=overlay_2_opacity,
                loop=overlay_2_loop,
                muted=overlay_2_muted,
                target_sections=target_sections,
                transition_type=overlay_2_transition_type.lower().replace(" ", "_"),
                transition_duration=overlay_2_transition_duration,
            )
        )

    # Process Overlay 3
    if overlay_3_file:
        target_sections: set[SectionName] = set()
        if overlay_3_target_intro:
            target_sections.add("intro")
        if overlay_3_target_main:
            target_sections.add("main")
        if overlay_3_target_outro:
            target_sections.add("outro")

        if not target_sections:
            target_sections = {"main"}

        configs.append(
            OverlayConfig(
                video_path=overlay_3_file,
                mask_threshold=overlay_3_mask_threshold,
                opacity=overlay_3_opacity,
                loop=overlay_3_loop,
                muted=overlay_3_muted,
                target_sections=target_sections,
                transition_type=overlay_3_transition_type.lower().replace(" ", "_"),
                transition_duration=overlay_3_transition_duration,
            )
        )

    return configs


def parse_resolution(
    resolution_str: str, custom_width: int | None, custom_height: int | None
) -> tuple[int, int]:
    """Parse resolution string to tuple."""
    resolution_map = {
        "1920x1080 (Full HD)": (1920, 1080),
        "1280x720 (HD)": (1280, 720),
        "3840x2160 (4K)": (3840, 2160),
        "1080x1920 (Vertical)": (1080, 1920),
    }
    if resolution_str == "Custom" and custom_width and custom_height:
        return (custom_width, custom_height)
    return resolution_map.get(resolution_str, (1920, 1080))


def handle_preview(
    lrc_file,
    lrc_text,
    audio_file,
    background_file,
    font_file,
    font_size,
    font_color,
    stroke_color,
    stroke_width,
    text_align,
    text_position,
    x_offset,
    y_offset,
    max_text_width,
    fade_enabled,
    fade_in_duration,
    fade_out_duration,
    resolution,
    custom_width,
    custom_height,
    fps,
    bitrate,
    preview_start,
    preview_duration,
):
    """Handle preview button click - renders short clip."""
    if not audio_file:
        raise gr.Error("Please upload an audio file")
    if not background_file:
        raise gr.Error("Please upload a background image or video")
    if not lrc_file and not lrc_text:
        raise gr.Error("Please provide LRC file or paste LRC text")

    lrc_path = None
    try:
        if lrc_file:
            lrc_path = lrc_file
        elif lrc_text:
            with tempfile.NamedTemporaryFile(
                suffix=".lrc", delete=False, mode="w", encoding="utf-8"
            ) as f:
                f.write(lrc_text)
                lrc_path = f.name

        output_path = tempfile.mktemp(suffix=".mp4")
        resolution_tuple = parse_resolution(resolution, custom_width, custom_height)
        max_text_width_val = max_text_width if max_text_width > 0 else None
        font_path_val = font_file if font_file else None

        start_time = preview_start
        end_time = preview_start + preview_duration

        create_lyric_video(
            audio_path=audio_file,
            lrc_path=lrc_path,
            output_path=output_path,
            background_path=background_file,
            resolution=resolution_tuple,
            fps=fps,
            font_path=font_path_val,
            font_size=font_size,
            font_color=font_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            text_align=text_align,
            text_position=text_position,
            position_x_offset=x_offset,
            position_y_offset=y_offset,
            max_text_width=max_text_width_val,
            fade_enabled=fade_enabled,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            start_time=start_time,
            end_time=end_time,
            bitrate=bitrate,
        )

        return (
            output_path,
            f"Preview rendered: {preview_duration}s clip from {preview_start}s",
        )
    except Exception as e:
        raise gr.Error(f"Preview failed: {str(e)}")
    finally:
        if lrc_path and lrc_text and os.path.exists(lrc_path):
            try:
                os.unlink(lrc_path)
            except Exception:
                pass


def handle_full_render(
    lrc_file,
    lrc_text,
    audio_file,
    background_file,
    font_file,
    font_size,
    font_color,
    stroke_color,
    stroke_width,
    text_align,
    text_position,
    x_offset,
    y_offset,
    max_text_width,
    fade_enabled,
    fade_in_duration,
    fade_out_duration,
    resolution,
    custom_width,
    custom_height,
    fps,
    bitrate,
):
    """Handle full render button click - renders entire song."""
    if not audio_file:
        raise gr.Error("Please upload an audio file")
    if not background_file:
        raise gr.Error("Please upload a background image or video")
    if not lrc_file and not lrc_text:
        raise gr.Error("Please provide LRC file or paste LRC text")

    lrc_path = None
    try:
        if lrc_file:
            lrc_path = lrc_file
        elif lrc_text:
            with tempfile.NamedTemporaryFile(
                suffix=".lrc", delete=False, mode="w", encoding="utf-8"
            ) as f:
                f.write(lrc_text)
                lrc_path = f.name

        output_path = tempfile.mktemp(suffix=".mp4")
        resolution_tuple = parse_resolution(resolution, custom_width, custom_height)
        max_text_width_val = max_text_width if max_text_width > 0 else None
        font_path_val = font_file if font_file else None

        create_lyric_video(
            audio_path=audio_file,
            lrc_path=lrc_path,
            output_path=output_path,
            background_path=background_file,
            resolution=resolution_tuple,
            fps=fps,
            font_path=font_path_val,
            font_size=font_size,
            font_color=font_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            text_align=text_align,
            text_position=text_position,
            position_x_offset=x_offset,
            position_y_offset=y_offset,
            max_text_width=max_text_width_val,
            fade_enabled=fade_enabled,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            start_time=None,
            end_time=None,
            bitrate=bitrate,
        )

        return output_path, "Full render completed!"
    except Exception as e:
        raise gr.Error(f"Render failed: {str(e)}")
    finally:
        if lrc_path and lrc_text and os.path.exists(lrc_path):
            try:
                os.unlink(lrc_path)
            except Exception:
                pass


def handle_combine_preview(
    lrc_file,
    lrc_text,
    audio_file,
    background_file,
    font_file,
    font_size,
    font_color,
    stroke_color,
    stroke_width,
    text_align,
    text_position,
    x_offset,
    y_offset,
    max_text_width,
    fade_enabled,
    fade_in_duration,
    fade_out_duration,
    resolution,
    custom_width,
    custom_height,
    fps,
    bitrate,
    preview_start,
    preview_duration,
    intro_video_file,
    outro_video_file,
    transition_type,
    transition_duration,
    include_intro_outro_audio,
    overlay_1_file,
    overlay_1_loop,
    overlay_1_mask_threshold,
    overlay_1_opacity,
    overlay_1_muted,
    overlay_1_target_intro,
    overlay_1_target_main,
    overlay_1_target_outro,
    overlay_1_transition_type,
    overlay_1_transition_duration,
    overlay_2_file,
    overlay_2_loop,
    overlay_2_mask_threshold,
    overlay_2_opacity,
    overlay_2_muted,
    overlay_2_target_intro,
    overlay_2_target_main,
    overlay_2_target_outro,
    overlay_2_transition_type,
    overlay_2_transition_duration,
    overlay_3_file,
    overlay_3_loop,
    overlay_3_mask_threshold,
    overlay_3_opacity,
    overlay_3_muted,
    overlay_3_target_intro,
    overlay_3_target_main,
    overlay_3_target_outro,
    overlay_3_transition_type,
    overlay_3_transition_duration,
):
    """Handle preview with intro/outro concatenation and overlays."""
    if not audio_file:
        raise gr.Error("Please upload an audio file")
    if not background_file:
        raise gr.Error("Please upload a background image or video")
    if not lrc_file and not lrc_text:
        raise gr.Error("Please provide LRC file or paste LRC text")

    # Collect overlay configurations
    overlay_configs = collect_overlay_configs(
        overlay_1_file,
        overlay_1_loop,
        overlay_1_mask_threshold,
        overlay_1_opacity,
        overlay_1_muted,
        overlay_1_target_intro,
        overlay_1_target_main,
        overlay_1_target_outro,
        overlay_1_transition_type,
        overlay_1_transition_duration,
        overlay_2_file,
        overlay_2_loop,
        overlay_2_mask_threshold,
        overlay_2_opacity,
        overlay_2_muted,
        overlay_2_target_intro,
        overlay_2_target_main,
        overlay_2_target_outro,
        overlay_2_transition_type,
        overlay_2_transition_duration,
        overlay_3_file,
        overlay_3_loop,
        overlay_3_mask_threshold,
        overlay_3_opacity,
        overlay_3_muted,
        overlay_3_target_intro,
        overlay_3_target_main,
        overlay_3_target_outro,
        overlay_3_transition_type,
        overlay_3_transition_duration,
    )

    # Validate overlay files if provided
    if overlay_configs:
        is_valid, error_msg = validate_overlay_files(overlay_configs)
        if not is_valid:
            raise gr.Error(f"Overlay validation failed: {error_msg}")

    lrc_path = None
    lyric_video_path = None
    try:
        # Create temp LRC file if needed
        if lrc_file:
            lrc_path = lrc_file
        elif lrc_text:
            with tempfile.NamedTemporaryFile(
                suffix=".lrc", delete=False, mode="w", encoding="utf-8"
            ) as f:
                f.write(lrc_text)
                lrc_path = f.name

        # Generate lyric video
        lyric_video_path = tempfile.mktemp(suffix=".mp4")
        resolution_tuple = parse_resolution(resolution, custom_width, custom_height)
        max_text_width_val = max_text_width if max_text_width > 0 else None
        font_path_val = font_file if font_file else None

        start_time = preview_start
        end_time = preview_start + preview_duration

        create_lyric_video(
            audio_path=audio_file,
            lrc_path=lrc_path,
            output_path=lyric_video_path,
            background_path=background_file,
            resolution=resolution_tuple,
            fps=fps,
            font_path=font_path_val,
            font_size=font_size,
            font_color=font_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            text_align=text_align,
            text_position=text_position,
            position_x_offset=x_offset,
            position_y_offset=y_offset,
            max_text_width=max_text_width_val,
            fade_enabled=fade_enabled,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            start_time=start_time,
            end_time=end_time,
            bitrate=bitrate,
        )

        # Check if intro/outro concatenation needed
        intro_path = intro_video_file if intro_video_file else None
        outro_path = outro_video_file if outro_video_file else None

        if intro_path or outro_path:
            # Validate intro/outro files
            is_valid, error_msg = validate_intro_outro_files(intro_path, outro_path)
            if not is_valid:
                raise gr.Error(error_msg)

            # Convert transition type from UI format to function format
            transition_type_val = transition_type.lower().replace(" ", "_")

            # Generate final output with transitions
            final_output_path = tempfile.mktemp(suffix=".mp4")
            concatenate_videos_with_transitions(
                intro_path=intro_path,
                lyric_video_path=lyric_video_path,
                outro_path=outro_path,
                output_path=final_output_path,
                transition_type=transition_type_val,
                transition_duration=transition_duration,
                include_intro_outro_audio=include_intro_outro_audio,
                target_resolution=resolution_tuple,
                target_fps=fps,
                bitrate=bitrate,
                overlays=overlay_configs,
            )

            # Clean up intermediate lyric video

            if os.path.exists(lyric_video_path):
                try:
                    os.unlink(lyric_video_path)
                except Exception:
                    pass
            lyric_video_path = None

            return (
                final_output_path,
                f"Preview with intro/outro: {preview_duration}s clip from {preview_start}s",
            )
        else:
            # No intro/outro, but still need to apply overlays if provided
            if overlay_configs:
                # Apply overlays to lyric video directly
                from video_overlay import process_overlays

                clips_dict = {
                    "intro": None,
                    "main": lyric_video_path,  # Will be loaded
                    "outro": None,
                }

                # Load the lyric video clip
                from moviepy.editor import VideoFileClip

                lyric_clip = VideoFileClip(lyric_video_path)

                clips_dict = {
                    "intro": None,
                    "main": lyric_clip,
                    "outro": None,
                }

                processed_clips = process_overlays(
                    clips_dict, overlay_configs, resolution_tuple
                )

                # Write the processed clip
                final_output_path = tempfile.mktemp(suffix=".mp4")
                processed_clips["main"].write_videofile(
                    final_output_path,
                    fps=fps,
                    codec="libx264",
                    audio_codec="aac",
                    bitrate=bitrate,
                    logger=None,
                )

                # Clean up
                lyric_clip.close()
                processed_clips["main"].close()

                if os.path.exists(lyric_video_path):
                    try:
                        os.unlink(lyric_video_path)
                    except Exception:
                        pass

                return (
                    final_output_path,
                    f"Preview with overlays: {preview_duration}s clip from {preview_start}s",
                )

            return (
                lyric_video_path,
                f"Preview rendered: {preview_duration}s clip from {preview_start}s",
            )
    except gr.Error:
        raise
    except Exception as e:
        raise gr.Error(f"Preview failed: {str(e)}")
    finally:
        if lrc_path and lrc_text and os.path.exists(lrc_path):
            try:
                os.unlink(lrc_path)
            except Exception:
                pass


def handle_combine_render(
    lrc_file,
    lrc_text,
    audio_file,
    background_file,
    font_file,
    font_size,
    font_color,
    stroke_color,
    stroke_width,
    text_align,
    text_position,
    x_offset,
    y_offset,
    max_text_width,
    fade_enabled,
    fade_in_duration,
    fade_out_duration,
    resolution,
    custom_width,
    custom_height,
    fps,
    bitrate,
    intro_video_file,
    outro_video_file,
    transition_type,
    transition_duration,
    include_intro_outro_audio,
    overlay_1_file,
    overlay_1_loop,
    overlay_1_mask_threshold,
    overlay_1_opacity,
    overlay_1_muted,
    overlay_1_target_intro,
    overlay_1_target_main,
    overlay_1_target_outro,
    overlay_1_transition_type,
    overlay_1_transition_duration,
    overlay_2_file,
    overlay_2_loop,
    overlay_2_mask_threshold,
    overlay_2_opacity,
    overlay_2_muted,
    overlay_2_target_intro,
    overlay_2_target_main,
    overlay_2_target_outro,
    overlay_2_transition_type,
    overlay_2_transition_duration,
    overlay_3_file,
    overlay_3_loop,
    overlay_3_mask_threshold,
    overlay_3_opacity,
    overlay_3_muted,
    overlay_3_target_intro,
    overlay_3_target_main,
    overlay_3_target_outro,
    overlay_3_transition_type,
    overlay_3_transition_duration,
):
    """Handle full render with intro/outro concatenation and overlays."""
    if not audio_file:
        raise gr.Error("Please upload an audio file")
    if not background_file:
        raise gr.Error("Please upload a background image or video")
    if not lrc_file and not lrc_text:
        raise gr.Error("Please provide LRC file or paste LRC text")

    # Collect overlay configurations
    overlay_configs = collect_overlay_configs(
        overlay_1_file,
        overlay_1_loop,
        overlay_1_mask_threshold,
        overlay_1_opacity,
        overlay_1_muted,
        overlay_1_target_intro,
        overlay_1_target_main,
        overlay_1_target_outro,
        overlay_1_transition_type,
        overlay_1_transition_duration,
        overlay_2_file,
        overlay_2_loop,
        overlay_2_mask_threshold,
        overlay_2_opacity,
        overlay_2_muted,
        overlay_2_target_intro,
        overlay_2_target_main,
        overlay_2_target_outro,
        overlay_2_transition_type,
        overlay_2_transition_duration,
        overlay_3_file,
        overlay_3_loop,
        overlay_3_mask_threshold,
        overlay_3_opacity,
        overlay_3_muted,
        overlay_3_target_intro,
        overlay_3_target_main,
        overlay_3_target_outro,
        overlay_3_transition_type,
        overlay_3_transition_duration,
    )

    # Validate overlay files if provided
    if overlay_configs:
        is_valid, error_msg = validate_overlay_files(overlay_configs)
        if not is_valid:
            raise gr.Error(f"Overlay validation failed: {error_msg}")

    lrc_path = None
    lyric_video_path = None
    try:
        # Create temp LRC file if needed
        if lrc_file:
            lrc_path = lrc_file
        elif lrc_text:
            with tempfile.NamedTemporaryFile(
                suffix=".lrc", delete=False, mode="w", encoding="utf-8"
            ) as f:
                f.write(lrc_text)
                lrc_path = f.name

        # Generate lyric video
        lyric_video_path = tempfile.mktemp(suffix=".mp4")
        resolution_tuple = parse_resolution(resolution, custom_width, custom_height)
        max_text_width_val = max_text_width if max_text_width > 0 else None
        font_path_val = font_file if font_file else None

        create_lyric_video(
            audio_path=audio_file,
            lrc_path=lrc_path,
            output_path=lyric_video_path,
            background_path=background_file,
            resolution=resolution_tuple,
            fps=fps,
            font_path=font_path_val,
            font_size=font_size,
            font_color=font_color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            text_align=text_align,
            text_position=text_position,
            position_x_offset=x_offset,
            position_y_offset=y_offset,
            max_text_width=max_text_width_val,
            fade_enabled=fade_enabled,
            fade_in_duration=fade_in_duration,
            fade_out_duration=fade_out_duration,
            start_time=None,
            end_time=None,
            bitrate=bitrate,
        )

        # Check if intro/outro concatenation needed
        intro_path = intro_video_file if intro_video_file else None
        outro_path = outro_video_file if outro_video_file else None

        if intro_path or outro_path:
            # Validate intro/outro files
            is_valid, error_msg = validate_intro_outro_files(intro_path, outro_path)
            if not is_valid:
                raise gr.Error(error_msg)

            # Convert transition type from UI format to function format
            transition_type_val = transition_type.lower().replace(" ", "_")

            # Generate final output with transitions
            final_output_path = tempfile.mktemp(suffix=".mp4")
            concatenate_videos_with_transitions(
                intro_path=intro_path,
                lyric_video_path=lyric_video_path,
                outro_path=outro_path,
                output_path=final_output_path,
                transition_type=transition_type_val,
                transition_duration=transition_duration,
                include_intro_outro_audio=include_intro_outro_audio,
                target_resolution=resolution_tuple,
                target_fps=fps,
                bitrate=bitrate,
                overlays=overlay_configs,
            )

            # Clean up intermediate lyric video

            if os.path.exists(lyric_video_path):
                try:
                    os.unlink(lyric_video_path)
                except Exception:
                    pass
            lyric_video_path = None

            return final_output_path, "Full render with intro/outro completed!"
        else:
            # No intro/outro, but still need to apply overlays if provided
            if overlay_configs:
                # Apply overlays to lyric video directly
                from video_overlay import process_overlays
                from moviepy.editor import VideoFileClip

                lyric_clip = VideoFileClip(lyric_video_path)

                clips_dict = {
                    "intro": None,
                    "main": lyric_clip,
                    "outro": None,
                }

                processed_clips = process_overlays(
                    clips_dict, overlay_configs, resolution_tuple
                )

                # Write the processed clip
                final_output_path = tempfile.mktemp(suffix=".mp4")
                processed_clips["main"].write_videofile(
                    final_output_path,
                    fps=fps,
                    codec="libx264",
                    audio_codec="aac",
                    bitrate=bitrate,
                    logger=None,
                )

                # Clean up
                lyric_clip.close()
                processed_clips["main"].close()

                if os.path.exists(lyric_video_path):
                    try:
                        os.unlink(lyric_video_path)
                    except Exception:
                        pass

                return final_output_path, "Full render with overlays completed!"

            return lyric_video_path, "Full render completed!"
    except gr.Error:
        raise
    except Exception as e:
        raise gr.Error(f"Render failed: {str(e)}")
    finally:
        if lrc_path and lrc_text and os.path.exists(lrc_path):
            try:
                os.unlink(lrc_path)
            except Exception:
                pass


def toggle_custom_resolution(resolution: str):
    """Show/hide custom resolution fields based on dropdown selection."""
    return gr.update(visible=resolution == "Custom"), gr.update(
        visible=resolution == "Custom"
    )


def add_overlay_slot(current_count: int) -> int:
    """Increment overlay count, max 3.

    Args:
        current_count: Current number of visible overlay slots.

    Returns:
        New overlay count.
    """
    return min(current_count + 1, 3)


def remove_overlay_slot(current_count: int) -> int:
    """Decrement overlay count, min 0.

    Args:
        current_count: Current number of visible overlay slots.

    Returns:
        New overlay count.
    """
    return max(current_count - 1, 0)


def update_overlay_visibility(count: int):
    """Update visibility of overlay groups based on count.

    Args:
        count: Number of overlays to show.

    Returns:
        List of gr.update objects for the three overlay groups.
    """
    return [
        gr.update(visible=count >= 1),
        gr.update(visible=count >= 2),
        gr.update(visible=count >= 3),
    ]


def get_overlay_configs(*args) -> list[dict]:
    """Collect all overlay settings into a list of configurations.

    This function expects groups of arguments for each overlay.
    Each group should contain the necessary fields for one overlay.

    Returns:
        List of overlay configuration dictionaries.
    """
    configs = []
    # Each overlay has 8 parameters currently (based on common video overlay needs)
    # This will be refined as UI components are added in Task 11
    # For now, we provide the structure.
    items_per_overlay = 8
    for i in range(0, len(args), items_per_overlay):
        overlay_args = args[i : i + items_per_overlay]
        if overlay_args[0]:  # If file is provided
            configs.append(
                {
                    "file": overlay_args[0],
                    "start_time": overlay_args[1],
                    "end_time": overlay_args[2],
                    "position": overlay_args[3],
                    "x_offset": overlay_args[4],
                    "y_offset": overlay_args[5],
                    "opacity": overlay_args[6],
                    "scale": overlay_args[7],
                }
            )
    return configs


with gr.Blocks(title="Video Lyric Music Generator", theme=gr.themes.Soft()) as demo:
    overlay_count = gr.State(value=0)
    gr.Markdown("# 🎬 Video Lyric Music Generator")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 📥 Inputs")

            with gr.Tabs():
                with gr.TabItem("📁 Upload .lrc"):
                    lrc_file = gr.File(
                        label="LRC File", file_types=[".lrc"], type="filepath"
                    )
                with gr.TabItem("📝 Paste LRC"):
                    lrc_text = gr.Textbox(
                        label="Paste LRC Text",
                        lines=15,
                        placeholder="[00:05.00] First line...",
                    )

            audio_file = gr.Audio(
                label="Audio File", sources=["upload"], type="filepath"
            )

            background_file = gr.File(
                label="Background Image/Video",
                file_types=["image", ".mp4", ".mov", ".avi", ".mkv", ".webm"],
                type="filepath",
            )

            font_file = gr.File(
                label="Font File (optional)",
                file_types=[".ttf", ".otf"],
                type="filepath",
            )

            with gr.Accordion("📝 Text Settings", open=True):
                font_size = gr.Slider(
                    minimum=16, maximum=200, value=100, step=1, label="Font Size"
                )
                font_color = gr.ColorPicker(value="#FFFFFF", label="Font Color")
                stroke_color = gr.ColorPicker(value="#000000", label="Stroke Color")
                stroke_width = gr.Slider(
                    minimum=0, maximum=10, value=5, step=1, label="Stroke Width"
                )
                text_align = gr.Dropdown(
                    choices=["left", "center", "right"],
                    value="center",
                    label="Text Alignment",
                )
                text_position = gr.Dropdown(
                    choices=["top", "center", "bottom"],
                    value="center",
                    label="Text Position",
                )
                x_offset = gr.Slider(
                    minimum=-500, maximum=500, value=0, step=10, label="X Offset"
                )
                y_offset = gr.Slider(
                    minimum=-500, maximum=500, value=0, step=10, label="Y Offset"
                )
                max_text_width = gr.Number(
                    value=0, label="Max Text Width (0=auto)", minimum=0, maximum=3840
                )

            with gr.Accordion("🌅 Fade Settings", open=False):
                fade_enabled = gr.Checkbox(value=True, label="Enable Fade")
                fade_in_duration = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.2,
                    step=0.1,
                    label="Fade In Duration",
                )
                fade_out_duration = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.2,
                    step=0.1,
                    label="Fade Out Duration",
                )

            with gr.Accordion("🎥 Video Settings", open=False):
                resolution = gr.Dropdown(
                    choices=[
                        "1920x1080 (Full HD)",
                        "1280x720 (HD)",
                        "3840x2160 (4K)",
                        "1080x1920 (Vertical)",
                        "Custom",
                    ],
                    value="1920x1080 (Full HD)",
                    label="Resolution",
                )
                custom_width = gr.Number(
                    value=1920, label="Custom Width", visible=False
                )
                custom_height = gr.Number(
                    value=1080, label="Custom Height", visible=False
                )
                fps = gr.Slider(minimum=12, maximum=60, value=24, step=1, label="FPS")
                bitrate = gr.Dropdown(
                    choices=["1000k", "2000k", "4000k", "8000k", "16000k"],
                    value="4000k",
                    label="Bitrate",
                )

            with gr.Accordion("👁️ Preview Settings", open=True):
                preview_start = gr.Slider(
                    minimum=0,
                    maximum=300,
                    value=0,
                    step=1,
                    label="Preview Start (seconds)",
                )
                preview_duration = gr.Slider(
                    minimum=5,
                    maximum=60,
                    value=10,
                    step=1,
                    label="Preview Duration (seconds)",
                )

            with gr.Accordion("🎬 Intro/Outro Settings", open=False):
                intro_video_file = gr.File(
                    label="Intro Video (optional)",
                    file_types=[".mp4", ".mov", ".avi", ".mkv", ".webm"],
                    type="filepath",
                )
                outro_video_file = gr.File(
                    label="Outro Video (optional)",
                    file_types=[".mp4", ".mov", ".avi", ".mkv", ".webm"],
                    type="filepath",
                )
                transition_type = gr.Dropdown(
                    choices=["Crossfade", "Hard Cut", "Fade to Black"],
                    value="Crossfade",
                    label="Transition Type",
                )
                transition_duration = gr.Slider(
                    minimum=0.1,
                    maximum=3.0,
                    value=1.0,
                    step=0.1,
                    label="Transition Duration (seconds)",
                )
                include_intro_outro_audio = gr.Checkbox(
                    value=False, label="Include intro/outro audio"
                )

            with gr.Accordion("🎨 Overlay Effects", open=False):
                gr.Markdown("Add video overlays to enhance your video. Max 3 overlays.")

                # Overlay 1 - Always visible when overlay_count >= 1
                with gr.Group(visible=False) as overlay_1_group:
                    gr.Markdown("### Overlay 1")
                    overlay_1_file = gr.File(
                        label="Overlay Video",
                        file_types=[".mp4", ".mov", ".avi", ".mkv", ".webm"],
                        type="filepath",
                    )
                    with gr.Row():
                        overlay_1_loop = gr.Checkbox(value=False, label="Loop Video")
                        overlay_1_muted = gr.Checkbox(value=True, label="Mute Audio")
                    with gr.Row():
                        overlay_1_mask_threshold = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.5,
                            step=0.05,
                            label="Mask Threshold",
                        )
                        overlay_1_opacity = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=1.0,
                            step=0.05,
                            label="Opacity",
                        )
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("**Target Sections**")
                            overlay_1_target_intro = gr.Checkbox(
                                value=False, label="Intro"
                            )
                            overlay_1_target_main = gr.Checkbox(
                                value=True, label="Main Video"
                            )
                            overlay_1_target_outro = gr.Checkbox(
                                value=False, label="Outro"
                            )
                    with gr.Row():
                        overlay_1_transition_type = gr.Dropdown(
                            choices=["Crossfade", "Hard Cut", "Fade to Black"],
                            value="Crossfade",
                            label="Transition Type",
                        )
                        overlay_1_transition_duration = gr.Slider(
                            minimum=0.1,
                            maximum=3.0,
                            value=1.0,
                            step=0.1,
                            label="Transition Duration (seconds)",
                        )
                    overlay_1_remove_btn = gr.Button(
                        "Remove Overlay 1", variant="secondary", size="sm"
                    )

                # Overlay 2 - Visible when overlay_count >= 2
                with gr.Group(visible=False) as overlay_2_group:
                    gr.Markdown("### Overlay 2")
                    overlay_2_file = gr.File(
                        label="Overlay Video",
                        file_types=[".mp4", ".mov", ".avi", ".mkv", ".webm"],
                        type="filepath",
                    )
                    with gr.Row():
                        overlay_2_loop = gr.Checkbox(value=False, label="Loop Video")
                        overlay_2_muted = gr.Checkbox(value=True, label="Mute Audio")
                    with gr.Row():
                        overlay_2_mask_threshold = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.2,
                            step=0.05,
                            label="Mask Threshold",
                        )
                        overlay_2_opacity = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=1.0,
                            step=0.05,
                            label="Opacity",
                        )
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("**Target Sections**")
                            overlay_2_target_intro = gr.Checkbox(
                                value=False, label="Intro"
                            )
                            overlay_2_target_main = gr.Checkbox(
                                value=True, label="Main Video"
                            )
                            overlay_2_target_outro = gr.Checkbox(
                                value=False, label="Outro"
                            )
                    with gr.Row():
                        overlay_2_transition_type = gr.Dropdown(
                            choices=["Crossfade", "Hard Cut", "Fade to Black"],
                            value="Crossfade",
                            label="Transition Type",
                        )
                        overlay_2_transition_duration = gr.Slider(
                            minimum=0.1,
                            maximum=3.0,
                            value=1.0,
                            step=0.1,
                            label="Transition Duration (seconds)",
                        )
                    overlay_2_remove_btn = gr.Button(
                        "Remove Overlay 2", variant="secondary", size="sm"
                    )

                # Overlay 3 - Visible when overlay_count >= 3
                with gr.Group(visible=False) as overlay_3_group:
                    gr.Markdown("### Overlay 3")
                    overlay_3_file = gr.File(
                        label="Overlay Video",
                        file_types=[".mp4", ".mov", ".avi", ".mkv", ".webm"],
                        type="filepath",
                    )
                    with gr.Row():
                        overlay_3_loop = gr.Checkbox(value=False, label="Loop Video")
                        overlay_3_muted = gr.Checkbox(value=True, label="Mute Audio")
                    with gr.Row():
                        overlay_3_mask_threshold = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.2,
                            step=0.05,
                            label="Mask Threshold",
                        )
                        overlay_3_opacity = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=1.0,
                            step=0.05,
                            label="Opacity",
                        )
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("**Target Sections**")
                            overlay_3_target_intro = gr.Checkbox(
                                value=False, label="Intro"
                            )
                            overlay_3_target_main = gr.Checkbox(
                                value=True, label="Main Video"
                            )
                            overlay_3_target_outro = gr.Checkbox(
                                value=False, label="Outro"
                            )
                    with gr.Row():
                        overlay_3_transition_type = gr.Dropdown(
                            choices=["Crossfade", "Hard Cut", "Fade to Black"],
                            value="Crossfade",
                            label="Transition Type",
                        )
                        overlay_3_transition_duration = gr.Slider(
                            minimum=0.1,
                            maximum=3.0,
                            value=1.0,
                            step=0.1,
                            label="Transition Duration (seconds)",
                        )
                    overlay_3_remove_btn = gr.Button(
                        "Remove Overlay 3", variant="secondary", size="sm"
                    )

                add_overlay_btn = gr.Button(
                    "+ Add Overlay", variant="primary", size="sm"
                )

            with gr.Row():
                preview_btn = gr.Button("🎬 Preview", variant="secondary")
                render_btn = gr.Button("🚀 Full Render", variant="primary")

            with gr.Row():
                preview_combined_btn = gr.Button(
                    "🎬 Preview Combined", variant="secondary"
                )
                render_with_intro_outro_btn = gr.Button(
                    "🚀 Full Render with Intro/Outro", variant="primary"
                )

        with gr.Column(scale=1):
            gr.Markdown("## 📤 Output")
            output_video = gr.Video(label="Output", autoplay=False)
            status_text = gr.Textbox(label="Status", interactive=False)

    resolution.change(
        toggle_custom_resolution,
        inputs=[resolution],
        outputs=[custom_width, custom_height],
    )

    preview_btn.click(
        fn=handle_preview,
        inputs=[
            lrc_file,
            lrc_text,
            audio_file,
            background_file,
            font_file,
            font_size,
            font_color,
            stroke_color,
            stroke_width,
            text_align,
            text_position,
            x_offset,
            y_offset,
            max_text_width,
            fade_enabled,
            fade_in_duration,
            fade_out_duration,
            resolution,
            custom_width,
            custom_height,
            fps,
            bitrate,
            preview_start,
            preview_duration,
        ],
        outputs=[output_video, status_text],
    )

    render_btn.click(
        fn=handle_full_render,
        inputs=[
            lrc_file,
            lrc_text,
            audio_file,
            background_file,
            font_file,
            font_size,
            font_color,
            stroke_color,
            stroke_width,
            text_align,
            text_position,
            x_offset,
            y_offset,
            max_text_width,
            fade_enabled,
            fade_in_duration,
            fade_out_duration,
            resolution,
            custom_width,
            custom_height,
            fps,
            bitrate,
        ],
        outputs=[output_video, status_text],
    )

    preview_combined_btn.click(
        fn=handle_combine_preview,
        inputs=[
            lrc_file,
            lrc_text,
            audio_file,
            background_file,
            font_file,
            font_size,
            font_color,
            stroke_color,
            stroke_width,
            text_align,
            text_position,
            x_offset,
            y_offset,
            max_text_width,
            fade_enabled,
            fade_in_duration,
            fade_out_duration,
            resolution,
            custom_width,
            custom_height,
            fps,
            bitrate,
            preview_start,
            preview_duration,
            intro_video_file,
            outro_video_file,
            transition_type,
            transition_duration,
            include_intro_outro_audio,
            overlay_1_file,
            overlay_1_loop,
            overlay_1_mask_threshold,
            overlay_1_opacity,
            overlay_1_muted,
            overlay_1_target_intro,
            overlay_1_target_main,
            overlay_1_target_outro,
            overlay_1_transition_type,
            overlay_1_transition_duration,
            overlay_2_file,
            overlay_2_loop,
            overlay_2_mask_threshold,
            overlay_2_opacity,
            overlay_2_muted,
            overlay_2_target_intro,
            overlay_2_target_main,
            overlay_2_target_outro,
            overlay_2_transition_type,
            overlay_2_transition_duration,
            overlay_3_file,
            overlay_3_loop,
            overlay_3_mask_threshold,
            overlay_3_opacity,
            overlay_3_muted,
            overlay_3_target_intro,
            overlay_3_target_main,
            overlay_3_target_outro,
            overlay_3_transition_type,
            overlay_3_transition_duration,
        ],
        outputs=[output_video, status_text],
    )

    render_with_intro_outro_btn.click(
        fn=handle_combine_render,
        inputs=[
            lrc_file,
            lrc_text,
            audio_file,
            background_file,
            font_file,
            font_size,
            font_color,
            stroke_color,
            stroke_width,
            text_align,
            text_position,
            x_offset,
            y_offset,
            max_text_width,
            fade_enabled,
            fade_in_duration,
            fade_out_duration,
            resolution,
            custom_width,
            custom_height,
            fps,
            bitrate,
            intro_video_file,
            outro_video_file,
            transition_type,
            transition_duration,
            include_intro_outro_audio,
            overlay_1_file,
            overlay_1_loop,
            overlay_1_mask_threshold,
            overlay_1_opacity,
            overlay_1_muted,
            overlay_1_target_intro,
            overlay_1_target_main,
            overlay_1_target_outro,
            overlay_1_transition_type,
            overlay_1_transition_duration,
            overlay_2_file,
            overlay_2_loop,
            overlay_2_mask_threshold,
            overlay_2_opacity,
            overlay_2_muted,
            overlay_2_target_intro,
            overlay_2_target_main,
            overlay_2_target_outro,
            overlay_2_transition_type,
            overlay_2_transition_duration,
            overlay_3_file,
            overlay_3_loop,
            overlay_3_mask_threshold,
            overlay_3_opacity,
            overlay_3_muted,
            overlay_3_target_intro,
            overlay_3_target_main,
            overlay_3_target_outro,
            overlay_3_transition_type,
            overlay_3_transition_duration,
        ],
        outputs=[output_video, status_text],
    )

    # --- Overlay Button Event Handlers ---
    add_overlay_btn.click(
        fn=add_overlay_slot,
        inputs=[overlay_count],
        outputs=[overlay_count],
    ).then(
        fn=update_overlay_visibility,
        inputs=[overlay_count],
        outputs=[overlay_1_group, overlay_2_group, overlay_3_group],
    )

    overlay_1_remove_btn.click(
        fn=remove_overlay_slot,
        inputs=[overlay_count],
        outputs=[overlay_count],
    ).then(
        fn=update_overlay_visibility,
        inputs=[overlay_count],
        outputs=[overlay_1_group, overlay_2_group, overlay_3_group],
    )

    overlay_2_remove_btn.click(
        fn=remove_overlay_slot,
        inputs=[overlay_count],
        outputs=[overlay_count],
    ).then(
        fn=update_overlay_visibility,
        inputs=[overlay_count],
        outputs=[overlay_1_group, overlay_2_group, overlay_3_group],
    )

    overlay_3_remove_btn.click(
        fn=remove_overlay_slot,
        inputs=[overlay_count],
        outputs=[overlay_count],
    ).then(
        fn=update_overlay_visibility,
        inputs=[overlay_count],
        outputs=[overlay_1_group, overlay_2_group, overlay_3_group],
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        max_file_size="200mb",
        allowed_paths=["/tmp"],
    )
