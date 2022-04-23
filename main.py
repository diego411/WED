from flask import Flask, flash, request, redirect
from werkzeug.utils import secure_filename
import os
from model import query_model
import redis
from cache_manager import CacheManager


cache_manager = CacheManager()
cache_manager.init_cache()

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

UPLOAD_FOLDER = "D:\Projects\WED\emotes"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_ROUTE = "/api/v1"


@app.route(BASE_ROUTE + "/")
def hello_world():
    return "<h1>Hello, World!</h1>"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route(BASE_ROUTE + "/hwis")
def hwis():
    req = request.json
    if 'channel' not in req or 'message' not in req:
        return "malformed request", 400

    if not r.get(req['channel']):
        return {"error": "This channel is currently not being cashed."}

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


@app.route("/upload", methods=['POST'])
def upload():
    print("upload")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            score = query_model.get_weeb_score(path)
            print(score)
            os.remove(path)
            return {"response_code": 200, "score": int(score)}
