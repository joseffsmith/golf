import os
from flask import Flask, request, jsonify, abort
from flask_apscheduler import APScheduler
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import pymongo
import logging

import app as js
from apscheduler.jobstores.mongodb import MongoDBJobStore
from asset import Library
app = Flask(__name__)
CORS(app)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
API_SECRET = os.getenv('API_SECRET')
LIVE = os.getenv('LIVE')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')


@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        return
    key = request.headers.get('X_MS_JS_API_KEY')
    if key != API_SECRET:
        abort(401)


@app.route('/curr_comps/', methods=['GET'])
def curr_comps():
    lib = Library(live=LIVE)
    comps = lib.read('curr_comps', default=[])
    return jsonify(status='ok', comps=comps)


@app.route('/curr_players/', methods=['GET'])
def curr_players():
    lib = Library(live=LIVE)
    players = lib.read('players', default=[])
    return jsonify(status='ok', players=players)


@app.route('/curr_bookings/', methods=['GET'])
def curr_bookings():
    lib = Library(live=LIVE)
    bookings = lib.read('bookings', default=[])
    return jsonify(status='ok', bookings=bookings)


@app.route('/scrape_comps/', methods=['POST'])
def scrape_and_save_comps():
    comps = js.scrape_and_save_comps()
    return jsonify(status='ok', comps=comps)


@app.route('/scrape_players/', methods=['POST'])
def scrape_and_save_players():
    players = js.scrape_and_save_players()
    return jsonify(status='ok', players=players)


@app.route('/scheduler/booking/', methods=['POST'])
def schedule_booking():
    json = request.json
    comp_id = json['comp_id']
    booking_time = json['booking_times']
    player_ids = json['player_ids']
    lib = Library(live=LIVE)
    comps = {c['id']: c for c in lib.read('curr_comps')}
    if comp_id not in comps:
        abort(404, 'comp not found')

    comp = comps[comp_id]

    scheduler.add_job(
        comp_id,
        js.book_job,
        args=[comp, booking_time, player_ids],
        replace_existing=True,
        next_run_time=datetime.fromtimestamp(
            int(comp['book_from'])) if comp['book_from'] else datetime.now(),
        misfire_grace_time=None
    )

    bookings = lib.read('bookings', default=[])
    bookings.append({
        'comp': comp,
        'booking_time': booking_time,
        'player_ids': player_ids,
        'booked': False
    })
    lib.write('bookings', bookings)
    return jsonify(status='ok')


class Config(object):
    JOBS = []

    SCHEDULER_JOBSTORES = {
        'mongo': MongoDBJobStore(client=pymongo.MongoClient(f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.jp1de.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"))
    }

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    SCHEDULER_API_ENABLED = False


app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
app.debug = True


@scheduler.task('cron', id='scrape-comps', hour='9', day='*')
def scrape_scheduled_comps():
    js.scrape_and_save_comps()


if __name__ == '__main__':
    app.run(port=5000)
