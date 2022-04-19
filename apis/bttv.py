from matplotlib.style import use
import requests
from twitch import get_user_id

CHANNEL_EMOTES_URL = "https://api.betterttv.net/3/cached/users/twitch/"
EMOTE_URL = "https://cdn.betterttv.net/emote/"


def fetch_image_link_for_emote(emote):
    print("todo")


def fetch_all_image_links_for_channel(channel):
    user_id = get_user_id(channel)
    if not user_id:
        return []
    response = requests.get(CHANNEL_EMOTES_URL + user_id)
    if response.ok:
        emote_ids = []
        channel_emotes = response.json()['channelEmotes']
        shared_emotes = response.json()['sharedEmotes']

        for emote in channel_emotes:
            emote_ids.append(emote['id'])
        for emote in shared_emotes:
            emote_ids.append(emote['id'])

        image_links = []

        for emote_id in emote_ids:
            image_links.append(image_link_for_emote_id(emote_id))

        return image_links
    else:
        return []


def image_link_for_emote_id(emote_id):
    return "https://cdn.betterttv.net/emote/" + str(emote_id) + "/3x"


print(fetch_all_image_links_for_channel("nymn"))
