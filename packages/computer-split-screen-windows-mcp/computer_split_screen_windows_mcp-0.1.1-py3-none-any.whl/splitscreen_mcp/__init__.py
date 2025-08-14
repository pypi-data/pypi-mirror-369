"""Computer Split Screen Windows MCP Server."""

__version__ = "0.1.1"
__author__ = "Computer Split Screen MCP Team"

from .windows_actions import (
    left_half_window_win, right_half_window_win,
    top_half_window_win, bottom_half_window_win,
    top_left_quadrant_window_win, top_right_quadrant_window_win,
    bottom_left_quadrant_window_win, bottom_right_quadrant_window_win,
    left_third_window_win, middle_third_window_win, right_third_window_win,
    left_two_thirds_window_win, right_two_thirds_window_win,
    maximise_window_win, minimise_window_win,
)

__all__ = [
    "__version__",
    "__author__",
    "left_half_window_win", "right_half_window_win",
    "top_half_window_win", "bottom_half_window_win",
    "top_left_quadrant_window_win", "top_right_quadrant_window_win",
    "bottom_left_quadrant_window_win", "bottom_right_quadrant_window_win",
    "left_third_window_win", "middle_third_window_win", "right_third_window_win",
    "left_two_thirds_window_win", "right_two_thirds_window_win",
    "maximise_window_win", "minimise_window_win",
]
