import textwrap
from PIL import ImageFont


def soft_wrap_text(
    text: str,
    fontsize: int,
    letter_spacing: int,
    font_family: str,
    max_width: int,
):
    # Note that font_family has to be an absolut path to your .ttf/.otf
    image_font = ImageFont.truetype(font_family, fontsize)

    # I am not sure my letter spacing calculation is accurate
    text_width = image_font.getlength(text) + (len(text) - 1) * letter_spacing
    letter_width = text_width / len(text)

    if text_width < max_width:
        return text

    max_chars = int(max_width / letter_width)

    # For Japanese/CJK text, we need to break on any character since
    # there are no spaces between words. Use break_long_words=True
    # and break_on_hyphens=False to handle this properly.
    wrapped_text = textwrap.fill(
        text, width=max_chars, break_long_words=True, break_on_hyphens=False
    )
    return wrapped_text
