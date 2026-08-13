from langchain_core.tools import tool
from tools.video_tools import get_video_comments
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer

analyzer = SentimentIntensityAnalyzer()

@tool
def get_comment_sentiment(video_id: str) -> dict:
    """
    Analyze the sentiment of comments on a YouTube video.
    Returns the percentage of positive, negative, and neutral comments based on VADER sentiment score.
    """
    comments = get_video_comments.invoke(
        {
            "video_id": video_id,
            "max_results": 100
        }
    )

    if not comments:
        return {"error": "No comments found or comments disabled for this video."}

    positive = 0
    negative = 0
    neutral = 0
    total = len(comments)

    for c in comments:
        score = analyzer.polarity_scores(c.get("text", ""))
        compound = score["compound"]

        if compound >= 0.05:
            positive += 1
        elif compound <= -0.05:
            negative += 1
        else:
            neutral += 1

    return {
        "comments_analyzed": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positive_percent": round((positive / total) * 100, 1),
        "negative_percent": round((negative / total) * 100, 1),
        "neutral_percent": round((neutral / total) * 100, 1)
    }


@tool
def extract_comment_topics(video_id: str) -> list:
    """
    Extract top discussion keywords and topics from a YouTube video's comments section.
    Accepts a video ID and returns the top 15 most common words discussed by viewers.
    """
    comments = get_video_comments.invoke(
        {
            "video_id": video_id,
            "max_results": 100
        }
    )

    if not comments:
        return []

    corpus = [c.get("text", "") for c in comments if c.get("text")]

    if not corpus:
        return []

    try:
        vectorizer = CountVectorizer(stop_words="english", max_features=15)
        X = vectorizer.fit_transform(corpus)
        freq = X.sum(axis=0)
        words = vectorizer.get_feature_names_out()
        scores = [(words[i], int(freq[0, i])) for i in range(len(words))]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    except Exception:
        return []
