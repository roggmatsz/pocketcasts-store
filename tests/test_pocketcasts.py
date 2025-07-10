"""
Tests for src/pocketcasts.py, focusing on network error handling and logging.
"""
import pytest
import json
from unittest.mock import Mock, patch, ANY

import urllib3.exceptions

# Functions to test from src.pocketcasts
from src.pocketcasts import (
    get_history,
    search_podcasts,
    get_subscriptions,
    add_subscription,
    get_episodes,
    update_podcast_episode,
    logger as pocketcasts_logger  # Import the logger instance
)

# To prevent real HTTP requests during tests
MOCK_TOKEN = "mock_token"
MOCK_HTTP = Mock(spec=urllib3.PoolManager)

@pytest.fixture(autouse=True)
def reset_mocks_fixture():
    """Reset mocks before each test."""
    MOCK_HTTP.reset_mock()
    # Explicitly clear side_effect and return_value that might persist
    MOCK_HTTP.request.side_effect = None
    MOCK_HTTP.request.return_value = None

@pytest.fixture
def caplog_debug(caplog):
    """Fixture to set log level to DEBUG for pocketcasts_logger for the duration of a test."""
    original_level = pocketcasts_logger.level
    pocketcasts_logger.setLevel("DEBUG")
    caplog.set_level("DEBUG", logger="pocketcasts_logger")
    yield caplog
    pocketcasts_logger.setLevel(original_level)

# Helper to check for log messages
def assert_log_message(caplog, level, message_part):
    """Asserts that a log message containing message_part at the given level exists."""
    for record in caplog.records:
        if record.levelname == level and message_part in record.message:
            return
    pytest.fail(f"Log message part '{message_part}' at level {level} not found in logs: {caplog.text}")

class MockResponse:
    def __init__(self, data, status=200):
        if isinstance(data, dict) or isinstance(data, list):
            self.data = json.dumps(data).encode('utf-8')
        elif isinstance(data, str): # Forcing malformed JSON test data
            self.data = data.encode('utf-8')
        else: # For anything else, like bytes
            self.data = data
        self.status = status

    def json(self): # Only used by the calling code if it expects valid JSON
        return json.loads(self.data.decode('utf-8'))

# --- Tests for get_history ---

def test_get_history_max_retry_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.MaxRetryError(MOCK_HTTP, "url", reason="test reason")
    result = get_history(MOCK_HTTP, MOCK_TOKEN)
    assert result == {'episodes': []}
    assert_log_message(caplog_debug, "ERROR", "Network error fetching history")
    MOCK_HTTP.request.assert_called_once()

def test_get_history_new_connection_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.NewConnectionError(MOCK_HTTP, "Failed to establish a new connection")
    result = get_history(MOCK_HTTP, MOCK_TOKEN)
    assert result == {'episodes': []}
    assert_log_message(caplog_debug, "ERROR", "Network error fetching history")
    MOCK_HTTP.request.assert_called_once()

def test_get_history_json_decode_error(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data="not valid json", status=200)
    result = get_history(MOCK_HTTP, MOCK_TOKEN)
    assert result == {'episodes': []}
    assert_log_message(caplog_debug, "ERROR", "Failed to decode JSON response from history API: b'not valid json'")
    MOCK_HTTP.request.assert_called_once()

def test_get_history_generic_exception(caplog_debug):
    MOCK_HTTP.request.side_effect = Exception("Something unexpected went wrong")
    result = get_history(MOCK_HTTP, MOCK_TOKEN)
    assert result == {'episodes': []}
    assert_log_message(caplog_debug, "ERROR", "An unexpected error occurred fetching history: Something unexpected went wrong")
    MOCK_HTTP.request.assert_called_once()

