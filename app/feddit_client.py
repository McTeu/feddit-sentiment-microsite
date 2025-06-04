import logging
from app.sentiment import analyze_sentiment

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8080/api/v1"


async def get_subfeddit_id_by_name(name: str) -> str:
    """
    Retrieve the unique ID of a subfeddit given its title.

    Args:
        name (str): The title of the subfeddit.

    Returns:
        str: The unique identifier of the subfeddit.

    Raises:
        ValueError: If no subfeddit with the given name is found.
        httpx.HTTPStatusError: If the request to Feddit fails.
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


async def get_comments(subfeddit: str, limit: int = 25) -> list[dict]:
    """
    Fetch the most recent comments for a given subfeddit by name.

    Args:
        subfeddit (str): The name (title) of the subfeddit.
        limit (int): Maximum number of comments to retrieve. Default is 25.

    Returns:
        list[dict]: A list of comment dictionaries retrieved from the Feddit API.

    Raises:
        ValueError: If the subfeddit name is invalid.
        httpx.HTTPStatusError: If the request to Feddit fails.
    """
    logger.info(f"Fetching comments for subfeddit '{subfeddit}' (limit={limit})")
    subfeddit_id = await get_subfeddit_id_by_name(subfeddit)

    url = f"{BASE_URL}/comments/"
    params = {"subfeddit_id": subfeddit_id, "skip": 0, "limit": limit}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.exception(
            f"Failed to fetch comments for subfeddit ID {subfeddit_id}: {e}"
        )
        raise

    comments = response.json()["comments"]
    comments = extract_text_and_id(comments)

    for c in comments:
        sentiment = analyze_sentiment(c["text"])
        c["polarity"] = sentiment["polarity"]
        c["classification"] = sentiment["classification"]

    logger.info(f"Retrieved {len(comments)} comments from subfeddit '{subfeddit}'")
    return comments


def extract_text_and_id(comments: list[dict]) -> list[dict]:
    """
    Extract only the ID and text from a list of comment dictionaries.

    Args:
        comments (list[dict]): The full list of comments returned by Feddit.

    Returns:
        list[dict]: A simplified list with only 'id' and 'text' fields.
    """
    return [{"id": c["id"], "text": c["text"]} for c in comments]
