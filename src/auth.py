import json
import urllib3
import logging

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

    if response.status != 200:
        logging.fatal(f'Failed to login: {response.status}')
        raise Exception(f'Response: {response.data.decode("utf-8")}')
    
    token = json.loads(response.data)["token"]
    if not token:
        logging.fatal('Failed to retrieve token from login response.')
        raise Exception('No token found in the response.')
    
    return token


def create_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
