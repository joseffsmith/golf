import logging
import os

import sentry_sdk
from dotenv import load_dotenv
from redis import Redis
from rq_scheduler import Scheduler

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PASS = os.getenv('REDIS_PASS')

PASSWORD = os.getenv('INT_PASSWORD')

from better_app import tryBookSquash

def main():
    if not REDIS_HOST:
        raise Exception('REDIS_HOST must be set in .env')
    
    connection = Redis(host=REDIS_HOST, port=6379, password=REDIS_PASS)
    
    logger.info('Creating scheduler recurring')
    
    scheduler = Scheduler('recurring', connection=connection, interval=5)
    
    for job in scheduler.get_jobs():
        queue_name = scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job}')
        if queue_name == 'recurring' or queue_name == 'default' or queue_name == 'squash':
            logger.info(f'cancelling job {job.description}')  # type: ignore
            scheduler.cancel(job)
            
    logger.info('Creating scheduler squash')
    
    squash_scheduler = Scheduler('squash', connection=connection, interval=5)

    for job in squash_scheduler.get_jobs():
        queue_name = squash_scheduler.get_queue_for_job(job).name
        logger.info(f'queue: {queue_name} job: {job}')
        if queue_name == 'recurring' or queue_name == 'default' or queue_name == 'squash':
            logger.info(f'cancelling job {job.description}')  # type: ignore
            squash_scheduler.cancel(job)
            
    # schedule a job for every day at 10pm uk time to booktime
    squash_scheduler.cron(
        cron_string="0 * * * 1-5",      # Every hour on the hour, Monday–Friday
        func=tryBookSquash,       # The function defined above
        queue_name='squash'
    )

    # scheduler.schedule(
    #     # Time for first execution, in UTC timezone
    #     scheduled_time=datetime.now() + timedelta(minutes=5),
    #     func=scrape_and_save_comps,                     # Function to be queued
    #     # Keyword arguments passed into function when executed
    #     # Time before the function is called again, in seconds
    #     interval=60*60*4,
    #     # Repeat this number of times (None means repeat forever)
    #     repeat=None,
    # )
    
    # scheduler.schedule(
    #     scheduled_time=datetime.now(),  # Time for first execution, in UTC timezone
    #     func=scrape_and_save_players,                     # Function to be queued
    #     # Keyword arguments passed into function when executed
    #     # Time before the function is called again, in seconds
    #     interval=60*60*24,
    #     # Repeat this number of times (None means repeat forever)
    #     repeat=None,
    # )
    logger.info(len(list(scheduler.get_jobs())))
    logger.info('Running scheduler')
    scheduler.run()


if __name__ == '__main__':
    sentry_sdk.init(
        dsn="https://3ac09515060a422c8b0fd6c72336bc6a@o4504389848137728.ingest.sentry.io/4504389849841664",

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )
    main()
