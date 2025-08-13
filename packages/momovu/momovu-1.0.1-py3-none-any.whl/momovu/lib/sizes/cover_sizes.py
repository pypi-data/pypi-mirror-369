"""Book cover size constants for Lulu print specifications.

This module defines standard book cover dimensions for various formats.
All measurements are in millimeters (mm) unless otherwise specified.

Data source: Lulu book size specifications for cover documents.
"""

from typing import Final

# Book cover size specifications
# All measurements in millimeters
BOOK_SIZES_COVER: Final[dict[str, dict[str, float]]] = {
    "A4": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 430,
        "total_height": 303.35,
        "trim_width": 210,
        "trim_height": 297,
    },
    "A4_LANDSCAPE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 604,
        "total_height": 216.35,
        "trim_width": 297,
        "trim_height": 210,
    },
    "A5": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 305,
        "total_height": 216.35,
        "trim_width": 148,
        "trim_height": 210,
    },
    "COMIC_BOOK": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 346,
        "total_height": 266.7,  # 10.5"
        "trim_width": 168.275,  # 6.625"
        "trim_height": 260.35,  # 10.25"
    },
    "COMIC_BOOK_INSIDE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 0,  # No barcode data in CSV
        "barcode_height": 0,
        "barcode_from_trim": 0,
        "total_width": 346,
        "total_height": 266.7,  # 10.5"
        "trim_width": 168.275,  # 6.625"
        "trim_height": 260.35,  # 10.25"
    },
    "CROWN_QUARTO": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 388,
        "total_height": 252.35,
        "trim_width": 189,
        "trim_height": 246,
    },
    "DIGEST": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 289,
        "total_height": 222.25,  # 8.75"
        "trim_width": 139.7,  # 5.5"
        "trim_height": 215.9,  # 8.5"
    },
    "EXECUTIVE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 365,
        "total_height": 260.35,  # 10.25"
        "trim_width": 177.8,  # 7"
        "trim_height": 254,  # 10"
    },
    "NOVELLA": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 263,
        "total_height": 209.55,  # 8.25"
        "trim_width": 127,  # 5"
        "trim_height": 203.2,  # 8"
    },
    "POCKET_BOOK": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 226,
        "total_height": 180.975,  # 7.125"
        "trim_width": 107.95,  # 4.25"
        "trim_height": 174.625,  # 6.875"
    },
    "ROYAL": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 322,
        "total_height": 240.35,
        "trim_width": 156,
        "trim_height": 234,
    },
    "SMALL_LANDSCAPE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 467,
        "total_height": 184.15,  # 7.25"
        "trim_width": 228.6,  # 9"
        "trim_height": 177.8,  # 7"
    },
    "SMALL_SQUARE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 391,
        "total_height": 197,  # 7.75"
        "trim_width": 190.5,  # 7.5"
        "trim_height": 190.5,  # 7.5"
    },
    "US_LETTER": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 441,
        "total_height": 285.75,  # 11.25"
        "trim_width": 215.9,  # 8.5"
        "trim_height": 279.4,  # 11"
    },
    "US_LETTER_LANDSCAPE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 568,
        "total_height": 222.25,  # 8.75"
        "trim_width": 279.4,  # 11"
        "trim_height": 215.9,  # 8.5"
    },
    "US_TRADE": {
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 3.175,  # 0.125"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 314,
        "total_height": 234.95,  # 9.25"
        "trim_width": 152.4,  # 6"
        "trim_height": 228.6,  # 9"
    },
}
