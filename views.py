from MasterScoreboard import MasterScoreboard
from datetime import datetime, timedelta
import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import app
import brs_app
from Library import Library
from q import create_connection
flaskapp = Flask(__name__)
CORS(flaskapp)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
API_SECRET = os.getenv('API_SECRET')
API_KEY = os.getenv('API_KEY')


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


@flaskapp.route('/brs/login/', methods=['GET'])
def brs_login():
    password = request.args.get('password')
    if not password:
        abort(401, 'No password')
    try:
        brs_app.login(password)
    except Exception as e:
        print(e)
        abort(400, 'Failed to login')

    return jsonify(status='ok')


@flaskapp.route('/brs/curr_bookings/', methods=['GET'])
def brs_curr_bookings():

    queue = create_connection()

    # resp = jsonify(status='ok', jobs=[queue.fetch_job(
    #     j).to_dict()['description'] for j in queue.scheduled_job_registry.get_job_ids()])
    # resp.headers.add('Access-Control-Allow-Origin', '*')
    # return resp
    return jsonify(status='ok', jobs=[])


@flaskapp.route('/brs/clear_bookings/', methods=['GET'])
def brs_clear_bookings():

    resp = jsonify(status='ok')
    resp.headers.add('Access-Control-Allow-Origin', '*')
    return resp


@flaskapp.route('/brs/scheduler/booking/', methods=['POST'])
def brs_schedule_booking():
    json = request.json
    date = json['date']
    hour = str(json['hour']).zfill(2)
    minute = str(json['minute']).zfill(2)
    parsed_date = datetime.strptime(date, '%Y/%m/%d')

    # snap to 10pm
    wait_until = parsed_date.replace(hour=22) - timedelta(days=7)
    next_run_time = wait_until - timedelta(seconds=10)

    logger.debug('Booking job')

    if wait_until < datetime.now():
        logger.debug('Comp likely open, scheduling for now')
        next_run_time = datetime.now() + timedelta(seconds=30)
        wait_until = None

    queue = create_connection()

    job = queue.enqueue_at(next_run_time, brs_app.book_job,
                           date, hour, minute, wait_until)

    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


flaskapp.debug = True

if __name__ == '__main__':
    flaskapp.run(port=5000)
    logger.debug('Enqueuing jobs')
    scheduler = create_connection()

    scheduler.schedule(
        scheduled_time=datetime.now(),  # Time for first execution, in UTC timezone
        func=scrape_and_save_comps,                     # Function to be queued
        # Keyword arguments passed into function when executed
        interval=60*60,                   # Time before the function is called again, in seconds
        # Repeat this number of times (None means repeat forever)
        repeat=None,
    )
    scheduler.schedule(
        scheduled_time=datetime.now(),  # Time for first execution, in UTC timezone
        func=scrape_and_save_players,                     # Function to be queued
        # Keyword arguments passed into function when executed
        # Time before the function is called again, in seconds
        interval=60*60*24,
        # Repeat this number of times (None means repeat forever)
        repeat=None,
    )
