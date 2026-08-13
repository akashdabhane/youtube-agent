from langchain_core.tools import tool
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import httplib2
import re

load_dotenv()

# Disable SSL verification — only for local dev/testing, never in production
http = httplib2.Http(disable_ssl_certificate_validation=True)

youtube = build(
    "youtube", 
    "v3", 
    developerKey=os.getenv("YOUTUBE_API_KEY"),
    http=http
)


def parse_iso8601_duration(duration_str: str) -> str:
    """Helper to convert ISO 8601 duration string (e.g., PT15M33S) into human readable time format."""
    pattern = re.compile(r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = pattern.match(duration_str)
    if not match:
        return duration_str
    
    parts = match.groupdict()
    hours = int(parts['hours'] or 0)
    minutes = int(parts['minutes'] or 0)
    seconds = int(parts['seconds'] or 0)
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@tool
def get_recent_videos(channel_id: str, max_results: int = 10) -> list:
    """
    Get the most recent videos from a YouTube channel.
    Returns a list of video titles, IDs, and publish dates.
    """
    try:
        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=max_results,
            order="date",
            type="video"
        ).execute()

        return [
            {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "description": item["snippet"]["description"][:300],
            }
            for item in response.get("items", [])
        ]
    except Exception as e:
        print(f"Error fetching recent videos for {channel_id}: {e}")
        return []


@tool
def get_video_stats(video_id: str) -> dict:
    """
    Get engagement statistics for a specific YouTube video.
    Returns view count, like count, and comment count.
    """
    try:
        response = youtube.videos().list(
            part="statistics,snippet",
            id=video_id
        ).execute()

        if not response.get("items"):
            return {"error": "Video not found"}

        item = response["items"][0]
        return {
            "title": item["snippet"]["title"],
            "views": item["statistics"].get("viewCount", "0"),
            "likes": item["statistics"].get("likeCount", "0"),
            "comments": item["statistics"].get("commentCount", "0"),
        }
    except Exception as e:
        print(f"Error fetching video stats for {video_id}: {e}")
        return {"error": "Unable to fetch video statistics"}


@tool
def get_video_details(video_id: str) -> dict:
    """
    Get detailed metadata for a specific YouTube video.
    Returns video duration, tags, category, view count, like count, comment count, and publish date.
    """
    try:
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()

        if not response.get("items"):
            return {"error": "Video not found"}

        item = response["items"][0]
        snippet = item["snippet"]
        stats = item["statistics"]
        content_details = item["contentDetails"]

        raw_duration = content_details.get("duration", "")
        readable_duration = parse_iso8601_duration(raw_duration)

        return {
            "video_id": video_id,
            "title": snippet.get("title"),
            "published_at": snippet.get("publishedAt"),
            "duration": readable_duration,
            "tags": snippet.get("tags", [])[:10],
            "category_id": snippet.get("categoryId"),
            "views": stats.get("viewCount", "0"),
            "likes": stats.get("likeCount", "0"),
            "comments": stats.get("commentCount", "0"),
            "definition": content_details.get("definition")
        }
    except Exception as e:
        print(f"Error fetching video details for {video_id}: {e}")
        return {"error": "Unable to fetch video details"}


@tool
def get_video_comments(video_id: str, max_results: int = 100) -> list:
    """
    Get top comments for a specific YouTube video.
    Returns a list of comments with author, text, and like count.
    """
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            order="relevance"
        ).execute()

        return [
            {
                "author": item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                "likes": item["snippet"]["topLevelComment"]["snippet"]["likeCount"],
            }
            for item in response.get("items", [])
        ]
    except Exception as e:
        print(f"Error fetching comments for video {video_id}: {e}")
        return []


@tool
def search_channel_videos(
    channel_id: str,
    keyword: str
) -> list:
    """
    Search for videos within a specific channel using a keyword.
    Returns a list of matching videos with their IDs and titles.
    """
    try:
        response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            q=keyword,
            maxResults=20,
            type="video"
        ).execute()

        return [
            {
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"]
            }
            for item in response.get("items", [])
        ]
    except Exception as e:
        print(f"Error searching channel videos: {e}")
        return []
