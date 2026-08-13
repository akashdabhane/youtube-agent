from langchain_core.tools import tool
from lib.youtube import youtube


@tool
def get_channel_playlists(channel_id: str) -> list:
    """
    Get all public playlists for a given YouTube channel.
    Returns a list of playlist titles, IDs, and video counts.
    """
    response = youtube.playlists().list(
        part="snippet,contentDetails",
        channelId=channel_id,
        maxResults=50
    ).execute()

    return [
        {
            "title": item["snippet"]["title"],
            "playlist_id": item["id"],
            "item_count": item["contentDetails"]["itemCount"],
            "published_at": item["snippet"]["publishedAt"]
        }
        for item in response.get("items", [])
    ]


@tool
def get_playlist_videos(playlist_id: str, max_results: int = 25) -> list:
    """
    Get videos contained within a specific YouTube playlist.
    Returns video titles, video IDs, positions, and publish dates.
    """
    response = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults=max_results
    ).execute()

    return [
        {
            "video_id": item["contentDetails"]["videoId"],
            "title": item["snippet"]["title"],
            "position": item["snippet"]["position"],
            "published_at": item["snippet"]["publishedAt"]
        }
        for item in response.get("items", [])
    ]
