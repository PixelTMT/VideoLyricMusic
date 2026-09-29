"""
LRC file parser module using Python standard library.
"""

import re
import os
from dataclasses import dataclass


@dataclass
class LyricLine:
    """Represents a single line of lyrics with its timestamp.

    Attributes:
        timestamp: Float representing seconds from start of audio.
        text: String containing the lyric text content.
    """

    timestamp: float
    text: str


def parse_lrc(file_path: str) -> list[LyricLine]:
    """Parses an LRC file and returns a sorted list of LyricLine objects.

    Args:
        file_path: Path to the .lrc file.

    Returns:
        A list of LyricLine objects, sorted by timestamp.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        OSError: If there is an error reading the file.
    """
    lyrics: list[LyricLine] = []

    # Metadata tag pattern: [key:value] where key is alphabetic
    metadata_pattern = re.compile(r"^\[[a-zA-Z]+:.*\]$")
    # Timestamp pattern: [mm:ss.xx] or [mm:ss.xxx]
    timestamp_pattern = re.compile(r"\[(\d{1,3}):(\d{2})[\.:](\d{2,3})\]")

    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Skip metadata tags
            if metadata_pattern.match(line):
                continue

            # Extract all timestamps and the remaining text
            matches = list(timestamp_pattern.finditer(line))
            if not matches:
                continue

            # Text is what remains after all timestamp tags
            # We find the end of the last timestamp match
            last_match_end = matches[-1].end()
            text = line[last_match_end:].strip()

            # Skip empty text lines (instrumental breaks)
            #if not text:
            #    continue

            for match in matches:
                minutes = int(match.group(1))
                seconds = int(match.group(2))
                fraction_str = match.group(3)

                # Normalization: 3 digits -> milliseconds, 2 digits -> centiseconds
                if len(fraction_str) == 3:
                    fraction = int(fraction_str) / 1000.0
                else:
                    fraction = int(fraction_str) / 100.0

                total_seconds = minutes * 60 + seconds + fraction
                lyrics.append(LyricLine(timestamp=total_seconds, text=text))

    # Sort results by timestamp ascending
    lyrics.sort(key=lambda x: x.timestamp)
    return lyrics


def filter_lyrics(
    lyrics: list[LyricLine], start_time: float, end_time: float
) -> list[LyricLine]:
    """Filters lyrics within a specific time window.

    Args:
        lyrics: List of LyricLine objects.
        start_time: Start of the window in seconds.
        end_time: End of the window in seconds.

    Returns:
        List of LyricLine objects within the window [start_time, end_time).
    """
    return [line for line in lyrics if start_time <= line.timestamp < end_time]


if __name__ == "__main__":
    # Demonstrate parsing a sample LRC string
    import tempfile

    sample = """[ti:Test Song]
[ar:Test Artist]
[00:05.00] First lyric line
[00:10.50] Second lyric line
[00:15.123] Third lyric with three-digit milliseconds
"""
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".lrc", delete=False, encoding="utf-8"
    )
    f.write(sample)
    f.close()
    try:
        result = parse_lrc(f.name)
        for line in result:
            print(f"  {line.timestamp:.3f}s: {line.text}")
    finally:
        if os.path.exists(f.name):
            os.unlink(f.name)