def test_get_history_success(caplog_debug):
    expected_data = {"episodes": [{"uuid": "123", "title": "Test Episode"}]}
    MOCK_HTTP.request.return_value = MockResponse(data=expected_data, status=200)
    result = get_history(MOCK_HTTP, MOCK_TOKEN)
    assert result == expected_data
    MOCK_HTTP.request.assert_called_once_with("POST", "https://api.pocketcasts.com/user/history", headers=ANY)
    assert not any(record.levelno >= pocketcasts_logger.getEffectiveLevel() for record in caplog_debug.records if "error" in record.message.lower()), "Error logs present on success"


# --- Tests for search_podcasts ---

def test_search_podcasts_max_retry_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.MaxRetryError(MOCK_HTTP, "url", reason="test reason")
    result = search_podcasts(MOCK_HTTP, MOCK_TOKEN, "test term")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error searching podcasts")
    MOCK_HTTP.request.assert_called_once()

def test_search_podcasts_new_connection_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.NewConnectionError(MOCK_HTTP, "Failed to establish a new connection")
    result = search_podcasts(MOCK_HTTP, MOCK_TOKEN, "test term")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error searching podcasts")
    MOCK_HTTP.request.assert_called_once()

def test_search_podcasts_json_decode_error(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data="not json at all", status=200)
    result = search_podcasts(MOCK_HTTP, MOCK_TOKEN, "test term")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Failed to decode JSON response from podcast search API: b'not json at all'")
    MOCK_HTTP.request.assert_called_once()

def test_search_podcasts_generic_exception(caplog_debug):
    MOCK_HTTP.request.side_effect = Exception("A generic search error")
    result = search_podcasts(MOCK_HTTP, MOCK_TOKEN, "test term")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "An unexpected error occurred searching podcasts: A generic search error")
    MOCK_HTTP.request.assert_called_once()

def test_search_podcasts_success(caplog_debug):
    expected_data = {"podcasts": [{"uuid": "p123", "title": "Test Podcast"}]}
    MOCK_HTTP.request.return_value = MockResponse(data=expected_data, status=200)
    result = search_podcasts(MOCK_HTTP, MOCK_TOKEN, "test term")
    assert result == expected_data
    MOCK_HTTP.request.assert_called_once_with(
        "POST",
        "https://api.pocketcasts.com/discover/search",
        headers=ANY,
        body=json.dumps({"term": "test term"}, ensure_ascii=False).encode("ascii", errors="ignore")
    )
    assert not any(record.levelno >= pocketcasts_logger.getEffectiveLevel() for record in caplog_debug.records if "error" in record.message.lower()), "Error logs present on success"

# --- Tests for get_subscriptions ---

def test_get_subscriptions_max_retry_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.MaxRetryError(MOCK_HTTP, "url", reason="test reason")
    result = get_subscriptions(MOCK_HTTP, MOCK_TOKEN)
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error fetching subscriptions")
    MOCK_HTTP.request.assert_called_once()

def test_get_subscriptions_new_connection_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.NewConnectionError(MOCK_HTTP, "Failed to establish a new connection")
    result = get_subscriptions(MOCK_HTTP, MOCK_TOKEN)
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error fetching subscriptions")
    MOCK_HTTP.request.assert_called_once()

def test_get_subscriptions_json_decode_error(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data="bad json data", status=200)
    result = get_subscriptions(MOCK_HTTP, MOCK_TOKEN)
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Failed to decode JSON response from subscriptions API: b'bad json data'")
    MOCK_HTTP.request.assert_called_once()

def test_get_subscriptions_generic_exception(caplog_debug):
    MOCK_HTTP.request.side_effect = Exception("Subscriptions fetch failed")
    result = get_subscriptions(MOCK_HTTP, MOCK_TOKEN)
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "An unexpected error occurred fetching subscriptions: Subscriptions fetch failed")
    MOCK_HTTP.request.assert_called_once()

