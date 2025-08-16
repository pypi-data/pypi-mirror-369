"""
Configuration settings for the subtitle translation system.
"""

# Subtitle processing settings
# Pattern to match and remove HTML-like tags from SRT files
SRT_TAG_PATTERN = r"<[^>]+>"

# ASS subtitle resolution settings
PLAY_RES_X = 1280
PLAY_RES_Y = 720

# Style names
SOURCE_STYLE = "Source"

# Top text (original language) styling
TOP_TEXT_FONTNAME = "Arial"
TOP_TEXT_FONTSIZE = 46
TOP_TEXT_COLOR = 0xD3D3D3  # Light gray
TOP_TEXT_SECONDARY_COLOR = 0xF0000000  # Black with alpha
TOP_TEXT_OUTLINE_COLOR = 0x101010  # Dark gray
TOP_TEXT_BACK_COLOR = 0x80000000  # Semi-transparent black

# Bottom text (translated language) styling
BOTTOM_TEXT_FONTNAME = "Microsoft YaHei"
BOTTOM_TEXT_FONTSIZE = 36
BOTTOM_TEXT_COLOR = 0x99CCFF  # Light orange
