import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from scraper import MasterScoreboard
from ms_parser import Parser
from asset import Library
app = Flask(__name__)
CORS(app)

from dotenv import load_dotenv
load_dotenv()
API_SECRET = os.getenv('API_SECRET')
LIVE=os.getenv('LIVE')


@app.before_request
def before_request():
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

    content = None
    if LIVE:
        ms = MasterScoreboard()
        ms.auth()
        content = ms.list_comps()

    parsed = Parser(content=content).parse()

    lib=Library(live=LIVE)
    lib.write('curr_comps', parsed)
    
    return jsonify(status='ok', comps=parsed)

if __name__ == '__main__':
    app.run(port=5000)