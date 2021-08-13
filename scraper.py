from ms_parser import Parser
import requests
import os
import logging
from dotenv import load_dotenv
load_dotenv()

PASSWORD = os.getenv('MS_PASSWORD')
USERNAME = os.getenv('MS_USERNAME')
BASE_URL = os.getenv('BASE_URL')
COMP_URL = os.getenv('COMP_URL')
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MasterScoreboard:
    def __init__(self, username=None, password=None):
        self.session = requests.Session()
        self.username = username
        self.password = password
        if not self.username:
            logger.debug(
                'No username and password supplied, falling back to default')
            self.username = USERNAME
            self.password = PASSWORD

    def _get(self, url, headers={}):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
        headers.update({'User-Agent': user_agent})
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r

    def auth(self):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
        self.session.headers = {'User-Agent': user_agent}

        login_content = self._get(BASE_URL).content
        parser = Parser()

        param = parser.login_param(login_content)
        payload = {
            'ms_name': 'HMWebUser',
            'ms_password': self.password,
            'ms_uniqueid': self.username,
            'Params': param
        }

        r = self.session.post(BASE_URL, data=payload)
        r.raise_for_status()

        if not parser.check_login(r.content):
            raise Exception('Login failed')

    def list_comps(self):
        logger.debug(f'Comp url - {COMP_URL}')
        r = self.session.get(COMP_URL)
        r.raise_for_status()
        return r.content

    def select_comp(self, action):
        url = 'https://www.masterscoreboard.co.uk' + action

        payload = {
            'Book': "    Book    "
        }
        logger.debug(payload)

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
        logger.debug(payload)

        r = self.session.post(next_page, data=payload)
        r.raise_for_status()
        return r.content

    def select_partners(self, partner_ids, form_data):
        next_page = 'https://www.masterscoreboard.co.uk/bookings1/BookTime.php'

        payload = form_data
        # add in the players we can
        payload.update({
            f"Partner_{idx+1}": str(p_id.split(':')[0]) for idx, p_id in enumerate(partner_ids)
        })
        payload['Book'] = 'Book'
        logger.debug(payload)

        r = self.session.post(next_page, data=payload)
        r.raise_for_status()
        return r.content

    def get_partners(self):
        r = self._get(
            'https://www.masterscoreboard.co.uk/ClubIndex.php?CWID=5070')

        return r.content
