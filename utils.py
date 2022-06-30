import os
import unicodedata
import re
import requests
import pathlib

ROOT = pathlib.Path(__file__).parent.resolve()


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def download_image(image_link, image_name):
    path = os.path.join(ROOT, "emotes")
    if not os.path.exists(path):
        os.mkdir(path)
    r = requests.get(image_link)
    path_to_emote = os.path.join(path, slugify(image_name) + ".png")
    file = open(path_to_emote, "wb")
    file.write(r.content)
    file.close()

    return path_to_emote


def matches_twitch_emote_pattern(word):
    r = re.search(
        r'[a-zA-Z][a-z0-9]{2,9}[A-Z0-9][a-zA-Z0-9]{0,19}', word)

    return True if r else False
