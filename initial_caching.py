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


for channel in channels:
    emotes = bttv.fetch_all_emotes_for_channel(channel)
    for emote in emotes:
        path = ROOT_FOLDER + "/emotes/" + channel + "/"
        download_emote(emote['image_link'], path, emote['name'])
        score = query_model.get_weeb_score(path + "/" + emote['name'] + ".png")
        print(emote['name'])
        print(score)
