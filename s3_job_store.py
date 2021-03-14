from __future__ import absolute_import

from apscheduler.jobstores.base import BaseJobStore, ConflictingIdError, JobLookupError
from apscheduler.util import datetime_to_utc_timestamp
from apscheduler.job import Job
from apscheduler.triggers.date import DateTrigger
from asset import Library
from datetime import datetime

import pytz

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class S3JobStore(BaseJobStore):
    """
    Stores jobs in a file in s3.

    Plugin alias: ``memory``
    """

    def __init__(self, live=False):
        super(S3JobStore, self).__init__()
        self.live = live
        # list of (job, timestamp), sorted by next_run_time and job id (ascending)

    def _reconstitute_job(self, job_state):
        job = Job.__new__(Job)
        job_state['next_run_time'] = datetime.fromtimestamp(
            float(job_state['next_run_time']), tz=pytz.UTC)
        job_state['trigger'] = DateTrigger(run_date=datetime.fromtimestamp(
            float(job_state['trigger']), tz=pytz.UTC))
        job.__setstate__(job_state)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        logger.debug(job.next_run_time)
        return job

    @property
    def _jobs(self):
        lib = Library(live=self.live)
        jobs = [self._reconstitute_job(j)
                for j in lib.read('jobs')]
        return sorted([(j, j.next_run_time.timestamp()) for j in jobs], key=lambda x: (x[0].next_run_time, x[0].id))

    @_jobs.setter
    def _jobs(self, jobs):
        lib = Library(live=self.live)
        logger.debug([job.__getstate__() for job, timestamp in jobs])
        state = [job.__getstate__() for job, timestamp in jobs]
        for s in state:
            s['next_run_time'] = s['next_run_time'].timestamp()
            s['trigger'] = s['trigger'].run_date.timestamp()
        logger.debug(state)
        lib.write('jobs', state)

    def _remove_job(self, index):
        jobs = self._jobs
        jobs.pop(index)
        self._jobs = jobs

    @ property
    def _jobs_index(self):
        return {j[0].id: j for j in self._jobs}

    def lookup_job(self, job_id):
        return self._jobs_index.get(job_id, (None, None))[0]

    def get_due_jobs(self, now):
        now_timestamp = datetime_to_utc_timestamp(now)
        pending = []
        for job, timestamp in self._jobs:
            if timestamp is None or timestamp > now_timestamp:
                break
            pending.append(job)

        return pending

    def get_next_run_time(self):
        return self._jobs[0][0].next_run_time if self._jobs else None

    def get_all_jobs(self):
        return [j[0] for j in self._jobs]

    def add_job(self, job):
        if job.id in self._jobs_index:
            raise ConflictingIdError(job.id)

        timestamp = datetime_to_utc_timestamp(job.next_run_time)
        index = self._get_job_index(timestamp, job.id)
        jobs = self._jobs
        jobs.insert(index, (job, timestamp))
        self._jobs = jobs

    def update_job(self, job):
        old_job, old_timestamp = self._jobs_index.get(job.id, (None, None))
        if old_job is None:
            raise JobLookupError(job.id)

        # If the next run time has not changed, simply replace the job in its present index.
        # Otherwise, reinsert the job to the list to preserve the ordering.
        old_index = self._get_job_index(old_timestamp, old_job.id)
        new_timestamp = datetime_to_utc_timestamp(job.next_run_time)
        if old_timestamp == new_timestamp:
            self._jobs[old_index] = (job, new_timestamp)
        else:
            self._remove_job(old_index)
            new_index = self._get_job_index(new_timestamp, job.id)
            self._jobs.insert(new_index, (job, new_timestamp))

    def remove_job(self, job_id):
        job, timestamp = self._jobs_index.get(job_id, (None, None))
        if job is None:
            raise JobLookupError(job_id)

        index = self._get_job_index(timestamp, job_id)
        self._remove_job(index)

    def remove_all_jobs(self):
        self._jobs = []

    def shutdown(self):
        pass

    def _get_job_index(self, timestamp, job_id):
        """
        Returns the index of the given job, or if it's not found, the index where the job should be
        inserted based on the given timestamp.

        :type timestamp: int
        :type job_id: str

        """
        lo, hi = 0, len(self._jobs)
        timestamp = float('inf') if timestamp is None else timestamp
        while lo < hi:
            mid = (lo + hi) // 2
            mid_job, mid_timestamp = self._jobs[mid]
            mid_timestamp = float(
                'inf') if mid_timestamp is None else mid_timestamp
            if mid_timestamp > timestamp:
                hi = mid
            elif mid_timestamp < timestamp:
                lo = mid + 1
            elif mid_job.id > job_id:
                hi = mid
            elif mid_job.id < job_id:
                lo = mid + 1
            else:
                return mid

        return lo
