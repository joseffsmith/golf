from redis import Redis
from rq_scheduler import Scheduler

import os
from dotenv import load_dotenv
load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASS = os.getenv('REDIS_PASS')


def create_connection():
    redis_conn = Redis(
        host=REDIS_HOST,
        port='6379',
        password=REDIS_PASS
    )
    scheduler = Scheduler('golf', connection=redis_conn)

    return scheduler
