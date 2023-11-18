import json
import logging
import os
from datetime import datetime, timedelta

import sentry_sdk
from dotenv import load_dotenv
from redis import Redis
from rq_scheduler import Scheduler

from IntelligentGolf import getCompsFromHtml, getHtmlCompPage, intLogin

# from app import scrape_and_save_comps, scrape_and_save_players

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASS = os.getenv('REDIS_PASS')

PASSWORD = os.getenv('INT_PASSWORD')


def get_redis_conn():
    return Redis(
        host=REDIS_HOST,
        port=16836,
        password=REDIS_PASS
    )


def create_connection(name):
    redis_conn = Redis(
        host=REDIS_HOST,
        port=16836,
        password=REDIS_PASS
    )

    scheduler = Scheduler(name, connection=redis_conn)

    return scheduler


def get_jobs_in_queue(name='test'):
    conn = create_connection(name)
    return [job for job in conn.get_jobs() if conn.get_queue_for_job(job).name == name]


def scrape_and_save_comps():
    session = intLogin(PASSWORD)
    content = getHtmlCompPage(session)
    comps = getCompsFromHtml(content)
    upsertComps(comps)
    logger.info('Saved comps')


def upsertComps(newComps):
    compDict = {f"comp:{obj['id']}": obj for obj in newComps}

    conn = get_redis_conn()

    dbCompDict = selectComps()

    if not dbComps:
        conn.mset(compDict)
        return

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
