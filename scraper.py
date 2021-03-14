import requests
import os
from dotenv import load_dotenv
from requests.api import head
load_dotenv()

PASSWORD = os.getenv('MS_PASSWORD')
USERNAME = os.getenv('MS_USERNAME')
BASE_URL = os.getenv('BASE_URL')
COMP_URL = os.getenv('COMP_URL')


class MasterScoreboard:
    def __init__(self):
        self.session = requests.Session()

    def _get(self, url, headers={}):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
        headers.update({'User-Agent': user_agent})
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r

    def auth(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'

        self.session.headers = {'User-Agent': user_agent}

        payload = {
            'ms_name': 'HMWebUser',
            'ms_password': PASSWORD,
            'ms_uniqueid': USERNAME
        }

        r = self.session.post(BASE_URL, data=payload)
        if (len(self.session.cookies) != 2):
            raise Exception('Not enough cookies in the jar auth failed')
        r.raise_for_status()

    def list_comps(self):
        return self.session.get(COMP_URL).content

    def select_comp(self, action):
        url = 'https://www.masterscoreboard.co.uk' + action

        payload = {
            'Book': "    Book    "
        }
        r = self.session.post(url, data=payload)
        r.raise_for_status()
        return r.content

    def select_slot(self, block_id_pair, form_data):
        next_page = 'https://www.masterscoreboard.co.uk/bookings1/BookSelectPartners.php?CWID=5070'

        payload = {
            k: v for k, v in form_data.items() if k.startswith('BlockNumAvailable')
        }
        payload.update(block_id_pair)
        payload['Params'] = form_data['Params']
        payload['MaxID'] = form_data['MaxID']

        r = self.session.post(next_page, data=payload)
        r.raise_for_status()
        return r.content

    def select_partners(self, partner_ids, form_data):
        next_page = 'https://www.masterscoreboard.co.uk/bookings1/BookTime.php'

        payload = form_data
        # add in the players we can
        payload.update({
            f"Partner_{idx+1}": str(p_id) for idx, p_id in enumerate(partner_ids)
        })
        payload['Book'] = 'Book'

        r = self.session.post(next_page, data=payload)
        r.raise_for_status()
        return r.content

    def get_partners(self):
        r = self._get(
            'https://www.masterscoreboard.co.uk/ClubIndex.php?CWID=5070')

        return r.content
