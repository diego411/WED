import os
import requests
from dotenv import load_dotenv

load_dotenv()

OAUTH = os.environ.get("OAUTH")
CLIENT_ID = os.environ.get("CLIENT_ID")

HELIX_USERS_URL = "https://api.twitch.tv/helix/users/"
HELIX_GLOBAL_EMOTES = "https://api.twitch.tv/helix/chat/emotes/global"
SUB_EMOTES_URL = "https://api.ivr.fi/v2/twitch/emotes/"


def fetch_sub_emote(emote_name):
    response = requests.get(SUB_EMOTES_URL + emote_name)

    if response.ok:
        emote = response.json()
        return {
            "name": emote['emoteCode'],
            "image_link": get_image_link(emote['emoteID'])
        }
    return None


def fetch_global_emote(emote_name):
    headers = {"Authorization": "Bearer " + OAUTH, "Client-Id": CLIENT_ID}
    response = requests.get(HELIX_GLOBAL_EMOTES, headers=headers)

    if response.ok:
        req_emote = {}
        global_emotes = response.json()['data']
        image_sizes = ["url_4x", "url_2x", "url_1x"]

        for emote in global_emotes:
            if emote_name == emote['name']:
                for image_size in image_sizes:
                    if image_size in emote['images']:
                        req_emote = {
                            "name": emote['name'],
                            "image_link": emote['images'][image_size]
                        }
                        return req_emote
        return None


def fetch_all_global_emotes():
    headers = {"Authorization": "Bearer " + OAUTH, "Client-Id": CLIENT_ID}
    response = requests.get(HELIX_GLOBAL_EMOTES, headers=headers)

    if response.ok:
        emotes = {}
        global_emotes = response.json()['data']

        for emote in global_emotes:
            emotes[emote['name']] = emote['id']

        return emotes
    return {}


def get_user_id(channel_name):
    headers = {"Authorization": "Bearer " + OAUTH, "Client-Id": CLIENT_ID}
    response = requests.get(
        HELIX_USERS_URL + "?login=" + channel_name, headers=headers)

    if response.ok and response.json()['data']:
        return response.json()['data'][0]['id']


def get_image_link(emoteID):
    return "https://static-cdn.jtvnw.net/emoticons/v2/" + str(emoteID) + "/default/dark/3.0"