def test_get_subscriptions_success(caplog_debug):
    expected_data = {"podcasts": [{"uuid": "sub123", "title": "Subscribed Podcast"}]}
    MOCK_HTTP.request.return_value = MockResponse(data=expected_data, status=200)
    result = get_subscriptions(MOCK_HTTP, MOCK_TOKEN)
    assert result == expected_data
    MOCK_HTTP.request.assert_called_once_with(
        "POST",
        "https://api.pocketcasts.com/user/podcast/list",
        headers=ANY,
        body=json.dumps({"v": 1}).encode("utf-8")
    )
    assert not any(record.levelno >= pocketcasts_logger.getEffectiveLevel() for record in caplog_debug.records if "error" in record.message.lower()), "Error logs present on success"

# --- Tests for add_subscription ---

def test_add_subscription_max_retry_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.MaxRetryError(MOCK_HTTP, "url", reason="test reason")
    result = add_subscription(MOCK_HTTP, MOCK_TOKEN, "uuid_to_add")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error adding subscription")
    MOCK_HTTP.request.assert_called_once()

def test_add_subscription_new_connection_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.NewConnectionError(MOCK_HTTP, "Failed to establish a new connection")
    result = add_subscription(MOCK_HTTP, MOCK_TOKEN, "uuid_to_add")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error adding subscription")
    MOCK_HTTP.request.assert_called_once()

def test_add_subscription_json_decode_error(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data="invalid json content", status=200)
    result = add_subscription(MOCK_HTTP, MOCK_TOKEN, "uuid_to_add")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Failed to decode JSON response from add subscription API: b'invalid json content'")
    MOCK_HTTP.request.assert_called_once()

def test_add_subscription_generic_exception(caplog_debug):
    MOCK_HTTP.request.side_effect = Exception("Could not add subscription")
    result = add_subscription(MOCK_HTTP, MOCK_TOKEN, "uuid_to_add")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "An unexpected error occurred adding subscription: Could not add subscription")
    MOCK_HTTP.request.assert_called_once()

def test_add_subscription_success(caplog_debug):
    expected_data = {"status": "ok"}
    MOCK_HTTP.request.return_value = MockResponse(data=expected_data, status=200)
    result = add_subscription(MOCK_HTTP, MOCK_TOKEN, "uuid_to_add")
    assert result == expected_data
    MOCK_HTTP.request.assert_called_once_with(
        "POST",
        "https://api.pocketcasts.com/user/podcast/subscribe",
        headers=ANY,
        body=json.dumps({"uuid": "uuid_to_add"}).encode("utf-8")
    )
    assert not any(record.levelno >= pocketcasts_logger.getEffectiveLevel() for record in caplog_debug.records if "error" in record.message.lower()), "Error logs present on success"

# --- Tests for get_episodes ---

def test_get_episodes_max_retry_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.MaxRetryError(MOCK_HTTP, "url", reason="test reason")
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error fetching episodes")
    MOCK_HTTP.request.assert_called_once()

def test_get_episodes_new_connection_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.NewConnectionError(MOCK_HTTP, "Failed to establish a new connection")
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error fetching episodes")
    MOCK_HTTP.request.assert_called_once()

def test_get_episodes_json_decode_error(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data="json is broken", status=200)
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Failed to decode JSON response from get_episodes API: b'json is broken'")
    MOCK_HTTP.request.assert_called_once()

def test_get_episodes_generic_exception(caplog_debug):
    MOCK_HTTP.request.side_effect = Exception("Episode retrieval error")
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "An unexpected error occurred fetching episodes: Episode retrieval error")
    MOCK_HTTP.request.assert_called_once()

def test_get_episodes_missing_podcast_key(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data={"episodes": []}, status=200)
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Unexpected response structure from get_episodes API")
    MOCK_HTTP.request.assert_called_once()

def test_get_episodes_missing_episodes_key(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data={"podcast": {"title": "Test"}}, status=200)
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Unexpected response structure from get_episodes API")
    MOCK_HTTP.request.assert_called_once()

