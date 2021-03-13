import requests


PASSWORD = ''
USERNAME = ''
BASE_URL = 'https://www.masterscoreboard.co.uk/ClubIndex.php?CWID=5070'
COMP_URL = 'https://www.masterscoreboard.co.uk/ListOfFutureCompetitions.php?CWID=5070'
print('here')


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

        self.session.post(BASE_URL, data=payload)
        print('authed')

    def list_comps(self):
        comps_url = COMP_URL


