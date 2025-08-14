from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from .windows_actions import (
    left_half_window_win, right_half_window_win,
    top_half_window_win, bottom_half_window_win,
    top_left_quadrant_window_win, top_right_quadrant_window_win,
    bottom_left_quadrant_window_win, bottom_right_quadrant_window_win,
    left_third_window_win, middle_third_window_win, right_third_window_win,
    maximise_window_win, minimise_window_win,
)

mcp = FastMCP("splitwin")

def ok(msg: str) -> TextContent:
    return TextContent(type="text", text=msg)

@mcp.tool("left-half", description="Snap current window to left half")
def left_half() -> TextContent:
    left_half_window_win()
    return ok("left-half: done")

@mcp.tool("right-half", description="Snap current window to right half")
def right_half() -> TextContent:
    right_half_window_win()
    return ok("right-half: done")

@mcp.tool("top-half", description="Snap current window to top half")
def top_half() -> TextContent:
    top_half_window_win()
    return ok("top-half: done")

@mcp.tool("bottom-half", description="Snap current window to bottom half")
def bottom_half() -> TextContent:
    bottom_half_window_win()
    return ok("bottom-half: done")

@mcp.tool("top-left", description="Top-left quadrant")
def top_left() -> TextContent:
    top_left_quadrant_window_win()
    return ok("top-left: done")

@mcp.tool("top-right", description="Top-right quadrant")
def top_right() -> TextContent:
    top_right_quadrant_window_win()
    return ok("top-right: done")

@mcp.tool("bottom-left", description="Bottom-left quadrant")
def bottom_left() -> TextContent:
    bottom_left_quadrant_window_win()
    return ok("bottom-left: done")

@mcp.tool("bottom-right", description="Bottom-right quadrant")
def bottom_right() -> TextContent:
    bottom_right_quadrant_window_win()
    return ok("bottom-right: done")

@mcp.tool("left-third", description="Left third (1/3)")
def left_third() -> TextContent:
    left_third_window_win()
    return ok("left-third: done")

@mcp.tool("middle-third", description="Middle third (1/3)")
def middle_third() -> TextContent:
    middle_third_window_win()
    return ok("middle-third: done")

@mcp.tool("right-third", description="Right third (1/3)")
def right_third() -> TextContent:
    right_third_window_win()
    return ok("right-third: done")

@mcp.tool("maximize", description="OS maximize (bordered)")
def maximize() -> TextContent:
    maximise_window_win()
    return ok("maximize: done")

@mcp.tool("minimize", description="Minimize")
def minimize() -> TextContent:
    success = minimise_window_win()
    return ok("minimize: done" if success else "minimize: failed")

def main():
    # Run the MCP server over stdio (what uvx expects)
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
