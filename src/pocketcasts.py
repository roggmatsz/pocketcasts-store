import json
import urllib3 # Added for exception handling
from .auth import create_auth_headers
from .logger import setup_logger

logger = setup_logger('pocketcasts_logger', 'pocketcasts_errors.log')

def get_history(http, token):
    header = create_auth_headers(token)
    try:
        response = http.request(
            "POST",
            "https://api.pocketcasts.com/user/history",
            headers=header,
        )
        data = json.loads(response.data)
        return data
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error fetching history: {e}")
        return {'episodes': []}  # Return default to prevent KeyError in main.py
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from history API: {response.data}")
        return {'episodes': []}
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching history: {e}")
        return {'episodes': []}

def search_podcasts(http, token, term):
    header = create_auth_headers(token)
    body = json.dumps({"term":term}, ensure_ascii=False).encode("ascii", errors="ignore")
    header["content-length"] = len(body)
    logger.debug(f"Search podcasts header: {header}") # Replaced print with logger
    logger.debug(f"Search podcasts body: {body}") # Replaced print with logger
    try:
        response = http.request(
            "POST",
            "https://api.pocketcasts.com/discover/search",
            headers=header,
            body=body,
        )
        return json.loads(response.data)
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error searching podcasts: {e}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from podcast search API: {response.data}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred searching podcasts: {e}")
        return {}


def search_podcasts_and_get_first_uuid(http, token, term):
    search_result = search_podcasts(http, token, term)
    try:
        search_result["podcasts"][0]
    except(IndexError, KeyError):
        return None
    # Get the first result
    # It would be very rare to have two podcasts with the same name
    # FIXME: Also check author here. Not sure if authors are consistent
    # across platforms.
    return search_result["podcasts"][0]["uuid"]


def get_subscriptions(http, token):
    header = create_auth_headers(token)
    body = json.dumps({"v": 1}).encode("utf-8")
    try:
        response = http.request(
            "POST",
            "https://api.pocketcasts.com/user/podcast/list",
            headers=header,
            body=body,
        )
        return json.loads(response.data)
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error fetching subscriptions: {e}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from subscriptions API: {response.data}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching subscriptions: {e}")
        return {}


def add_subscription(http, token, uuid):
    header = create_auth_headers(token)
    body = json.dumps({"uuid": uuid}).encode("utf-8")
    try:
        response = http.request(
            "POST", "https://api.pocketcasts.com/user/podcast/subscribe", headers=header, body=body
        )
        return json.loads(response.data)
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error adding subscription: {e}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from add subscription API: {response.data}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred adding subscription: {e}")
        return {}


def get_episodes(http, token, podcast_uuid):
    header = create_auth_headers(token)
    try:
        response = http.request(
            "GET", f"https://podcast-api.pocketcasts.com/podcast/full/{podcast_uuid}",
            headers=header
        )
        data = json.loads(response.data)
        # Ensure "podcast" and "episodes" keys exist before accessing
        if "podcast" in data and "episodes" in data["podcast"]:
            episodes = {}
            for episode in data["podcast"]["episodes"]:
                episodes[episode["title"]] = episode["uuid"]
            return episodes
        else:
            logger.error(f"Unexpected response structure from get_episodes API: {data}")
            return {}
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error fetching episodes: {e}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from get_episodes API: {response.data}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred fetching episodes: {e}")
        return {}

def update_podcast_episode(http, token, body):
    logger.info(f"Updating episode: {body}")
    header = create_auth_headers(token)
    try:
        response = http.request(
            "POST", "https://api.pocketcasts.com/sync/update_episode", headers=header, body=body
        )
        return json.loads(response.data)
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error updating podcast episode: {e}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from update_episode API: {response.data}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred updating podcast episode: {e}")
        return {}