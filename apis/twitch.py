import os
import requests
from dotenv import load_dotenv

load_dotenv()

OAUTH = os.environ.get("OAUTH")
CLIENT_ID = os.environ.get("CLIENT_ID")

HELIX_USERS_URL = "https://api.twitch.tv/helix/users/"


def get_user_id(channel_name):
    headers = {"Authorization": "Bearer " + OAUTH, "Client-Id": CLIENT_ID}
    response = requests.get(
        HELIX_USERS_URL + "?login=" + channel_name, headers=headers)

    if response.ok and response.json()['data']:
        return response.json()['data'][0]['id']
