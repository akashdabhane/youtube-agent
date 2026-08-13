from tools.video_tools import get_recent_videos, get_video_stats
from langchain_core.tools import tool
from datetime import datetime
from lib.youtube import youtube


@tool
def get_trending_videos(region_code: str = "IN"):
    """
    Get trending videos in a specific region.
    Returns a list of trending video titles, channel names, and their view counts.
    Accepts a region code (e.g., 'US', 'IN', 'GB') and returns the most popular videos.
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
            "channel_title": item["snippet"]["channelTitle"],
            "views": item["statistics"].get("viewCount"),
        }
        for item in response.get("items", [])
    ]


@tool
def search_global_videos(query: str, max_results: int = 10) -> list:
    """
    Search YouTube globally for videos matching any search query/keyword.
    Returns a list of video titles, video IDs, channel names, and publish dates across YouTube.
    """
    response = (
        youtube.search()
        .list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            order="relevance"
        )
        .execute()
    )

    return [
        {
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel_title": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"]
        }
        for item in response.get("items", [])
    ]


@tool
def analyze_upload_frequency(channel_id: str):
    """
    Analyze how frequently a channel uploads videos.
    Accepts a channel ID and calculates the average number of uploads per week based on recent publish dates.
    Returns average uploads per week and total videos analyzed.
    """
    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 50})

    dates = [
        datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")) for v in videos
    ]

    if len(dates) < 2:
        return "Not enough videos to analyze upload frequency"

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
    Accepts a channel ID and returns the top 10 videos sorted by view count, including titles, views, and likes.
    """
    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 50})

    enriched = []
    for v in videos:
        stats = get_video_stats.invoke(v["video_id"])
        enriched.append({**v, **stats})

    enriched.sort(key=lambda x: int(x.get("views", 0)), reverse=True)

    return enriched[:10]


@tool
def calculate_channel_engagement_rate(channel_id: str) -> dict:
    """
    Calculate the average engagement rate (%) for a YouTube channel based on recent videos.
    Engagement Rate = ((Total Likes + Total Comments) / Total Views) * 100.
    Returns average view count, average likes, average comments, and engagement rate percentage.
    """
    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 20})

    if not videos:
        return {"error": "No videos found for channel"}

    total_views = 0
    total_likes = 0
    total_comments = 0
    valid_videos = 0

    for v in videos:
        stats = get_video_stats.invoke(v["video_id"])
        views = int(stats.get("views", 0))
        likes = int(stats.get("likes", 0))
        comments = int(stats.get("comments", 0))

        if views > 0:
            total_views += views
            total_likes += likes
            total_comments += comments
            valid_videos += 1

    if valid_videos == 0 or total_views == 0:
        return {"error": "Insufficient video statistics to calculate engagement rate"}

    engagement_rate = ((total_likes + total_comments) / total_views) * 100

    return {
        "channel_id": channel_id,
        "videos_analyzed": valid_videos,
        "average_views": round(total_views / valid_videos),
        "average_likes": round(total_likes / valid_videos),
        "average_comments": round(total_comments / valid_videos),
        "engagement_rate_percent": round(engagement_rate, 2)
    }


@tool
def get_youtube_video_categories(region_code: str = "US") -> list:
    """
    Get official YouTube video categories and category ID mapping for a region.
    Returns category IDs and category titles (e.g. Science & Technology, Gaming, Education, Entertainment).
    """
    response = youtube.videoCategories().list(
        part="snippet",
        regionCode=region_code
    ).execute()

    return [
        {
            "id": item["id"],
            "title": item["snippet"]["title"]
        }
        for item in response.get("items", [])
    ]
