import logging

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi import Query
from typing import Optional, Literal
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
    start: datetime = Query(None, description="Start datetime in ISO 8601 format"),
    end: datetime = Query(None, description="End datetime in ISO 8601 format"),
    sort_by_polarity_score: Optional[Literal["asc", "desc"]] = Query(
        None, description="Optional sort order for polarity score: 'asc' or 'desc'"
    ),
):
    """
    Retrieve a limited number of recent comments from a specific subfeddit,
    along with their sentiment classification. Supports optional filtering by time
    and optional sorting by polarity score.

    Args:
        subfeddit (str): Name of the subfeddit to query.
        limit (int): Maximum number of comments to retrieve. Must be between 1 and 100.
        start (datetime, optional): Only include comments created at or after this timestamp.
        end (datetime, optional): Only include comments created at or before this timestamp.
        sort_by_polarity_score (Literal["asc", "desc"], optional): If provided, sorts the result
            by polarity score in ascending or descending order.

    Returns:
        list[dict]: A list of comments, each containing:
            - id (str): Unique identifier of the comment.
            - text (str): Content of the comment.
            - polarity (float): Sentiment polarity score.
            - classification (str): Sentiment classification ("positive" or "negative").

    Raises:
        HTTPException:
            404 if the subfeddit does not exist or if no comments are found.
            500 for unexpected internal server errors.
    """
    logger.info(f"Received request for comments from subfeddit: '{subfeddit}'")

    try:
        start_ts = int(start.timestamp()) if start else None
        end_ts = int(end.timestamp()) if end else None

        # Get comments
        comments_data = await get_comments(
            subfeddit=subfeddit,
            limit=limit,
            start=start_ts,
            end=end_ts,
        )
        logger.info(f"Successfully retrieved comments for subfeddit: '{subfeddit}'")

        # Sort by polarity_score
        if sort_by_polarity_score == "asc":
            comments_data.sort(key=lambda c: c["polarity"])
            logger.info(
                f"Successfully ordered comments by polarity_score '{sort_by_polarity_score}'"
            )
        elif sort_by_polarity_score == "desc":
            comments_data.sort(key=lambda c: c["polarity"], reverse=True)
            logger.info(
                f"Successfully ordered comments by polarity_score '{sort_by_polarity_score}'"
            )

        return comments_data
    except ValueError as ve:
        logger.error(ve)
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
