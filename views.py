from MasterScoreboard import MasterScoreboard
from datetime import datetime
import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import app
from Library import Library
from q import create_connection
flaskapp = Flask(__name__)
CORS(flaskapp)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
API_SECRET = os.getenv('API_SECRET')


@flaskapp.before_request
def before_request():
    if request.method == 'OPTIONS':
        return
    key = request.headers.get('X-MS-JS-API-KEY')
    if key != API_SECRET:
        abort(401)


@flaskapp.route('/test_pass/', methods=['POST'])
def test_pass():
    json = request.json
    username = json['username']
    password = json['password']
    ms = MasterScoreboard(username, password)
    try:
        ms.auth()
    except Exception:
        logger.exception('Incorrect password')
        abort(401)
    return jsonify(status='ok')


@flaskapp.route('/curr_comps/', methods=['GET'])
def curr_comps():
    lib = Library()
    comps = lib.read('curr_comps', default=[])
    return jsonify(status='ok', comps=comps)


@flaskapp.route('/curr_players/', methods=['GET'])
def curr_players():
    lib = Library()
    players = lib.read('players', default=[])
    return jsonify(status='ok', players=players)


@flaskapp.route('/curr_bookings/', methods=['GET'])
def curr_bookings():
    lib = Library()
    bookings = lib.read('bookings', default={})
    return jsonify(status='ok', bookings=list(bookings.values()))


@flaskapp.route('/scrape_comps/', methods=['POST'])
def scrape_and_save_comps():
    comps = app.scrape_and_save_comps()
    return jsonify(status='ok', comps=comps)


@flaskapp.route('/scrape_players/', methods=['POST'])
def scrape_and_save_players():
    players = app.scrape_and_save_players()
    return jsonify(status='ok', players=players)


@flaskapp.route('/scheduler/booking/', methods=['POST'])
def schedule_booking():
    json = request.json
    comp_id = json['comp_id']
    booking_time = json['booking_times']
    player_ids = json['player_ids']
    username = json['username']
    password = json['password']
    lib = Library()
    comps = {c['id']: c for c in lib.read('curr_comps')}
    if comp_id not in comps:
        abort(404, 'comp not found')

    comp = comps[comp_id]

    next_run_time = datetime.fromtimestamp(int(comp['book_from']))

    queue = create_connection()

    job = queue.enqueue_at(next_run_time, app.book_job,
                           comp, booking_time, player_ids, username, password)

    return jsonify(status='ok', bookings=[])


flaskapp.debug = True

if __name__ == '__main__':
    flaskapp.run(port=5000)
    logger.debug('Enqueuing jobs')
    scheduler = create_connection()

    scheduler.schedule(
        scheduled_time=datetime.now(), # Time for first execution, in UTC timezone
        func=scrape_and_save_comps,                     # Function to be queued
        kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=60*60,                   # Time before the function is called again, in seconds
        repeat=None,                     # Repeat this number of times (None means repeat forever)
    )
    scheduler.schedule(
        scheduled_time=datetime.now(), # Time for first execution, in UTC timezone
        func=scrape_and_save_players,                     # Function to be queued
        kwargs={'foo': 'bar'},         # Keyword arguments passed into function when executed
        interval=60*60*24,                   # Time before the function is called again, in seconds
        repeat=None,                     # Repeat this number of times (None means repeat forever)
    )

