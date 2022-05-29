import redis
import os
from flask import Flask, request
from cache_manager import CacheManager
from controllers import config

from dotenv import load_dotenv

load_dotenv()

redis_host = os.environ.get("REDIS_HOST")
redis_port = os.environ.get("REDIS_PORT")

r = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

config = config.pull_config()

if config:
    r.delete("channels")
    for channel in config["channels"]:
        r.sadd("channels", channel)

cache_manager = CacheManager(r)
cache_manager.init_cache()

app = Flask(__name__)

BASE_ROUTE = "/api/v1"


@app.route("/")
def index():
    return "NaM"


@app.route(BASE_ROUTE + "/hwis")
def hwis():
    req = request.json
    if 'channel' not in req or 'message' not in req:
        return "malformed request", 400

    if not req['channel'] in r.smembers("channels"):
        return "This channel is currently not being cashed", 404

    stats = cache_manager.get_stats(req['message'], req['channel'])

    return {
        "response_code": 200,
        "is_weeb": stats['is_weeb'],
        "confidence": stats['confidence'],
        "number_of_weeb_terms": stats['number_of_weeb_terms']
    }


@app.route(BASE_ROUTE + "/channels", methods=["GET", "POST"])
def join():
    if request.method == "GET":
        channels = []
        for channel in r.smembers("channels"):
            channels.append(channel)
        return {
            "response_code": 200,
            "channels": channels
        }

    if request.method == "POST":
        req = request.json
        if 'channel' not in req:
            return "malformed request: you need to specify a channel to join", 400

        r.sadd('channels', req['channel'])
        cache_manager.init_channel_cache(req['channel'])

        return {"response_code": 200}


@app.route(BASE_ROUTE + "/whitelist", methods=["GET", "POST"])
def whitelist():
    if request.method == "GET":
        whitelist = []
        print(r.smembers("whitelist"))
        for term in r.smembers("whitelist"):
            whitelist.append(term)
        return {
            "response_code": 200,
            "whitelist": whitelist
        }

    if request.method == "POST":
        req = request.json
        if 'term' not in req:
            return "malformed request: you need to specify the term to whitelist", 400

        r.sadd("whitelist", req["term"])

        return {"response_code": 200}
