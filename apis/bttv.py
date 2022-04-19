from matplotlib.style import use
import requests
from apis import twitch

CHANNEL_EMOTES_URL = "https://api.betterttv.net/3/cached/users/twitch/"
EMOTE_URL = "https://cdn.betterttv.net/emote/"


def fetch_image_link_for_emote(emote):
    print("todo")


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
    else:
        return []


def image_link_for_emote_id(emote_id):
    return "https://cdn.betterttv.net/emote/" + str(emote_id) + "/3x"