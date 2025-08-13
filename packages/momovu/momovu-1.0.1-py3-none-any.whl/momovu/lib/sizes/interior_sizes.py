"""Book interior size constants for Lulu print specifications.

This module defines standard book interior page dimensions for various formats.
All measurements are in millimeters (mm) unless otherwise specified.

Data source: Lulu book size specifications for interior documents.
"""

from typing import Final

# Book interior size specifications
# All measurements in millimeters
BOOK_SIZES_INTERIOR: Final[dict[str, dict[str, float]]] = {
    "A4": {
        "total_width": 216.35,
        "total_height": 303.35,
        "trim_width": 210,
        "trim_height": 297,
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "A4_LANDSCAPE": {
        "total_width": 303.35,
        "total_height": 216.35,
        "trim_width": 297,
        "trim_height": 210,
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "A5": {
        "total_width": 154.35,
        "total_height": 216.35,
        "trim_width": 148,
        "trim_height": 210,
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "COMIC_BOOK": {
        "total_width": 174.625,  # 6.875"
        "total_height": 266.7,  # 10.5"
        "trim_width": 168.275,  # 6.625"
        "trim_height": 260.35,  # 10.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "CROWN_QUARTO": {
        "total_width": 195.35,
        "total_height": 252.35,
        "trim_width": 189,
        "trim_height": 246,
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "DIGEST": {
        "total_width": 146.05,  # 5.75"
        "total_height": 222.25,  # 8.75"
        "trim_width": 139.7,  # 5.5"
        "trim_height": 215.9,  # 8.5"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "EXECUTIVE": {
        "total_width": 184.15,  # 7.25"
        "total_height": 260.35,  # 10.25"
        "trim_width": 177.8,  # 7"
        "trim_height": 254,  # 10"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "NOVELLA": {
        "total_width": 133.35,  # 5.25"
        "total_height": 209.55,  # 8.25"
        "trim_width": 127,  # 5"
        "trim_height": 203.2,  # 8"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "POCKET_BOOK": {
        "total_width": 114.3,  # 4.5"
        "total_height": 180.975,  # 7.125"
        "trim_width": 107.95,  # 4.25"
        "trim_height": 174.625,  # 6.875"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "ROYAL": {
        "total_width": 162.35,
        "total_height": 240.35,
        "trim_width": 156,
        "trim_height": 234,
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "SMALL_LANDSCAPE": {
        "total_width": 234.95,  # 9.25"
        "total_height": 184.15,  # 7.25"
        "trim_width": 228.6,  # 9"
        "trim_height": 177.8,  # 7"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "SMALL_SQUARE": {
        "total_width": 197,  # 7.75"
        "total_height": 197,  # 7.75"
        "trim_width": 190.5,  # 7.5"
        "trim_height": 190.5,  # 7.5"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "US_LETTER": {
        "total_width": 222.25,  # 8.75"
        "total_height": 285.75,  # 11.25"
        "trim_width": 215.9,  # 8.5"
        "trim_height": 279.4,  # 11"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "US_LETTER_LANDSCAPE": {
        "total_width": 285.75,  # 11.25"
        "total_height": 222.25,  # 8.75"
        "trim_width": 279.4,  # 11"
        "trim_height": 215.9,  # 8.5"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
    "US_TRADE": {
        "total_width": 158.75,  # 6.25"
        "total_height": 234.95,  # 9.25"
        "trim_width": 152.4,  # 6"
        "trim_height": 228.6,  # 9"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
    },
}
