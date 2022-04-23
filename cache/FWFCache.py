import json


class FWFCache:
    # Cache implementing the Flush When Full (FWF) strategy

    def __init__(self, cache_client, key, MAX_SIZE, miss_callback):
        self.cache_client = cache_client
        self.KEY = key
        self.miss_callback = miss_callback
        self.MAX_SIZE = MAX_SIZE

        cache = cache_client.get(self.KEY)
        self.current_size = len(
            json.loads(cache).keys()) if cache else 0

    # KKona
    def shoot(self, target):
        cache = self.cache_client.get(self.KEY)
        if not cache:
            self.cache_client.set(self.KEY, json.dumps({}))
            cache = {}
        else:
            cache = json.loads(cache)

        # cache hit
        if target in cache:
            print("Cache hit for target: " +
                  target + " in context: " + self.KEY)
            return cache[target]

        # cache miss
        print("Cache miss for target: " + target + " in context: " + self.KEY)

        missed_value = self.miss_callback(target)

        if not missed_value:
            return None

        if self.current_size >= self.MAX_SIZE:  # flush on full cash miss
            self.flush()
            cache = {}

        self.current_size = self.current_size + 1

        cache[target] = missed_value

        self.cache_client.set(self.KEY, json.dumps(cache))

        print("Cached target: " +
              target + " with value " + str(missed_value))

        return missed_value

    def flush(self):
        self.current_size = 0
        self.cache_client.delete(self.KEY)
        print("Flushed cache")
