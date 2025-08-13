"""
YouTube MCP Server

A simple MCP server that fetches YouTube video information and transcripts.
"""

import os
import re
from urllib.parse import urlparse, parse_qs
from mcp.server.fastmcp import FastMCP
from .youtube import get_video_info, get_video_transcript, format_video_info
from .logger import get_logger

# for sse transport testing 
#from dotenv import load_dotenv
#load_dotenv()  # Add this line near the top

logger = get_logger(__name__)

# Create the MCP server
mcp = FastMCP("YouTube Video Analyzer")

def extract_video_id(url_or_id: str) -> str | None:
    """
    Extracts the YouTube video ID from a URL or returns the string if it's already an ID.
    
    Args:
        url_or_id: A YouTube URL or a video ID.
        
    Returns:
        The extracted video ID, or None if it's not a valid YouTube URL or ID.
    """
    # Regex to match YouTube video ID
    video_id_regex = r"^[a-zA-Z0-9_-]{11}$"
    if re.match(video_id_regex, url_or_id):
        return url_or_id

    # Regex to find video ID in a URL
    url_regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(url_regex, url_or_id)
    if match:
        return match.group(1)
        
    return None

@mcp.tool()
def get_yt_video_info(url_or_id: str) -> str:
    """
    Fetch YouTube video information and transcript from a video ID or URL.
    
    Args:
        url_or_id: The YouTube video ID (e.g., 'dQw4w9WgXcQ') or full URL.
    
    Returns:
        A formatted string containing video information and transcript.
    """
    video_id = extract_video_id(url_or_id)
    if not video_id:
        return f"Error: Invalid YouTube URL or video ID provided: {url_or_id}"
    logger.info(f"MCP tool called: get_yt_video_info with video_id: {video_id}")
    
    # Try to get API key from environment variable first, then from context
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        logger.error("YOUTUBE_API_KEY not configured in server settings")
        return "Error: YOUTUBE_API_KEY not configured. Please set it in the server configuration."
    
    logger.info("API_KEY found successfully")
    result = []
    
    try:
        # Get video information
        logger.info(f"Processing video: {video_id}")
        video_info = get_video_info(api_key, video_id)
        result.append("=== VIDEO INFORMATION ===")
        result.append(format_video_info(video_info))
        result.append("")
        
        # Get transcript
        transcript = get_video_transcript(video_id)
        result.append("=== TRANSCRIPT ===")
        if transcript and not transcript.startswith("Transcript error:") and not transcript.startswith("Could not retrieve"):
            result.append(transcript)
            logger.info(f"Successfully processed video {video_id} with transcript")
        else:
            if transcript and (transcript.startswith("Transcript error:") or transcript.startswith("Could not retrieve")):
                result.append(f"Transcript issue: {transcript}")
                logger.warning(f"Transcript issue for video {video_id}: {transcript}")
            else:
                result.append("No transcript available for this video.")
                logger.warning(f"Video {video_id} processed but no transcript available")
        
        final_result = "\n".join(result)
        logger.debug(f"Tool execution completed for video {video_id}, result length: {len(final_result)} characters")
        return final_result
        
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}", exc_info=True)
        return f"Error processing video {video_id}: {str(e)}"

def main():
    """Main entry point for the MCP server."""
    logger.info("Starting YouTube MCP Server with stdio transport")
    try:
        mcp.run()

    #"""Main entry point for the MCP server."""
    #logger.info("Starting YouTube MCP Server with SSE transport")
    #try:
    #    mcp.run(transport="sse")

    #"""Main entry point for the MCP server."""
    #logger.info("Starting YouTube MCP Server with HTTP transport")
    #try:
    #    mcp.run(transport="streamable-http")

    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
