import json
import logging
import os
import time
from datetime import datetime, timedelta

import bs4
import dateutil.parser as dateutils
import pytz
import requests
import sentry_sdk
from dotenv import load_dotenv

from q import get_redis_conn

bst = pytz.timezone('Europe/London')

load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

USERNAME = os.getenv('INT_USERNAME')
PASSWORD = os.getenv('INT_PASSWORD')
BASE_URL = os.getenv('INT_BASE_URL')


def int_login(password=None, session=None):
    if not session:
        session = requests.Session()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    session.headers = {'User-Agent': user_agent}
    logger.info(f'Logging in...')

    resp = session.post(BASE_URL, data={
        "task": "login",
        "topmenu": 1,
        "memberid": USERNAME,
        "pin": PASSWORD,
        "cachemid": 1,
        "Submit": "Login",
    })
    resp.raise_for_status()
    logger.info(f'Logged in: {resp.status_code}')
    return session


def get_comp_page():
    session = int_login()
    logger.info(f'Getting comps...')
    resp = session.get(f'{BASE_URL}competition2.php?time=future')
    resp.raise_for_status()
    return resp.content


def get_comp_page_debug():
    with open('debug/comp_list', "r") as f:
        content = f.read()
    return content


def get_comps_from_page(content):
    b = bs4.BeautifulSoup(content, features='html.parser')
    comp_table = b.find('div', attrs={'id': 'compsTableWrapper'})

    comps = []
    for t in comp_table.find_all('tr'):
        raw_signupDatetime = t.find(
            'div', attrs={'class': 'comp-signup-time-info'})
        if raw_signupDatetime:

            signupDatetime = dateutils.parse(raw_signupDatetime.get_text(
                strip=True).replace('Signup Opens at ', '').replace('on ', ''))

            wait_until = bst.localize(signupDatetime).astimezone(pytz.utc)
            next_run_time = (wait_until - timedelta(seconds=10)).timestamp()

        else:
            next_run_time = None
        comp = {
            'id': int(t.find('input', attrs={'name': 'compid'}).get('value')),
            'name': t.find('div', attrs={'class': 'comp-name'}).find('a').get_text(strip=True).replace('\n', ' '),
            'date': t.find('div', attrs={'class': 'comp-date'}).get_text(strip=True),
            'signup-date': next_run_time,
        }
        comps.append(comp)

    return comps


# def test():
    # conn = get_redis_conn()
    # print(json.loads(conn.get('joe_test')))

# def book_job(date, hour, minute, wait_until):
#     book_time = f"{str(hour).zfill(2)}:{minute}"

#     session = login(PASSWORD)
#     if wait_until:
#         logger.info(f'Checking for wait')
#         while pytz.UTC.localize(datetime.utcnow()) < wait_until:
#             time.sleep(.01)
#             logger.info(f'Waiting...')
#             continue

#     # wait until it's the time specified
#     logger.info(f'Getting tee times for {date}...')
#     resp = session.get(
#         f'https://members.brsgolf.com/thevalehotelspa/tee-sheet/data/1/{date}')
#     logger.info(f'Got tee times: {resp.status_code}')
#     data = resp.json()

#     times = data['times']

#     booking = times[book_time]['tee_time']
#     if not booking['bookable']:
#         raise Exception('Cannot book, is booked')

#     if booking['reservation']:
#         raise Exception("Part booking, don't do it")

#     logger.info(f'Booking: ${booking}')

#     url = BASE_URL + booking['url']

#     logger.info(f'Getting booking page...')
#     resp = session.get(url)
#     logger.info(f'Got booking page: {resp.status_code}')

#     b = bs4.BeautifulSoup(resp.content, features='html.parser')

#     token = b.find(attrs={'name': 'member_booking_form[token]'}).get('value')
#     _token = b.find(attrs={'id': 'member_booking_form__token'}).get('value')

#     logger.info(f'Booking...')
#     resp = session.post(f"https://members.brsgolf.com/thevalehotelspa/bookings/store/1/{date.replace('/', '')}/{book_time.replace(':', '')}", data={
#         "member_booking_form[token]": token,
#         "member_booking_form[player_1]": 1102,
#         "member_booking_form[player_2]": 1103,
#         "member_booking_form[player_3]": 1104,
#         "member_booking_form[player_4]": 1105,
#         "member_booking_form[vendor-tx-code]": "",
#         "member_booking_form[_token]": _token
#     })
#     logger.info(f'Booked: {resp.status_code}')
#     sentry_sdk.capture_message('Booked')

if __name__ == "__main__":
    content = get_comp_page_debug()
    get_comps_from_page(content)
