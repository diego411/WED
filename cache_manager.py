import json
import os
import utils
from controllers import bttv
from controllers import ffz
from controllers import seventv
from controllers import twitch
from model import query_model
from cache.FWFCache import FWFCache
from cache.ExpiringCache import ExpiringCache


class CacheManager:

    def __init__(self, cach_client):
        self.r = cach_client
        self.channels = self.r.smembers(
            'channels') if self.r.smembers('channels') else []
        self.channel_cache_map = {}
        self.global_twitch_emotes_cache = {}
        self.globa_third_party_emotes_cache = {}
        self.sub_emote_cache = FWFCache(
            self.r, "sub-emotes", 500, self.miss_callback_sub_emotes)
        self.EXIRING_RATE = float(os.environ.get("EXPIRING_RATE"))

        self.init_cache()

    def init_cache(self):
        self.init_third_party_emote_cache()

        self.init_global_emote_cache()

    def init_channel_cache(self, channel):
        self.channel_cache_map[channel] = ExpiringCache(
            self.r, channel, self.miss_callback_third_party_emotes, self.EXIRING_RATE, self.fetch_all_third_party_target_names)

    def init_third_party_emote_cache(self):
        for channel in self.channels:
            self.channel_cache_map[channel] = ExpiringCache(
                self.r, channel, self.miss_callback_third_party_emotes, self.EXIRING_RATE, self.fetch_all_third_party_target_names)

    def init_global_emote_cache(self):
        self.global_twitch_emotes_cache = ExpiringCache(
            self.r, "global-twitch", self.miss_callback_global_twitch_emotes, self.EXIRING_RATE, self.fetch_all_global_twitch_target_names)
        self.globa_third_party_emotes_cache = ExpiringCache(
            self.r, "global-third-party", self.miss_callback_global_third_party_emotes, self.EXIRING_RATE, self.fetch_all_global_third_party_target_names)

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
        if target in json.loads(self.r.get(context + "-emotes-bttv")):
            emote = bttv.fetch_emote(target, context)
        elif target in json.loads(self.r.get(context + "-emotes-ffz")):
            emote = ffz.fetch_emote(target, context)
        elif target in json.loads(self.r.get(context + "-emotes-seventv")):
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
        all_names_bttv = bttv.fetch_all_emotes_for_channel(channel)
        self.r.set(channel + "-emotes-bttv", json.dumps(all_names_bttv))
        all_names_ffz = ffz.fetch_all_emotes_for_channel(channel)
        self.r.set(channel + "-emotes-ffz", json.dumps(all_names_ffz))
        all_names_seventv = seventv.fetch_all_emotes_for_channel(channel)
        self.r.set(channel + "-emotes-seventv",
                   json.dumps(all_names_seventv))

        return all_names_bttv | all_names_ffz | all_names_seventv

    def fetch_all_global_twitch_target_names(self, channel):
        global_twitch = twitch.fetch_all_global_emotes()
        self.r.set("global-emotes-twitch", json.dumps(global_twitch))

        return global_twitch

    def fetch_all_global_third_party_target_names(self, channel):
        global_bttv = bttv.fetch_all_global_emotes()
        self.r.set("global-emotes-bttv", json.dumps(global_bttv))
        global_ffz = ffz.fetch_all_global_emotes()
        self.r.set("global-emotes-ffz", json.dumps(global_ffz))
        global_seventv = seventv.fetch_all_global_emotes()
        self.r.set("global-emotes-seventv", json.dumps(global_seventv))

        return global_bttv | global_ffz | global_seventv

    def get_stats(self, message, channel, emotes):
        # priority: global-twitch-emotes, sub-emotes, third-party-channel-emotes, global-third-party-emotes
        score_manager = ScoreManager()

        white_list = self.r.smembers("whitelist")
        words = message.split(' ')

        words = list(filter(lambda w: w not in white_list, words))

        for word in words:

            hit = score_manager.shoot_tmp_cache(word)
            if hit:
                continue

            if not emotes == None:
                if word in emotes:
                    if score_manager.shoot_expiring_cache(self.global_twitch_emotes_cache, word):
                        continue

                    if score_manager.shoot_fwf_cache(self.sub_emote_cache, word, emotes[word]):
                        continue
            else:
                if score_manager.shoot_expiring_cache(self.global_twitch_emotes_cache, word):
                    continue

                if utils.matches_twitch_emote_pattern(word):
                    if score_manager.shoot_fwf_cache(self.sub_emote_cache, word, None):
                        continue

            if score_manager.shoot_expiring_cache(self.channel_cache_map[channel], word):
                continue

            if score_manager.shoot_expiring_cache(self.globa_third_party_emotes_cache, word):
                continue

            score_manager.set_tmp(word, 0)

        return score_manager.get_score_stats()


class ScoreManager:
    def __init__(self):
        self.tmp_cache = {}
        self.scores = []

    def shoot_tmp_cache(self, target):
        if target in self.tmp_cache:
            self.scores.append(self.tmp_cache[target])
            return True
        return False

    def set_tmp(self, target, score):
        self.tmp_cache[target] = score

    def shoot_expiring_cache(self, cache, target):
        score = cache.shoot(target)
        if score:
            self.scores.append(score)
            self.tmp_cache[target] = score
            return True
        return False

    def shoot_fwf_cache(self, cache, target, target_id):
        score = cache.shoot(target, target_id)
        if score:
            self.scores.append(score)
            self.tmp_cache[target] = score
            return True
        return False

    def get_score_stats(self):
        if self.scores:
            max_score = 0
            number_of_weeb_terms = 0
            for score in self.scores:
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
