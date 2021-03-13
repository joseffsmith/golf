from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore



job_stores = {
    'default': MemoryJobStore
}

sched = BlockingScheduler()
# sched.add_job.


@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')


sched.start()

referrer = 'Referer: https://www.masterscoreboard.co.uk/bookings1/Book.php?CWID=5070&intCompID=160668'