def test_get_episodes_success(caplog_debug):
    api_response_data = {
        "podcast": {
            "episodes": [
                {"title": "Episode 1", "uuid": "ep1_uuid"},
                {"title": "Episode 2", "uuid": "ep2_uuid"}
            ]
        }
    }
    expected_episodes = {
        "Episode 1": "ep1_uuid",
        "Episode 2": "ep2_uuid"
    }
    MOCK_HTTP.request.return_value = MockResponse(data=api_response_data, status=200)
    result = get_episodes(MOCK_HTTP, MOCK_TOKEN, "podcast_uuid")
    assert result == expected_episodes
    MOCK_HTTP.request.assert_called_once_with(
        "GET",
        f"https://podcast-api.pocketcasts.com/podcast/full/podcast_uuid",
        headers=ANY
    )
    assert not any(record.levelno >= pocketcasts_logger.getEffectiveLevel() for record in caplog_debug.records if "error" in record.message.lower()), "Error logs present on success"


# --- Tests for update_podcast_episode ---

def test_update_podcast_episode_max_retry_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.MaxRetryError(MOCK_HTTP, "url", reason="test reason")
    result = update_podcast_episode(MOCK_HTTP, MOCK_TOKEN, {"uuid": "ep_uuid", "playingStatus": 1})
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error updating podcast episode")
    MOCK_HTTP.request.assert_called_once()

def test_update_podcast_episode_new_connection_error(caplog_debug):
    MOCK_HTTP.request.side_effect = urllib3.exceptions.NewConnectionError(MOCK_HTTP, "Failed to establish a new connection")
    result = update_podcast_episode(MOCK_HTTP, MOCK_TOKEN, {"uuid": "ep_uuid", "playingStatus": 1})
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Network error updating podcast episode")
    MOCK_HTTP.request.assert_called_once()

def test_update_podcast_episode_json_decode_error(caplog_debug):
    MOCK_HTTP.request.return_value = MockResponse(data="this is not json data", status=200)
    result = update_podcast_episode(MOCK_HTTP, MOCK_TOKEN, {"uuid": "ep_uuid", "playingStatus": 1})
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "Failed to decode JSON response from update_episode API: b'this is not json data'")
    MOCK_HTTP.request.assert_called_once()

def test_update_podcast_episode_generic_exception(caplog_debug):
    MOCK_HTTP.request.side_effect = Exception("Update failed unexpectedly")
    result = update_podcast_episode(MOCK_HTTP, MOCK_TOKEN, {"uuid": "ep_uuid", "playingStatus": 1})
    assert result == {}
    assert_log_message(caplog_debug, "ERROR", "An unexpected error occurred updating podcast episode: Update failed unexpectedly")
    MOCK_HTTP.request.assert_called_once()

def test_update_podcast_episode_success(caplog_debug):
    expected_data = {"status": "ok"}
    body_payload = {"uuid": "ep_uuid", "playingStatus": 1, "playedUpTo": 120}
    MOCK_HTTP.request.return_value = MockResponse(data=expected_data, status=200)

    result = update_podcast_episode(MOCK_HTTP, MOCK_TOKEN, body_payload)

    assert result == expected_data
    assert_log_message(caplog_debug, "INFO", f"Updating episode: {body_payload}")
    MOCK_HTTP.request.assert_called_once_with(
        "POST",
        "https://api.pocketcasts.com/sync/update_episode",
        headers=ANY,
        body=body_payload # In current src, body is passed as dict
    )
    # Check that no ERROR logs were made for this specific call
    # This is a bit tricky if other tests run in parallel and log errors,
    # but caplog should be specific to this test.
    # We can check that the *last relevant log* was INFO or that no errors for *this operation* occurred.
    # The assert_log_message for INFO already confirms the info log.
    # To ensure no error for *this* operation, we can check the caplog.text or records more carefully.
    # For simplicity, if the INFO log is there and no exception was raised by the function,
    # and the result is correct, it implies correct execution for this test.
    # Adding a check to ensure no error messages were logged by this specific test:
    current_test_errors = [
        r for r in caplog_debug.records
        if r.levelname == "ERROR" and "update_episode" in r.message # crude check
    ]
    assert not current_test_errors, f"Error logs found during successful update: {current_test_errors}"
