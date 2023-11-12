from MasterScoreboard import MasterScoreboard
from datetime import datetime, timedelta
import os
from flask import Flask, Response, request, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import app
import brs_app
from Library import Library
from q import create_connection
import sentry_sdk
import pytz
bst = pytz.timezone('Europe/London')

sentry_sdk.init(
    dsn="https://3ac09515060a422c8b0fd6c72336bc6a@o4504389848137728.ingest.sentry.io/4504389849841664",
    traces_sample_rate=1.0
)
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
    # lib = Library()
    # bookings = lib.read('bookings', default={})
    # return jsonify(status='ok', bookings=list(bookings.values()))
    db = DB()
    db_comps = db.client.golf.comps
    print(db_comps)
    return jsonify(status='ok')


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

    wait_until = datetime.fromtimestamp(int(comp['book_from']))
    # snap to 10pm
    next_run_time = wait_until - timedelta(seconds=10)

    logger.info('Booking job')
    if wait_until < datetime.now():
        logger.info('Comp likely open, scheduling for now')
        next_run_time = datetime.now() + timedelta(seconds=30)
        wait_until = None

    queue = create_connection('golf')

    job = queue.enqueue_at(next_run_time, app.book_job,
                           comp, booking_time, player_ids, username, password, wait_until)

    return jsonify(status='ok', bookings=[])


# BRS


@flaskapp.route('/brs/login/', methods=['GET'])
def brs_login():
    password = request.args.get('password')
    if not password:
        abort(401, 'No password')
    try:
        brs_app.login(password)
    except Exception as e:
        logger.exception(e)
        abort(400, 'Failed to login')

    return jsonify(status='ok')


@flaskapp.route('/brs/curr_bookings/', methods=['GET'])
def brs_curr_bookings():

    scheduler = create_connection('brs')
    jobs = []
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job.description}')
        if queue_name == 'brs':
            jobs.append(job)

    resp = jsonify(status='ok', jobs=[dict(
        description=job.description, kwargs=job.kwargs, id=job.id) for job in jobs])
    return resp


@flaskapp.route('/brs/clear_bookings/', methods=['GET'])
def brs_clear_bookings():

    scheduler = create_connection('brs')
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job.description}')
        if queue_name == 'brs':
            job.delete()

    resp = jsonify(status='ok')
    return resp


@flaskapp.route('/brs/delete_booking/', methods=['POST'])
def brs_delete_booking():

    json = request.json
    job_id = json['id']

    scheduler = create_connection('brs')
    for job in scheduler.get_jobs():
        if job.id == job_id:
            logger.info(f'Deleting job: {job.id}')
            job.delete()

    resp = jsonify(status='ok')
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
    wait_until = bst.localize(wait_until).astimezone(pytz.utc)
    next_run_time = wait_until - timedelta(seconds=10)

    logger.info('Booking job')
    now = pytz.UTC.localize(datetime.utcnow())
    if wait_until < now:
        logger.info('Comp likely open, scheduling for now')
        next_run_time = now + timedelta(seconds=30)
        wait_until = None

    logger.info(
        f'parsed_date: {parsed_date}, wait_until: {wait_until}, next_run_time: {next_run_time}')

    queue = create_connection('brs')

    job = queue.enqueue_at(next_run_time, brs_app.book_job,
                           date=date, hour=hour, minute=minute, wait_until=wait_until)

    response = jsonify({'status': 'ok'})
    return response


flaskapp.debug = True

if __name__ == '__main__':
    flaskapp.run(port=5000)
    logger.info('Enqueuing jobs')
