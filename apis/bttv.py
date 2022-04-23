import requests
from apis import twitch

CHANNEL_EMOTES_URL = "https://api.betterttv.net/3/cached/users/twitch/"
EMOTE_URL = "https://cdn.betterttv.net/emote/"
GLOBAL_EMOTES_URL = "https://api.betterttv.net/3/cached/emotes/global"


def fetch_global_emote(emote_name):
    response = requests.get(GLOBAL_EMOTES_URL)

    if response.ok:
        req_emote = {}
        global_emotes = response.json()

        for emote in global_emotes:
            if emote_name == emote['code']:
                req_emote = {
                    "name": emote['code'],
                    "image_link": image_link_for_emote_id(emote['id'])
                }
                return req_emote
        return None


def fetch_all_global_emotes():
    response = requests.get(GLOBAL_EMOTES_URL)

    if response.ok:
        emotes = []
        global_emotes = response.json()

        for emote in global_emotes:
            emote_id = emote['id']
            emotes.append({
                "name": emote['code'],
                "image_link": image_link_for_emote_id(emote_id)
            })

        return emotes
    return []


def fetch_all_global_emote_names():
    all_names = []
    all_global_emotes = fetch_all_global_emotes()

    for emote in all_global_emotes:
        all_names.append(emote['name'])

    return all_names


def fetch_emote(emote_name, channel):
    user_id = twitch.get_user_id(channel)

    if not user_id:
        return None
    response = requests.get(CHANNEL_EMOTES_URL + user_id)
    if response.ok:
        req_emote = {}
        channel_emotes = response.json()['channelEmotes']
        shared_emotes = response.json()['sharedEmotes']

        for emote in channel_emotes + shared_emotes:
            if emote_name == emote['code']:
                req_emote = {
                    "name": emote['code'], "image_link": image_link_for_emote_id(emote['id'])}
                return req_emote
        return None


def fetch_all_emotes_for_channel(channel):
    user_id = twitch.get_user_id(channel)
    if not user_id:
        return []
    response = requests.get(CHANNEL_EMOTES_URL + user_id)
    if response.ok:
        emotes = []
        channel_emotes = response.json()['channelEmotes']
        shared_emotes = response.json()['sharedEmotes']

        for emote in channel_emotes + shared_emotes:
            emote_id = emote['id']
            emotes.append({
                "name": emote['code'],
                "image_link": image_link_for_emote_id(emote_id)
            })

        return emotes
    return []


def fetch_all_emote_names(channel):
    all_names = []
    all_emotes = fetch_all_emotes_for_channel(channel)

    for emote in all_emotes:
        all_names.append(emote['name'])

    return all_names


def image_link_for_emote_id(emote_id):
    return "https://cdn.betterttv.net/emote/" + str(emote_id) + "/3x"
