import logging
import os
from datetime import datetime, timedelta

import pytz
import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, request
from flask_cors import CORS

import brs_app
import IntelligentGolf as int_app
from q import selectComps
from redis_helpers import create_connection

bst = pytz.timezone('Europe/London')

sentry_sdk.init(
    dsn="https://3ac09515060a422c8b0fd6c72336bc6a@o4504389848137728.ingest.sentry.io/4504389849841664",
    traces_sample_rate=1.0
)
flaskapp = Flask(__name__)
CORS(flaskapp)

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
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
    comps = selectComps()
    return jsonify(status='ok', comps=comps)


@flaskapp.route('/curr_players/', methods=['GET'])
def curr_players():
    return jsonify(status='ok', players=int_app.players)


@flaskapp.route('/int/login/', methods=['GET'])
def int_login():
    password = request.args.get('password')
    if not password:
        abort(401, 'No password')
    try:
        int_app.intLogin(password)
    except Exception as e:
        logger.exception(e)
        abort(400, 'Failed to login')

    return jsonify(status='ok')


@flaskapp.route('/int/curr_bookings/', methods=['GET'])
def int_curr_bookings():

    scheduler = create_connection('int')
    jobs = []
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job.description}')
        if queue_name == 'int':
            jobs.append(job)

    resp = jsonify(status='ok', jobs=[dict(
        description=job.description, kwargs=job.kwargs, id=job.id) for job in jobs])
    return resp


@flaskapp.route('/int/clear_bookings/', methods=['GET'])
def int_clear_bookings():

    scheduler = create_connection('int')
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job.description}')
        if queue_name == 'int':
            job.delete()

    resp = jsonify(status='ok')
    return resp


@flaskapp.route('/int/delete_booking/', methods=['POST'])
def int_delete_booking():

    json = request.json
    job_id = json['id']

    scheduler = create_connection('int')
    for job in scheduler.get_jobs():
        if job.id == job_id:
            logger.info(f'Deleting job: {job.id}')
            job.delete()

    resp = jsonify(status='ok')
    return resp


@flaskapp.route('/int/scheduler/booking/', methods=['POST'])
def int_schedule_booking():
    # {
    #     wait_until: timestamp
    #     hour: stirng
    #     minute:
    #     comp_id:
    #     partnerIds
    # }
    json = request.json
    comp_id = json['comp_id']
    partnerIds = json['partnerIds']
    date = json['wait_until']
    hour = str(json['hour']).zfill(2)
    minute = str(json['minute']).zfill(2)

    logger.info(f'wait_until: {date}, hour: {hour}, minute: {minute}')

    if date:
        parsed = datetime.fromtimestamp(float(date))
    else:
        logger.info("No date, using now")
        parsed = datetime.now()

    wait_until = bst.localize(parsed).astimezone(pytz.utc)
    next_run_time = wait_until - timedelta(seconds=10)

    logger.info('Booking job')
    now = pytz.UTC.localize(datetime.utcnow())
    if wait_until < now:
        logger.info('Comp likely open, scheduling for now')
        next_run_time = now + timedelta(seconds=30)
        wait_until = None

    logger.info(
        f'parsed_date: {parsed}, wait_until: {wait_until}, next_run_time: {next_run_time}')

    queue = create_connection('int')

    job = queue.enqueue_at(next_run_time, int_app.book_job,
                           comp_id=comp_id, partnerIds=partnerIds,
                           hour=hour, minute=minute, wait_until=wait_until)

    response = jsonify({'status': 'ok'})
    return response
# BRS


@flaskapp.route('/api/login/', methods=['GET'])
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


@flaskapp.route('/api/curr_bookings/', methods=['GET'])
def brs_curr_bookings():

    scheduler = create_connection('brs')
    jobs = []
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        if queue_name == 'brs':
            logger.info(f'queue: {queue_name} job: {job.description}')
            jobs.append(job)

    resp = jsonify(status='ok', jobs=[dict(
        description=job.description, kwargs=job.kwargs, id=job.id) for job in jobs])
    return resp


@flaskapp.route('/api/clear_bookings/', methods=['GET'])
def brs_clear_bookings():

    scheduler = create_connection('brs')
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        if queue_name == 'brs':
            logger.info(f'queue: {queue_name} job: {job.description}')
            job.delete()

    resp = jsonify(status='ok')
    return resp


@flaskapp.route('/api/delete_booking/', methods=['POST'])
def brs_delete_booking():

    json = request.json
    if not json:
        raise Exception('No json')
    
    job_id = json['id']

    scheduler = create_connection('brs')
    for job in scheduler.get_jobs():
        if job.id == job_id:
            logger.info(f'Deleting job: {job.id}')
            job.delete()

    resp = jsonify(status='ok')
    return resp


@flaskapp.route('/api/scheduler/booking/', methods=['POST'])
def brs_schedule_booking():
    json = request.json
    if not json:
        raise Exception('No json')
    
    password=json['password']
    if not password:
         abort(401, 'No password')
    try:
        brs_app.login(password)
    except Exception as e:
        logger.exception(e)
        abort(400, 'Failed to login')
    
    
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
