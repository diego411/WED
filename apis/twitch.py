import os
import requests
from dotenv import load_dotenv

load_dotenv()

OAUTH = os.environ.get("OAUTH")
CLIENT_ID = os.environ.get("CLIENT_ID")

HELIX_USERS_URL = "https://api.twitch.tv/helix/users/"
HELIX_GLOBAL_EMOTES = "https://api.twitch.tv/helix/chat/emotes/global"


def fetch_all_global_emotes():
    headers = {"Authorization": "Bearer " + OAUTH, "Client-Id": CLIENT_ID}
    response = requests.get(HELIX_GLOBAL_EMOTES, headers=headers)

    if response.ok:
        emotes = []
        global_emotes = response.json()['data']
        image_sizes = ["url_4x", "url_2x", "url_1x"]

        for emote in global_emotes:
            for image_size in image_sizes:
                if image_size in emote['images']:
                    emotes.append({
                        "name": emote['name'],
                        "image_link": emote['images'][image_size]
                    })
                    break
        print(emotes)
        return emotes
    return []


def get_user_id(channel_name):
    headers = {"Authorization": "Bearer " + OAUTH, "Client-Id": CLIENT_ID}
    response = requests.get(
        HELIX_USERS_URL + "?login=" + channel_name, headers=headers)

    if response.ok and response.json()['data']:
        return response.json()['data'][0]['id']
