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
    Get the most recent comments from a given subfeddit with sentiment classification.

    Args:
        subfeddit (str): The name (title) of the subfeddit to query.

    Returns:
        list[dict]: A list of comments including their id, text, polarity score,
        and classification.

    Raises:
        HTTPException:
            - 404 if the subfeddit is not found.
            - 500 for general internal errors.
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
