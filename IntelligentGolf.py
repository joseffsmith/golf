import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Literal
from urllib.parse import parse_qs

import bs4
import dateutil.parser as dateutils
import pytz
import requests
from dotenv import load_dotenv

from redis_helpers import get_redis_conn

bst = pytz.timezone('Europe/London')

load_dotenv()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

INT_USERNAME = os.getenv('INT_USERNAME')
INT_PASSWORD = os.getenv('INT_PASSWORD')
INT_BASE_URL = os.getenv('INT_BASE_URL')
SIGNUP_URL = "https://llanishen.intelligentgolf.co.uk/online_signup_ajax_api.php"

rhys = "10671"
steffan = "10468"
tony = "10970"
jeff = "10846"

players = [{"name": "Rhys", "id": rhys}, {
    "name": "Steffan", "id": steffan}, {"name": "Tony B", "id": tony}, {"name": "Jeff", "id": jeff}]

URLS: Dict[Literal["knole", "llanishen"], str] = {
    "knole": "https://www.knoleparkgolfclub.co.uk/",
    "llanishen": "https://llanishen.intelligentgolf.co.uk/"
}

def getSystems():
    return URLS

def intLogin(username, password, courseName: str, session=None, debug=False):
    if not session:
        session = requests.Session()
        
    if courseName not in URLS:
        raise ValueError(f'Invalid url: {courseName}')
    
    url = URLS[courseName]
    
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
    session.headers['User-Agent'] = user_agent
    logger.info(f'Logging in...')

    logger.info(f'Logging in with {username}, {password}, {url}')

    try: 
        resp = session.post(url, data={
            "task": "login",
            "topmenu": 1,
            "memberid": username,
            "pin": password,
            "cachemid": 1,
            "Submit": "Login",
        },
        timeout=10
    )
    except Exception as e:
        logger.error(f'Error logging in: {e}')
        raise e
    
    if debug:
        print(resp.text)
        
    resp.raise_for_status()
    logger.info(f'Logged in: {resp.status_code}')
    return session


def getHtmlCompPage(session):
    logger.info(f'Getting comps...')
    resp = session.get(f'{INT_BASE_URL}competition2.php?time=future')
    resp.raise_for_status()
    return resp.content


def getHtmlCompPage_debug():
    with open('debug/comp_list', "r") as f:
        content = f.read()
    return content


def getCompsFromHtml(content):
    b = bs4.BeautifulSoup(content, features='html.parser')
    comp_table = b.find('div', attrs={'id': 'compsTableWrapper'})

    comps = []
    for t in comp_table.find_all('tr'):
        raw_signupDatetime = t.find(
            'div', attrs={'class': 'comp-signup-time-info'})

        if raw_signupDatetime and ('Signup Closes at' in raw_signupDatetime.get_text(
                strip=True)):

            date = raw_signupDatetime.get_text(
                strip=True).replace('Signup Closes at ', '').replace('on ', '')

            closeTime = dateutils.parse(date, dayfirst=True)
            close = (bst.localize(closeTime).astimezone(
                pytz.utc)).timestamp()
        else:
            close = None

        if raw_signupDatetime and ('Signup Opens at' in raw_signupDatetime.get_text(
                strip=True)):
            date = raw_signupDatetime.get_text(
                strip=True).replace('Signup Opens at ', '').replace('on ', '')

            signupDatetime = dateutils.parse(date, dayfirst=True)
            next_run_time = bst.localize(
                signupDatetime).astimezone(pytz.utc).timestamp()

        else:
            next_run_time = None

        comp = {
            'id': int(t.find('input', attrs={'name': 'compid'}).get('value')),
            'name': t.find('div', attrs={'class': 'comp-name'}).find('a').get_text(strip=True).replace('\n', ' '),
            'date': t.find('div', attrs={'class': 'comp-date'}).get_text(strip=True).replace("  ", " "),
            'signup-date': next_run_time,
            'signup-close': close
        }
        comps.append(comp)

    return comps


def getHtmlSlots_debug():
    with open('debug/2-slots-file', "r") as f:
        content = f.read()
    return content


def getHtmlSlots(session, compId):
    logger.info(f'Getting slots...')
    resp = session.get(SIGNUP_URL, params={
        "go": "signup",
        "compid": compId,
        "accept": "1",
        "team": "-1",
        "requestType": "ajax"
    })
    resp.raise_for_status()
    return resp.content


