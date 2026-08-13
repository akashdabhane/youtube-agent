from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.tools import tool

ytt_api = YouTubeTranscriptApi()

@tool
def get_video_transcript(video_id: str) -> str:
    """
    Get transcript/captions from a YouTube video.
    Useful for answering content-based questions.
    Accepts a video ID and returns the transcript text.
    Returns a string containing the transcript text or an error message if transcript is unavailable.
    """
    try:
        transcript = ytt_api.fetch(video_id)
        text = " ".join(
            chunk.text
            for chunk in transcript
        )
        return text
    except Exception as e:
        print(f"Transcript fetch error for video {video_id}: {e}")
        return "Transcript is unavailable or disabled for this video."


@tool
def get_video_transcript_with_start_and_duration(video_id: str) -> str:
    """
    Get transcript/captions from a YouTube video with start and duration.
    Useful for answering content-based questions.
    Returns the transcript structure or an error message if transcript is unavailable.
    """
    try:
        transcript = ytt_api.fetch(video_id)
        return str(transcript)
    except Exception as e:
        print(f"Transcript fetch error for video {video_id}: {e}")
        return "Transcript is unavailable or disabled for this video."


@tool
def get_all_available_transcript_languages(video_id: str) -> list:
    """
    Get all available transcript languages for a YouTube video.
    Accepts a video ID and returns a list of available transcript languages.
    """
    try:
        transcript_list = ytt_api.list(video_id)
        return [transcript.language_code for transcript in transcript_list]
    except Exception as e:
        print(f"Transcript list error for video {video_id}: {e}")
        return []
