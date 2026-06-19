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
def get_channel_playlists(channel_id: str) -> list:
    """
    Get all playlists for a given YouTube channel.
    Returns a list of playlist titles and IDs.
    """

    response = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50
    ).execute()

    return [
        {
            "title": item["snippet"]["title"],
            "playlist_id": item["id"]
        }
        for item in response["items"]
    ]

