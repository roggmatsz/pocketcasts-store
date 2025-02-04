import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def do_login(http, user, pw):
    if not user or not pw:
        return None

    data = {"email": f"{user}", "password": f"{pw}", "scope": "webplayer"}
    encoded_data = json.dumps(data).encode("utf-8")
    http = urllib3.PoolManager(cert_reqs='CERT_NONE', assert_hostname=False)
    response = http.request(
        "POST",
        "https://api.pocketcasts.com/user/login",
        headers={"Content-Type": "application/json"},
        body=encoded_data,
    )
    token = json.loads(response.data)["token"]
    return token


def create_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
