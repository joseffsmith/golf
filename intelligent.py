import requests
import bs4
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime
import sentry_sdk
load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

USERNAME = os.getenv('INT_USERNAME')
PASSWORD = os.getenv('INT_PASSWORD')
BASE_URL = os.getenv('INT_BASE_URL')


def login(password, session=None):
    if not session:
        session = requests.Session()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    session.headers = {'User-Agent': user_agent}
    logger.info(f'Getting login page...')

    formInfo = {
        "task": "login",
        "topmenu": "1",
        "memberid": USERNAME,
        "pin": password,
        "Submit": "Login",
    }

    resp = session.post(BASE_URL, data=formInfo)
    resp.raise_for_status()
    if (len(resp.history) == 0):
        raise Exception('No redirect so likely failed login')
    return session
