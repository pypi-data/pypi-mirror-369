"""Book dustjacket size constants for Lulu print specifications.

This module defines standard book dustjacket dimensions for various formats.
Note: Only certain book formats support dustjackets.
All measurements are in millimeters (mm) unless otherwise specified.

Data source: Lulu book size specifications for dustjacket documents.
"""

from typing import Final

# Book dustjacket size specifications
# All measurements in millimeters
BOOK_SIZES_DUSTJACKET: Final[dict[str, dict[str, float]]] = {
    "A4": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 303,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 623,
        "total_height": 316.35,
        "cover_width": 213,
        "cover_height": 303,
        "trim_width": 210,
        "trim_height": 297,
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 303,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
    "A5": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 216,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 499,
        "total_height": 229.35,
        "cover_width": 151,
        "cover_height": 216,
        "trim_width": 148,
        "trim_height": 210,
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 216,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
    "DIGEST": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 222,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 483,
        "total_height": 235.25,  # 9.25"
        "cover_width": 143,
        "cover_height": 222,
        "trim_width": 139.7,  # 5.5"
        "trim_height": 215.9,  # 8.5"
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 222,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
    "NOVELLA": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 210,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 457,
        "total_height": 222.55,  # 8.75"
        "cover_width": 130,
        "cover_height": 210,
        "trim_width": 127,  # 5"
        "trim_height": 203.2,  # 8"
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 210,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
    "ROYAL": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 240,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 515,
        "total_height": 253.35,
        "cover_width": 159,
        "cover_height": 240,
        "trim_width": 156,
        "trim_height": 234,
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 240,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
    "US_LETTER": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 286,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 635,
        "total_height": 298.75,  # 11.75"
        "cover_width": 219,
        "cover_height": 286,
        "trim_width": 215.9,  # 8.5"
        "trim_height": 279.4,  # 11"
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 286,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
    "US_TRADE": {
        "back_flap_width": 82.55,  # 3.25"
        "back_flap_height": 235,
        "back_flap_fold_margin": 6.35,  # 0.25"
        "safety_margin": 12.7,  # 0.5"
        "bleed_area": 6.35,  # 0.25"
        "barcode_width": 92.075,  # 3.625"
        "barcode_height": 31.75,  # 1.25"
        "barcode_from_trim": 12.7,  # 0.5"
        "total_width": 508,
        "total_height": 247.95,  # 9.75"
        "cover_width": 156,
        "cover_height": 235,
        "trim_width": 152.4,  # 6"
        "trim_height": 228.6,  # 9"
        "front_flap_width": 82.55,  # 3.25"
        "front_flap_height": 235,
        "front_flap_fold_margin": 6.35,  # 0.25"
    },
}
