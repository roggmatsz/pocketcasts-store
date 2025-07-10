import json
import urllib3
from .logger import setup_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = setup_logger('auth_logger', 'pocketcasts_errors.log')

def do_login(http, user, pw):
    if not user or not pw:
        logger.error("Username or password not provided.")
        return None

    data = {"email": f"{user}", "password": f"{pw}", "scope": "webplayer"}
    encoded_data = json.dumps(data).encode("utf-8")

    try:
        response = http.request(
            "POST",
            "https://api.pocketcasts.com/user/login",
            headers={"Content-Type": "application/json"},
            body=encoded_data,
        )
        response_data = json.loads(response.data)
        token = response_data["token"]
        return token
    except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
        logger.error(f"Network error during login: {e}")
        return None
    except KeyError:
        logger.error("Login failed. 'token' not found in response. Check credentials.")
        return None
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from login API: {response.data}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during login: {e}")
        return None


def create_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
