import json

from auth import create_auth_headers

def get_history(http, token):
    header = create_auth_headers(token)
    response = http.request(
        "POST",
        "https://api.pocketcasts.com/user/history",
        headers=header,
    )
    data = json.loads(response.data)
    return data

def search_podcasts(http, token, term):
    header = create_auth_headers(token)
    body = json.dumps({"term":term}, ensure_ascii=False).encode("ascii", errors="ignore")
    header["content-length"] = len(body)
    print(header)
    print(body)
    response = http.request(
        "POST",
        "https://api.pocketcasts.com/discover/search",
        headers=header,
        body=body,
    )
    return json.loads(response.data)


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
    response = http.request(
        "POST",
        "https://api.pocketcasts.com/user/podcast/list",
        headers=header,
        body=body,
    )
    return json.loads(response.data)


def add_subscription(http, token, uuid):
    header = create_auth_headers(token)
    body = json.dumps({"uuid": uuid}).encode("utf-8")
    response = http.request(
        "POST", "https://api.pocketcasts.com/user/podcast/subscribe", headers=header, body=body
    )
    return json.loads(response.data)


def get_episodes(http, token, podcast_uuid):
    header = create_auth_headers(token)
    response = http.request(
        "GET", f"https://podcast-api.pocketcasts.com/podcast/full/{podcast_uuid}", 
        headers=header
    )
    data = json.loads(response.data)
    try:
        data["podcast"]["episodes"]
    except(IndexError, KeyError):
        return {}

    episodes = {}
    for episode in data["podcast"]["episodes"]:
        episodes[episode["title"]] = episode["uuid"]
    return episodes

def update_podcast_episode(http, token, body):
    print("Updating episode:")
    print(body)
    header = create_auth_headers(token)
    response = http.request(
        "POST", "https://api.pocketcasts.com/sync/update_episode", headers=header, body=body
    )
    return json.loads(response.data)