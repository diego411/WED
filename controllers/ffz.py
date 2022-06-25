import requests
from controllers import twitch

CHANNEL_EMOTES_URL = "https://api.betterttv.net/3/cached/frankerfacez/users/twitch/"
GLOBAL_EMOTES_URL = "https://api.frankerfacez.com/v1/set/global"


def fetch_global_emote(emote_name):
    response = requests.get(GLOBAL_EMOTES_URL)
    if response.ok:
        req_emote = {}
        global_emotes = response.json(
        )["sets"]["3"]["emoticons"] + response.json()['sets']["4330"]["emoticons"]

        for emote in global_emotes:
            if emote_name == emote['name']:
                req_emote = {
                    "name": emote['name'],
                    "image_link": image_link_for_emote_id(emote['id'])
                }
                return req_emote
        return None


def fetch_all_global_emotes():
    response = requests.get(GLOBAL_EMOTES_URL)

    if response.ok:
        emotes = {}
        global_emotes = response.json(
        )["sets"]["3"]["emoticons"] + response.json()['sets']["4330"]["emoticons"]

        for emote in global_emotes:
            emotes[emote['name']] = emote['id']

        return emotes
    return []


def fetch_emote(emote_name, channel):
    user_id = twitch.get_user_id(channel)
    if not user_id:
        return []
    response = requests.get(CHANNEL_EMOTES_URL + user_id)
    if response.ok:
        req_emote = {}
        channel_emotes = response.json()
        image_sizes = ['4x', '2x', '1x']

        for emote in channel_emotes:
            if emote_name == emote['code']:
                for img_size in image_sizes:
                    if emote['images'][img_size]:
                        req_emote = {
                            "name": emote['code'],
                            "image_link": emote['images'][img_size]
                        }
                        return req_emote
        return None


def fetch_all_emotes_for_channel(channel):
    user_id = twitch.get_user_id(channel)
    if not user_id:
        return {}
    response = requests.get(CHANNEL_EMOTES_URL + user_id)
    if response.ok:
        emotes = {}
        channel_emotes = response.json()

        for emote in channel_emotes:
            emotes[emote['code']] = emote['id']

        return emotes
    return []


def image_link_for_emote_id(emote_id):
    return "https://cdn.frankerfacez.com/emote/" + str(emote_id) + "/4"
