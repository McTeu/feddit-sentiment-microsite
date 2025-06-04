import pytest
import logging
from httpx import AsyncClient
from httpx import ASGITransport
from app.main import app

# Configure test logger
logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)


@pytest.mark.asyncio
async def test_comments_endpoint_returns_200(monkeypatch):
    """
    Test successful response from `/comments/{subfeddit}` endpoint.

    This test mocks `get_comments` to return a fake list of comments and ensures
    that the API returns 200 OK and the expected JSON structure.
    """
    logger.info("[TEST] test_comments_endpoint_returns_200: started")

    async def mock_get_comments(subfeddit: str, limit: int, start=None, end=None):
        logger.info(
            f"[MOCK] get_comments called with subfeddit='{subfeddit}', limit={limit}, start={start}, end={end}"
        )
        return [
            {
                "id": 1001,
                "text": "I love this product!",
                "polarity": 0.85,
                "classification": "positive",
            },
            {
                "id": 1002,
                "text": "This is terrible and disappointing.",
                "polarity": -0.8,
                "classification": "negative",
            },
        ]

    monkeypatch.setattr("app.main.get_comments", mock_get_comments)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/comments/testsub")

    logger.info(f"[ASSERT] Status code: {response.status_code}")
    assert response.status_code == 200

    data = response.json()
    logger.info(f"[ASSERT] Response data: {data}")
    assert isinstance(data, list)
    assert data[1]["polarity"] == -0.8
    logger.info("[TEST] test_comments_endpoint_returns_200: passed")


@pytest.mark.asyncio
async def test_comments_endpoint_returns_404(monkeypatch):
    """
    Test that `/comments/{subfeddit}` returns 404 when get_comments raises ValueError.
    """
    logger.info("[TEST] test_comments_endpoint_returns_404: started")

    async def mock_get_comments(subfeddit: str, limit: int, start=None, end=None):
        logger.info(
            f"[MOCK] get_comments called with subfeddit='{subfeddit}', limit={limit}, start={start}, end={end}"
        )
        raise ValueError("Subfeddit not found")

    monkeypatch.setattr("app.main.get_comments", mock_get_comments)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/comments/unknownsub")

    logger.info(f"[ASSERT] Status code: {response.status_code}")
    assert response.status_code == 404
    logger.info(f"[ASSERT] Detail: {response.json()['detail']}")
    assert response.json()["detail"] == "Subfeddit not found"
    logger.info("[TEST] test_comments_endpoint_returns_404: passed")


@pytest.mark.asyncio
async def test_comments_endpoint_returns_500(monkeypatch):
    """
    Test that `/comments/{subfeddit}` returns 500 when get_comments raises unexpected Exception.
    """
    logger.info("[TEST] test_comments_endpoint_returns_500: started")

    async def mock_get_comments(subfeddit: str, limit: int, start=None, end=None):
        logger.info(
            f"[MOCK] get_comments called with subfeddit='{subfeddit}', limit={limit}, start={start}, end={end}"
        )
        raise Exception("Database is down")

    monkeypatch.setattr("app.main.get_comments", mock_get_comments)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/comments/Topic1")

    logger.info(f"[ASSERT] Status code: {response.status_code}")
    assert response.status_code == 500
    logger.info(f"[ASSERT] Detail: {response.json()['detail']}")
    assert response.json()["detail"] == "Database is down"
    logger.info("[TEST] test_comments_endpoint_returns_500: passed")


@pytest.mark.asyncio
async def test_comments_sorted_by_polarity_desc(monkeypatch):
    """
    Test that comments are sorted in descending order of polarity score.

    This test mocks `get_comments` to return a predefined list of comments
    with known polarity values. It then checks that the API response is
    sorted in descending order when the `sort_by_polarity_score=desc` parameter
    is used.

    Args:
        monkeypatch (pytest.MonkeyPatch): Used to mock the `get_comments` function.
    """

    async def mock_get_comments(subfeddit: str, limit: int, start=None, end=None):
        return [
            {"id": 1, "text": "meh", "polarity": 0.1, "classification": "positive"},
            {"id": 2, "text": "bad", "polarity": -0.5, "classification": "negative"},
            {"id": 3, "text": "great", "polarity": 0.9, "classification": "positive"},
        ]

    monkeypatch.setattr("app.main.get_comments", mock_get_comments)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/comments/testsub?sort_by_polarity_score=desc")

    assert response.status_code == 200
    result = response.json()
    polarities = [c["polarity"] for c in result]
    assert polarities == sorted(polarities, reverse=True)


@pytest.mark.asyncio
async def test_limit_validation():
    """
    Test that the `limit` query parameter is validated.

    Sends a request with an invalid limit value (`limit=0`) and expects
    a 422 Unprocessable Entity response from FastAPI due to the limit
    being out of the accepted range (minimum 1).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/comments/testsub?limit=0")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_start_param():
    """
    Test that an invalid `start` datetime string returns a 422 error.

    Sends a request with a malformed `start` parameter (`start=not-a-date`)
    and checks that FastAPI returns a 422 Unprocessable Entity response
    due to failed type validation.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/comments/testsub?start=not-a-date")
        assert response.status_code == 422
