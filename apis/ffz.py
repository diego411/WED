import requests
from apis import twitch

CHANNEL_EMOTES_URL = "https://api.betterttv.net/3/cached/frankerfacez/users/twitch/"


def fetch_image_link_for_emote(emote):
    print("todo")


def fetch_all_emotes_for_channel(channel):
    user_id = twitch.get_user_id(channel)
    if not user_id:
        return []
    response = requests.get(CHANNEL_EMOTES_URL + user_id)
    if response.ok:
        emotes = []
        channel_emotes = response.json()
        image_sizes = ['4x', '2x', '1x']

        for emote in channel_emotes:
            for img_size in image_sizes:
                if emote['images'][img_size]:
                    emotes.append({
                        "name": emote['code'],
                        "image_link": emote['images'][img_size]
                    })
                    break

        return emotes
    else:
        return []
