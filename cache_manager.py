import json
import os
import redis
from apis import bttv
from apis import ffz
from apis import seventv
from apis import twitch
from model import query_model
from cache.FWFCache import FWFCache
from cache.ExpiringCache import ExpiringCache
import utils


class CacheManager:

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379,
                             db=0, decode_responses=True)
        self.channels = self.r.get('channels').split(' ')
        self.ROOT_FOLDER = "D:/Projects/WED"
        self.channel_cache_map = {}
        self.global_twitch_emotes_cache = {}
        self.globa_third_party_emotes_cache = {}
        self.sub_emote_cache = FWFCache(
            self.r, "sub-emotes", 500, self.miss_callback_sub_emotes)
        self.init_cache()

    def init_cache(self):
        if not os.path.exists(self.ROOT_FOLDER + "/emotes/"):
            os.mkdir(self.ROOT_FOLDER + "/emotes/")

        self.init_third_party_emote_cache()

        if not os.path.exists(self.ROOT_FOLDER + "/emotes/"):
            os.mkdir(self.ROOT_FOLDER + "/emotes/")

        self.init_global_emote_cache()

    def init_third_party_emote_cache(self):
        for channel in self.channels:
            self.channel_cache_map[channel] = ExpiringCache(
                self.r, channel, self.miss_callback_third_party_emotes, 7200, self.fetch_all_third_party_target_names)

    def miss_callback_sub_emotes(self, target):
        emote = twitch.fetch_sub_emote(target)
        # is not a sub emote
        if not emote:
            return None

        if not os.path.exists(self.ROOT_FOLDER + "/emotes/"):
            os.mkdir(self.ROOT_FOLDER + "/emotes/")

        path = "D:/Projects/WED" + "/emotes/" + emote['name'] + "/"
        path_to_emote = path + utils.slugify(emote['name']) + ".png"
        utils.download_emote(emote['image_link'], path,
                             utils.slugify(emote['name']))
        score = query_model.get_weeb_score(path_to_emote)
        os.remove(path_to_emote)
        if os.path.exists(path):
            os.rmdir(path)
        return score.item()

    def miss_callback_third_party_emotes(self, target, context):
        if target in json.loads(self.r.get(context + "-emote_names-bttv")):
            emote = bttv.fetch_emote(target, context)
        elif target in json.loads(self.r.get(context + "-emote_names-ffz")):
            emote = ffz.fetch_emote(target, context)
        elif target in json.loads(self.r.get(context + "-emote_names-seventv")):
            emote = seventv.fetch_emote(target, context)
        if not emote:
            return None

        if not os.path.exists(self.ROOT_FOLDER + "/emotes/"):
            os.mkdir(self.ROOT_FOLDER + "/emotes/")

        path = "D:/Projects/WED" + "/emotes/" + emote['name'] + "/"
        path_to_emote = path + utils.slugify(emote['name']) + ".png"
        utils.download_emote(emote['image_link'], path,
                             utils.slugify(emote['name']))
        score = query_model.get_weeb_score(path_to_emote)
        os.remove(path_to_emote)
        if os.path.exists(path):
            os.rmdir(path)
        return score.item()

    def fetch_all_third_party_target_names(self, channel):
        all_names_bttv = bttv.fetch_all_emote_names(channel)
        self.r.set(channel + "-emote-names-bttv", json.dumps(all_names_bttv))
        all_names_ffz = ffz.fetch_all_emote_names(channel)
        self.r.set(channel + "-emote-names-ffz", json.dumps(all_names_ffz))
        all_names_seventv = ffz.fetch_all_emote_names(channel)
        self.r.set(channel + "-emote-names-seventv",
                   json.dumps(all_names_seventv))

        return all_names_bttv + all_names_ffz + all_names_seventv

    def init_global_emote_cache(self):
        self.global_twitch_emotes_cache = ExpiringCache(
            self.r, "global-twitch", self.miss_callback_global_twitch_emotes, 7200, self.fetch_all_global_twitch_target_names)
        self.globa_third_party_emotes_cache = ExpiringCache(
            self.r, "global-third-party", self.miss_callback_global_third_party_emotes, 7200, self.fetch_all_global_third_party_target_names)

    def miss_callback_global_twitch_emotes(self, target, context):
        if target in json.loads(self.r.get("global-emotes-twitch")):
            emote = twitch.fetch_global_emote(target)

        if not emote:
            return None

        if not os.path.exists(self.ROOT_FOLDER + "/emotes/"):
            os.mkdir(self.ROOT_FOLDER + "/emotes/")

        path = "D:/Projects/WED" + "/emotes/"  # + emote['name'] + "/"
        path_to_emote = path + utils.slugify(emote['name']) + ".png"
        utils.download_emote(emote['image_link'], path,
                             utils.slugify(emote['name']))
        score = query_model.get_weeb_score(path_to_emote)
        os.remove(path_to_emote)
        if os.path.exists(path):
            os.rmdir(path)
        return score.item()

    def miss_callback_global_third_party_emotes(self, target, context):
        if target in json.loads(self.r.get("global-emotes-bttv")):
            emote = bttv.fetch_global_emote(target)
        elif target in json.loads(self.r.get("global-emotes-ffz")):
            emote = ffz.fetch_global_emote(target)
        elif target in json.loads(self.r.get("global-emotes-seventv")):
            emote = seventv.fetch_global_emote(target)

        if not emote:
            return None

        if not os.path.exists(self.ROOT_FOLDER + "/emotes/"):
            os.mkdir(self.ROOT_FOLDER + "/emotes/")

        path = "D:/Projects/WED" + "/emotes/"  # + emote['name'] + "/"
        path_to_emote = path + utils.slugify(emote['name']) + ".png"
        utils.download_emote(emote['image_link'], path,
                             utils.slugify(emote['name']))
        score = query_model.get_weeb_score(path_to_emote)
        os.remove(path_to_emote)
        if os.path.exists(path):
            os.rmdir(path)
        return score.item()

    def fetch_all_global_twitch_target_names(self, channel):
        global_twitch = twitch.fetch_all_global_emote_names()
        self.r.set("global-emotes-twitch", json.dumps(global_twitch))

        return global_twitch

    def fetch_all_global_third_party_target_names(self, channel):
        global_bttv = bttv.fetch_all_global_emote_names()
        self.r.set("global-emotes-bttv", json.dumps(global_bttv))
        global_ffz = ffz.fetch_all_global_emote_names()
        self.r.set("global-emotes-ffz", json.dumps(global_ffz))
        global_seventv = seventv.fetch_all_global_emote_names()
        self.r.set("global-emotes-seventv", json.dumps(global_seventv))

        return global_bttv + global_ffz + global_seventv

    def get_score(self, word, channel):
        # priority: global-twitch-emotes, sub-emotes, third-party-channel-emotes, global-third-party-emotes
        score = self.global_twitch_emotes_cache.shoot(word)

        if score:
            return score

        score = self.sub_emote_cache.shoot(word)

        if score:
            return score

        score = self.channel_cache_map[channel].shoot(word)

        if score:
            return score

        score = self.globa_third_party_emotes_cache.shoot(word)

        return score
