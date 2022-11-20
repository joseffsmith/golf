from datetime import datetime
from dotenv import load_dotenv
import os
from rq.queue import Queue
from rq_scheduler.utils import setup_loghandlers
import sys
from redis import Redis
from rq_scheduler import Scheduler
import logging

from app import scrape_and_save_comps, scrape_and_save_players
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASS = os.getenv('REDIS_PASS')


def create_connection(name):
    redis_conn = Redis(
        host=REDIS_HOST,
        port=16836,
        password=REDIS_PASS
    )
    scheduler = Scheduler(name, connection=redis_conn)

    return scheduler


def main():
    connection = Redis(host=REDIS_HOST, port=16836, password=REDIS_PASS)
    logger.info('Creating scheduler')
    scheduler = Scheduler('recurring', connection=connection, interval=5)
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job.description}')
        if queue_name == 'recurring' or queue_name == 'default':
            logger.info(f'cancelling job {job.description}')
            scheduler.cancel(job)

    scheduler.schedule(
        scheduled_time=datetime.now(),  # Time for first execution, in UTC timezone
        func=scrape_and_save_comps,                     # Function to be queued
        # Keyword arguments passed into function when executed
        # Time before the function is called again, in seconds
        interval=60*60*4,
        # Repeat this number of times (None means repeat forever)
        repeat=None,
    )
    scheduler.schedule(
        scheduled_time=datetime.now(),  # Time for first execution, in UTC timezone
        func=scrape_and_save_players,                     # Function to be queued
        # Keyword arguments passed into function when executed
        # Time before the function is called again, in seconds
        interval=60*60*24,
        # Repeat this number of times (None means repeat forever)
        repeat=None,
    )
    logger.info(len(list(scheduler.get_jobs())))

    scheduler.run()


if __name__ == '__main__':
    main()
