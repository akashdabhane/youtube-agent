from langchain_core.tools import tool
from tools.video_tools import get_video_comments
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

@tool
def get_comment_sentiment(
    video_id: str
):
    """
    Analyze the sentiment of comments on a YouTube video.
    Returns the percentage of positive, negative, and neutral comments.
    Accepts a video ID and analyzes the sentiment of the comments, returning the percentage of positive, negative, and neutral comments based on the compound score from VADER sentiment analysis.
    """

    comments = get_video_comments.invoke(
        {
            "video_id": video_id,
            "max_results": 100
        }
    )

    positive = 0
    negative = 0
    neutral = 0

    for c in comments:

        score = analyzer.polarity_scores(
            c["text"]
        )

        compound = score["compound"]

        if compound >= 0.05:
            positive += 1
        elif compound <= -0.05:
            negative += 1
        else:
            neutral += 1

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral
    }

