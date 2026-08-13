from dotenv import load_dotenv
from googleapiclient.discovery import build
import os
import httplib2
from youtube_transcript_api import YouTubeTranscriptApi


load_dotenv()


# Disable SSL verification — only for local dev/testing, never in production
http = httplib2.Http(disable_ssl_certificate_validation=True)

# Initialize YouTube Data API client
youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"), http=http)


# Initialize YouTubeTranscriptApi 
ytt_api = YouTubeTranscriptApi()
