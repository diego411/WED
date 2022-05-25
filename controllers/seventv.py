import requests

USER_URL = "https://api.7tv.app/v2/users/"
GLOBAL_EMOTES_URL = "https://api.7tv.app/v2/emotes/global"


def fetch_global_emote(emote_name):
    response = requests.get(GLOBAL_EMOTES_URL)

    if response.ok:
        req_emote = {}
        global_emotes = response.json()

        for emote in global_emotes:
            if emote_name == emote['name']:
                req_emote = {
                    "name": emote['name'],
                    "image_link": emote['urls'][-1][1]
                }
                return req_emote
        return None


def fetch_all_global_emotes():
    response = requests.get(GLOBAL_EMOTES_URL)

    if response.ok:
        emotes = []
        global_emotes = response.json()

        for emote in global_emotes:
            image_links = emote['urls']
            emotes.append({
                "name": emote['name'],
                "image_link": image_links[-1][1]
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
    response = requests.get(USER_URL + channel + "/emotes")
    if response.ok:
        req_emote = {}
        channel_emotes = response.json()

        for emote in channel_emotes:
            if emote_name == emote['name']:
                req_emote = {
                    "name": emote['name'],
                    "image_link": emote['urls'][-1][1]
                }
                return req_emote
        return None


def fetch_all_emotes_for_channel(channel):
    response = requests.get(USER_URL + channel + "/emotes")
    if response.ok:
        emotes = []
        channel_emotes = response.json()

        for emote in channel_emotes:
            image_links = emote['urls']
            emotes.append({
                "name": emote['name'],
                "image_link": image_links[-1][1]
            })

        return emotes
    return []


def fetch_all_emote_names(channel):
    all_names = []
    all_emotes = fetch_all_emotes_for_channel(channel)

    for emote in all_emotes:
        all_names.append(emote['name'])

    return all_names
