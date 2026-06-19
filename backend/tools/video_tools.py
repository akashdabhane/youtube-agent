from langchain_core.tools import tool
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import ssl
import httplib2


load_dotenv()

# Disable SSL verification — only for local dev/testing, never in production
http = httplib2.Http(disable_ssl_certificate_validation=True)


youtube = build(
    "youtube", 
    "v3", 
    developerKey=os.getenv("YOUTUBE_API_KEY"),
    http=http
)


@tool
def get_recent_videos(channel_id: str, max_results: int = 10) -> list:
    """
    Get the most recent videos from a YouTube channel.
    Returns a list of video titles, IDs, and publish dates.
    """
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
        for item in response["items"]
    ]


@tool
def get_video_stats(video_id: str) -> dict:
    """
    Get engagement statistics for a specific YouTube video.
    Returns view count, like count, and comment count.
    """
    response = youtube.videos().list(
        part="statistics,snippet",
        id=video_id
    ).execute()

    item = response["items"][0]
    return {
        "title": item["snippet"]["title"],
        "views": item["statistics"].get("viewCount"),
        "likes": item["statistics"].get("likeCount"),
        "comments": item["statistics"].get("commentCount"),
    }


@tool
def get_video_comments(video_id: str, max_results: int = 100) -> list:  # ← added types
    """
    Get top comments for a specific YouTube video.
    Returns a list of comments with author, text, and like count.
    """
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
        for item in response["items"]       # ← also fixed the list bug from your ChatGPT convo
    ]


@tool
def search_channel_videos(
    channel_id: str,
    keyword: str
) -> list:
    """
    Search for videos within a specific channel using a keyword.
    Returns a list of matching videos with their IDs and titles.
    Accepts a channel ID and a search keyword, and returns videos from that channel that match the keyword in their title or description.
    """

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
        for item in response["items"]
    ]

