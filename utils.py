import os
import unicodedata
import re
import requests


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def download_emote(image_link, path, emote_name):
    if not os.path.exists(path):
        os.mkdir(path)
    r = requests.get(image_link)
    file = open(path + emote_name + ".png", "wb")
    file.write(r.content)
    file.close()
