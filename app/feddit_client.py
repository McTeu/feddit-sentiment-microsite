import logging
from app.sentiment import analyze_sentiment
from typing import Optional
from app.config import BASE_URL, PAGE_SIZE

import httpx

logger = logging.getLogger(__name__)


async def get_subfeddit_id_by_name(name: str) -> str:
    """
    Retrieve the unique ID of a subfeddit given its title.

    Args:
        name (str): The title of the subfeddit.

    Returns:
        str: The unique identifier of the subfeddit.

    Raises:
        ValueError: If no subfeddit with the given name is found.
        httpx.HTTPError: If the request to Feddit fails.
    """
    url = f"{BASE_URL}/subfeddits/"
    logger.info(f"Fetching ID for subfeddit '{name}'")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.exception(f"Failed to fetch subfeddits from Feddit: {e}")
        raise

    subfeddits = response.json()["subfeddits"]
    logger.debug(f"Available subfeddits: {[s['title'] for s in subfeddits]}")

    for sub in subfeddits:
        if sub["title"].lower() == name.lower():
            return sub["id"]

    logger.warning(f"No matching subfeddit found for name: '{name}'")
    raise ValueError(f"Subfeddit '{name}' not found")


async def get_comments(
    subfeddit: str,
    limit: int = 25,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> list[dict]:
    """
    Fetch comments from a subfeddit, filtered by time and enriched with sentiment.

    Args:
        subfeddit (str): The name of the subfeddit.
        limit (int): Maximum number of comments to retrieve.
        start (Optional[int]): Start timestamp (inclusive).
        end (Optional[int]): End timestamp (inclusive).

    Returns:
        list[dict]: List of comments with sentiment analysis.

    Raises:
        ValueError: If no comments are found matching the criteria.
        httpx.HTTPError: If the request to Feddit fails.
    """
    collected_comments = []
    skip = 0

    logger.info(
        f"Fetching comments for subfeddit '{subfeddit}' (limit={limit}, start={start}, end={end})"
    )
    subfeddit_id = await get_subfeddit_id_by_name(subfeddit)

    url = f"{BASE_URL}/comments/"

    async with httpx.AsyncClient() as client:
        while len(collected_comments) < limit:
            params = {
                "subfeddit_id": subfeddit_id,
                "skip": skip,
                "limit": PAGE_SIZE,
            }
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
            except httpx.HTTPError as e:
                logger.exception(f"Failed to fetch comments: {e}")
                break

            comments = response.json().get("comments", [])
            if not comments:
                logger.info("No more comments returned from API.")
                break

            for comment in comments:
                if is_within_time_range(comment, start, end):
                    enriched = enrich_with_sentiment(comment)
                    collected_comments.append(enriched)

                if len(collected_comments) >= limit:
                    break

            skip += PAGE_SIZE

    if not collected_comments:
        raise ValueError("No comments found matching the given criteria")

    for c in collected_comments:
        sentiment = analyze_sentiment(c["text"])
        c["polarity"] = sentiment["polarity"]
        c["classification"] = sentiment["classification"]

    logger.info(
        f"Retrieved {len(collected_comments)} comments from subfeddit '{subfeddit}'"
    )
    return collected_comments


def is_within_time_range(
    comment: dict, start: Optional[int], end: Optional[int]
) -> bool:
    """
    Check if a comment falls within the given time range.

    Args:
        comment (dict): The comment to evaluate.
        start (Optional[int]): Start timestamp.
        end (Optional[int]): End timestamp.

    Returns:
        bool: True if the comment is within range, else False.
    """
    created_at = comment.get("created_at")
    if start and created_at < start:
        return False
    if end and created_at > end:
        return False
    return True


def enrich_with_sentiment(comment: dict) -> dict:
    """
    Add sentiment analysis to a comment.

    Args:
        comment (dict): A dictionary with at least 'id' and 'text'.

    Returns:
        dict: The original comment enriched with 'polarity' and 'classification'.
    """
    sentiment = analyze_sentiment(comment["text"])
    return {
        "id": comment["id"],
        "text": comment["text"],
        "polarity": sentiment["polarity"],
        "classification": sentiment["classification"],
    }
