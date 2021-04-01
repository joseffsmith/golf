from scheduler import background_sched_add_jobs
import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import logging

import app as js
from asset import Library
app = Flask(__name__)
CORS(app)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
API_SECRET = os.getenv('API_SECRET')
LIVE = os.getenv('LIVE')


@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        return
    key = request.headers.get('X-MS-JS-API-KEY')
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
    bookings = lib.read('bookings', default={})
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
    background_sched_add_jobs.start()
    background_sched_add_jobs.add_job(
        js.book_job,
        id=comp_id,
        args=[comp, booking_time, player_ids],
        replace_existing=True,
        next_run_time=datetime.fromtimestamp(
            int(comp['book_from'])) if comp['book_from'] else datetime.now(),
        misfire_grace_time=None
    )
    background_sched_add_jobs.shutdown()

    bookings = lib.read('bookings', default={})
    bookings[comp_id] = {
        'comp': comp,
        'booking_time': booking_time,
        'player_ids': player_ids,
        'booked': False
    }
    lib.write('bookings', bookings)
    return jsonify(status='ok', bookings=bookings)


app.debug = True

if __name__ == '__main__':
    app.run(port=5000)
