import requests
import bs4
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime
load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

USERNAME = os.getenv('BRS_USERNAME')
PASSWORD = os.getenv('BRS_PASSWORD')
BASE_URL = os.getenv('BRS_BASE_URL')


def login(password, session=None):
    if not session:
        session = requests.Session()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    session.headers = {'User-Agent': user_agent}
    logger.info(f'Getting login page...')
    resp = session.get('https://members.brsgolf.com/thevalehotelspa/login')
    logger.info(f'Get login page: {resp.status_code}')
    b = bs4.BeautifulSoup(resp.content, features='html.parser')

    token = b.find(attrs={'id': 'login_form__token'}).get('value')
    logger.info(f'Logging in...')
    resp = session.post('https://members.brsgolf.com/thevalehotelspa/login', data={
        'login_form[username]': USERNAME,
        'login_form[password]': password,
        'login_form[login]': '',
        'login_form[_token]': token
    })
    if resp.status_code == 302 and resp.headers.get('location') == '/thevalehotelspa/login':
        logger.info(f'Failed to log in')
        raise Exception('Failed to login')
    logger.info(f'Logged in: {resp.status_code}')
    return session


def book_job(date, hour, minute, wait=None):
    book_time = f"{str(hour).zfill(2)}:{minute}"

    session = login(PASSWORD)
    if wait:
        logger.info(f'Checking for wait')
        while datetime.now() < wait:
            time.sleep(.01)
            logger.info(f'Waiting...')
            continue

    # wait until it's the time specified
    logger.info(f'Getting tee times for {date}...')
    resp = session.get(
        f'https://members.brsgolf.com/thevalehotelspa/tee-sheet/data/1/{date}')
    logger.info(f'Got tee times: {resp.status_code}')
    data = resp.json()

    times = data['times']

    booking = times[book_time]['tee_time']
    if not booking['bookable']:
        raise Exception('Cannot book, is booked')

    if booking['reservation']:
        raise Exception("Part booking, don't do it")

    logger.info(f'Booking: ${booking}')

    url = BASE_URL + booking['url']

    logger.info(f'Getting booking page...')
    resp = session.get(url)
    logger.info(f'Got booking page: {resp.status_code}')

    b = bs4.BeautifulSoup(resp.content, features='html.parser')

    token = b.find(attrs={'name': 'member_booking_form[token]'}).get('value')
    _token = b.find(attrs={'id': 'member_booking_form__token'}).get('value')

    logger.info(f'Booking...')
    resp = session.post(f"https://members.brsgolf.com/thevalehotelspa/bookings/store/1/{date.replace('/', '')}/{book_time.replace(':', '')}", data={
        "member_booking_form[token]": token,
        "member_booking_form[player_1]": 1102,
        "member_booking_form[player_2]": 1103,
        "member_booking_form[player_3]": 1104,
        "member_booking_form[player_4]": 1105,
        "member_booking_form[vendor-tx-code]": "",
        "member_booking_form[_token]": _token
    })
    logger.info(f'Booked: {resp.status_code}')
