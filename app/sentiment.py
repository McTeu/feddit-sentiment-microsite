import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of a given text using VADER.

    Args:
        text (str): The comment text to analyze.

    Returns:
        dict: A dictionary containing the polarity score and the
              sentiment classification (positive, negative).
    """
    if not text or not text.strip():
        logger.warning("Empty or invalid text received for sentiment analysis.")
        return {"polarity": 0.0, "sentiment": "negative"}

    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    classification = classify_sentiment(compound)

    logger.debug(
        f"Text: '{text}' | Compound: {compound} | Classification: {classification}"
    )

    return {"polarity": compound, "classification": classification}


def classify_sentiment(compound: float) -> str:
    """
    Classify the sentiment based on VADER's compound score.

    Args:
        compound (float): The compound sentiment score.

    Returns:
        str: One of "positive" or "negative"
    """
    if compound > 0:
        return "positive"
    else:
        return "negative"
