import os
import pytz
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta, timezone

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

USERNAME = os.getenv('SQUASH_USERNAME')
PASSWORD = os.getenv('SQUASH_PASSWORD')
BASE_URL = os.getenv('SQUASH_BASE_URL') 
MEMBERSHIP_USER_ID = os.getenv('SQUASH_MEMBERSHIP_USER_ID')

if not USERNAME or not PASSWORD or not BASE_URL or not MEMBERSHIP_USER_ID:
    raise Exception('SQUASH_USERNAME, SQUASH_PASSWORD, SQUASH_BASE_URL, SQUASH_MEMBERSHIP_USER_ID must be set in .env')

def login(password, session=None):
    if not session:
        session = requests.Session()
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    session.headers['User-Agent'] = user_agent
    session.headers['Accept'] = 'application/json'
    session.headers['Accept-Language'] = 'en-GB,en-US;q=0.9,en;q=0.8'
    session.headers['Content-Type'] = 'application/json'
    session.headers['Origin'] = 'https://bookings.better.org.uk'
    

    logger.info(f'Logging in...')
    loginUrl = f"{BASE_URL}auth/customer/login"
    resp = session.post(loginUrl, json={
        'username': USERNAME,
        'password': password,
    })
    resp.raise_for_status()
    logger.info(f'Logged in: {resp.status_code}')

    token = resp.json()['token']
    session.headers['Authorization'] = f"Bearer {token}"
    return session


def getSlots(date, startTime, endTime, session=None):
    if not session:
        session = login(PASSWORD)

    venue = "britannia-leisure-centre"

    slotsUrl = f"{BASE_URL}activities/venue/{venue}/activity/squash-court-40min/slots?date={date}&start_time={startTime}&end_time={endTime}"

    logger.info(f'Getting slots for {date}...')
    resp = session.get(slotsUrl)
    resp.raise_for_status()
    logger.info(f'Got slots: {resp.status_code}')

    json = resp.json()
    data = json['data']

    [myCourtId] = [d['id'] for d in data if d['location']['slug'] == "squash-court-3"]

    return myCourtId


def addToCart(courtId, session):
    bookUrl = f"{BASE_URL}activities/cart/add"

    logger.info(f'Adding to cart {courtId}...')
    resp = session.post(bookUrl, json={
        "items": [{
            "id":courtId,
            "type":"activity",
            "pricing_option_id":1071, # what to put here? assume fixed
            "apply_benefit":True,
            "activity_restriction_ids":[]
        }],
        "membership_user_id": MEMBERSHIP_USER_ID,
        "selected_user_id":None
    })
    resp.raise_for_status()
    logger.info(f'Added to cart: {resp.status_code}')

    
    return resp.json()['data']['id']

def checkout(session):
    logger.info(f'Checking out...')
    req = {"completed_waivers":[],"payments":[],"selected_user_id":None,"source":"activity-booking","terms":[1]}
    
    resp = session.post(f"{BASE_URL}checkout/complete", json=req)
    resp.raise_for_status()
    logger.info(f'Checked out: {resp.status_code}')
    return resp.json()

def bookTime(date, startTime = "07:20", endTime = "08:00"):
    session = login(PASSWORD)
    courtId = getSlots(date, startTime, endTime, session)
    addToCart(courtId, session)
    checkout(session)
    return

# at 10pm uk time can book 7 days in advance
def tryBookSquash():
    """
    Check the current time in London; if it's 10:00 PM exactly, run the real job logic.
    Otherwise, do nothing.
    """
    now_utc = datetime.now(timezone.utc)
    
    # Convert UTC → London time
    london_tz = pytz.timezone("Europe/London")
    now_london = now_utc.astimezone(london_tz)
    
    # If it’s exactly 10:00 PM in the UK, run the job
    if now_london.hour == 22:
        logger.info(f"[RUNNING] It's 10 PM in the UK. London time: {now_london}")
        bookTime((now_london + timedelta(days=7)).strftime("%Y-%m-%d"))

    else:
        logger.info(f"[SKIPPED] Not 10 PM in the UK. London time: {now_london}")

