import json
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from mcp_ffmpeg_detector.ffmpeg_utils import which_ffmpeg, ffmpeg_version, install_ffmpeg

# Configure logging to stderr (important for stdio servers)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("ffmpeg-detector")


@mcp.tool()
def detect_ffmpeg() -> str:
    """
    Args:
        None
    
    Returns:
        result: JSON string with fields: available (bool), path (str|None), version (str|None)
    """
    path = which_ffmpeg()
    if path:
        return json.dumps({
            "available": True,
            "path": path,
            "version": ffmpeg_version(path),
        })
    else:
        return json.dumps({
            "available": False,
            "path": None,
            "version": None,
        })


@mcp.tool()
def ensure_ffmpeg() -> str:
    """
    Args:
        None

    Returns:
        result: JSON string with fields: installed (bool), path (str|None), message (str)
    """
    path = which_ffmpeg()
    if path:
        return json.dumps({
            "installed": True,
            "path": path,
            "message": f"ffmpeg already available: {ffmpeg_version(path)}",
        })

    ok, exe, msg = install_ffmpeg()
    if ok and exe:
        return json.dumps({
            "installed": True,
            "path": exe,
            "message": msg,
        })
    else:
        return json.dumps({
            "installed": False,
            "path": None,
            "message": msg,
        })


def main() -> None:
    """
    Args:
        None
    
    Returns:
        result: None. Starts the MCP server over stdio.
    """
    # On startup, attempt to ensure ffmpeg exists for convenience
    try:
        if not which_ffmpeg():
            logger.info("ffmpeg not found, attempting to install...")
            install_ffmpeg()
    except Exception as e:
        logger.warning(f"ffmpeg install attempt failed: {e}")

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()