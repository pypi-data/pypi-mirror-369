#!/usr/bin/env python3
"""
Command-line interface for YouTube video extraction
"""
import argparse
import os
import sys
import re
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Add the src directory to Python path for absolute imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Use absolute imports instead of relative imports
from mcp_youtube_extract.youtube import get_video_info, get_video_transcript, format_video_info

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

def main():
    parser = argparse.ArgumentParser(description="Extract YouTube video information and transcript from a video ID or URL")
    #parser.add_argument("url_or_id", help='YouTube video ID (e.g., dQw4w9WgXcQ) or full URL (e.g., "https://www.youtube.com/watch?v=dQw4w9WgXcQ")')
    parser.add_argument("url_or_id", help='''YouTube video ID (e.g., dQw4w9WgXcQ) or full URL (e.g.,  
                                           IMPORTANT: use quotes around URLs: 
                                           "https://www.youtube.com/watch?v=dQw4w9WgXcQ")''')
    parser.add_argument("--info-only", action="store_true", help="Get only video information, skip transcript")
    parser.add_argument("--transcript-only", action="store_true", help="Get only transcript, skip video info")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    video_id = extract_video_id(args.url_or_id)
    if not video_id:
        print(f"Error: Invalid YouTube URL or video ID provided: {args.url_or_id}", file=sys.stderr)
        sys.exit(1)
        
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables", file=sys.stderr)
        print("Please set it in your .env file or environment", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = []
        
        if not args.transcript_only:
            # Get video information
            print(f"Fetching video info for: {video_id}", file=sys.stderr)
            video_info = get_video_info(api_key, video_id)
            result.append("=== VIDEO INFORMATION ===")
            result.append(format_video_info(video_info))
            result.append("")
        
        if not args.info_only:
            # Get transcript
            print(f"Fetching transcript for: {video_id}", file=sys.stderr)
            transcript = get_video_transcript(video_id)
            result.append("=== TRANSCRIPT ===")
            
            if transcript and not transcript.startswith("Transcript error:") and not transcript.startswith("Could not retrieve"):
                result.append(transcript)
            else:
                result.append(f"Transcript issue: {transcript}")
        
        output = "\n".join(result)
        
        # Write output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            print(output)
            
    except Exception as e:
        print(f"Error processing video {video_id}: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
