import logging

from fastapi import FastAPI, HTTPException
from fastapi import Query

from app.feddit_client import get_comments
from app.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/comments/{subfeddit}")
async def comments(
    subfeddit: str,
    limit: int = Query(
        25,
        ge=1,
        le=100,
        description="Number of comments to retrieve (default: 25, max: 100)",
    ),
):
    """
    Retrieve a limited number of recent comments from a specific subfeddit,
    along with their sentiment classification.

    Args:
        subfeddit (str): Name of the subfeddit to query.
        limit (int): Maximum number of comments to retrieve (default: 25, max: 100).

    Returns:
        List[dict]: A list of comments, each including:
            - id (str): Unique identifier of the comment
            - text (str): Content of the comment
            - polarity (float): Sentiment polarity score
            - sentiment (str): Sentiment classification ("positive" or "negative")

    Raises:
        HTTPException:
            404: If the subfeddit does not exist or returns no comments.
            500: For any unexpected server error.
    """
    logger.info(f"Received request for comments from subfeddit: '{subfeddit}'")

    try:
        comments_data = await get_comments(subfeddit=subfeddit, limit=limit)
        logger.info(f"Successfully retrieved comments for subfeddit: '{subfeddit}'")
        return comments_data
    except ValueError as ve:
        logger.error(ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