def getSlotsFromHTML(content, partners=1):
    c = json.loads(content)['html']
    b = bs4.BeautifulSoup(c, features='html.parser')
    rows = b.find_all('tr')
    times = {}

    for row in rows:

        if not row.find('a'):
            continue

        cells = [r.get_text(strip=True)
                 for r in row.find_all('td', {'class': 'slot'})]
        empties = [c for c in cells if not c]

        if (len(empties) < partners):
            continue

        time = row.find('td', {"class": 'startsheet_time'}
                        ).get_text(strip=True)
        r = row.find('a')
        times[time] = r.attrs['href']

    return times


def getHtmlPartnerSlots_debug():
    with open('debug/3-signUp', "r") as f:
        content = f.read()
    return content


def getHtmlPartnerSlots(session, href):
    resp = session.get(SIGNUP_URL + href)
    resp.raise_for_status()
    return resp.content


def getPartnerSlots(content):
    c = json.loads(content)['html']
    b = bs4.BeautifulSoup(c, features='html.parser')

    slots = [r.attrs['href'] for r in b.find('table').find_all('a')]
    sids = [parse_qs(a)['sid'][0] for a in slots]
    return sids


def bookPartner(session, compId, sid, partnerId):
    logger.info(f'Booking partner...')
    resp = session.get(
        SIGNUP_URL, params={
            'compid': compId,
            'go': 'signup',
            'partners': 1,
            'sid': sid,
            'partnerid': partnerId,
            'requestType': 'ajax'
        })
    resp.raise_for_status()


def searchPlayer(session, name):
    resp = session.post(SIGNUP_URL, params={
        "requestType": "ajax",
        "compid": "861"
    }, data={
        "partner": name,
        "sid": "223842",
        "compid": "861",
        "partners": "1"
    })
    resp.raise_for_status()
    return resp.content


def searchPlayer_debug():
    with open('debug/brow', "r") as f:
        content = f.read()
    return content


def getPlayerIdsFromContent(content):
    c = json.loads(content)['html']
    b = bs4.BeautifulSoup(c, features='html.parser')
    print(b.prettify())


def book_job(comp_id, partnerIds, hour, minute, wait_until):
    book_time = f"{str(hour).zfill(2)}:{minute}"

    session = intLogin(INT_USERNAME, INT_PASSWORD, 'llanishen')
    if wait_until:
        logger.info(f'Checking for wait')
        while pytz.UTC.localize(datetime.utcnow()) < wait_until:
            time.sleep(.01)
            logger.info(f'Waiting...')
            continue

    logger.info(f'Getting tee times for {comp_id}...')
    content = getHtmlSlots(session, comp_id)
    slots = getSlotsFromHTML(content, len(partnerIds))
    logger.info(f'Got tee times: ${len(slots)}')

    href = slots[book_time]
    content = getHtmlPartnerSlots(session, href)
    sids = getPartnerSlots(content)

    for idx, partnerId in enumerate(partnerIds):
        logger.info('Booking partner' + partnerId)
        bookPartner(session, comp_id, sids[idx], partnerId)


# if __name__ == "__main__":
#     content = get_comp_page_debug()
#     get_comps_from_page(content)


def scrape_and_save_comps():
    urls = getSystems()
    session = intLogin(INT_USERNAME, INT_PASSWORD, 'llanishen')
    content = getHtmlCompPage(session)
    comps = getCompsFromHtml(content)
    upsertComps(comps)
    logger.info('Saved comps')


def upsertComps(newComps):
    compDict = {f"comp:{obj['id']}": obj for obj in newComps}

    conn = get_redis_conn()

    dbCompDict = selectComps()

    for key, newComp in compDict.items():
        if key not in dbCompDict:
            conn.set(key, json.dumps(newComp))
            continue

        dbComp = dbCompDict[key]
        if not newComp.get('signup-date'):
            dbComp['signup-date'] = newComp['signup-date']
        if not newComp.get('signup-close'):
            dbComp['signup-close'] = newComp['signup-close']
        if not newComp.get('name'):
            dbComp['name'] = newComp['name']

        conn.set(key, json.dumps(dbComp))


def selectComps():
    conn = get_redis_conn()

    keys = conn.keys('comp:*')
    dbComps = [json.loads(val) for val in conn.mget(keys) if val]
    dbCompDict = {f"comp:{obj['id']}": obj for obj in dbComps}
    return dbCompDict
