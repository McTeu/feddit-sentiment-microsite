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

    async def mock_get_comments(subfeddit: str):
        logger.info(f"[MOCK] get_comments called with subfeddit='{subfeddit}'")
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

    async def mock_get_comments(subfeddit: str):
        logger.info(
            f"[MOCK] get_comments raising ValueError for subfeddit='{subfeddit}'"
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

    async def mock_get_comments(subfeddit: str):
        logger.info(
            f"[MOCK] get_comments raising Exception for subfeddit='{subfeddit}'"
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
