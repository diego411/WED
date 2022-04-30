import json
import os
import utils
from apis import bttv
from apis import ffz
from apis import seventv
from apis import twitch
from model import query_model
from cache.FWFCache import FWFCache
from cache.ExpiringCache import ExpiringCache


class CacheManager:

    def __init__(self, cach_client):
        self.r = cach_client
        self.channels = self.r.get('channels').split(
            ' ') if self.r.get('channels') else []
        self.channel_cache_map = {}
        self.global_twitch_emotes_cache = {}
        self.globa_third_party_emotes_cache = {}
        self.sub_emote_cache = FWFCache(
            self.r, "sub-emotes", 500, self.miss_callback_sub_emotes)
        self.init_cache()

    def init_cache(self):
        self.init_third_party_emote_cache()

        self.init_global_emote_cache()

    def init_channel_cache(self, channel):
        self.channel_cache_map[channel] = ExpiringCache(
            self.r, channel, self.miss_callback_third_party_emotes, 7200, self.fetch_all_third_party_target_names)

    def init_third_party_emote_cache(self):
        for channel in self.channels:
            self.channel_cache_map[channel] = ExpiringCache(
                self.r, channel, self.miss_callback_third_party_emotes, 7200, self.fetch_all_third_party_target_names)

    def init_global_emote_cache(self):
        self.global_twitch_emotes_cache = ExpiringCache(
            self.r, "global-twitch", self.miss_callback_global_twitch_emotes, 7200, self.fetch_all_global_twitch_target_names)
        self.globa_third_party_emotes_cache = ExpiringCache(
            self.r, "global-third-party", self.miss_callback_global_third_party_emotes, 7200, self.fetch_all_global_third_party_target_names)

    def get_emote_score(self, emote):
        if not emote:
            return None

        path_to_emote = utils.download_emote(
            emote['image_link'], emote['name'])
        score = query_model.get_weeb_score(path_to_emote)
        os.remove(path_to_emote)

        return score.item()

    def miss_callback_sub_emotes(self, target):
        emote = twitch.fetch_sub_emote(target)
        # is not a sub emote
        return self.get_emote_score(emote)

    def miss_callback_third_party_emotes(self, target, context):
        if target in json.loads(self.r.get(context + "-emote-names-bttv")):
            emote = bttv.fetch_emote(target, context)
        elif target in json.loads(self.r.get(context + "-emote-names-ffz")):
            emote = ffz.fetch_emote(target, context)
        elif target in json.loads(self.r.get(context + "-emote-names-seventv")):
            emote = seventv.fetch_emote(target, context)

        return self.get_emote_score(emote)

    def miss_callback_global_twitch_emotes(self, target, context):
        if target in json.loads(self.r.get("global-emotes-twitch")):
            emote = twitch.fetch_global_emote(target)

        if not emote:
            return None

        return self.get_emote_score(emote)

    def miss_callback_global_third_party_emotes(self, target, context):
        if target in json.loads(self.r.get("global-emotes-bttv")):
            emote = bttv.fetch_global_emote(target)
        elif target in json.loads(self.r.get("global-emotes-ffz")):
            emote = ffz.fetch_global_emote(target)
        elif target in json.loads(self.r.get("global-emotes-seventv")):
            emote = seventv.fetch_global_emote(target)

        return self.get_emote_score(emote)

    def fetch_all_third_party_target_names(self, channel):
        all_names_bttv = bttv.fetch_all_emote_names(channel)
        self.r.set(channel + "-emote-names-bttv", json.dumps(all_names_bttv))
        all_names_ffz = ffz.fetch_all_emote_names(channel)
        self.r.set(channel + "-emote-names-ffz", json.dumps(all_names_ffz))
        all_names_seventv = seventv.fetch_all_emote_names(channel)
        self.r.set(channel + "-emote-names-seventv",
                   json.dumps(all_names_seventv))

        return all_names_bttv + all_names_ffz + all_names_seventv

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

    def get_stats(self, message, channel):
        # priority: global-twitch-emotes, sub-emotes, third-party-channel-emotes, global-third-party-emotes
        scores = []
        tmp_cache = {}

        words = message.split(' ')

        for word in words:

            if word in tmp_cache:
                scores.append(tmp_cache[word])
                continue

            score = self.global_twitch_emotes_cache.shoot(word)

            if score:
                scores.append(score)
                tmp_cache[word] = score
                continue

            if utils.matches_twitch_emote_pattern(word):
                score = self.sub_emote_cache.shoot(word)

                if score:
                    scores.append(score)
                    tmp_cache[word] = score
                    continue

            score = self.channel_cache_map[channel].shoot(word)

            if score:
                scores.append(score)
                tmp_cache[word] = score
                continue

            score = self.globa_third_party_emotes_cache.shoot(word)

            if score:
                scores.append(score)
                tmp_cache[word] = score

        if scores:
            max_score = 0
            number_of_weeb_terms = 0
            for score in scores:
                if score > max_score:
                    max_score = score
                if score > 0.7:
                    number_of_weeb_terms = number_of_weeb_terms + 1

            isWeeb = max_score > 0.7
            return {
                "is_weeb": isWeeb,
                "confidence": max_score if isWeeb else 1 - max_score,
                "number_of_weeb_terms": number_of_weeb_terms
            }
        return {
            "is_weeb": False,
            "confidence": 1,
            "number_of_weeb_terms": 0
        }
