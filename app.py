import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from dotenv import load_dotenv

from scraper import MasterScoreboard
from ms_parser import Parser
from asset import Library
app = Flask(__name__)
CORS(app)

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


@app.route('/scrape/', methods=['POST'])
def scrape():

    lib = Library(live=LIVE)
    parsed = lib.read('curr_comps')
    if LIVE:
        ms = MasterScoreboard()
        ms.auth()
        content = ms.list_comps()
        parsed = Parser().parse(content))

    lib.write('curr_comps', parsed)

    return jsonify(status = 'ok', comps = parsed)


def book_job(comp, time, partner_ids):

    # time in 16:00 format, 10 min incs
    # need correct number of partners

    ms=MasterScoreboard()
    ms.auth()
    parser=Parser()
    # assumes that the comp is live

    # all the time booking slots
    raw_slots_available=ms.choose_comp(comp['action'])

    form_data=parser.booking_page(raw_slots_available)
    block_id_pair={k: v for k, v in form_data.values() if v.startswith(time)}

    raw_partner_choosing=ms.choose_slot(block_id_pair, form_data)


if __name__ == '__main__':
    app.debug=True
    app.run(port = 5000)
