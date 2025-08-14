"""Dustjacket spine width lookup table for page count ranges.

This module defines the spine width lookup table for dustjackets based on page count.
The table provides discrete spine width values for specific page count ranges,
unlike covers which use a continuous formula.

Data source: Restored from git commit 42505ca (was in margin_sizes.py)
All measurements are in millimeters (mm).
"""

from typing import Final


def get_dustjacket_spine_width(page_count: int) -> float:
    """Get dustjacket spine width in mm for given page count.

    Args:
        page_count: Number of pages in the document

    Returns:
        Spine width in millimeters

    Note:
        For page counts outside the 24-800 range, returns 6mm (minimum width)
    """
    if 24 <= page_count <= 84:
        return 6.0
    elif 85 <= page_count <= 140:
        return 13.0
    elif 141 <= page_count <= 168:
        return 16.0
    elif 169 <= page_count <= 194:
        return 17.0
    elif 195 <= page_count <= 222:
        return 19.0
    elif 223 <= page_count <= 250:
        return 21.0
    elif 251 <= page_count <= 278:
        return 22.0
    elif 279 <= page_count <= 306:
        return 24.0
    elif 307 <= page_count <= 334:
        return 25.0
    elif 335 <= page_count <= 360:
        return 27.0
    elif 361 <= page_count <= 388:
        return 29.0
    elif 389 <= page_count <= 416:
        return 30.0
    elif 417 <= page_count <= 444:
        return 32.0
    elif 445 <= page_count <= 472:
        return 33.0
    elif 473 <= page_count <= 500:
        return 35.0
    elif 501 <= page_count <= 528:
        return 37.0
    elif 529 <= page_count <= 556:
        return 38.0
    elif 557 <= page_count <= 582:
        return 40.0
    elif 583 <= page_count <= 610:
        return 41.0
    elif 611 <= page_count <= 638:
        return 43.0
    elif 639 <= page_count <= 666:
        return 44.0
    elif 667 <= page_count <= 694:
        return 46.0
    elif 695 <= page_count <= 722:
        return 48.0
    elif 723 <= page_count <= 750:
        return 49.0
    elif 751 <= page_count <= 778:
        return 51.0
    elif 779 <= page_count <= 799:
        return 52.0
    elif page_count == 800:
        return 54.0
    else:
        # Default for out of range values (< 24 or > 800)
        return 6.0


# Lookup table as a constant for reference
DUSTJACKET_SPINE_WIDTH_TABLE: Final[dict[tuple[int, int], float]] = {
    (24, 84): 6.0,
    (85, 140): 13.0,
    (141, 168): 16.0,
    (169, 194): 17.0,
    (195, 222): 19.0,
    (223, 250): 21.0,
    (251, 278): 22.0,
    (279, 306): 24.0,
    (307, 334): 25.0,
    (335, 360): 27.0,
    (361, 388): 29.0,
    (389, 416): 30.0,
    (417, 444): 32.0,
    (445, 472): 33.0,
    (473, 500): 35.0,
    (501, 528): 37.0,
    (529, 556): 38.0,
    (557, 582): 40.0,
    (583, 610): 41.0,
    (611, 638): 43.0,
    (639, 666): 44.0,
    (667, 694): 46.0,
    (695, 722): 48.0,
    (723, 750): 49.0,
    (751, 778): 51.0,
    (779, 799): 52.0,
    (800, 800): 54.0,
}
