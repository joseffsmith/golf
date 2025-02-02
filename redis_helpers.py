import logging
import os

from dotenv import load_dotenv
from redis import Redis
from rq_scheduler import Scheduler


logger = logging.getLogger(__name__)
load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASS = os.getenv('REDIS_PASS')

INT_PASSWORD = os.getenv('INT_PASSWORD')

def get_redis_conn():
    if not REDIS_HOST:
        raise Exception('REDIS_HOST and REDIS_PASS must be set in .env')
    return Redis(
        host=REDIS_HOST,
        port=6379,
        password=REDIS_PASS
    )


def create_connection(name):
    if not REDIS_HOST:
        raise Exception('REDIS_HOST and REDIS_PASS must be set in .env')
    redis_conn = Redis(
        host=REDIS_HOST,
        port=6379,
        password=REDIS_PASS
    )

    scheduler = Scheduler(name, connection=redis_conn)

    return scheduler

def get_jobs_in_queue(name='test'):
    conn = create_connection(name)
    return [job for job in conn.get_jobs() if conn.get_queue_for_job(job).name == name]

