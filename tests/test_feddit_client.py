import pytest
from httpx import Response, Request
from app.feddit_client import (
    get_subfeddit_id_by_name,
    get_comments,
    extract_text_and_id,
)
import logging
from json import dumps

# Configure logger for tests
logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)


@pytest.mark.asyncio
async def test_get_subfeddit_id_by_name_found(monkeypatch):
    """
    Test retrieving a subfeddit ID by name when the subfeddit exists.

    This test mocks the HTTP response from the Feddit API and checks that
    the function returns the correct subfeddit ID for a known subfeddit title.

    Args:
        monkeypatch: pytest fixture to replace the httpx client with a mock.

    Raises:
        AssertionError: if the returned ID is not the expected one.
    """
    logger.info("[TEST] test_get_subfeddit_id_by_name_found: started")

    mock_subfeddits = {
        "subfeddits": [
            {
                "id": 1,
                "username": "admin_1",
                "title": "Dummy Topic 1",
                "description": "Dummy Topic 1",
            },
            {
                "id": 2,
                "username": "admin_2",
                "title": "Dummy Topic 2",
                "description": "Dummy Topic 2",
            },
            {
                "id": 55,
                "username": "admin_5",
                "title": "Dummy Topic 5",
                "description": "Dummy Topic 5",
            },
        ]
    }

    async def mock_get(*args, **kwargs):
        logger.info("[MOCK] Returning mocked subfeddit list")
        return Response(
            status_code=200,
            content=dumps(mock_subfeddits).encode("utf-8"),
            request=Request("GET", "http://test"),
        )

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return await mock_get()

    monkeypatch.setattr("app.feddit_client.httpx.AsyncClient", lambda: MockClient())

    subfeddit_id = await get_subfeddit_id_by_name("Dummy Topic 5")
    logger.info(f"[ASSERT] Retrieved ID: {subfeddit_id}")
    assert subfeddit_id == 55
    logger.info("[TEST] test_get_subfeddit_id_by_name_found: passed")


@pytest.mark.asyncio
async def test_get_comments(monkeypatch):
    """
    Test retrieving comments from a subfeddit.

    This test mocks both the subfeddit ID resolution and the comments API response,
    and verifies that the correct comment data is returned.

    Args:
        monkeypatch: pytest fixture to mock internal function and HTTP call.

    Raises:
        AssertionError: if the returned comment data does not match the expected format.
    """
    logger.info("[TEST] test_get_comments: started")

    async def mock_get_subfeddit_id_by_name(name):
        logger.info("[MOCK] Returning fake subfeddit ID")
        return "123"

    monkeypatch.setattr(
        "app.feddit_client.get_subfeddit_id_by_name", mock_get_subfeddit_id_by_name
    )

    mock_comments = {
        "subfeddit_id": 2,
        "limit": 25,
        "skip": 0,
        "comments": [
            {
                "id": 1001,
                "username": "mock_user_1",
                "text": "Well done! Great effort.",
                "created_at": 1627655936,
            },
            {
                "id": 1002,
                "username": "mock_user_2",
                "text": "Could have been better...",
                "created_at": 1627659536,
            },
        ],
    }

    async def mock_get(*args, **kwargs):
        logger.info("[MOCK] Returning mocked comments list")
        return Response(
            status_code=200,
            content=dumps(mock_comments).encode("utf-8"),
            request=Request("GET", "http://test"),
        )

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, *args, **kwargs):
            return await mock_get()

    monkeypatch.setattr("app.feddit_client.httpx.AsyncClient", lambda: MockClient())

    comments = await get_comments("cats")
    logger.info(comments)
    logger.info(f"[ASSERT] Retrieved {len(comments)} comments")
    assert isinstance(comments, list)
    assert comments[0]["id"] == 1001
    logger.info("[TEST] test_get_comments: passed")


def test_extract_text_and_id():
    sample_input = [
        {"id": "123", "text": "Great!", "created_at": 111, "username": "bob"},
        {"id": "456", "text": "Awful!", "created_at": 112, "username": "alice"},
    ]
    expected = [{"id": "123", "text": "Great!"}, {"id": "456", "text": "Awful!"}]
    assert extract_text_and_id(sample_input) == expected
