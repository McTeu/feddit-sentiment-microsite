import logging

import pytest

from app.sentiment import analyze_sentiment, classify_sentiment

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "text,expected_classificaiton",
    [
        ("I love this product!", "positive"),
        ("This is terrible and disappointing.", "negative"),
        #     ("It’s okay, I guess.", "positive"),
        #     ("", "neutral"),  # Edge case: empty string
        #     ("     ", "neutral"),  # Edge case: only whitespace
    ],
)
def test_analyze_sentiment_returns_expected_classification(
    text, expected_classificaiton
):
    """
    Test analyze_sentiment returns correct sentiment classification for a variety of inputs.

    Args:
        text (str): The input comment.
        expected_classificaiton (str): Expected classification result.
    """
    result = analyze_sentiment(text)
    logger.debug(f"Input: {text} | Result: {result}")
    assert isinstance(result, dict)
    assert "polarity" in result
    assert "classification" in result
    assert result["classification"] == expected_classificaiton


@pytest.mark.parametrize(
    "compound,expected_label",
    [
        (0.9, "positive"),
        (0.3, "positive"),
        (0.0, "negative"),
        (-0.29, "negative"),
        (-0.5, "negative"),
    ],
)
def test_classify_sentiment_returns_correct_label(compound, expected_label):
    """
    Test classify_sentiment returns expected classification label for compound scores.

    Args:
        compound (float): The VADER compound score.
        expected_label (str): Expected sentiment classification.
    """
    result = classify_sentiment(compound)
    logger.debug(f"Compound: {compound} | Result: {result}")
    assert result == expected_label
