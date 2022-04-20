import requests

USER_URL = "https://api.7tv.app/v2/users/"
GLOBAL_EMOTES_URL = "https://api.7tv.app/v2/emotes/global"


def fetch_image_link_for_emote(emote):
    print("todo")


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
