import json
from flask import Flask, request, jsonify

from scraper import MasterScoreboard
from ms_parser import Parser
from asset import Library
app = Flask(__name__)

LIVE=False

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
    app.run()