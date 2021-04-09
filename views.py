from scheduler import background_sched_add_jobs
import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
import dateutil
import logging
import app
from asset import Library
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
    return jsonify(status='ok', bookings=bookings)


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
    lib = Library()
    comps = {c['id']: c for c in lib.read('curr_comps')}
    if comp_id not in comps:
        abort(404, 'comp not found')

    comp = comps[comp_id]
    background_sched_add_jobs.start()
    background_sched_add_jobs.add_job(
        app.book_job,
        id=comp_id,
        args=[comp, booking_time, player_ids],
        replace_existing=True,
        next_run_time=dateutil.parser.parse('8pm 9th april 2021'),
        # int(comp['book_from'])) if comp['book_from'] else datetime.now(),
        misfire_grace_time=None,
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


flaskapp.debug = True

if __name__ == '__main__':
    flaskapp.run(port=5000)
