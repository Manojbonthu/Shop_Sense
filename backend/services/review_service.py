"""
Sentiment analysis using TextBlob NLP library.
"""
import re
from textblob import TextBlob
from backend.models.schemas import ReviewAnalyzeRequest, ReviewAnalyzeResponse

POSITIVE_LEXICON = {
    "amazing", "excellent", "great", "good", "fantastic", "wonderful", "superb",
    "outstanding", "perfect", "love", "awesome", "brilliant", "best", "quality",
    "comfortable", "fast", "smooth", "clear", "sharp", "durable", "reliable",
    "recommend", "satisfied", "happy", "impressed", "nice", "beautiful", "premium",
    "value", "easy", "efficient", "powerful", "solid", "sturdy", "long"
}

NEGATIVE_LEXICON = {
    "bad", "poor", "terrible", "awful", "worst", "hate", "horrible", "disappointing",
    "broken", "defective", "slow", "heavy", "cheap", "noisy", "loud", "uncomfortable",
    "difficult", "hard", "expensive", "overpriced", "average", "mediocre", "weak",
    "short", "fragile", "flimsy", "unreliable", "problem", "issue", "fail", "failure"
}


def analyze_review(request: ReviewAnalyzeRequest) -> ReviewAnalyzeResponse:
    text = request.review
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1.0 to +1.0

    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    positive_words = sorted(set(w for w in words if w in POSITIVE_LEXICON))
    negative_words = sorted(set(w for w in words if w in NEGATIVE_LEXICON))

    summary = (
        f"The review is {sentiment.lower()} with a sentiment score of {polarity:.2f}."
    )

    return ReviewAnalyzeResponse(
        sentiment=sentiment,
        sentiment_score=round(polarity, 4),
        positive_words=positive_words,
        negative_words=negative_words,
        summary=summary
    )
