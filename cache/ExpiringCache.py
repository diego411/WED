import json
import time


class ExpiringCache:

    def __init__(self, cache_client, key, miss_callback, refresh_treshold, fetch_all_target_names):
        self.cache_client = cache_client
        self.KEY = key
        self.miss_callback = miss_callback
        self.fetch_all_target_names = fetch_all_target_names
        self.all_target_names = fetch_all_target_names(self.KEY)
        self.targets_refresh_timestamp = time.time()
        self.refresh_treshold = refresh_treshold

        self.shoot("init")
        for target in self.all_target_names:
            self.shoot(target)

    # KKona
    def shoot(self, target):
        if target not in self.all_target_names:
            return None

        all_targets = self.cache_client.get(self.KEY)

        if not all_targets:
            self.cache_client.set(self.KEY, json.dumps({}))
            all_targets = {}
        else:
            all_targets = json.loads(all_targets)

        self.refresh_targets()

        if target not in self.all_target_names:
            return None

        # cache hit
        if target in all_targets:
            # force cache miss on expired value
            if not self.expired(all_targets[target]):
                print("Cache hit for target: " +
                      target + " in context: " + self.KEY)
                return all_targets[target]["value"]
            print("Cached value for target: " + target + " is expired")

        # cache miss
        print("Cache miss for target: " + target + " in context: " + self.KEY)
        missed_value = self.miss_callback(target, self.KEY)

        if not missed_value:
            return None

        all_targets[target] = {
            "value": missed_value,
            "timestamp": time.time()
        }

        self.cache_client.set(self.KEY, json.dumps(all_targets))

        print("Cached target: " +
              target + " with value " + str(missed_value))

        return missed_value

    def refresh_targets(self):
        if abs(self.targets_refresh_timestamp - time.time()) >= self.refresh_treshold:
            print("Refreshing targets for context: " + self.KEY)
            self.targets_refresh_timestamp = time.time()
            self.all_target_names = self.fetch_all_target_names(self.KEY)

    def expired(self, target):
        return abs(target["timestamp"] - time.time()) >= self.refresh_treshold
