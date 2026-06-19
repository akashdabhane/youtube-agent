from tools.video_tools import get_recent_videos, get_video_stats
from langchain_core.tools import tool
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import ssl
import httplib2
from datetime import datetime

load_dotenv()

# Disable SSL verification — only for local dev/testing, never in production
http = httplib2.Http(disable_ssl_certificate_validation=True)


youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"), http=http)


@tool
def get_trending_videos(region_code: str = "IN"):
    """
    Get trending videos in a specific region.
    Returns a list of trending video titles and their view counts.
    Accepts a region code (e.g., 'US', 'IN') and returns the most popular videos in that region, along with their view counts.
    """

    response = (
        youtube.videos()
        .list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=25,
        )
        .execute()
    )

    return [
        {
            "title": item["snippet"]["title"],
            "views": item["statistics"].get("viewCount"),
        }
        for item in response["items"]
    ]


@tool
def analyze_upload_frequency(channel_id: str):
    """
    Analyze how frequently a channel uploads videos.
    Accepts a channel ID and calculates the average number of uploads per week based on the publish dates of recent videos.
    Returns the average number of uploads per week based on the publish dates of recent videos.
    """

    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 50})

    dates = [
        datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")) for v in videos
    ]

    if len(dates) < 2:
        return "Not enough videos"

    span = (max(dates) - min(dates)).days

    uploads_per_week = (len(dates) / max(span, 1)) * 7

    return {
        "videos_analyzed": len(dates),
        "uploads_per_week": round(uploads_per_week, 2),
    }


@tool
def get_top_performing_videos(channel_id: str):
    """
    Get the top performing videos of a channel based on view count.
    Accepts a channel ID and returns the top 10 videos sorted by view count, including their titles and view counts.

    """

    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 50})

    enriched = []

    for v in videos:

        stats = get_video_stats.invoke(v["video_id"])

        enriched.append({**v, **stats})

    enriched.sort(key=lambda x: int(x["views"]), reverse=True)

    return enriched[:10]
