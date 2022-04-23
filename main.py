import redis
from flask import Flask, request
from cache_manager import CacheManager

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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

    if not r.get(req['channel']):
        return "This channel is currently not being cashed", 404

    stats = cache_manager.get_stats(req['message'], req['channel'])

    return {
        "response_code": 200,
        "isWeeb": stats['isWeeb'],
        "confidence": stats['confidence'],
        "number_of_weeb_terms": stats['number_of_weeb_terms']
    }


@app.route(BASE_ROUTE + "/join")
def join():
    req = request.json
    if 'channel' not in req:
        return "malformed request: you need to specify a channel to join", 400

    r.set('channels', r.get('channels') +
          req['channel'] + " " if r.get('channels') else req['channel'] + " ")
    cache_manager.init_channel_cache(req['channel'])

    return {"response_code": 200}
