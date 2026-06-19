from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.tools import tool

ytt_api = YouTubeTranscriptApi()

@tool
def get_video_transcript(video_id: str) -> str:
    """
    Get transcript/captions from a YouTube video.
    Useful for answering content-based questions.
    Accepts a video ID and returns the transcript text, which can be used for content analysis or question answering. 
    Returns a string containing the transcript text.
    """

    transcript = ytt_api.fetch(video_id)

    text = " ".join(
        chunk.text
        for chunk in transcript
    )

    return text



@tool
def get_video_transcript_with_start_and_duration(video_id: str) -> str:
    """
    Get transcript/captions from a YouTube video with start and duration.
    Useful for answering content-based questions.
    Accepts a video ID and returns the transcript text, which can be used for content analysis or question answering.
    Returns a string containing the transcript text with start and duration.
    """

    transcript = ytt_api.fetch(video_id)

    return transcript


@tool
def get_all_available_transcript_languages(video_id: str) -> list:
    """
    Get all available transcript languages for a YouTube video.
    Accepts a video ID and returns a list of available transcript languages.
    """

    transcript_list = ytt_api.list(video_id)

    return [transcript.language_code for transcript in transcript_list]




# @tool
# def answer_question_from_video(
#     video_id: str,
#     question: str
# ) -> str:
#     """
#     Answer user questions from transcript.
#     """

#     transcript = get_video_transcript.invoke(video_id)

#     return f"""
#     Transcript:

#     {transcript[:15000]}

#     Question:
#     {question}
#     """
