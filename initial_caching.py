import json
import os
import unicodedata
import re
import redis
import requests
from apis import bttv
from apis import ffz
from apis import seventv
from model import query_model

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

channels = r.get('channels').split(' ')

ROOT_FOLDER = "D:/Projects/WED"


def download_emote(image_link, path, emote_name):
    if not os.path.exists(path):
        os.mkdir(path)
    r = requests.get(image_link)
    file = open(path + emote_name + ".png", "wb")
    file.write(r.content)
    file.close()


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode(
            'ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def cache_emote_score(channel, emote_name, score):
    cache_for_channel = r.get(channel)
    cache = {}

    if cache_for_channel:
        cache = json.loads(cache_for_channel)
    cache[emote_name] = score.item()
    r.set(channel, json.dumps(cache))
    print("Cached emote " + emote_name + " with score " +
          str(score) + " for " + "[#" + channel + "]")


def fetch_and_cache(context, emote_provider):
    if context == "global":
        emotes = emote_provider.fetch_all_global_emotes()
    else:
        emotes = emote_provider.fetch_all_emotes_for_channel(context)

    path = ROOT_FOLDER + "/emotes/" + context + "/"
    for emote in emotes:
        path_to_emote = path + slugify(emote['name']) + ".png"
        download_emote(emote['image_link'], path, slugify(emote['name']))
        score = query_model.get_weeb_score(path_to_emote)
        cache_emote_score(context, emote['name'], score)
        os.remove(path_to_emote)
    if os.path.exists(path):
        os.rmdir(path)


def init_third_party_emote_cache():
    for channel in channels:
        fetch_and_cache(channel, bttv)
        fetch_and_cache(channel, ffz)
        fetch_and_cache(channel, seventv)


def init_global_emote_cache():
    fetch_and_cache("global", bttv)
    fetch_and_cache("global", ffz)


def run():
    if not os.path.exists(ROOT_FOLDER + "/emotes/"):
        os.mkdir(ROOT_FOLDER + "/emotes/")

    init_third_party_emote_cache()

    if not os.path.exists(ROOT_FOLDER + "/emotes/"):
        os.mkdir(ROOT_FOLDER + "/emotes/")

    init_global_emote_cache()
