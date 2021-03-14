import os
from s3_job_store import S3JobStore
from flask import Flask, request, jsonify, abort
from flask_apscheduler import APScheduler
from flask_cors import CORS
from dotenv import load_dotenv
import logging

from scraper import MasterScoreboard
from ms_parser import Parser
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
    key = request.headers.get('X_MS_JS_API_KEY')
    if key != API_SECRET:
        abort(401)


@app.route('/comps/', methods=['GET'])
def index():
    lib = Library(live=LIVE)
    comps = lib.read('curr_comps')
    return jsonify(status='ok', comps=comps)


@app.route('/scrape_comps/', methods=['POST'])
def scrape():

    lib = Library(live=LIVE)
    parsed = lib.read('curr_comps')
    if LIVE:
        ms = MasterScoreboard()
        ms.auth()
        content = ms.list_comps()
        parsed = Parser().parse(content)

    lib.write('curr_comps', parsed)

    return jsonify(status='ok', comps=parsed)


@app.route('/scheduler/scrape_comps/', methods=['GET'])
def scrape_scheduler():
    from datetime import datetime, timedelta
    now = datetime.now() + timedelta(minutes=1)
    scheduler.add_job('123', scrape_players,
                      next_run_time=now, replace_existing=True)
    return jsonify(status='ok')


def scrape_players():
    logger.debug(f'Scraping players, live={LIVE}')
    lib = Library(live=LIVE)
    parser = Parser()
    parsed_players = lib.read('players')
    if LIVE:
        ms = MasterScoreboard()
        content = ms.get_partners()
        parsed_players = parser.partner_ids(content)
    print('hello')
    lib.write('players', parsed_players)


@app.route('/scrape_players/', methods=['POST'])
def scrape_players_req():

    lib = Library(live=LIVE)
    parser = Parser()
    parsed_players = lib.read('players')
    if LIVE:
        ms = MasterScoreboard()
        content = ms.get_partners()
        parsed_players = parser.partner_ids(content)

    lib.write('players', parsed_players)
    return jsonify(status='ok', players=parsed_players)


class Config(object):
    JOBS = []

    SCHEDULER_JOBSTORES = {
        'default': S3JobStore(live=LIVE)
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

if __name__ == '__main__':
    app.run(port=5000)
