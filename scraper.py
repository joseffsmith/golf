import requests
import os
from dotenv import load_dotenv
load_dotenv()

PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('USERNAME')
BASE_URL = os.getenv('BASE_URL')
COMP_URL = os.getenv('COMP_URL')


class MasterScoreboard:
    def __init__(self):
        self.session = requests.Session()
        

    def auth(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'

        self.session.headers = {'User-Agent': user_agent}

        payload = {
            'ms_name': 'HMWebUser',
            'ms_password': PASSWORD,
            'ms_uniqueid': USERNAME,
        }

        r = self.session.post(BASE_URL, data=payload)
        r.raise_for_status()

    def list_comps(self):
        comps_url = COMP_URL


