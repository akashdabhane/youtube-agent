from tools.video_tools import get_recent_videos
from langchain_core.tools import tool
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import ssl
import httplib2
from sklearn.feature_extraction.text import CountVectorizer


load_dotenv()

# Disable SSL verification — only for local dev/testing, never in production
http = httplib2.Http(disable_ssl_certificate_validation=True)


youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"), http=http)


@tool
def get_channel_info_by_id(channel_id: str) -> dict:
    """
    Get YouTube channel statistics and info given a channel ID.
    Returns subscriber count, view count, video count, title, description.
    """
    response = (
        youtube.channels().list(part="snippet,statistics", id=channel_id).execute()
    )

    item = response["items"][0]
    return {
        "channel_id": item["id"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "subscribers": item["statistics"].get("subscriberCount"),
        "total_views": item["statistics"].get("viewCount"),
        "video_count": item["statistics"].get("videoCount"),
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

    item = response["items"][0]
    return {
        "channel_id": item["snippet"]["channelId"],
        "title": item["snippet"]["title"],
    }


@tool
def get_channel_by_handle(handle: str) -> dict:  # ← added : str -> dict
    """
    Get YouTube channel information by its handle (e.g., @GoogleDeepMind).
    Returns channel ID, title, description, and statistics.
    """
    response = (
        youtube.channels()
        .list(
            part="snippet,statistics,brandingSettings",
            forHandle=handle.replace("@", ""),
        )
        .execute()
    )

    if not response["items"]:
        return {}  # ← return {} instead of None

    item = response["items"][0]
    return {
        "channel_id": item["id"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "subscribers": item["statistics"].get("subscriberCount"),
        "total_views": item["statistics"].get("viewCount"),
    }


@tool
def compare_channels(channel_ids: list[str]):
    """
    Compare multiple YouTube channels by their IDs.
    Returns a list of channel info dictionaries for each channel ID provided.
    """

    data = []

    for channel_id in channel_ids:

        info = get_channel_info_by_id.invoke(channel_id)

        data.append(info)

    return data



@tool
def extract_channel_topics(channel_id: str):
    """
    Extract common topics from a channel's recent video titles.
    Returns a list of the most frequent words in the video titles.
    """

    videos = get_recent_videos.invoke({"channel_id": channel_id, "max_results": 50})

    corpus = [v["title"] for v in videos]

    vectorizer = CountVectorizer(stop_words="english")

    X = vectorizer.fit_transform(corpus)

    freq = X.sum(axis=0)

    words = vectorizer.get_feature_names_out()

    scores = [(words[i], freq[0, i]) for i in range(len(words))]

    scores.sort(key=lambda x: x[1], reverse=True)

    return scores[:20]
