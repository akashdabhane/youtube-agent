from tools.video_tools import get_recent_videos
from langchain_core.tools import tool
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import httplib2
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer

load_dotenv()

# Disable SSL verification — only for local dev/testing, never in production
http = httplib2.Http(disable_ssl_certificate_validation=True)

youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"), http=http)


@tool
def get_channel_info_by_id(channel_id: str) -> dict:
    """
    Get YouTube channel statistics and info given a channel ID.
    Returns subscriber count, view count, video count, title, description, custom URL, and published date.
    """
    response = (
        youtube.channels().list(part="snippet,statistics", id=channel_id).execute()
    )

    if not response.get("items"):
        return {"error": "Channel not found"}

    item = response["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]

    return {
        "channel_id": item["id"],
        "title": snippet["title"],
        "description": snippet["description"],
        "custom_url": snippet.get("customUrl"),
        "published_at": snippet.get("publishedAt"),
        "subscribers": stats.get("subscriberCount", "0"),
        "total_views": stats.get("viewCount", "0"),
        "video_count": stats.get("videoCount", "0"),
    }


@tool
def search_channel_by_name(company_name: str) -> dict:
    """
    Search for a YouTube channel by company or creator name.
    Returns the channel ID and title of the best match.
    """
    response = (
        youtube.search()
        .list(part="snippet", q=company_name, type="channel", maxResults=1)
        .execute()
    )

    if not response.get("items"):
        return {"error": "No matching channel found"}

    item = response["items"][0]
    return {
        "channel_id": item["snippet"]["channelId"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"][:200]
    }


@tool
def get_channel_by_handle(handle: str) -> dict:
    """
    Get YouTube channel information by its handle (e.g., @GoogleDeepMind or GoogleDeepMind).
    Returns channel ID, title, description, subscribers, total views, and video count.
    """
    clean_handle = handle.replace("@", "").strip()
    response = (
        youtube.channels()
        .list(
            part="snippet,statistics,brandingSettings",
            forHandle=clean_handle,
        )
        .execute()
    )

    if not response.get("items"):
        # Fallback to search if handle resolution returns empty
        search_res = search_channel_by_name.invoke(clean_handle)
        if "channel_id" in search_res:
            return get_channel_info_by_id.invoke(search_res["channel_id"])
        return {"error": f"Channel handle @{clean_handle} not found"}

    item = response["items"][0]
    snippet = item["snippet"]
    stats = item["statistics"]

    return {
        "channel_id": item["id"],
        "title": snippet["title"],
        "description": snippet["description"],
        "custom_url": snippet.get("customUrl"),
        "subscribers": stats.get("subscriberCount", "0"),
        "total_views": stats.get("viewCount", "0"),
        "video_count": stats.get("videoCount", "0"),
    }


@tool
def compare_channels(channel_ids: list[str]) -> list:
    """
    Compare multiple YouTube channels by their IDs.
    Returns a list of channel statistics and metadata for each channel ID provided.
    """
    data = []
    for channel_id in channel_ids:
        info = get_channel_info_by_id.invoke(channel_id)
        if "error" not in info:
            data.append(info)
    return data


@tool
def extract_channel_topics(channel_id: str) -> list:
    """
    Extract common topics and keywords from a channel's recent video titles.
    Returns a list of top frequent topic words and their frequencies.
    """
    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 50})

    if not videos:
        return []

    corpus = [v["title"] for v in videos if "title" in v]

    if not corpus:
        return []

    try:
        vectorizer = CountVectorizer(stop_words="english", max_features=20)
        X = vectorizer.fit_transform(corpus)
        freq = X.sum(axis=0)
        words = vectorizer.get_feature_names_out()
        scores = [(words[i], int(freq[0, i])) for i in range(len(words))]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    except Exception:
        return []


@tool
def estimate_channel_growth_and_age(channel_id: str) -> dict:
    """
    Estimate channel age, average views per video, and subscriber efficiency ratio.
    Accepts a channel ID and returns channel age in days/years, average views per upload, and view-to-subscriber ratio.
    """
    info = get_channel_info_by_id.invoke(channel_id)
    if "error" in info:
        return info

    pub_at = info.get("published_at")
    subscribers = int(info.get("subscribers", 0))
    total_views = int(info.get("total_views", 0))
    video_count = int(info.get("video_count", 0))

    avg_views_per_video = round(total_views / max(video_count, 1)) if video_count > 0 else 0
    views_per_sub = round(total_views / max(subscribers, 1), 2) if subscribers > 0 else 0

    channel_age_days = None
    channel_age_years = None

    if pub_at:
        try:
            created_date = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
            now = datetime.now(created_date.tzinfo)
            channel_age_days = (now - created_date).days
            channel_age_years = round(channel_age_days / 365.25, 1)
        except Exception:
            pass

    return {
        "channel_title": info.get("title"),
        "channel_age_years": channel_age_years,
        "channel_age_days": channel_age_days,
        "total_videos": video_count,
        "total_subscribers": subscribers,
        "total_views": total_views,
        "avg_views_per_video": avg_views_per_video,
        "views_per_subscriber_ratio": views_per_sub
    }


@tool
def get_channel_sections(channel_id: str) -> list:
    """
    Get channel layout sections (e.g. Featured Playlists, Popular Uploads, Created Playlists).
    Accepts a channel ID and returns the list of layout section types and titles.
    """
    response = youtube.channelSections().list(
        part="snippet,contentDetails",
        channelId=channel_id
    ).execute()

    return [
        {
            "type": item["snippet"].get("type"),
            "style": item["snippet"].get("style"),
            "title": item["snippet"].get("title", item["snippet"].get("type"))
        }
        for item in response.get("items", [])
    ]
