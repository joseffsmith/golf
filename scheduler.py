from pytz import timezone
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
import six
from threading import Event
import pickle
import pymongo
import logging
import os
from dotenv import load_dotenv

from app import scrape_and_save_comps, scrape_and_save_players

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
load_dotenv()

#: constant indicating a scheduler's stopped state
STATE_STOPPED = 0
#: constant indicating a scheduler's running state (started and processing jobs)
STATE_RUNNING = 1
#: constant indicating a scheduler's paused state (started but not processing jobs)
STATE_PAUSED = 2

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASS = os.getenv('MONGO_PASS')


jobstores = {
    'default': MongoDBJobStore(
        client=pymongo.MongoClient(
            f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.jp1de.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        ), pickle_protocol=pickle.DEFAULT_PROTOCOL
    )
}
blocking_sched = BlockingScheduler(
    jobstores=jobstores, timezone=timezone('europe/london'))


class BackgroundAddScheduler(BlockingScheduler):

    def start(self, *args, **kwargs):
        if self._event is None or self._event.is_set():
            self._event = Event()

        if self.state != STATE_STOPPED:
            raise SchedulerAlreadyRunningError
        super(BlockingScheduler, self).start(*args, **kwargs)
        self._check_uwsgi()

        with self._jobstores_lock:
            # Create a default job store if nothing else is configured
            if 'default' not in self._jobstores:
                self.add_jobstore(self._create_default_jobstore(), 'default')

            # Start all the job stores
            for alias, store in six.iteritems(self._jobstores):
                store.start(self, alias)

            # Schedule all pending jobs
            for job, jobstore_alias, replace_existing in self._pending_jobs:
                self._real_add_job(job, jobstore_alias, replace_existing)
            del self._pending_jobs[:]


background_sched_add_jobs = BackgroundAddScheduler(
    jobstores=jobstores, timezone=timezone('europe/london')
)


def check_for_jobs():
    logger.debug(
        f"Jobs: {', '.join([j.name for j in blocking_sched.get_jobs()])}")


if __name__ == '__main__':
    blocking_sched.add_job(
        scrape_and_save_comps,
        'cron',
        replace_existing=True,
        id='scrape-comps',
        name='Scrape comps',
        hour='*',
        day='*',
        minute='40',
    )
    blocking_sched.add_job(
        scrape_and_save_players,
        'cron',
        replace_existing=True,
        id='scrape-players',
        name='Scrape players',
        hour='9',
        day='*',
        minute='1'
    )
    logger.debug('Starting scheduler')
    blocking_sched.start()
