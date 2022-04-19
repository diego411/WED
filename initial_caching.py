import json
import os
import redis
import requests
from apis import bttv
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


def cache_emote_score(channel, emote_name, score):
    cache_for_channel = r.get(channel)
    cache = {}

    if cache_for_channel:
        cache = json.loads(cache_for_channel)
    cache[emote_name] = score.item()
    r.set(channel, json.dumps(cache))


def run():
    if not os.path.exists(ROOT_FOLDER + "/emotes/"):
        os.mkdir(ROOT_FOLDER + "/emotes/")

    for channel in channels:
        emotes = bttv.fetch_all_emotes_for_channel(channel)
        path = ROOT_FOLDER + "/emotes/" + channel + "/"
        for emote in emotes:
            download_emote(emote['image_link'], path, emote['name'])
            path_to_emote = path + "/" + emote['name'] + ".png"
            score = query_model.get_weeb_score(path_to_emote)
            cache_emote_score(channel, emote['name'], score)
            print(emote['name'])
            print(score)
            os.remove(path_to_emote)
        if os.path.exists(path):
            os.rmdir(path)
